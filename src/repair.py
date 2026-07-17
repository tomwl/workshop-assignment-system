# -*- coding: utf-8 -*-
"""
Created on Fri Jul 17 09:37:29 2026

@author: tom
"""

import days
import scoring

def tryMoveSomeoneElse(unassignedStudent,
                       desiredWorkshop,
                       workshops,
                       forms,
                       day):

    for occupant in desiredWorkshop.getStudentsOnDay(day).copy():
        # don't move preassigned students
        if desiredWorkshop.preAssigned:
            continue
        if occupant not in desiredWorkshop.getStudentsOnDay(day):
            continue

        # can occupant move?
        for alternative in occupant.getAvailablePreferencesAscByPopularity(day):
            if (alternative == desiredWorkshop 
                or alternative.isFull(day) 
                or alternative.isTwoDay):
                continue
            
            old_score = scoring.scoreWorkshops(workshops, forms, day)
            # move occupant
            alternative.moveStudentToDay(occupant, day)

            # assign rescued student
            desiredWorkshop.assignStudentToDay(unassignedStudent, day)
            
            new_score = scoring.scoreWorkshops(workshops, forms, day)
            
            # if the scoring is lower (=better), then keep the change
            if new_score.total < old_score.total:
                return True
            
            # else revert back
            desiredWorkshop.moveStudentToDay(occupant, day)
            unassignedStudent.removeFromWorkshop(day)

    return False

def repairStudent(student, workshops, forms, day):
    prefs = student.getAllValidPrefences(day)
    for desiredWorkshop in prefs:
        # skip two day workshops
        if desiredWorkshop.isTwoDay:
            continue
        
        # if space exists
        if not desiredWorkshop.isFull(day):
            desiredWorkshop.assignStudentToDay(student, day)
            return True

        # workshop full, try swapping
        if tryMoveSomeoneElse(student,
                              desiredWorkshop,
                              workshops,
                              forms,
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
                if repairStudent(student, workshops, forms, days.day1):
                    improved = True

            if student.getWorkshopOnDay(days.day2) is None:
                if repairStudent(student, workshops, forms, days.day2):
                    improved = True
