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
    
    other_day = days.day2 if day == days.day1 else days.day1
    for occupant in desiredWorkshop.getStudentsOnDay(day).copy():
        # don't move preassigned students
        if desiredWorkshop.preAssigned:
            continue
        if occupant not in desiredWorkshop.getStudentsOnDay(day):
            continue

        # can occupant move?
        for alternative in occupant.getAvailablePreferencesAscByPopularity(day):
            if (alternative == desiredWorkshop 
                or occupant.getWorkshopOnDay(other_day) == alternative
                or alternative.isFull(day) 
                or alternative.isTwoDay):
                continue
            
            old_score = scoring.scoreWorkshops(workshops, forms, day)
            # move occupant
            if not alternative.moveStudentToDay(occupant, day):
                raise RuntimeError("Failed to move student to new workshop")

            # assign rescued student
            desiredWorkshop.assignStudentToDay(unassignedStudent, day)
            
            new_score = scoring.scoreWorkshops(workshops, forms, day)
            
            # if the scoring is lower (=better), then keep the change
            if new_score.total < old_score.total:
                return True
            
            # else revert back
            if not desiredWorkshop.moveStudentToDay(occupant, day):
                raise RuntimeError("Failed to revert student move")
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
    students_checked = 0
    successful_moves = 0
    
    max_cycles = 10
    cycle = 0
    
    improved = True
    while improved and cycle < max_cycles:
        cycle += 1
        old_score = (
            scoring.scoreWorkshops(workshops, forms, days.day1).total
            + scoring.scoreWorkshops(workshops, forms, days.day2).total
            )
        students = [s for f in forms for s in f.getStudents()]

        for student in students:
            students_checked += 1
            if student.getWorkshopOnDay(days.day1) is None:
                if repairStudent(student, workshops, forms, days.day1):
                    successful_moves += 1
                    improved = True

            if student.getWorkshopOnDay(days.day2) is None:
                if repairStudent(student, workshops, forms, days.day2):
                    successful_moves += 1
                    improved = True
            if students_checked > 1000 and students_checked % 200 == 0:
                print(
                    "Students checked:", students_checked,
                    "Successful moves:", successful_moves
                )
        new_score = (
            scoring.scoreWorkshops(workshops, forms, days.day1).total
            + scoring.scoreWorkshops(workshops, forms, days.day2).total
            )
        if new_score < old_score:
            improved = True
        else:
            improved = False
