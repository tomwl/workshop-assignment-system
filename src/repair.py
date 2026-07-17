# -*- coding: utf-8 -*-
"""
Created on Fri Jul 17 09:37:29 2026

@author: tom
"""

import days

def tryMoveSomeoneElse(unassignedStudent,
                       desiredWorkshop,
                       workshops,
                       day):

    occupants = list(desiredWorkshop.getStudentsOnDay(day))
    for occupant in occupants:
        #
        # don't move preassigned students
        #
        if desiredWorkshop.preAssigned:
            continue

        #
        # can occupant move?
        #
        for alternative in occupant.getAvailablePreferencesAscByPopularity(day):
            if (alternative == desiredWorkshop 
                or alternative.isFull(day) 
                or alternative.isTwoDay):
                continue
            
            #
            # move occupant
            #
            desiredWorkshop.getStudentsOnDay(day).remove(occupant)
            alternative.assignStudentToDay(occupant, day)

            #
            # assign rescued student
            #
            desiredWorkshop.assignStudentToDay(unassignedStudent, day)

            return True

    return False

def repairStudent(student, workshops, day):
    prefs = student.getAllValidPrefences(day)
    for desiredWorkshop in prefs:
        # skip two day workshops
        if desiredWorkshop.isTwoDay:
            continue
        
        #
        # if space exists
        #
        if not desiredWorkshop.isFull(day):
            desiredWorkshop.assignStudentToDay(student, day)
            return True

        #
        # workshop full
        #
        if tryMoveSomeoneElse(student,
                              desiredWorkshop,
                              workshops,
                              day):
            return True

    return False

def repairAssignments(forms, workshops):
    improved = True
    while improved:
        improved = False
        students = [s for f in forms for s in f.getStudents()]

        for student in students:
            if student.getWorkshopOnDay(days.day1) is None:
                if repairStudent(student, workshops, days.day1):
                    improved = True

            if student.getWorkshopOnDay(days.day2) is None:
                if repairStudent(student, workshops, days.day2):
                    improved = True
