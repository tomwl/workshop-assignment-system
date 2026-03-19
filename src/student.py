# -*- coding: utf-8 -*-
"""
Created on Tue Dec 31 10:49:34 2024

Contains the Student class, where a Student is to be assigned workshop(s)

@author: tom
"""

import days
import workshop as ws
import random

class Student:
    def __init__(self, firstname: str, lastname: str, form):
        """Constructor for Student

        Parameters
        ----------
        firstname : str
            student's first name.
        lastname : str
            student's last name.
        form : Form
            The form the student is in.

        Returns
        -------
        None.

        """
        self.firstname = firstname
        self.lastname = lastname
        self.workshops = {days.day1: None, days.day2: None}
        self.resetWorkshops()
        self.form = form
        self.year = int(form.name[:1])
        self.preferences: list[ws.Workshop] = []
        self.aloneOnDayOne = False
        
    def __str__(self):
        return "{0} {1} in class {2}".format(
            self.firstname, self.lastname, self.form)
    
    def getName(self):
        return "{0} {1}".format(self.firstname, self.lastname)  
    
    def getForm(self):
        return self.form
    
    def resetWorkshops(self):
        """
        Resets the student's workshops (excludes workshops that are pre assigned)

        Returns
        -------
        None.

        """
        if not self.workshops[days.day1] is None:
            if not self.workshops[days.day1].preAssigned:
                self.workshops[days.day1] = None
        if not self.workshops[days.day2] is None:
            if not self.workshops[days.day2].preAssigned:
                self.workshops[days.day2] = None
    
    def copyDay1Workshop(self):
        self.workshops[days.day2] = self.workshops[days.day1]
            
    def filterPreferencesByAge(self):
        for p in self.preferences:
            if p.minYear > self.year or p.maxYear < self.year:
                self.preferences.remove(p)
                
    def shufflePreferences(self):
        random.shuffle(self.preferences)
           
    def getAllPreferences(self):
        return self.preferences
    
    def getAvailablePreferences(self, day):
        """Finds available preferences of a student based on if preference full, 
        not 2 day workshop and not already assigned to the student on day 1
    
        Parameters
        ----------
        day : str
            Day1 or Day2.

        Returns
        -------
        result : list of Workshop
            The available workshops for this student.

        """        
        result = list(
            filter(
            lambda p: not p.preAssigned and 
                not p.isFull(day) and 
                p.isStudentAgeCorrectOnDay(self, day), 
            self.preferences)
            )
        if day == days.day2:
            result = list(filter(lambda p: not p.isTwoDay, result))
            if self.workshops[days.day1] in result: 
                result.remove(self.workshops[days.day1])
                
        return result
    
    def getAvailablePreferencesAscByPopularity(self, day):
        return sorted(
            self.getAvailablePreferences(day), 
            key=lambda p: (p.prospectiveStudents, len(p.getStudentsOnDay(day))))
        
    def assignPreference(self, preference):
        if not preference is None:
            self.preferences.append(preference)
    
    def assignWorkshop(self, workshop, day):
        self.workshops[day] = workshop
        
    def getWorkshopNames(self):
        return [ws.name if not ws is None else "" for ws in self.workshops.values()]
    
    def getWorkshops(self):
        return list(self.workshops.values())
    
    def getWorkshopOnDay(self, day):
        return self.workshops[day]
    
    def hasSameWorkshopsAndNotTwoDay(self):
        wsDay1 = self.getWorkshopOnDay(days.day1)
        wsDay2 = self.getWorkshopOnDay(days.day2)
        if not wsDay1 is None and not wsDay2 is None and not wsDay1.isTwoDay:
            return wsDay1 == wsDay2
        