# -*- coding: utf-8 -*-
"""
Created on Wed Jan  1 15:49:10 2025

Handles the input and output of data for the program

@author: tom
"""

import pandas as pd
import workshop as ws
import student
import form
import days
import re
import unicodedata
from difflib import SequenceMatcher
from logging_config import logger

class FileIO:
    def __init__(self, pFile, wFile, sFout, wFout):
        self.prefencesFileIn = pFile
        self.workshopsFileIn = wFile
        self.studentsFileOut = sFout
        self.workshopsFileOut = wFout
        
    def initialiseWorkshops(self):
        """Read in the workshops list excel and create a list of workshops
        Requires excel in format: Name: str | Capacity: int | IsTwoDay: bool 
            | Mininum class: int | Maximum class: int
    
        Parameters
        ----------
        fname : str
            name of workshops excel list.
    
        Returns
        -------
        list of workshops.
    
        """
        workshops = pd.read_excel(self.workshopsFileIn, 
                                  engine="openpyxl",
                                  keep_default_na=False,  # don't convert NA
                                  dtype=str               # treat all cells as strings
                                  )
        result = []
        for index, row in workshops.iterrows():
            minMaxYears = {}
            if not row["MinMaxDay1"] == "":
                minMaxYears[days.day1] = tuple(
                    map(int, str(row["MinMaxDay1"]).split(',')))
            if not row["MinMaxDay2"] == "":
                minMaxYears[days.day2] = tuple(
                    map(int, str(row["MinMaxDay2"]).split(',')))
                
            result.append(ws.Workshop(row["Name"], 
                                      int(row["Capacity"]), 
                                      minMaxYears,
                                      row["IsTwoDay"].strip().upper() == "TRUE"))
        return result
    
    def initialisePreferences(self, workshops):
        """Create a list of forms filled with students and their preferences 

        Parameters
        ----------
        workshops : list of Workshops
            The list of workshops that can have students assigned to them.

        Returns
        -------
        forms : list of Form
            A list, where each form contains a list of students.

        """
        preferences = pd.read_excel(self.prefencesFileIn, keep_default_na=False)
        forms = []
        for index, row in preferences.iterrows():
            firstname = row["Vorname"]
            lastname = row["Nachname"]
            form_name = row["Klasse"]
            if not form_name:
                raise Exception("Student has no form")
            f = next((fo for fo in forms if fo.name == form_name), None)
            if f is None:
                # New form, add it to the list
                forms.append(form.Form(form_name))
                f = forms[-1]
            s = student.Student(firstname, lastname, f)
            # find and allocate preferences from workshop list
            for i in range(1, 6):
                preference_i = row["Wunsch " + str(i)]
                ws = [x for x in workshops if x.name == preference_i]
                if ws:
                    for result in ws:
                        s.assignPreference(result)
                else:
                    logger.warning("WARNING: WORKSHOP NOT FOUND: " + preference_i)
            f.addStudent(s)
        return forms
    
    def blockStudents(self, fin, students, workshops):
        """
        Some workshops have their students automatically assigned.
        This function reads in an excel list of students with the respective day
        that they are attending a certain workshop and sets the student's blocked
        dictionary to this workshop on this day and assigns the workshop this student

        Parameters
        ----------
        fin : str
            data file with the list of students and the workshops that they are
            pre-determined to attend on a given day
        students : list
            A list of all the students.
        workshops : list
            A list of all the workshops.

        Returns
        -------
        numberAssigned : list
            The students that are pre-assigned workshops.

        """
        data = pd.read_excel(fin, keep_default_na=False)
        preAssignedStudents = []
        for index, row in data.iterrows():
            firstname = row["Vorname"]
            lastname = row["Nachname"]
            dayNumber = row["Belegter Tag"]
            workshop = row["Workshop"]
            student = list(filter(
                lambda s: s.firstname == firstname and s.lastname == lastname, 
                students))
            day = next((s for s in days.daysList if str(dayNumber) in s), None)
            ws = next((x for x in workshops if x.name == workshop), None)
            if not student or not len(student) == 1 or not day or not ws:
                logger.warning("WARNING: STUDENT {0} {1} NOT ABLE TO BE BLOCKED"
                      .format(firstname, lastname))
                continue
            ws.preAssigned = True
            if not ws.assignStudentToDay(student[0], day, True):
                logger.warning("WARNING: STUDENT {0} {1} NOT ABLE TO BE ASSIGNED WORKSHOP"
                      .format(firstname, lastname))
                continue
            preAssignedStudents.append(student[0])
            
        return preAssignedStudents
        
        
    def writeWorkshops(self, workshops):
        """Given a list of workshops with students assigned, write this information
        to a file

        Parameters
        ----------
        workshops : list of Workshop
            The list of workshops with students assigned to them.

        Returns
        -------
        None.

        """
        data = []
        day = days.day1
        for w in workshops:
            wname = w.name
            students = w.getStudentsOnDay(day)
            for s in students:
                data.append([wname, s.getName(), s.form.name])
        df1 = pd.DataFrame(data, columns=['Workshop', 'Student Name', 'Class'])
        
        data = []
        day = days.day2
        for w in workshops:
            wname = w.name
            students = w.getStudentsOnDay(day)
            for s in students:
                data.append([wname, s.getName(), s.form.name])
        df2 = pd.DataFrame(data, columns=['Workshop', 'Student Name', 'Class'])
        with pd.ExcelWriter(self.workshopsFileOut) as writer:  
            df1.to_excel(writer, sheet_name=days.day1, index=False)
            df2.to_excel(writer, sheet_name=days.day2, index=False)
            
    def writeStudents(self, forms):
        """Given a list of forms, containing students to whom workshops have
        been assigned, write this information to file

        Parameters
        ----------
        forms : list of Form
            The forms containing the students and their assigned workshops.

        Returns
        -------
        None.

        """
        data = []
        for f in forms:
            for s in f.getStudents():
                data.append([s.getName(), str(s.getForm())] + s.getWorkshopNames())
        df = pd.DataFrame(data, 
                          columns=['Student Name', 'Class', 'Workshop day 1', 'Workshop day 2'])
        with pd.ExcelWriter(self.studentsFileOut) as writer:  
            df.to_excel(writer, index=False)

"""
The following functions are for pre-handling data and for checking 
against unassigned students
"""            
def readWriteStudentChoices(fin, 
                            fout, 
                            firstName_idx, 
                            lastName_idx, 
                            form_idx, 
                            ws_idx):
    """
    Reads in the data exported from MS forms and filters out unecessary  
    data and splits workshop preferences into individual columns
    Writes the results to a new file

    Parameters
    ----------
    fin : str
        file name to read - the one that comes from MS Forms results.
    fout : str
        file to write to.
    firstName_idx : int
        The column number (0-indexed) from fin with the first name.
    lastName_idx : int
        The column number (0-indexed) from fin with the last name.
    form_idx : int
        The column number (0-indexed) from fin with the form.
    ws_idx : int
        The column number (0-indexed) from fin with the workshop.

    Returns
    -------
    None.

    """
    data = pd.read_excel(fin, keep_default_na=False)
    dataOut = []
    studentsRead = []
    for index, row in data.iterrows():
        ws = row.iloc[ws_idx].split(";")
        ws = list(filter(None, ws))
        workshops = []
        for w in ws:
            n = re.sub("[\(\[].*?[\)\]]", "", w).strip()
            n = n.strip("...")
            workshops.append(n)
        firstname = row.iloc[firstName_idx]
        lastname = row.iloc[lastName_idx]
        form = row.iloc[form_idx]
        studentsRead.append(" ".join([firstname, lastname]))
        duplicate = next(
            filter(lambda it: it[0] == firstname and it[1] == lastname, dataOut), 
            None)
        if duplicate:
            dataOut.remove(duplicate)
        dataOut.append([firstname, lastname, form] + workshops)
        
    print(dataOut[0])
    try:
        df = pd.DataFrame(
            dataOut, 
            columns=['Vorname', 
                     'Nachname', 
                     'Klasse', 
                     'Wunsch 1', 'Wunsch 2', 'Wunsch 3', 'Wunsch 4', 'Wunsch 5'])
        with pd.ExcelWriter(fout) as writer:  
            df.to_excel(writer, index=False)
    except ValueError:
        # ToDo: handle this possible exception better...!
        print("ValueError: writing failed!")
    
def strip_accents(string): 
    return "".join(c for c in unicodedata.normalize("NFD", string) if not unicodedata.combining(c))         

def createForms(students, formName, firstName, lastName):
    forms = []
    for index, row in students.iterrows():
        form_name = row[formName]
        firstname = row[firstName].lower()
        lastname = row[lastName].lower()
        f = next((fo for fo in forms if fo.name == form_name), None)
        if f is None:
            forms.append(form.Form(form_name))
            f = forms[-1]
        s = student.Student(firstname, lastname, f)
        f.addStudent(s)
    return forms

def createFormsNew(students, formName, fullName):
    forms = []
    for index, row in students.iterrows():
        form_name = row[formName]
        name = row[fullName].lower().split(" ", 1)
        firstname = name[0]   
        lastname = name[1]
        f = next((fo for fo in forms if fo.name == form_name), None)
        if f is None:
            forms.append(form.Form(form_name))
            f = forms[-1]
        s = student.Student(firstname, lastname, f)
        f.addStudent(s)
    return forms
    
def compareStudentsAssignedWithActualStudents(fname_actual, fname_sorted, fout):
    """
    A big mess of a function to compare the students that have been assigned
    with a list of all school students to see who hasn't completed the survey

    Parameters
    ----------
    fname_actual : str
        Name of the excel sheet with the actual list of students in the school.
    fname_sorted : str
        Name of the excel sheet with the students who completed the survey.
    fout : str
        File name to write a list of students who never completed the survey.

    Returns
    -------
    None.

    """
    actualStudents = pd.read_excel(fname_actual, keep_default_na=False)
    classes = ('1', '2', '3', '4', '5', '6', '7')
    actualStudents = actualStudents[actualStudents.klasse.astype(str).str.startswith(classes)]          
    sortedStudents = pd.read_excel(fname_sorted, keep_default_na=False)
    # plan: organise into classes and then compare on a class by class basis
    actualForms = createForms(actualStudents, "klasse", "foreName", "longName")
    sortedForms = createFormsNew(sortedStudents, "Wähle deine Klasse aus!", "Name")
    names = set(list(sortedStudents["Name"]))
    # first compare the number of students in each case
    print(str(len(sortedStudents)) + " " + str(len(actualStudents)))
    missingStudents = []
    for f in actualForms:
        compareClass = list(filter(lambda c: c.name == f.name, sortedForms))
        if len(compareClass) > 1:
            raise RuntimeError("Too many matches")
        names = [s.getName() for s in compareClass[0].getStudents()]
        for s in f.getStudents():
            sname = s.getName().replace(" ", "")
            maxMatch = max(
                SequenceMatcher(a=sname,b=n.replace(" ", "")).ratio() for n in names)
            if not maxMatch > 0.9:
                print(sname + " " + str(maxMatch))
                missingStudents.append(s.getName())
    print(len(missingStudents))
    # finally write the leftovers to file
    df = pd.DataFrame(missingStudents, columns=['Name'])
    with pd.ExcelWriter("FehlenderSchuelerinnen.xlsx") as writer: 
        df.to_excel(writer, index=False)    
        
def main():
    #readWriteStudentChoices("Workshoptage 2026__Zukunft gestalten__Demokratie leben_.xlsx",
    #                        "student_data_2026.xlsx", 
    #                        5, 6, 7, 8)
    compareStudentsAssignedWithActualStudents("all_students_2026.xls", 
                                              "Workshoptage 2026__Zukunft gestalten__Demokratie leben_.xlsx", 
                                              "unassignedStudents.xlsx")
    
if __name__ == '__main__':
    main()