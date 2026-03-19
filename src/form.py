# -*- coding: utf-8 -*-
"""
Created on Tue Dec 31 10:51:19 2024

This file contains the Form class that works with a given form (group of students).
It contains functions to group students and assign students to available
workshops. Also to try and then assign ungrouped students in a form to a relevant
workshop

@author: tom
"""

import random
from logging_config import logger

class Form:
    def __init__(self, name: str):
        self._name = name
        self.students = []
        self.groups = {}
        self.grouped = set()
        self.maxGroupSize = 3
        
    def __str__(self):
        return self.name
        
    def addStudent(self, student):
        self.students.append(student)
        
    def getStudents(self):
        return self.students
    
    def resetStudentsWorkshop(self):
        for s in self.students:
            s.resetWorkshops()
    
    def shuffleStudentsPreferences(self, day):
        for s in self.studentsToAssign(day):
            s.shufflePreferences()
            
    def shuffleStudents(self):
        random.shuffle(self.students)
    
    def studentsToAssign(self, day):
        return list(filter(lambda s: s.workshops[day] is None, self.students))
        
    @property
    def name(self):
        return self._name
    
    def getGroups(self):
        return self.groups
    
    def getNumberOfUnassigned(self, day):
        return len(list(filter(lambda s: s.getWorkshopOnDay(day) is None, self.students)))
    
    def resetGroups(self):
        self.groups = {}
        self.grouped = set()
    
    def groupStudentsTogether(self, students, day):
        """group students based on matching preferences

        Parameters
        ----------
        students : list of Student
            The students to group.
        day : str
            Which workshop day: Day1 or Day2.

        Returns
        -------
        None.

        """
        for si in students:
            # first check the student isn't already ina  group
            if not si in self.grouped:
                # get their preferences
                prefi = si.getAvailablePreferencesAscByPopularity(day)
                #scan through others students 
                for sj in list(filter(lambda v: v is not si, students)):
                    # make sure that other student isn't grouped
                   if not sj in self.grouped:
                       # get the other student's preferences
                       prefj = sj.getAvailablePreferencesAscByPopularity(day)
                       # check for matches
                       matchingWS = next((k for k in prefi if k in prefj), None)
                       if not matchingWS is None:
                           if matchingWS.name not in self.groups:
                               self.groups[matchingWS.name] = set()
                           if len(self.groups[matchingWS.name]) < self.maxGroupSize:
                                self.groups[matchingWS.name].add(si)
                                self.groups[matchingWS.name].add(sj)
                                self.grouped.add(si)
                                self.grouped.add(sj)
                           
         
    def groupStudents(self, day):
        """Organise students together into groups
        
        Parameters
        ----------
        day : str
            Which workshop day: Day1 or Day2.

        Returns
        -------
        None.

        """
        #students = self.studentsToAssign(day)
        students = sorted(
            self.studentsToAssign(day),
            key=lambda s: len(s.getAvailablePreferencesAscByPopularity(day))
        )
        self.groupStudentsTogether(students, day)
        # scanning back down the list can help to find some new groups
        self.groupStudentsTogether(reversed(students), day)
                
    def addStudentGroupsToWorkshops(self, workshops, day):
        """Add the now organised groups of students to workshops 
        The workshops class will check where this is possible, as it may
        be that a workshop is full on that day
        
        Parameters
        ----------
        workshops : list of Workshop
            The workshops that will be assigned student groups.
        day : str
            Which workshop day: Day1 or Day2.
            
        Returns
        -------
        None.

        """
        for key, value in self.groups.items():
            w = [x for x in workshops if x.name == key]
            for ws in w:
                for s in value:
                    success = ws.assignStudentToDay(s, day)
                    if not success:
                        logger.warning(
                            "Student %s from group not assigned workshop on day %s" 
                            % (s, day))
                
    def addUnassignedStudents(self, workshops, day):
        """Try to add ungrouped students to workshops based on their preferences
        and which workshops have space on this day

        Parameters
        ----------
        workshops : list of Workshop
            The workshops that can be assigned to.
        day : str
            Which workshop day: Day1 or Day2.

        Returns
        -------
        None.

        """
        #unassignedStudents = self.studentsToAssign(day)
        unassignedStudents = sorted(
            self.studentsToAssign(day),
            key=lambda s: len(s.getAvailablePreferencesAscByPopularity(day))
        )
        for student in unassignedStudents:
            success = False
            prefs = [p.name for p in student.getAvailablePreferencesAscByPopularity(day)]
            availableGroupKeys = list(
                filter(lambda k: k in prefs, self.groups.keys()))
            if not availableGroupKeys: 
                # none of the students prefs align with existing groups
                logger.warning(
                            "No groups found. Student %s not assigned workshop on day %s" 
                            % (student, day))
                logger.info("Preferences:")
                logger.info("%s" % ",".join(prefs))
                logger.info("Available workshops:")
                logger.info("%s" % ",".join(availableGroupKeys))
                continue            
            for key in availableGroupKeys:
                # try and assign student to an available group
                w = [x for x in workshops if x.name == key]
                for ws in w:
                    # try and assign them to a workshop (but may be full)
                    success = ws.assignStudentToDay(student, day)
                    self.grouped.add(student)
                    if success:
                        break
            # all the free workshops that matched existing groups in the class were full
            if not success:
                logger.warning(
                    "No free workshops. Student %s not assigned workshop on day %s" 
                    % (student, day))
                
    def assignLeftoverStudents(self, workshops, day):
        #students = self.studentsToAssign(day)
        students = sorted(
            self.studentsToAssign(day),
            key=lambda s: len(s.getAvailablePreferencesAscByPopularity(day))
        )
        for s in students:
            success = False
            for p in s.getAvailablePreferencesAscByPopularity(day):
                p_name = p.name
                w = [x for x in workshops if x.name == p_name]
                for ws in w:
                    success = ws.assignStudentToDay(s, day)
                    if success:
                        break
            if not success:
                # TODO: obviously need to add something here!!
                #print("This student hasn't been assigned a workshop!! {0}".format(s.getName()))
                pass