# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 10:58:57 2026

@author: tom

execute in command line in src directory:
    python -m pytest ../tests/ -v to run all tests
"""

import pytest

import scoring
import days
import form
import student
import workshop

# ----------------------------------
# Helpers
# ----------------------------------

def make_student(first_name="John", last_name="Smith", f=form.Form("1A")):
    return student.Student(first_name, last_name, f)

def make_workshop(name="Workshop 1", capacity=10, min_max_years=None):
    if min_max_years is None:
        min_max_years = {
            days.day1: (1, 4),
            days.day2: (1, 4)
        }

    return workshop.Workshop(
        name,
        capacity,
        min_max_years
    )
# ----------------------------------
# AssignmentScore
# ----------------------------------

def test_AssignmentScore_initialises_with_zero_penalties():
    score = scoring.AssignmentScore()
    
    assert score.unassigned == 0
    assert score.form_alone_penalty == 0
    assert score.large_groups == 0
    assert score.total == 0

def test_AssignmentScore_total_returns_weighted_score():
    score = scoring.AssignmentScore()
    
    score.unassigned = 2
    score.form_alone_penalty = 3
    score.large_groups = 4
    
    expected = (
        2 * scoring.AssignmentScore.UNASSIGNED_WEIGHT
        + 3 * scoring.AssignmentScore.FORM_ALONE_WEIGHT
        + 4 * scoring.AssignmentScore.LARGE_GROUP_WEIGHT
    )
    
    assert score.total == expected

@pytest.mark.parametrize(
    "unassigned, form_alone, large_groups, expected",
    [
    (0, 0, 0, 0),
    (1, 0, 0, 2000),
    (0, 1, 0, 100),
    (0, 0, 1, 10),
    (2, 3, 4, 4340),
    ]
)
def test_AssignmentScore_total_applies_correct_weights(
        unassigned,
        form_alone,
        large_groups,
        expected
    ):
    score = scoring.AssignmentScore()
    
    score.unassigned = unassigned
    score.form_alone_penalty = form_alone
    score.large_groups = large_groups
    
    assert score.total == expected
    
    
# ----------------------------------
# scoreWorkshop
# ----------------------------------

def test_scoreWorkshop_returns_zero_for_empty_workshop():
    ws = make_workshop()
    
    assert scoring.scoreWorkshop(
        ws,
        days.day1
    ) == 0

def test_scoreWorkshop_applies_form_alone_penalty():
    ws = make_workshop()
    
    s = make_student()
    
    ws.assignStudentToDay(
        s,
        days.day1
    )

    # One form with one student gives a form-alone penalty of 10
    expected = (
        10
        * scoring.AssignmentScore.FORM_ALONE_WEIGHT
    )
    
    assert scoring.scoreWorkshop(
        ws,
        days.day1
    ) == expected

def test_scoreWorkshop_applies_large_group_penalty():
    ws = make_workshop()
    f = form.Form("1A")
    
    students = [
        make_student("1", "2", f),
        make_student("2", "2", f),
        make_student("3", "2", f),
        make_student("4", "2", f),
        make_student("5", "2", f),
    ]
    
    for s in students:
        ws.assignStudentToDay(s, days.day1)
    
    # A group of 5 gives:
    #
    # (5 - 4) ** 2 = 1
    #
    expected = (
        1
        * scoring.AssignmentScore.LARGE_GROUP_WEIGHT
    )
    
    assert scoring.scoreWorkshop(
        ws,
        days.day1
    ) == expected

def test_scoreWorkshop_combines_form_alone_and_large_group_penalties():
    ws = make_workshop()
    f = form.Form("1A")
    
    students = [
        make_student("5", "3", f),
        make_student("2", "2", f),
        make_student("3", "2", f),
        make_student("4", "2", f),
        make_student("5", "2", f),
        make_student("5", "3", form.Form("2A"))
    ]
    
    for s in students:
        ws.assignStudentToDay(s, days.day1)
    
    # Form 1A has 5 students:
    # large group penalty = (5 - 4) ** 2 = 1
    #
    # Form 2A has 1 student:
    # form-alone penalty = 10
    #
    expected = (
        10 * scoring.AssignmentScore.FORM_ALONE_WEIGHT
        + 1 * scoring.AssignmentScore.LARGE_GROUP_WEIGHT
    )
    
    assert scoring.scoreWorkshop(
        ws,
        days.day1
    ) == expected

# ----------------------------------
# scoreWorkshops
# ----------------------------------

def test_scoreWorkshops_returns_zero_for_no_penalties():
    ws = make_workshop()
    f = form.Form("1A")
    
    assert scoring.scoreWorkshops(
        [ws],
        [f],
        days.day1
    ).total == 0

def test_scoreWorkshops_counts_unassigned_students():
    ws = make_workshop()
    f = form.Form("1A")
    
    s1 = make_student("Student1")
    s2 = make_student("Student2")
    
    f.addStudent(s1)
    f.addStudent(s2)
    
    score = scoring.scoreWorkshops(
        [ws],
        [f],
        days.day1
    )
    
    assert score.unassigned == 2
    assert score.total == (
        2 * scoring.AssignmentScore.UNASSIGNED_WEIGHT
    )

def test_scoreWorkshops_counts_penalties_from_workshops():
    ws = make_workshop()
    f = form.Form("1A")
    
    s = make_student()
    
    f.addStudent(s)
    ws.assignStudentToDay(s, days.day1)
    
    score = scoring.scoreWorkshops(
        [ws],
        [f],
        days.day1
    )
    
    assert score.form_alone_penalty == 10
    assert score.large_groups == 0
    assert score.unassigned == 0
    
    assert score.total == (
        10 * scoring.AssignmentScore.FORM_ALONE_WEIGHT
    )

def test_scoreWorkshops_combines_all_penalty_types():
    ws = make_workshop()
    f = form.Form("1A")
    
    assigned_student = make_student("Assigned")
    unassigned_student = make_student("Unassigned")
    
    f.addStudent(assigned_student)
    f.addStudent(unassigned_student)
    
    ws.assignStudentToDay(
        assigned_student,
        days.day1
    )
    
    score = scoring.scoreWorkshops(
        [ws],
        [f],
        days.day1
    )
    
    assert score.unassigned == 1
    assert score.form_alone_penalty == 10
    assert score.large_groups == 0

    expected = (
        1 * scoring.AssignmentScore.UNASSIGNED_WEIGHT
        + 10 * scoring.AssignmentScore.FORM_ALONE_WEIGHT
    )
    
    assert score.total == expected


# ----------------------------------
# scoreLocalChange
# ----------------------------------

def test_scoreLocalChange_returns_zero_for_empty_workshops():
    assert scoring.scoreLocalChange(
    [],
    days.day1,
    0
    ) == 0

def test_scoreLocalChange_includes_workshop_penalties():
    ws = make_workshop()
    s = make_student()
    
    ws.assignStudentToDay(s, days.day1)
    
    expected = (
        10
        * scoring.AssignmentScore.FORM_ALONE_WEIGHT
    )
    
    assert scoring.scoreLocalChange(
        [ws],
        days.day1,
        0
    ) == expected

def test_scoreLocalChange_includes_unassigned_change():
    ws = make_workshop()
    
    expected = (
        2
        * scoring.AssignmentScore.UNASSIGNED_WEIGHT
    )
    
    assert scoring.scoreLocalChange(
        [ws],
        days.day1,
        2
    ) == expected

@pytest.mark.parametrize(
    "unassigned_change, expected",
    [
    (0, 0),
    (1, 2000),
    (2, 4000),
    (-1, -2000),
    ]
)
def test_scoreLocalChange_applies_unassigned_weight(
        unassigned_change,
        expected
        ):
    assert scoring.scoreLocalChange(
        [],
        days.day1,
        unassigned_change
    ) == expected

def test_scoreLocalChange_combines_workshop_and_unassigned_penalties():
    ws = make_workshop()
    s = make_student()
    
    ws.assignStudentToDay(s, days.day1)
    
    expected = (
        10 * scoring.AssignmentScore.FORM_ALONE_WEIGHT
        + 2 * scoring.AssignmentScore.UNASSIGNED_WEIGHT
    )
    
    assert scoring.scoreLocalChange(
        [ws],
        days.day1,
        2
    ) == expected
