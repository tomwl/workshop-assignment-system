# -*- coding: utf-8 -*-
"""
Created on Fri Jul 17 11:13:03 2026

@author: tom
"""

class AssignmentScore:

    def __init__(self):
        self.unassigned = 0
        self.form_alone_penalty = 0
        self.large_groups = 0

    @property
    def total(self):
        return (
            self.unassigned * 2000
            + self.form_alone_penalty * 100
            + self.large_groups * 10
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