# -*- coding: utf-8 -*-
"""
Created on Fri Dec 20 07:53:49 2024

@author: tom

execute in command line in src directory:
    python -m pytest ../tests/ -v to run all tests
"""

import pytest
from collections import Counter
import days
import form
import workshop
import student

# ----------------------------------
# Helper functions
# ----------------------------------

def make_student(first_name="1", last_name="1", f = None):
    if f is None:
        f = form.Form("1A")
    return student.Student(first_name, last_name, f)
    
def make_workshop(capacity=2, min_max_years=None, is_two_day=False):
    if min_max_years is None:
        min_max_years = {
            days.day1: (1, 4),
            days.day2: (1, 4)
        }
    
    return workshop.Workshop(
        "1",
        capacity,
        min_max_years,
        is_two_day
    )

# ----------------------------------
# Tests for constructor and string
# ----------------------------------

def test_name_returns_name_as_string():
    ws = workshop.Workshop(123, 2, {days.day1: (1, 4)})
    
    assert ws.name == "123"

def test_constructor_sets_capacity():
    ws = make_workshop(capacity=5)
    
    assert ws.capacity == 5

def test_constructor_sets_is_two_day():
    ws = make_workshop(is_two_day=True)
    
    assert ws.isTwoDay is True

def test_constructor_sets_minimum_year():
    ws = workshop.Workshop("1", 2, {days.day1: (2, 4), days.day2: (1, 5)})
    
    assert ws.minYear == 1

def test_constructor_sets_maximum_year():
    ws = workshop.Workshop("1", 2, {days.day1: (2, 4), days.day2: (1, 5)})
    
    assert ws.maxYear == 5


# ----------------------------------
# Tests resetStudents
# ----------------------------------

def test_resetStudents_empties_both_days():
    ws = make_workshop()
    s = make_student()
    s.assignPreference(ws)
    
    ws.assignStudentToDay(s, days.day1)
    
    assert ws.getStudentsOnDay(days.day1) == [s]
    
    ws.resetStudents()
    
    assert ws.getStudentsOnDay(days.day1) == []
    assert ws.getStudentsOnDay(days.day2) == []
    
# ----------------------------------
# Tests for copyDay1Students
# ----------------------------------
    
def test_copyDay1Students_copies_students_to_day2():
    ws = make_workshop()
    
    s = make_student()
    s.assignPreference(ws)
    
    ws.assignStudentToDay(s, days.day1)
    ws.copyDay1Students()
    
    assert ws.getStudentsOnDay(days.day2) == [s]
    
def test_copyDay1Students_copies_empty_day1_to_day2():
    ws = make_workshop()
    
    ws.copyDay1Students()
    
    assert ws.getStudentsOnDay(days.day2) == []
    
# ----------------------------------
# Tests for isFull
# ----------------------------------    
    
def test_isFull_returns_false_when_below_capacity():
    ws = make_workshop(capacity=2)
    s = make_student()
    
    s.assignPreference(ws)
    ws.assignStudentToDay(s, days.day1)
    
    assert ws.isFull(days.day1) is False

def test_isFull_returns_true_when_at_capacity():
    ws = make_workshop(capacity=1)
    s = make_student()
    
    s.assignPreference(ws)
    ws.assignStudentToDay(s, days.day1)
    
    assert ws.isFull(days.day1) is True

def test_isFull_returns_true_when_over_capacity():
    ws = make_workshop(capacity=1)
    
    s1 = make_student("1")
    s2 = make_student("2")
    
    for s in [s1, s2]:
        s.assignPreference(ws)
        ws.assignStudentToDay(
            s,
            days.day1,
            forceAssign=True
        )
    
    assert ws.isFull(days.day1) is True
    
# ----------------------------------
# Tests for getStudentsOnDay
# ----------------------------------
           
def test_getStudentsOnDay_returns_empty_list_if_no_students_on_that_day():
    ws = make_workshop()
    
    assert ws.getStudentsOnDay(days.day1) == []
    assert ws.getStudentsOnDay(days.day2) == []
    
def test_getStudentsOnDay_returns_none_if_invalid_day():
    ws = make_workshop()
    
    assert ws.getStudentsOnDay("asdfasd") is None
    
def test_getStudentsOnDay_returns_students_on_correct_day():
    ws = make_workshop()
    s = make_student()
    s.assignPreference(ws)
    
    ws.assignStudentToDay(s, days.day1)
    
    assert ws.getStudentsOnDay(days.day1) == [s]

    
# ----------------------------------
# Tests for getStudentsOnDay
# ----------------------------------

def test_assignStudentToDay_assigns_student_to_correct_day():
    ws = make_workshop()
    s = make_student()
    
    s.assignPreference(ws)
    
    result = ws.assignStudentToDay(s, days.day1)
    
    assert result is True
    assert s in ws.getStudentsOnDay(days.day1)

def test_assignStudentToDay_returns_false_if_student_is_too_young():
    ws = make_workshop(min_max_years={days.day1: (2, 4)})
    s = make_student(f = form.Form("1A"))
    s.assignPreference(ws)

    assert ws.assignStudentToDay(s, days.day1) is False

def test_assignStudentToDay_returns_false_if_student_is_too_old():
    ws = make_workshop(min_max_years={days.day1: (1, 4)})
    s = make_student(f = form.Form("5A"))
    s.assignPreference(ws)

    assert ws.assignStudentToDay(s, days.day1) is False

def test_assignStudentToDay_returns_true_if_student_is_minimum_age():
    ws = make_workshop(min_max_years={days.day1: (2, 4)})
    
    s = make_student(f = form.Form("2A"))
    s.assignPreference(ws)
    
    assert ws.assignStudentToDay(s, days.day1) is True

def test_assignStudentToDay_returns_true_if_student_is_maximum_age():
    ws = make_workshop(min_max_years={days.day1: (2, 4)})
    
    s = make_student(f = form.Form("4A"))
    s.assignPreference(ws)

    assert ws.assignStudentToDay(s, days.day1) is True

def test_assignStudentToDay_forceAssign_ignores_capacity():
    ws = make_workshop(capacity=0)
    s = make_student()
    
    s.assignPreference(ws)
    
    assert ws.assignStudentToDay(
        s,
        days.day1,
        forceAssign=True
    ) is True

def test_assignStudentToDay_forceAssign_ignores_age():
    ws = make_workshop(min_max_years={days.day1: (2, 4)})
    s = make_student(f = form.Form("1A"))
    s.assignPreference(ws)
    
    assert ws.assignStudentToDay(
        s,
        days.day1,
        forceAssign=True
    ) is True

def test_assignStudentToDay_returns_false_if_day_not_valid():
    ws = make_workshop()
    s = make_student()
    
    assert ws.assignStudentToDay(s, "asdf") is False
    
def test_assignStudentToDay_returns_false_if_workshop_full():
    ws = make_workshop(capacity=0)
    s = make_student()
    
    assert ws.assignStudentToDay(s, days.day1) is False
    
def test_assignStudentToDay_returns_false_if_student_already_assigned_on_day1():
    ws = make_workshop()
    s = make_student()
    s.assignPreference(ws)
    
    assert ws.assignStudentToDay(s, days.day1) is True
    assert ws.assignStudentToDay(s, days.day2) is False
    
def test_assignStudentToDay_returns_false_if_student_already_assigned_on_day2():
    ws = make_workshop()
    s = make_student()
    s.assignPreference(ws)
    
    assert ws.assignStudentToDay(s, days.day2) is True
    assert ws.assignStudentToDay(s, days.day1) is False
    
# ----------------------------------
# Tests for moveStudentToDay
# ----------------------------------

def test_moveStudentToDay_moves_student_to_new_workshop():
    old_ws = make_workshop()
    new_ws = workshop.Workshop("2", 2, {days.day1: (1, 4),days.day2: (1, 4) } )
    
    s = make_student()
    s.assignPreference(old_ws)
    
    old_ws.assignStudentToDay(s, days.day1)
    
    result = new_ws.moveStudentToDay(s, days.day1)
    
    assert result is True
    assert s not in old_ws.getStudentsOnDay(days.day1)
    assert s in new_ws.getStudentsOnDay(days.day1)

def test_moveStudentToDay_returns_false_if_student_has_no_old_workshop():
    ws = make_workshop()
    s = make_student()
    
    assert ws.moveStudentToDay(s, days.day1) is False
    
def test_moveStudentToDay_returns_false_if_student_already_has_this_workshop_on_other_day():
    ws = make_workshop()
    s = make_student()
    
    s.assignPreference(ws)
    ws.assignStudentToDay(s, days.day1)
    
    assert ws.moveStudentToDay(s, days.day2) is False
    
    
# ----------------------------------
# Tests for getFormGroupSizes
# ----------------------------------

def test_getFormGroupSizes_returns_number_of_students_per_form():
    form_a = form.Form("1A")
    form_b = form.Form("1B")
    
    students = [
        student.Student("1", "1", form_a),
        student.Student("2", "1", form_a),
        student.Student("3", "1", form_b)
    ]
    
    ws = make_workshop(capacity=3)
    
    for s in students:
        s.assignPreference(ws)
        ws.assignStudentToDay(s, days.day1)
    
    result = ws.getFormGroupSizes(days.day1)
    
    assert result == Counter({
        form_a: 2,
        form_b: 1
    })
    
# ----------------------------------
# Tests for getNumberOfStudentsAloneOnDay
# ----------------------------------
    
def test_getNumberOfStudentsAloneOnDay_counts_single_student_forms():
    ws = make_workshop()
    
    s1 = make_student("1", "1", f = form.Form("1A"))
    s2 = make_student("2", "1", f = form.Form("2A"))
    
    for s in [s1, s2]:
        s.assignPreference(ws)
        ws.assignStudentToDay(s, days.day1)

    assert ws.getNumberOfStudentsAloneOnDay(days.day1) == 2

def test_getNumberOfStudentsAloneOnDay_does_not_count_forms_with_multiple_students():
    f = form.Form("1A")
    
    s1 = student.Student("1", "1", f)
    s2 = student.Student("2", "1", f)
    
    ws = make_workshop()
    
    for s in [s1, s2]:
        s.assignPreference(ws)
        ws.assignStudentToDay(s, days.day1)
    
    assert ws.getNumberOfStudentsAloneOnDay(days.day1) == 0
    

# ----------------------------------
# Tests for getFormAlonePenalty
# ----------------------------------

def test_getFormAlonePenalty_gives_penalty_of_10_for_single_student_form():
    ws = make_workshop()
    
    s = make_student()
    s.assignPreference(ws)
    ws.assignStudentToDay(s, days.day1)
    
    assert ws.getFormAlonePenalty(days.day1) == 10

def test_getFormAlonePenalty_gives_penalty_of_1_for_two_student_form():
    f = form.Form("1A")
    
    s1 = student.Student("1", "1", f)
    s2 = student.Student("2", "1", f)
    
    ws = make_workshop()
    
    for s in [s1, s2]:
        s.assignPreference(ws)
        ws.assignStudentToDay(s, days.day1)
    
    assert ws.getFormAlonePenalty(days.day1) == 1

def test_getFormAlonePenalty_returns_zero_for_form_of_three():
    f = form.Form("1A")
    
    students = [
        student.Student("1", "1", f),
        student.Student("2", "1", f),
        student.Student("3", "1", f)
    ]
    
    ws = make_workshop(capacity = 3)
    
    for s in students:
        s.assignPreference(ws)
        ws.assignStudentToDay(s, days.day1)
    
    assert ws.getFormAlonePenalty(days.day1) == 0
    
    
# ----------------------------------
# Tests for getLargeFormGroupPenalty
# ----------------------------------

def test_getLargeFormGroupPenalty_returns_zero_for_four_students():
    f = form.Form("1A")
    
    students = [
        student.Student(str(i), "1", f)
        for i in range(4)
    ]
    
    ws = make_workshop(capacity=4)
    
    for s in students:
        s.assignPreference(ws)
        ws.assignStudentToDay(s, days.day1)
    
    assert ws.getLargeFormGroupPenalty(days.day1) == 0

def test_getLargeFormGroupPenalty_penalises_groups_larger_than_four():
    f = form.Form("1A")
    
    students = [
        student.Student(str(i), "1", f)
        for i in range(5)
    ]
    
    ws = make_workshop(capacity=5)
    
    for s in students:
        s.assignPreference(ws)
        ws.assignStudentToDay(s, days.day1)
    
    assert ws.getLargeFormGroupPenalty(days.day1) == 1

def test_getLargeFormGroupPenalty_for_six_students_is_four():
    f = form.Form("1A")
    
    students = [
        student.Student(str(i), "1", f)
        for i in range(6)
    ]
    
    ws = make_workshop(capacity=6)
    
    for s in students:
        s.assignPreference(ws)
        ws.assignStudentToDay(s, days.day1)
    
    assert ws.getLargeFormGroupPenalty(days.day1) == 4
    
    
# ----------------------------------
# Tests for isStudentAgeCorrectOnDay
# ----------------------------------
    
@pytest.mark.parametrize(
    "formName, expected",
    [
    ("1A", False),
    ("2A", True),
    ("3A", True),
    ("4A", True),
    ("5A", False),
    ]
)
def test_isStudentAgeCorrectOnDay(formName, expected):
    ws = make_workshop(min_max_years={days.day1: (2, 4)})
    
    s = make_student(f = form.Form(formName))
    
    assert ws.isStudentAgeCorrectOnDay(
        s,
        days.day1
    ) is expected

def test_isStudentAgeCorrectOnDay_returns_false_for_invalid_day():
    ws = make_workshop(min_max_years={days.day1: (1, 4)})
    
    s = make_student()
    
    assert ws.isStudentAgeCorrectOnDay(
        s,
        "InvalidDay"
    ) is False
