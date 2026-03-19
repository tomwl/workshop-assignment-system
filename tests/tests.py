# -*- coding: utf-8 -*-
"""
Created on Fri Dec 20 07:53:49 2024

@author: tom
"""

import unittest
import workshop
import student
import form
from unittest import mock

class WorkshopAssignerWorkshopTests(unittest.TestCase):
    def testCopyDay1StudentsCopies(self):
        f = form.Form("1A")
        students = [student.Student("1", "1", f), student.Student("2", "2", f)]
        ws = workshop.Workshop("1", 4, {"Day1": (1, 4)}, True)
        for s in students:
            s.assignPreference(ws)
            ws.assignStudentToDay(s, "Day1")
        ws.copyDay1Students()
        self.assertTrue(
            ws.getStudentsOnDay("Day1") == ws.getStudentsOnDay("Day2"))
        
    def testIsFullReturnsCorrect(self):
        f = form.Form("1A")
        students = [student.Student("1", "1", f), student.Student("2", "2", f)]
        ws = workshop.Workshop("1", 1, {"Day1": (1, 4)}, True)
        for s in students:
            s.assignPreference(ws)
        self.assertTrue(ws.assignStudentToDay(students[0], "Day1"))
        self.assertFalse(ws.assignStudentToDay(students[1], "Day1"))
            
    def testGetStudentsOnDayReturnsFalseOrNoneIfNoStudents(self):
        ws = workshop.Workshop("1", 2, {"Day1": (1, 4)})
        self.assertFalse(ws.getStudentsOnDay("Day1"))
        self.assertFalse(ws.getStudentsOnDay("Day2"))
        self.assertIsNone(ws.getStudentsOnDay("asdf"))
        
    def testAssignStudentToDayReturnsFalseIfDayNotValid(self):
        f = form.Form("1A")
        s = student.Student("1", "1", f)
        ws1 = workshop.Workshop("1", 1, {"Day1": (1, 4)})
        # if wrong day return false
        self.assertFalse(ws1.assignStudentToDay(s, "asdf"))
        ws2 = workshop.Workshop("1", 0, {"Day1": (1, 4)})
        # if ws full return false
        self.assertFalse(ws2.assignStudentToDay(s, "Day1"))
    
    def testAssignStudentsToDayAddsStudent(self):
        f = form.Form("1A")
        s = student.Student("1", "1", f)
        ws = workshop.Workshop("1", 5, {"Day1": (1, 4)})
        s.assignPreference(ws)
        self.assertTrue(ws.assignStudentToDay(s, "Day1"))
        self.assertTrue(s in ws.students["Day1"])
        
class WorkshopAssignerStudentTests(unittest.TestCase):
    def testCopyDay1WorkshopCopies(self):
        s = student.Student("1", "1", form.Form("1A"))
        ws = workshop.Workshop("1", 5, {"Day1": (1, 4)})
        s.assignPreference(ws)
        ws.assignStudentToDay(s, "Day1")
        s.copyDay1Workshop()
        self.assertTrue(s.workshops["Day1"] == s.workshops["Day2"])
      
    def testAssignPreferenceAddsPreference(self):
        s = student.Student("1", "1", form.Form("1A"))
        ws = workshop.Workshop("1", 5, {"Day1": (1, 4)})
        s.assignPreference(ws)
        self.assertTrue(len(s.getAllPreferences()) == 1)
        self.assertTrue(s.getAllPreferences()[0] == ws)
       
    def testFilterPreferencesRemovesIfTooYoung(self):
        s = student.Student("1", "1", form.Form("1A"))
        ws = workshop.Workshop("1", 5, {"Day1": (2, 4)})
        s.assignPreference(ws)
        s.filterPreferencesByAge()
        self.assertFalse(s.getAllPreferences())
        
    def testFilterPreferencesRemovesIfTooOld(self):
        s = student.Student("1", "1", form.Form("4A"))
        ws = workshop.Workshop("1", 5, {"Day1": (1, 3)})
        s.assignPreference(ws)
        s.filterPreferencesByAge()
        self.assertFalse(s.getAllPreferences())
        
    def testGetAvailablePreferences(self):
        s = student.Student("1", "1", form.Form("1A"))
        ws = workshop.Workshop("1", 5, {"Day1": (1, 4)})
        s.assignPreference(ws)
        self.assertFalse(s.getAvailablePreferences("Day2"))
        
    def testGetAvailablePreferencesReturnsFalseIfWorkshopAlreadyOnDay1(self):
        s = student.Student("1", "1", form.Form("1A"))
        ws = workshop.Workshop("1", 5, {"Day1": (1, 4)})
        s.assignPreference(ws)
        ws.assignStudentToDay(s, "Day1")
        result = s.getAvailablePreferences("Day2")
        self.assertFalse(result)
        
    def testGetAvailablePreferenceReturnsEmptyListIfWorkshopFull(self):
        s = student.Student("1", "1", form.Form("1A"))
        ws = workshop.Workshop("1", 5, {"Day1": (1, 4)})
        ws.isFull = mock.Mock()
        ws.isFull.return_value = True
        s.assignPreference(ws)
        self.assertTrue(ws in s.preferences)
        self.assertIsNone(s.workshops["Day1"])
        self.assertTrue(len(s.getAvailablePreferences("Day1")) == 0)
       
    def testGetAvailablePreferenceReturnsEmptyListIfWorkshopAlreadyAssignedOnDay1(self):
        s = student.Student("1", "1", form.Form("1A"))
        ws = workshop.Workshop("1", 5, {"Day1": (1, 4), "Day2": (1, 4)})
        s.assignPreference(ws)
        ws.assignStudentToDay(s, "Day1")
        self.assertTrue(ws in s.preferences)
        self.assertTrue(s.workshops["Day1"] == ws)
        self.assertFalse(s.preferences[0].isFull("Day2"))
        self.assertTrue(len(s.getAvailablePreferences("Day2")) == 0)
        
    def testGetAvailablePreferenceReturnsEmptyListIfWorkshop2DayAndLookingOnDay2(self):
        s = student.Student("1", "1", form.Form("1A"))
        ws = workshop.Workshop("1", 5, {"Day1": (1, 4), "Day2": (1, 4)}, True)
        s.assignPreference(ws)
        self.assertTrue(ws in s.preferences)
        self.assertIsNone(s.workshops["Day1"])
        self.assertFalse(s.preferences[0].isFull("Day2"))
        self.assertTrue(len(s.getAvailablePreferences("Day2")) == 0)
        
    def testGetAvailablePreferenceAscByPopularityReturnsCorrectlyOrderedList(self):
        s1 = student.Student("1", "1", form.Form("1A"))
        s2 = student.Student("1", "1", form.Form("1A"))
        s3 = student.Student("1", "1", form.Form("1A"))
        ws = [workshop.Workshop("1", 5, {"Day1": (1, 4)}), 
              workshop.Workshop("2", 5, {"Day1": (1, 4)})]
        for w in ws:
            s1.assignPreference(w)    
        ws[0].assignStudentToDay(s2, "Day1")
        ws[1].assignStudentToDay(s2, "Day1")
        ws[1].assignStudentToDay(s3, "Day1")
        result = s1.getAvailablePreferencesAscByPopularity("Day1")
        self.assertTrue(len(result) == 2)
        self.assertTrue(result[0] is ws[0])
        self.assertTrue(result[1] is ws[1])
        
    def testAssignWorkshopAddsWorkshop(self):
        s = student.Student("1", "1", form.Form("1A"))
        ws = workshop.Workshop("1", 5, {"Day1": (1, 4)})
        s.assignPreference(ws)
        s.assignWorkshop(ws, "Day1")
        self.assertTrue(s.workshops["Day1"] == ws)
        
    def testGetWorkshopReturnsCorrectWorkshops(self):
        s = student.Student("1", "1", form.Form("1A"))
        ws = [workshop.Workshop("1", 5, {"Day1": (1, 4)}), 
              workshop.Workshop("2", 5, {"Day2": (1, 4)}), 
              workshop.Workshop("3", 5, {"Day1": (1, 4)})]
        s.assignPreference(ws[0])
        s.assignPreference(ws[1])
        s.assignWorkshop(ws[0], "Day1")
        s.assignWorkshop(ws[1], "Day2")
        self.assertTrue(s.getWorkshops()[0] == ws[0])
        self.assertTrue(s.getWorkshops()[1] == ws[1])
           
    def testGetWorkshopsNamesReturnsCorrectNames(self):
        s = student.Student("1", "1", form.Form("1A"))
        ws = [workshop.Workshop("1", 5, {"Day1": (1, 4)}), 
              workshop.Workshop("2", 5, {"Day2": (1, 4)}), 
              workshop.Workshop("3", 5, {"Day1": (1, 4)})]
        s.assignPreference(ws[0])
        s.assignPreference(ws[1])
        s.assignWorkshop(ws[0], "Day1")
        s.assignWorkshop(ws[1], "Day2")
        self.assertTrue(s.getWorkshopNames() == ["1", "2"])
      

def main():
    unittest.main()

if __name__ == '__main__':
    main()