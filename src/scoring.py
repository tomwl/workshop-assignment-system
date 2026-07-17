# -*- coding: utf-8 -*-
"""
Created on Fri Jul 17 11:13:03 2026

@author: tom
"""

class AssignmentScore:

    UNASSIGNED_WEIGHT = 2000
    FORM_ALONE_WEIGHT = 100
    LARGE_GROUP_WEIGHT = 10
    
    def __init__(self):
        self.unassigned = 0
        self.form_alone_penalty = 0
        self.large_groups = 0

    @property
    def total(self):
        return (
            self.unassigned * self.UNASSIGNED_WEIGHT
            + self.form_alone_penalty * self.FORM_ALONE_WEIGHT
            + self.large_groups * self.LARGE_GROUP_WEIGHT
        )
    
def scoreWorkshops(workshops, forms, day):
    score = AssignmentScore()

    # lonely students and big groups add to the penalty
    for workshop in workshops:
        score.form_alone_penalty += workshop.getFormAlonePenalty(day)
        score.large_groups +=  workshop.getLargeFormGroupPenalty(day)

    # unassigned students add to the penalty
    for form in forms:
        score.unassigned += form.getNumberOfUnassigned(day)

    return score

def scoreWorkshop(workshop, day):
    score = 0

    score += workshop.getFormAlonePenalty(day) * AssignmentScore.FORM_ALONE_WEIGHT
    score += workshop.getLargeFormGroupPenalty(day) * AssignmentScore.LARGE_GROUP_WEIGHT

    return score

def scoreLocalChange(affected_workshops, day, unassigned_change):
    score = sum(
        scoreWorkshop(w, day)
        for w in affected_workshops
    )

    score += unassigned_change * AssignmentScore.UNASSIGNED_WEIGHT

    return score