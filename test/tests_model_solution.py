import unittest
import os
from server import db
from dbInteractions import *
from Model import *

class TestEnrolment(unittest.TestCase):

    def setUp(self):
        db.create_all()
        read_all_courses('../courses.csv')
        read_passwords('../passwords.csv')
        read_all_enrolments('../Student_enrolments.csv')

    def test_enrol_student_invalid_course(self):
        """
        :post : There will be no changes in the database
        """
        zID = 12
        course_offering = ""

        prev_students = num_enrolled_students(course_offering)
        with self.assertRaises(InvalidInputException):
            enrol_user(zID, course_offering)
        curr_students = num_enrolled_students(course_offering)

        self.assertEqual(prev_students, curr_students)
        self.assertEqual(get_user(zID), None)

    def test_enrol_invalid_user(self):
        """
        :pre  : The student isn't already enrolled in the course
        :post : The database will have a relationship between
                the course offering and the student
        """
        zID = "z511"
        course_offering = "COMP1531 17s2"

        prev_students = num_enrolled_students(course_offering)
        with self.assertRaises(InvalidInputException):
            enrol_user(zID, course_offering)
        curr_students = num_enrolled_students(course_offering)

        self.assertEqual(prev_students, curr_students)
        self.assertEqual(get_user(zID), None)

    def test_enrol_non_existent_user(self):
        """
        :pre  : The student isn't already enrolled in the course
        :post : The database will have a relationship between
                the course offering and the student
        """
        zID = 12
        course_offering = "COMP1531 17s2"

        prev_students = num_enrolled_students(course_offering)
        with self.assertRaises(UserNotFoundException):
            enrol_user(zID, course_offering)
        curr_students = num_enrolled_students(course_offering)

        self.assertEqual(prev_students, curr_students)
        self.assertEqual(get_user(zID), None)

    def test_enrol_valid(self):
        """
        :pre  : The student isn't already enrolled in the course
        :post : The database will have a relationship between
                the course offering and the student
        """
        zID = 571
        course_offering = "COMP1531 17s2"
        assert course_offering not in get_user(zID).courses
        prev_students = num_enrolled_students(course_offering)
        enrol_user(zID, course_offering)
        curr_students = num_enrolled_students(course_offering)

        self.assertEqual(prev_students + 1, curr_students)
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()

class TestAddStaff(unittest.TestCase):

    def setUp(self):
        """
        Create table for tests
        """
        db.create_all()
        os.system("chmod 766 unique.db")
    
    def test_add_staff_invalid_id(self):
        """
        :post : No new additions will appear in the db table
        """
        staff_id = ""
        num_staff = len(get_staff(all=True))
        with self.assertRaises(InvalidInputException):
            add_staff(staff_id)

        cur_num_staff = len(get_staff(all=True))
        self.assertEqual(num_staff, cur_num_staff)

    def test_add_staff_valid_id(self):
        """
        :pre : The staff member to be inserted doesn't exist yet
        :post : A new staff member will be added to the table
        """
        staff_id = 290
        self.assertEqual(get_staff(290), None)
        num_staff = len(get_staff(all=True))
        add_staff(staff_id)
        cur_num_staff = len(get_staff(all=True))
        self.assertEqual(num_staff + 1, cur_num_staff)
        self.assertNotEqual(get_staff(staff_id), None)

    def tearDown(self):
        db.session.remove()
        db.drop_all()

if __name__=="__main__":
    unittest.main()
