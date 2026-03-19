# Workshop Assignment System

## Description
Assigns students to workshops based on preferences, constraints, and grouping.

In src/FileIO.py there is also some extra stuff to run before and after if required to sort some of the data and check the results

## Features
- Preference-based assignment
- Capacity constraints
- Two-day workshops
- Student grouping within classes

## How to run
1. Install dependencies:
   pip install -r requirements.txt

2. Run:
   python src/workshop-assigner.py (main code for doing the assignment)
   python src/FileIO.py (pre and post data sorting)

## Input files
- An excel file with student name and class in the first columns and then their preferences in the next columns
- An excel file with a list of: workshop name, capacity, whether it is a two day workshop, class ranges day 1, class ranges day 2

## Output
Two excel files:
- Student names and the corresponding workshops they have been assigned on day 1 and 2
- Workshop list with the students assigned on day 1 (first tab) and day 2 (second tab) 
