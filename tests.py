import unittest
import sqlite3
import functions as f
import db_models as m
from db_functions import *
import create as c
from authenticate import *


class TestCourse(unittest.TestCase):

    def setUp(self):
        self.controller = m.Controller()
        drop_tables()
        initialiseDB()

    def test_add_course(self):
        self.controller.model.add_course('COMP1531', '17s2')
        course_id = self.controller.model.course_id('COMP1531', '17s2')
        course = self.controller.search_courses(course_id)
        self.assertEqual(course, [('COMP1531', '17s2')])

    def test_add_course_with_incorrect_input(self):
        with self.assertRaises(TypeError):
            self.controller.model.add_course('COMP1531')

    def test_add_user_to_course(self):
        self.controller.add_user('Ben', 'Lebron', 'Staff')
        self.controller.model.add_course('COMP1531', '17s2')
        course_id = self.controller.model.course_id('COMP1531', '17s2')
        self.controller.add_enrolment('Ben', course_id)
        user = get_user('Ben')
        self.assertEqual(user.role, 'Staff')
        self.assertEqual(user._password, 'Lebron')
        self.assertEqual(self.controller.search_courses(
            user._courses[0]), [('COMP1531', '17s2')])

    def test_add_user_to_course_that_doesnt_exist(self):
        self.controller.add_user('Nikola', 'Lebron', 'Student')
        with self.assertRaises(AssertionError):
            self.controller.add_enrolment('Nikola', 9999909)


class TestQuestion(unittest.TestCase):

    def setUp(self):
        self.controller = m.Controller()

    def test_add_man_and_mcq_question(self):
        c.question('Test mcq Q', [], 1, 1)
        question_id = self.controller.question_id('Test mcq Q')
        question = f.find_question(question_id)
        self.assertEqual(question.text, 'Test mcq Q')
        self.assertEqual(question.mandatory, 1)
        self.assertEqual(question.mcq, 1)

    def test_add_man_text_question(self):
        c.question('Test text Q', [], 1, 0)
        question_id = self.controller.question_id('Test text Q')
        question = f.find_question(question_id)
        self.assertEqual(question.text, 'Test text Q')
        self.assertEqual(question.mandatory, 1)
        self.assertEqual(question.mcq, 0)

    def test_add_non_man_question(self):
        c.question('Test non-man Q', [], 0, 1)
        question_id = self.controller.question_id('Test non-man Q')
        question = f.find_question(question_id)
        self.assertEqual(question.text, 'Test non-man Q')
        self.assertEqual(question.mandatory, 0)
        self.assertEqual(question.mcq, 1)

    def test_add_question_with_no_q_name(self):
        with self.assertRaises(TypeError):
            c.question([], 1, 1)

    def test_add_question_with_no_text_list(self):
        with self.assertRaises(TypeError):
            c.question('Test 2', 1, 1)

    def test_add_question_with_no_mandatory(self):
        with self.assertRaises(TypeError):
            c.question('Test 3', [], 1)

    def test_add_question_with_no_mcq(self):
        with self.assertRaises(TypeError):
            c.question('Test 4', [], 1)


class TestSurvey(unittest.TestCase):

    def setUp(self):
        self.controller = m.Controller()
        drop_tables()
        initialiseDB()

    def test_create_survey(self):
        c.question('Test1', [], 1, 1)
        c.question('Test2', [], 0, 1)
        q_id1 = self.controller.question_id('Test1')
        q_id2 = self.controller.question_id('Test2')
        self.controller.model.add_course('COMP1531', '17s2')
        c.survey([q_id1, q_id2], 'COMP1531', '17s2', 'Test Survey', '')
        course_id = self.controller.model.course_id('COMP1531', '17s2')
        survey_id = self.controller.model.survey_id('Test Survey', course_id)
        survey = f.find_survey(survey_id)
        survey_qs = self.controller.model.survey_questions(course_id)
        question1 = f.find_question(survey_qs[0][0])
        question2 = f.find_question(survey_qs[1][0])

        self.assertEqual(survey.title, 'Test Survey')
        self.assertEqual(question1.text, 'Test1')
        self.assertEqual(question2.text, 'Test2')

    def test_create_survey_without_questions(self):
        self.controller.model.add_course('COMP1531', '17s2')
        with self.assertRaises(AssertionError):
            c.survey([], 'COMP1531', '17s2', 'Test Survey', '')

    def test_create_survey_without_course(self):
        c.question('Test1', [], 1, 1)
        c.question('Test2', [], 0, 1)
        q_id1 = self.controller.question_id('Test1')
        q_id2 = self.controller.question_id('Test2')
        with self.assertRaises(TypeError):
            c.survey([q_id1, q_id2], 'Test Survey', '')

    def test_create_survey_with_course_that_doesnt_exist(self):
        c.question('Test1', [], 1, 1)
        c.question('Test2', [], 0, 1)
        q_id1 = self.controller.question_id('Test1')
        q_id2 = self.controller.question_id('Test2')
        with self.assertRaises(IndexError):
            c.survey([q_id1, q_id2], 'COMP9999', '99s2', 'Test Survey', '')


class TestUser(unittest.TestCase):

    def setUp(self):
        drop_tables()
        initialiseDB()
        self.controller = m.Controller()

    def test_add_user(self):
        self.controller.add_user('Rahil', 'Lebron', 'Staff')
        user = get_user('Rahil')
        self.assertEqual(user.role, 'Staff')
        self.assertEqual(user._password, 'Lebron')
        self.assertEqual(user.courses, [])

    def test_add_user_to_a_course(self):
        self.controller.add_user('Jack', 'Lebron', 'Student')
        self.controller.model.add_course('COMP1531', '17s2')
        course_id = self.controller.model.course_id('COMP1531', '17s2')
        course = self.controller.search_courses(course_id)
        self.controller.model.add_enrolment('Jack', course_id)
        user = get_user('Jack')
        self.assertEqual(self.controller.search_courses(
            user._courses[0]), [('COMP1531', '17s2')])

    def test_add_user_without_id(self):
        with self.assertRaises(TypeError):
            self.controller.add_user('Lebron', 'Admin')


class TestAnswer(unittest.TestCase):

    def setUp(self):
        drop_tables()
        initialiseDB()
        self.controller = m.Controller()
        c.question('Test1', [], 1, 1)
        c.question('Test2', [], 0, 1)
        q_id1 = self.controller.question_id('Test1')
        q_id2 = self.controller.question_id('Test2')
        self.controller.model.add_course('COMP1531', '17s2')
        c.survey([q_id1, q_id2], 'COMP1531', '17s2', 'Test Survey', '')

    def test_add_answers_to_survey(self):
        course_id = self.controller.model.course_id('COMP1531', '17s2')
        survey_id = self.controller.model.survey_id('Test Survey', course_id)
        self.controller.add_answer(survey_id, ['1', '2'])
        self.controller.add_answer(survey_id, ['3', '2'])
        answers = self.controller.retrieve_answers(survey_id)
        self.assertEqual(answers, [['1', '2'], ['3', '2']])

    def test_add_answers_to_survey_without_surveyID(self):
        course_id = self.controller.model.course_id('COMP1531', '17s2')
        survey_id = self.controller.model.survey_id('Test Survey', course_id)
        with self.assertRaises(TypeError):
            self.controller.add_answer(['1', '2'])

    def test_add_answers_to_survey_that_doesnt_exist(self):
        with self.assertRaises(AssertionError):
            self.controller.add_answer(9999, ['1', '2'])


if __name__ == '__main__':
    unittest.main()
