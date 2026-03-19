# -*- coding: utf-8 -*-
"""
Created on Thu Dec 19 11:54:03 2024

A program to organise the workshop days at Draschestraße

@author: tom
"""

import os
import FileIO
from logging_config import logger
from logging_config import logging_cleanup
import days
import numpy as np

# TODO: try and spread the kids more to avoid tiny workshop class sizes, also over the days
# TODO: make sure that someone who is alone on day one is not alone on day 2

# if there are less than this number of students who want to do a workshop it is "low demand"
low_demand_workshop_value = 40

# the number of iterations we should perform to try and best match students to workshops
iterations = 20000
    
def assignWorkshops(forms, workshops, fileIO):
    """
    This is where the main assignment of workshops happens.
    The basic idea is to assign students in groups to workshops on the days.
    The procedure is iterated many times with the students in each form
    shuffled in between to try and optimise the maximum number of 
    students assigned to a workshop with a fellow classmate

    Parameters
    ----------
    forms : list of class Form
        The classes in the school.
    workshops : list of class Workshop
        The workshops.
    fileIO : class FileIO
        FileIO class for manging writing of data to excel.

    Returns
    -------
    None.

    """
    optimise = True
    counter = 1
    unassignedlist = []
    
    while optimise and counter <= iterations:
        logger.info("Iteration %s" % counter)
        day = days.day1
        unassigned = 0
        for w in workshops:
            w.resetStudents()
        for f in forms:
            f.resetStudentsWorkshop()             
            f.shuffleStudents()
            assignLessDemand(f, workshops, day)     
            f.groupStudents(day)
            f.addStudentGroupsToWorkshops(workshops, day)
            f.addUnassignedStudents(workshops, day)
            for s in f.getStudents():
                ws = s.workshops[day]
                if not ws is None and ws.isTwoDay:
                    s.copyDay1Workshop()
            f.assignLeftoverStudents(workshops, day)
            f.resetGroups()
            unassigned += f.getNumberOfUnassigned(day)
            
        for w in workshops:
            if w.isTwoDay:
                w.copyDay1Students()
                
        day = days.day2
        for f in forms: 
            f.shuffleStudents()
            assignLessDemand(f, workshops, day)
            f.groupStudents(day)
            f.addStudentGroupsToWorkshops(workshops, day)
            f.addUnassignedStudents(workshops, day)
            f.assignLeftoverStudents(workshops, day)
            f.resetGroups()
            unassigned += f.getNumberOfUnassigned(day)
        
        # if unassigned < 30 then this is awesome and we can stop after this iteration
        if unassigned < 30:
            optimise = False
        if np.all(np.array(unassignedlist) > unassigned):
            errorChecking(workshops, getAllStudents(forms))
            fileIO.writeWorkshops(workshops)
            fileIO.writeStudents(forms)
        unassignedlist.append(unassigned)       
        counter += 1
        logger.warning("Unassigned = %s" % unassigned)
        
    logger.warning("Unassigned %s", unassignedlist)
    logger.warning("Min unassigned %s", min(unassignedlist))
    print("Unassigned min. " + str(min(unassignedlist)))
    
    
def getAllStudents(forms):
    return [s for f in forms for s in f.getStudents()]

def errorChecking(workshops, students):    
    for w in workshops:
        if w.isTwoDay and not w.getStudentsOnDay(days.day1) == w.getStudentsOnDay(days.day2):
            raise RuntimeError("Two day workshop students don't match")
    names = (w.getStudentsOnDay(days.day1) for w in workshops)
    names = [j for sub in names for j in sub]
    if not len(names) == len(set(names)):
        raise RuntimeError("Student has been assigned two workshops on day1")
    names = list(w.getStudentsOnDay(days.day2) for w in workshops)
    names = [j for sub in names for j in sub]   

    for s in students:
        for ws in s.workshops.values():
            if ws is not None and ws not in s.getAllPreferences():
                raise RuntimeError("Student has been assigned workshop not in preferences")
        if s.hasSameWorkshopsAndNotTwoDay():
            raise RuntimeError("Student has been assigned same workshops on both days")

def assignLessDemand(form, workshops, day):
    for s in form.studentsToAssign(day):
        assignedWorkshop = False
        for p in s.getAvailablePreferencesAscByPopularity(day):
            if p.prospectiveStudents <= low_demand_workshop_value and not assignedWorkshop:
                p_name = p.name
                w = [x for x in workshops if x.name == p_name]
                for ws in w:
                    if ws.assignStudentToDay(s, day):
                        assignedWorkshop = True
                        break
 
def getProspectiveStudentCountForWorkshops(forms, preAssignedStudents):
    for f in forms:
        for s in f.getStudents():
            if s in preAssignedStudents:
                continue
            for p in s.getAllPreferences():
                p.prospectiveStudents += 1  
                
def orderForms(forms):
    # the 2nd arg of int is needed as getName of form 1A or 2C etc. --> convert from hex
    return sorted(forms, key=lambda f: int(f.name, 16))
           
def main():
    try:
        # read in the student preferences and workshop names
        preferenceFile = os.path.join(os.getcwd(), 'student_data_2026.xlsx')
        workshopsFile = os.path.join(os.getcwd(), 'Workshops_LIO.xlsx')
        studentFileOut = "test_students_1.xlsx"
        workshopsFileOut = "test_workshops_1.xlsx"
        fileIO = FileIO.FileIO(
            preferenceFile, workshopsFile, studentFileOut, workshopsFileOut)
        workshops = fileIO.initialiseWorkshops()
        
        # assign students to forms (e.g. 1A, 2C, etc.)
        forms = fileIO.initialisePreferences(workshops)
        
        # force assign students that have already had a workshop decided for them
        preAssignedStudents = fileIO.blockStudents('ListeChinesischUndSI.xlsx', 
                                               getAllStudents(forms), 
                                               workshops)
        
        
        # filter in case students are too young/old for a workshop
        for f in forms:
            for s in f.getStudents():
                s.filterPreferencesByAge()
                
        # figure out how many people want to do each workshop
        getProspectiveStudentCountForWorkshops(forms, preAssignedStudents)
        
        # order the list of forms 1A, 1B, 1C, ..., 2A, ...
        forms = orderForms(forms)
        
        # this is where the magic happens
        assignWorkshops(forms, workshops, fileIO)
        
        # print some stuff at the end to get some feeling for the results
        #for w in workshops:
         #   print(w.name, w.prospectiveStudents)
          #  print(len(w.getStudentsOnDay(days.day1)))
           # print(len(w.getStudentsOnDay(days.day2)))
    finally:
        logging_cleanup()
    
if __name__ == '__main__':
    main()
    