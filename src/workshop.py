# -*- coding: utf-8 -*-
"""
Created on Tue Dec 31 10:48:43 2024

The workshops that can be assigned a list of Student for the respective days

@author: tom
"""
import days

class Workshop:
    def __init__(
            self, 
            name: str, 
            capacity: int, 
            minMaxYears: dict,
            isTwoDay: bool = False):
        """Constructor for Workshop

        Parameters
        ----------
        name : str
            name of workshop.
        capacity : int
            how many students allowed per day.
        minMaxYears: dict, optional
            dict: key = day, value = tuple (pairs!!) of min and max form for that day
            NOTE: if values are (0, 0) workshop should not be assigned on this day
        isTwoDay : bool, optional
            Is this a 2 day workshop. The default is False.
            
        Returns
        -------
        None.

        """
        self._name = name
        self.students = {}
        self.isTwoDay = isTwoDay
        self.capacity = capacity
        self.minMaxYears = minMaxYears
        yearValues = list(minMaxYears.values())
        self.minYear = min(v for values in yearValues for v in values)
        self.maxYear = max(v for values in yearValues for v in values)
        self.prospectiveStudents = 0
        self.preAssigned = False
        self.resetStudents()
        
    def __str__(self):
        pre = "Name: {0}, Is Two Day? {1}\n".format(
            self.name, self.isTwoDay)
        day1 = "Day1: {} students\n".format(len(self.students[days.day1]))
        for s in self.students[days.day1]:
            day1 += "{}\n".format(s)
        day2 ="Day2: {} students\n".format(len(self.students[days.day2]))
        for s in self.students[days.day2]:
            day2 += "{}\n".format(s)
        return pre + day1 + day2

    @property
    def name(self):
        return str(self._name)
    
    def resetStudents(self):
        """Reset the students lists for the 2 days to empty lists unless it is
        a pre assigned workshop
        """
        if not self.preAssigned:
            self.students[days.day1] = []
            self.students[days.day2] = []
    
    def copyDay1Students(self):
        """Copies the students from Day1 to Day2 --> useful for 2 day workshops"""
        self.students[days.day2] = self.students[days.day1]
        
    def assignStudentToDay(self, student, day, forceAssign=False):
        if not day in self.students or not student.workshops[day] is None:
            return False
        if (forceAssign or 
            not self.isFull(day) and 
            self.isStudentAgeCorrectOnDay(student, day)
            ):
            self.students[day].append(student)
            student.assignWorkshop(self, day)
            return True   
        return False
        
    def getStudentsOnDay(self, day):
        if not day in self.students:
            return None
        return self.students[day]
    
    def isFull(self, day):
        if len(self.getStudentsOnDay(day)) >= self.capacity:
            return True
        return False
    
    def isStudentAgeCorrectOnDay(self, student, day):
        if not day in self.minMaxYears:
            return False
        values = self.minMaxYears[day]
        return student.year <= max(values) and student.year >= min(values)     