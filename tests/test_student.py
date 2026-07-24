# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 10:21:29 2026

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
# Helper methods
# ----------------------------------

def make_form(form_name="1A"):
    return form.Form(form_name)


def make_student(
    first_name="Tom",
    last_name="Smith",
    f = None
    ):
    if f is None:
        f = make_form()
    return student.Student(first_name, last_name, f)


def make_workshop(
    name="Workshop 1",
    capacity=10,
    min_max_years=None,
    is_two_day=False
    ):
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

# ----------------------------------
# Tests for constructor and strings
# ----------------------------------

def test_constructor_sets_name():
    s = make_student()

    assert s.firstname == "Tom"
    assert s.lastname == "Smith"
    assert s.form.name == "1A"
    assert s.year == 1
    
def test_constructor_starts_with_no_workshops():
    s = make_student()

    assert s.getWorkshops() == [None, None]
    
def test_constructor_starts_with_no_preferences():
    s = make_student()

    assert s.getAllPreferences() == []
    
def test_getName_returns_full_name():
    s = make_student(
        first_name="Tom",
        last_name="Smith"
    )

    assert s.getName() == "Tom Smith"
    
def test_getForm_returns_students_form():
    f = make_form("3A")
    s = student.Student("Tom", "Smith", f)

    assert s.getForm() == f
    
def test_str_returns_expected_string():
    s = make_student(
        first_name="Tom",
        last_name="Smith",
        f = make_form("3A")
    )

    assert str(s) == "Tom Smith in class 3A"
    
# ----------------------------------
# Tests for assignPreference
# ----------------------------------

def test_assignPreference_adds_preference():
    s = make_student()
    ws = make_workshop()

    s.assignPreference(ws)

    assert s.getAllPreferences() == [ws]
    
def test_assignPreference_does_not_add_none():
    s = make_student()

    s.assignPreference(None)

    assert s.getAllPreferences() == []

def test_assignPreference_can_add_multiple_preferences():
    s = make_student()

    ws1 = make_workshop("Workshop 1")
    ws2 = make_workshop("Workshop 2")

    s.assignPreference(ws1)
    s.assignPreference(ws2)

    assert s.getAllPreferences() == [ws1, ws2]
   
# ----------------------------------
# Tests for assignWorkshop
# ----------------------------------

def test_assignWorkshop_assigns_workshop_to_day():
    s = make_student()
    ws = make_workshop()

    s.assignWorkshop(ws, days.day1)

    assert s.getWorkshopOnDay(days.day1) == ws
    
def test_getWorkshopOnDay_returns_correct_workshop():
    s = make_student()

    ws1 = make_workshop("Workshop 1")
    ws2 = make_workshop("Workshop 2")

    s.assignWorkshop(ws1, days.day1)
    s.assignWorkshop(ws2, days.day2)

    assert s.getWorkshopOnDay(days.day1) == ws1
    assert s.getWorkshopOnDay(days.day2) == ws2
    
def test_getWorkshops_returns_both_workshops():
    s = make_student()

    ws1 = make_workshop("Workshop 1")
    ws2 = make_workshop("Workshop 2")

    s.assignWorkshop(ws1, days.day1)
    s.assignWorkshop(ws2, days.day2)

    assert s.getWorkshops() == [ws1, ws2]
    
def test_getWorkshopNames_returns_workshop_names():
    s = make_student()

    ws1 = make_workshop("Workshop 1")
    ws2 = make_workshop("Workshop 2")

    s.assignWorkshop(ws1, days.day1)
    s.assignWorkshop(ws2, days.day2)

    assert s.getWorkshopNames() == [
        "Workshop 1",
        "Workshop 2"
    ]
    
def test_getWorkshopNames_returns_empty_string_for_unassigned_day():
    s = make_student()

    assert s.getWorkshopNames() == ["", ""]
 
 
# ----------------------------------
# Tests for resetWorkshops
# ----------------------------------   
 
def test_resetWorkshops_removes_normal_workshops():
    s = make_student()
    ws = make_workshop()

    s.assignWorkshop(ws, days.day1)
    s.assignWorkshop(ws, days.day2)

    s.resetWorkshops()

    assert s.getWorkshops() == [None, None]
    
def test_resetWorkshops_keeps_preAssigned_workshop():
    s = make_student()

    normal_ws = make_workshop("Normal")
    preassigned_ws = make_workshop("Preassigned")

    preassigned_ws.preAssigned = True

    s.assignWorkshop(normal_ws, days.day1)
    s.assignWorkshop(preassigned_ws, days.day2)

    s.resetWorkshops()

    assert s.getWorkshopOnDay(days.day1) is None
    assert s.getWorkshopOnDay(days.day2) == preassigned_ws
    
# ----------------------------------
# Tests for filterPreferencesByAge
# ----------------------------------   

def test_filterPreferencesByAge_removes_workshops_for_wrong_age():
    s = make_student(f = make_form("3A"))

    valid_ws = make_workshop(
        "Valid",
        min_max_years={
            days.day1: (2, 4)
        }
    )

    invalid_ws = make_workshop(
        "Invalid",
        min_max_years={
            days.day1: (4, 6)
        }
    )

    s.assignPreference(valid_ws)
    s.assignPreference(invalid_ws)

    s.filterPreferencesByAge()

    assert s.getAllPreferences() == [valid_ws]
    
@pytest.mark.parametrize(
    "form_name, expected",
    [
        ("1A", False),
        ("2A", True),
        ("3A", True),
        ("4A", True),
        ("5A", False),
    ]
)
def test_filterPreferencesByAge_includes_boundary_years(
    form_name,
    expected):
    s = make_student(f = make_form(form_name))

    ws = make_workshop(
        min_max_years={
            days.day1: (2, 4)
        }
    )

    s.assignPreference(ws)

    s.filterPreferencesByAge()

    assert (ws in s.getAllPreferences()) is expected
 
    
# ----------------------------------
# Tests for getAllValidPreferences
# ----------------------------------   

def test_getAllValidPreferences_excludes_preassigned_workshops():
    s = make_student()

    normal_ws = make_workshop("Normal")
    preassigned_ws = make_workshop("Preassigned")

    preassigned_ws.preAssigned = True

    s.assignPreference(normal_ws)
    s.assignPreference(preassigned_ws)

    result = s.getAllValidPrefences(days.day1)

    assert result == [normal_ws]
    
def test_getAllValidPreferences_excludes_wrong_age_workshops():
    s = make_student(f = make_form())

    valid_ws = make_workshop(
        "Valid",
        min_max_years={
            days.day1: (1, 3)
        }
    )

    invalid_ws = make_workshop(
        "Invalid",
        min_max_years={
            days.day1: (2, 4)
        }
    )

    s.assignPreference(valid_ws)
    s.assignPreference(invalid_ws)

    result = s.getAllValidPrefences(days.day1)

    assert result == [valid_ws]
    
def test_getAllValidPreferences_day2_excludes_two_day_workshops():
    s = make_student()

    two_day_ws = make_workshop(
        "Two Day",
        is_two_day=True
    )

    one_day_ws = make_workshop(
        "One Day",
        is_two_day=False
    )

    s.assignPreference(two_day_ws)
    s.assignPreference(one_day_ws)

    result = s.getAllValidPrefences(days.day2)

    assert result == [one_day_ws]
    
    
def test_getAllValidPreferences_day2_excludes_day1_workshop():
    s = make_student()

    ws1 = make_workshop("Workshop 1")
    ws2 = make_workshop("Workshop 2")

    s.assignPreference(ws1)
    s.assignPreference(ws2)

    s.assignWorkshop(ws1, days.day1)

    result = s.getAllValidPrefences(days.day2)

    assert ws1 not in result
    assert ws2 in result
    
# ----------------------------------
# Tests for getAvailablePreferences
# ----------------------------------   
def test_getAvailablePreferences_excludes_full_workshops():
    s = make_student()

    full_ws = make_workshop(
        "Full",
        capacity=0
    )

    available_ws = make_workshop(
        "Available",
        capacity=10
    )

    s.assignPreference(full_ws)
    s.assignPreference(available_ws)

    result = s.getAvailablePreferences(days.day1)

    assert result == [available_ws]
    
def test_getAvailablePreferences_excludes_preassigned_workshops():
    s = make_student()

    normal_ws = make_workshop("Normal")
    preassigned_ws = make_workshop("Preassigned")

    preassigned_ws.preAssigned = True

    s.assignPreference(normal_ws)
    s.assignPreference(preassigned_ws)

    result = s.getAvailablePreferences(days.day1)

    assert result == [normal_ws]
    
def test_getAvailablePreferences_excludes_wrong_age_workshops():
    s = make_student(f = make_form())

    valid_ws = make_workshop(
        "Valid",
        min_max_years={
            days.day1: (1, 3)
        }
    )

    invalid_ws = make_workshop(
        "Invalid",
        min_max_years={
            days.day1: (2, 4)
        }
    )

    s.assignPreference(valid_ws)
    s.assignPreference(invalid_ws)

    result = s.getAvailablePreferences(days.day1)

    assert result == [valid_ws]
    
# ----------------------------------
# Tests for getAvailablePreferencesAscByPopularity
# ----------------------------------   
def test_getAvailablePreferencesAscByPopularity_sorts_by_prospective_students():
    s = make_student()

    ws1 = make_workshop("Workshop 1")
    ws2 = make_workshop("Workshop 2")
    ws3 = make_workshop("Workshop 3")

    ws1.prospectiveStudents = 10
    ws2.prospectiveStudents = 2
    ws3.prospectiveStudents = 5

    s.assignPreference(ws1)
    s.assignPreference(ws2)
    s.assignPreference(ws3)

    result = s.getAvailablePreferencesAscByPopularity(days.day1)

    assert result == [ws2, ws3, ws1]
    
def test_getAvailablePreferencesAscByPopularity_uses_number_of_students_as_tiebreaker():
    s = make_student()

    ws1 = make_workshop("Workshop 1")
    ws2 = make_workshop("Workshop 2")

    ws1.prospectiveStudents = 5
    ws2.prospectiveStudents = 5

    # Add students to ws1 so it is less popular according
    # to the second sorting criterion.
    other_student = make_student(
        first_name="Other"
    )

    ws1.students[days.day1].append(other_student)

    s.assignPreference(ws1)
    s.assignPreference(ws2)

    result = s.getAvailablePreferencesAscByPopularity(days.day1)

    assert result == [ws2, ws1]
    
# ----------------------------------
# Tests for hasSameWorkshopsAndNotTwoDay
# ----------------------------------       
def test_hasSameWorkshopsAndNotTwoDay_returns_true_for_same_one_day_workshop():
    s = make_student()

    ws = make_workshop(
        is_two_day=False
    )

    s.assignWorkshop(ws, days.day1)
    s.assignWorkshop(ws, days.day2)

    assert s.hasSameWorkshopsAndNotTwoDay() is True
    
def test_hasSameWorkshopsAndNotTwoDay_returns_false_for_different_workshops():
    s = make_student()

    ws1 = make_workshop("Workshop 1")
    ws2 = make_workshop("Workshop 2")

    s.assignWorkshop(ws1, days.day1)
    s.assignWorkshop(ws2, days.day2)

    assert s.hasSameWorkshopsAndNotTwoDay() is False
    
def test_hasSameWorkshopsAndNotTwoDay_returns_false_for_two_day_workshop():
    s = make_student()

    ws = make_workshop(
        is_two_day=True
    )

    s.assignWorkshop(ws, days.day1)
    s.assignWorkshop(ws, days.day2)

    assert s.hasSameWorkshopsAndNotTwoDay() is False
    
def test_hasSameWorkshopsAndNotTwoDay_returns_false_if_day1_unassigned():
    s = make_student()

    ws = make_workshop()

    s.assignWorkshop(ws, days.day2)

    assert s.hasSameWorkshopsAndNotTwoDay() is False
    

# ----------------------------------
# Tests for removeFromWorkshop
# ----------------------------------       
def test_removeFromWorkshop_removes_student_from_workshop():
    s = make_student()
    ws = make_workshop()

    ws.students[days.day1].append(s)
    s.assignWorkshop(ws, days.day1)

    s.removeFromWorkshop(days.day1)

    assert s.getWorkshopOnDay(days.day1) is None
    assert s not in ws.students[days.day1]
    
def test_removeFromWorkshop_does_not_fail_if_student_not_in_workshop_list():
    s = make_student()
    ws = make_workshop()

    s.assignWorkshop(ws, days.day1)

    s.removeFromWorkshop(days.day1)

    assert s.getWorkshopOnDay(days.day1) is None
    
def test_removeFromWorkshop_does_nothing_if_no_workshop_assigned():
    s = make_student()

    s.removeFromWorkshop(days.day1)

    assert s.getWorkshopOnDay(days.day1) is None