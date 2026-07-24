# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 10:49:34 2026

@author: tom

execute in command line in src directory:
    python -m pytest ../tests/ -v to run all tests
"""

import pytest

import days
import form
import student
import workshop

# ----------------------------------
# Helpers
# ----------------------------------

def make_form(name="1A"):
    return form.Form(name)

def make_student(first_name="John", last_name="Smith", f=None):
    if f is None:
        f = make_form()
    return student.Student(first_name, last_name, f)

def make_workshop(
        name="Workshop 1", 
        capacity=10, 
        min_max_years=None, 
        is_two_day=False):
    if min_max_years is None:
        min_max_years = {
            days.day1: (1, 4),
            days.day2: (1, 4)
        }
    
    return workshop.Workshop(
        name,
        capacity,
        min_max_years,
        is_two_day
    )

def add_preference(student_object, workshop_object):
    student_object.assignPreference(workshop_object)

# ----------------------------------
# Basic Form tests
# ----------------------------------

def test_form_initialises_with_empty_students_and_groups():
    f = make_form()
    
    assert f.getStudents() == []
    assert f.getGroups() == {}
    assert f.grouped == set()
    assert f.maxGroupSize == 3

def test_form_name_returns_correct_name():
    f = make_form("1A")
    
    assert f.name == "1A"
    assert str(f) == "1A"

def test_addStudent_adds_student():
    f = make_form()
    s = make_student(f)
    
    f.addStudent(s)
    
    assert f.getStudents() == [s]

def test_getStudents_returns_students():
    f = make_form()
    s1 = make_student("John", f=f)
    s2 = make_student("Jane", f=f)
    
    f.addStudent(s1)
    f.addStudent(s2)
    
    assert f.getStudents() == [s1, s2]
    
# ----------------------------------
# Student assignment / reset tests
# ----------------------------------

def test_studentsToAssign_returns_students_without_workshop_on_day():
    f = make_form()
    s1 = make_student("John", f=f)
    s2 = make_student("Jane", f=f)
    ws = make_workshop()
    
    f.addStudent(s1)
    f.addStudent(s2)
    
    s1.assignWorkshop(ws, days.day1)
    
    assert f.studentsToAssign(days.day1) == [s2]

def test_studentsToAssign_returns_all_students_when_none_assigned():
    f = make_form()
    s1 = make_student("John", f=f)
    s2 = make_student("Jane", f=f)
    
    f.addStudent(s1)
    f.addStudent(s2)
    
    assert f.studentsToAssign(days.day1) == [s1, s2]

def test_getNumberOfUnassigned_returns_correct_number():
    f = make_form()
    s1 = make_student("John", f=f)
    s2 = make_student("Jane", f=f)
    ws = make_workshop()
    
    f.addStudent(s1)
    f.addStudent(s2)
    
    s1.assignWorkshop(ws, days.day1)
    
    assert f.getNumberOfUnassigned(days.day1) == 1

def test_getNumberOfUnassigned_returns_zero_when_all_assigned():
    f = make_form()
    s1 = make_student("John", f=f)
    s2 = make_student("Jane", f=f)
    ws = make_workshop()
    
    f.addStudent(s1)
    f.addStudent(s2)
    
    s1.assignWorkshop(ws, days.day1)
    s2.assignWorkshop(ws, days.day1)
    
    assert f.getNumberOfUnassigned(days.day1) == 0

def test_resetStudentsWorkshop_resets_non_preassigned_workshops():
    f = make_form()
    s = make_student(f=f)
    ws = make_workshop()
    
    f.addStudent(s)
    s.assignWorkshop(ws, days.day1)
    
    f.resetStudentsWorkshop()
    
    assert s.getWorkshopOnDay(days.day1) is None

def test_resetStudentsWorkshop_does_not_reset_preassigned_workshops():
    f = make_form()
    s = make_student(f=f)
    ws = make_workshop()
    ws.preAssigned = True
    
    f.addStudent(s)
    s.assignWorkshop(ws, days.day1)
    
    f.resetStudentsWorkshop()
    
    assert s.getWorkshopOnDay(days.day1) == ws
    
# ----------------------------------
# Group/reset tests
# ----------------------------------

def test_resetGroups_clears_groups_and_grouped_students():
    f = make_form()
    s = make_student(f=f)
    
    f.groups["Workshop 1"] = {s}
    f.grouped.add(s)
    
    f.resetGroups()
    
    assert f.getGroups() == {}
    assert f.grouped == set()
    
# ----------------------------------
# Grouping students
# ----------------------------------

def test_groupStudentsTogether_groups_two_students_with_matching_preference():
    f = make_form()
    
    s1 = make_student("John", f=f)
    s2 = make_student("Jane", f=f)
    
    ws = make_workshop("Workshop 1")
    
    add_preference(s1, ws)
    add_preference(s2, ws)
    
    f.addStudent(s1)
    f.addStudent(s2)
    
    f.groupStudentsTogether([s1, s2], days.day1)
    
    assert "Workshop 1" in f.groups
    assert s1 in f.groups["Workshop 1"]
    assert s2 in f.groups["Workshop 1"]
    
    assert s1 in f.grouped
    assert s2 in f.grouped

def test_groupStudentsTogether_does_not_group_students_without_matching_preferences():
    f = make_form()
    
    s1 = make_student("John", f=f)
    s2 = make_student("Jane", f=f)
    
    ws1 = make_workshop("Workshop 1")
    ws2 = make_workshop("Workshop 2")
    
    add_preference(s1, ws1)
    add_preference(s2, ws2)
    
    f.groupStudentsTogether([s1, s2], days.day1)
    
    assert f.groups == {}
    assert f.grouped == set()

def test_groupStudentsTogether_does_not_group_already_grouped_students():
    f = make_form()
    
    s1 = make_student("John", f=f)
    s2 = make_student("Jane", f=f)
    
    ws = make_workshop("Workshop 1")
    
    add_preference(s1, ws)
    add_preference(s2, ws)
    
    f.grouped.add(s1)
    
    f.groupStudentsTogether([s1, s2], days.day1)
    
    assert f.groups == {}

def test_groupStudents_does_not_group_students_already_assigned():
    f = make_form()
    
    s1 = make_student("John", f=f)
    s2 = make_student("Jane", f=f)
    
    ws = make_workshop("Workshop 1")
    
    add_preference(s1, ws)
    add_preference(s2, ws)
    
    f.addStudent(s1)
    f.addStudent(s2)
    
    s1.assignWorkshop(ws, days.day1)
    
    f.groupStudents(days.day1)
    
    # Only s2 is eligible for grouping because s1 is already assigned
    assert s1 not in f.grouped

def test_groups_do_not_exceed_max_group_size():
    f = make_form()
    f.maxGroupSize = 3
    
    students = [
        make_student("Student1", f=f),
        make_student("Student2", f=f),
        make_student("Student3", f=f),
        make_student("Student4", f=f),
    ]
    
    ws = make_workshop("Workshop 1")
    
    for s in students:
        add_preference(s, ws)
    
    f.groupStudentsTogether(students, days.day1)
    
    # The current algorithm creates pairs, but the group should never
    # exceed the configured maximum.
    assert len(f.groups["Workshop 1"]) <= f.maxGroupSize
    
    
# ----------------------------------
# Adding groups to workshops
# ----------------------------------

def test_addStudentGroupsToWorkshops_assigns_grouped_students():
    f = make_form()
    
    s1 = make_student("John", f=f)
    s2 = make_student("Jane", f=f)
    
    ws = make_workshop("Workshop 1")
    
    f.groups["Workshop 1"] = {s1, s2}
    
    f.addStudentGroupsToWorkshops([ws], days.day1)
    
    assert s1 in ws.getStudentsOnDay(days.day1)
    assert s2 in ws.getStudentsOnDay(days.day1)
    
    assert s1.getWorkshopOnDay(days.day1) == ws
    assert s2.getWorkshopOnDay(days.day1) == ws

def test_addStudentGroupsToWorkshops_does_not_assign_when_workshop_full():
    f = make_form()
    
    s1 = make_student("John", f=f)
    s2 = make_student("Jane", f=f)
    
    ws = make_workshop("Workshop 1", capacity=1)
    
    f.groups["Workshop 1"] = {s1, s2}
    
    f.addStudentGroupsToWorkshops([ws], days.day1)
    
    assert len(ws.getStudentsOnDay(days.day1)) == 1

def test_addStudentGroupsToWorkshops_ignores_workshop_not_in_list():
    f = make_form()
    
    s = make_student(f=f)
    ws = make_workshop("Workshop 1")
    
    f.groups["Workshop 1"] = {s}
    
    f.addStudentGroupsToWorkshops([], days.day1)
    
    assert s.getWorkshopOnDay(days.day1) is None
    assert ws.getStudentsOnDay(days.day1) == []
    
    
# ----------------------------------
# Adding unassigned students to existing groups
# ----------------------------------

def test_addUnassignedStudents_assigns_student_to_matching_existing_group():
    f = make_form()
    
    s1 = make_student("John", f=f)
    s2 = make_student("Jane", f=f)
    
    ws = make_workshop("Workshop 1")
    
    add_preference(s1, ws)
    add_preference(s2, ws)
    
    f.addStudent(s1)
    f.addStudent(s2)
    
    # Existing group
    f.groups["Workshop 1"] = {s1}
    f.grouped.add(s1)
    
    f.addUnassignedStudents([ws], days.day1)
    
    assert s2.getWorkshopOnDay(days.day1) == ws
    assert s2 in ws.getStudentsOnDay(days.day1)

def test_addUnassignedStudents_does_not_assign_student_without_matching_group():
    f = make_form()
    
    s = make_student(f=f)
    
    ws1 = make_workshop("Workshop 1")
    ws2 = make_workshop("Workshop 2")
    
    add_preference(s, ws1)
    
    f.addStudent(s)
    
    # Existing group is for another workshop
    f.groups["Workshop 2"] = set()
    
    f.addUnassignedStudents([ws1, ws2], days.day1)
    
    assert s.getWorkshopOnDay(days.day1) is None

def test_addUnassignedStudents_does_not_assign_when_matching_workshop_is_full():
    f = make_form()
    
    s1 = make_student("John", f=f)
    s2 = make_student("Jane", f=f)
    
    ws = make_workshop("Workshop 1", capacity=1)
    
    add_preference(s1, ws)
    add_preference(s2, ws)
    
    f.groups["Workshop 1"] = {s1}
    f.grouped.add(s1)
    
    s1.assignWorkshop(ws, days.day1)
    ws.students[days.day1].append(s1)
    
    f.addUnassignedStudents([ws], days.day1)
    
    assert s2.getWorkshopOnDay(days.day1) is None
    
    
# ----------------------------------
# Assigning leftover students
# ----------------------------------

def test_assignLeftoverStudents_assigns_student_to_available_preference():
    f = make_form()
    
    s = make_student(f=f)
    ws = make_workshop("Workshop 1")
    
    add_preference(s, ws)
    
    f.addStudent(s)
    
    f.assignLeftoverStudents([ws], days.day1)
    
    assert s.getWorkshopOnDay(days.day1) == ws
    assert s in ws.getStudentsOnDay(days.day1)

def test_assignLeftoverStudents_tries_next_preference_if_first_is_full():
    f = make_form()
    
    s = make_student(f=f)
    
    ws1 = make_workshop("Workshop 1", capacity=0)
    ws2 = make_workshop("Workshop 2", capacity=10)
    
    add_preference(s, ws1)
    add_preference(s, ws2)
    
    f.addStudent(s)
    
    f.assignLeftoverStudents([ws1, ws2], days.day1)
    
    assert s.getWorkshopOnDay(days.day1) == ws2

def test_assignLeftoverStudents_leaves_student_unassigned_if_no_workshop_available():
    f = make_form()
    
    s = make_student(f=f)
    
    ws = make_workshop("Workshop 1", capacity=0)
    
    add_preference(s, ws)
    
    f.addStudent(s)
    
    f.assignLeftoverStudents([ws], days.day1)
    
    assert s.getWorkshopOnDay(days.day1) is None
    
    
# ----------------------------------
# Sorting / popularity
# ----------------------------------

def test_students_with_fewer_available_preferences_are_processed_first():
    f = make_form()
    
    s1 = make_student("John", f=f)
    s2 = make_student("Jane", f=f)
    
    ws1 = make_workshop("Workshop 1")
    ws2 = make_workshop("Workshop 2")
    
    add_preference(s1, ws1)
    
    add_preference(s2, ws1)
    add_preference(s2, ws2)
    
    f.addStudent(s1)
    f.addStudent(s2)
    
    # This mainly tests the intended behaviour indirectly:
    # both students should still be assigned successfully.
    f.assignLeftoverStudents([ws1, ws2], days.day1)
    
    assert s1.getWorkshopOnDay(days.day1) is not None
    assert s2.getWorkshopOnDay(days.day1) is not None
    
    
# ----------------------------------
# Day 2-specific behaviour
# ----------------------------------

def test_grouping_on_day2_does_not_use_two_day_workshops():
    f = make_form()
    
    s1 = make_student("John", f=f)
    s2 = make_student("Jane", f=f)
    
    two_day_ws = make_workshop(
        "Two Day Workshop",
        is_two_day=True
    )
    
    add_preference(s1, two_day_ws)
    add_preference(s2, two_day_ws)
    
    f.groupStudentsTogether([s1, s2], days.day2)
    
    assert f.groups == {}

def test_assignLeftoverStudents_does_not_assign_two_day_workshop_on_day2():
    f = make_form()
    
    s = make_student(f=f)
    
    two_day_ws = make_workshop(
        "Two Day Workshop",
        is_two_day=True
    )
    
    add_preference(s, two_day_ws)
    
    f.assignLeftoverStudents([two_day_ws], days.day2)
    
    assert s.getWorkshopOnDay(days.day2) is None