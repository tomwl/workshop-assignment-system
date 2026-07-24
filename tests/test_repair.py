# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 11:42:07 2026

@author: tom

execute in command line in src directory:
    python -m pytest ../tests/ -v to run all tests
"""

import pytest
import days
import form
import student
import workshop
import repair

# ----------------------------------
# Helpers
# ----------------------------------

def make_form(name="1A"):
    return form.Form(name)

def make_student(first_name="John", last_name="Smith", f=None):
    if f is None:
        f = form.Form("1A")

    return student.Student(first_name, last_name, f)


def make_workshop(
        name="Workshop 1",
        capacity=2,
        min_max_years=None,
        is_two_day=False):

    if min_max_years is None:
        min_max_years = {
            days.day1: (1, 4),
            days.day2: (1, 4),
        }

    return workshop.Workshop(
        name,
        capacity,
        min_max_years,
        is_two_day
    )

# ----------------------------------
# Tests for repairStudent
# ----------------------------------

def test_repairStudent_assigns_student_to_available_preference():
    f = make_form()
    s = make_student(f=f)

    ws = make_workshop()

    s.assignPreference(ws)

    result = repair.repairStudent(
        s,
        [ws],
        days.day1
    )

    assert result is True
    assert s.getWorkshopOnDay(days.day1) == ws
    assert s in ws.getStudentsOnDay(days.day1)
    
def test_repairStudent_skips_two_day_workshop():
    f = make_form()
    s = make_student(f=f)

    ws = make_workshop(
        is_two_day=True
    )

    s.assignPreference(ws)

    result = repair.repairStudent(
        s,
        [ws],
        days.day1
    )

    assert result is False
    assert s.getWorkshopOnDay(days.day1) is None
    
def test_repairStudent_returns_false_with_no_preferences():
    f = make_form()
    s = make_student(f=f)

    result = repair.repairStudent(
        s,
        [],
        days.day1
    )

    assert result is False
    assert s.getWorkshopOnDay(days.day1) is None
    
def test_repairStudent_returns_false_when_workshop_full():
    f = make_form()

    student1 = make_student("John", "Smith", f)
    student2 = make_student("Jane", "Smith", f)
    unassigned = make_student("Bob", "Smith", f)

    ws = make_workshop(capacity=2)

    for s in [student1, student2]:
        s.assignPreference(ws)
        ws.assignStudentToDay(s, days.day1)

    unassigned.assignPreference(ws)

    result = repair.repairStudent(
        unassigned,
        [ws],
        days.day1
    )

    assert result is False
    assert unassigned.getWorkshopOnDay(days.day1) is None
    
    
# ----------------------------------
# Tests for tryMoveSomethingElse
# ----------------------------------

def test_tryMoveSomeoneElse_moves_student_when_score_improves():
    f = make_form()

    occupant = make_student("John", "Smith", f)
    existing = make_student("Jane", "Smith", f)
    unassigned = make_student("Bob", "Smith", f)

    desired = make_workshop(
        name="Desired",
        capacity=1
    )

    alternative = make_workshop(
        name="Alternative",
        capacity=2
    )

    # Occupant is currently alone in Desired
    desired.assignStudentToDay(
        occupant,
        days.day1
    )

    # Existing student is in Alternative
    alternative.assignStudentToDay(
        existing,
        days.day1
    )

    # Occupant wants Alternative as an alternative preference
    occupant.assignPreference(alternative)

    result = repair.tryMoveSomeoneElse(
        unassigned,
        desired,
        [desired, alternative],
        days.day1
    )

    assert result is True

    assert occupant.getWorkshopOnDay(days.day1) == alternative
    assert occupant in alternative.getStudentsOnDay(days.day1)

    assert unassigned.getWorkshopOnDay(days.day1) == desired
    assert unassigned in desired.getStudentsOnDay(days.day1)
    
    
def test_tryMoveSomeoneElse_reverts_if_score_does_not_improve():
    f = make_form()

    occupant = make_student("John", "Smith", f)
    alternative_student = make_student("Jane", "Smith", f)
    unassigned = make_student("Bob", "Smith", f)

    desired = make_workshop(
        name="Desired",
        capacity=1
    )

    alternative = make_workshop(
        name="Alternative",
        capacity=2
    )

    desired.assignStudentToDay(
        occupant,
        days.day1
    )

    alternative.assignStudentToDay(
        alternative_student,
        days.day1
    )

    occupant.assignPreference(desired)

    result = repair.tryMoveSomeoneElse(
        unassigned,
        desired,
        [desired, alternative],
        days.day1
    )

    assert result is False

    # Occupant should have been restored
    assert occupant.getWorkshopOnDay(days.day1) == desired
    assert occupant in desired.getStudentsOnDay(days.day1)

    # Unassigned student should remain unassigned
    assert unassigned.getWorkshopOnDay(days.day1) is None
    

def test_tryMoveSomeoneElse_skips_full_alternative():
    f = make_form()

    occupant = make_student("John", "Smith", f)
    alternative_student = make_student("Jane", "Smith", f)
    another_student = make_student("Bob", "Smith", f)
    unassigned = make_student("Alice", "Smith", f)

    desired = make_workshop(
        name="Desired",
        capacity=1
    )

    alternative = make_workshop(
        name="Alternative",
        capacity=2
    )

    desired.assignStudentToDay(
        occupant,
        days.day1
    )

    alternative.assignStudentToDay(
        alternative_student,
        days.day1
    )

    alternative.assignStudentToDay(
        another_student,
        days.day1
    )

    occupant.assignPreference(alternative)

    result = repair.tryMoveSomeoneElse(
        unassigned,
        desired,
        [desired, alternative],
        days.day1
    )

    assert result is False

    assert occupant.getWorkshopOnDay(days.day1) == desired
    assert unassigned.getWorkshopOnDay(days.day1) is None
    

def test_tryMoveSomeoneElse_skips_two_day_alternative():
    f = make_form()

    occupant = make_student(f=f)
    unassigned = make_student("Jane", "Smith", f)

    desired = make_workshop(
        name="Desired",
        capacity=1
    )

    alternative = make_workshop(
        name="Alternative",
        capacity=2,
        is_two_day=True
    )

    desired.assignStudentToDay(
        occupant,
        days.day1
    )

    occupant.assignPreference(alternative)

    result = repair.tryMoveSomeoneElse(
        unassigned,
        desired,
        [desired, alternative],
        days.day1
    )

    assert result is False
    assert occupant.getWorkshopOnDay(days.day1) == desired
    assert unassigned.getWorkshopOnDay(days.day1) is None
    

# ----------------------------------
# Tests for repairAssignments
# ----------------------------------
def test_repairAssignments_assigns_unassigned_student():
    f = make_form()

    s = make_student(f=f)

    ws = make_workshop()

    s.assignPreference(ws)
    f.addStudent(s)

    repair.repairAssignments(
        [f],
        [ws]
    )

    assert s.getWorkshopOnDay(days.day1) == ws
    
def test_repairAssignments_assigns_student_on_both_days():
    f = make_form()

    s = make_student(f=f)

    ws1 = make_workshop(
        name="Workshop 1"
    )

    ws2 = make_workshop(
        name="Workshop 2"
    )

    s.assignPreference(ws1)
    s.assignPreference(ws2)

    f.addStudent(s)

    repair.repairAssignments(
        [f],
        [ws1, ws2]
    )

    assert s.getWorkshopOnDay(days.day1) is not None
    assert s.getWorkshopOnDay(days.day2) is not None
    
def test_repairAssignments_does_not_assign_two_day_workshop_on_day2():
    f = make_form()

    s = make_student(f=f)

    two_day = make_workshop(
        name="Two Day",
        is_two_day=True
    )

    s.assignPreference(two_day)

    two_day.assignStudentToDay(
        s,
        days.day1
    )

    f.addStudent(s)

    repair.repairAssignments(
        [f],
        [two_day]
    )

    assert s.getWorkshopOnDay(days.day1) == two_day
    assert s.getWorkshopOnDay(days.day2) is None
