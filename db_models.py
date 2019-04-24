import sqlite3
import functions as f


class Controller(object):

    def __init__(self):
        self.model = LibraryModel()

    def get_everything(self, source):
        return self.model.get_everything(source)

    def search_courses(self, courseID):
        return self.model.search_courses(courseID)

    def add_question(self, text, mandatory, mcq):
        self.model.add_question(text, mandatory, mcq)

    def add_survey(self, title, code, sem, q_list, status=2):
        courseID = self.model.course_id(code, sem)
        self.model.add_survey(title, courseID, q_list, status)

    def add_answer(self, s_key, answers):
        if f.find_survey(s_key) is None:
            raise AssertionError()
        ans_string = '.'.join(answers)
        self.model.add_answer(s_key, ans_string)

    def add_user(self, user_id, password, role):
        self.model.add_user(user_id, password, role)

    def add_guest(self, user_id, approved):
        self.model.add_guest(user_id, approved)

    def add_enrolment(self, user_id, course_id):
        if self.search_courses(course_id) == []:
            raise AssertionError
        self.model.add_enrolment(user_id, course_id)

    def retrieve_answers(self, s_key):
        ans_list = self.model.retrieve_answers(s_key)
        return_list = []
        for item in ans_list:
            return_list.append(item[0].split('.'))
        return return_list

    def question_id(self, text):
        return self.model.question_id(text)

    def survey_id(self, title, code, sem):
        courseID = self.model.course_id(code, sem)
        return self.model.survey_id(title, courseID)

    def get_user(self, user_id):
        return self.model.get_user(user_id)

    def get_enrolments(self, user_id):
        return self.model.get_enrolments(user_id)

    def update_survey(self, s_id, status, q_list=None):
        self.model.update_survey(s_id, status, q_list)

    def add_completion(self, user_id, s_id):
        self.model.add_completion(user_id, s_id)

    def check_completed(self, user_id, s_id):
        completed = self.model.check_completed(user_id, s_id)
        return len(completed) == 0

    def get_guests(self):
        return self.model.get_guests()

    def approve_guest(self, user_id):
        self.model.approve_guest(user_id)

    def guest_approved(self, user_id):
        approved = self.model.guest_approved(user_id)
        if len(approved) > 0:
            return approved[0][0] == 1
        else:
            return False

    def add_time(self, s_id, timeobj):
        self.model.add_time(s_id, timeobj)

    def get_time(self, s_id):
        return self.model.get_time(s_id)


class LibraryModel(object):

    def __init__(self):
        pass

    def get_everything(self, source):
        if source == "QUESTIONS":
            query = "SELECT * FROM QUESTIONS"
        elif source == "SURVEYS":
            query = "SELECT * FROM SURVEYS"
        else:
            query = "SELECT * FROM COURSES"
        return self._dbreturn(query, ())

    def search_courses(self, ID):
        query = "SELECT CODE, SEM FROM COURSES WHERE COURSE_ID = ?"
        return self._dbreturn(query, (ID,))

    def add_question(self, text, mandatory, mcq):
        query = "INSERT INTO QUESTIONS (QUESTION, MANDATORY, MCQ) \
                 VALUES (?, ?, ?)"
        payload = (text, mandatory, mcq)
        self._dbadd(query, payload)

    def add_course(self, code, sem):
        query = "INSERT INTO COURSES (CODE, SEM) VALUES (?, ?)"
        payload = (code, sem)
        self._dbadd(query, payload)

    def add_survey(self, title, courseID, q_list, status):
        query = "INSERT INTO SURVEYS (TITLE, COURSE_ID, OPEN) \
                 VALUES (?, ?, ?)"
        payload = (title, courseID, status)
        self._dbadd(query, payload)
        s_id = self.survey_id(title, courseID)
        for q in q_list:
            query = "INSERT INTO SURVEY_QUESTIONS (Q_ID, SURVEY_ID) \
                     VALUES (?, ?)"
            payload = (q, s_id)
            self._dbadd(query, payload)

    def add_answer(self, s_key, answers):
        query = "INSERT INTO METRICS (SURVEYID, ANSWERS) \
                 VALUES (?, ?)"
        payload = (s_key, answers)
        self._dbadd(query, payload)

    def add_user(self, user_id, password, role):
        query = "INSERT INTO USERS (USER_ID, HASHED_PASS, ROLE) \
                 VALUES (?, ?, ?);"
        payload = (user_id, password, role)
        self._dbadd(query, payload)

    def add_guest(self, user_id, approved):
        query = "INSERT INTO GUEST_APPROVALS (USER_ID, APPROVED) \
                 VALUES (?, ?)"
        payload = (user_id, approved)
        self._dbadd(query, payload)

    def add_enrolment(self, user_id, course_id):
        query = "INSERT INTO ENROLMENTS (USER_ID, COURSE_ID) \
                 VALUES (?, ?)"
        payload = (user_id, course_id)
        self._dbadd(query, payload)

    def retrieve_answers(self, s_key):
        query = "SELECT ANSWERS FROM METRICS WHERE SURVEYID = ?"
        return self._dbreturn(query, (s_key,))

    def question_id(self, text):
        query = "SELECT Q_ID FROM QUESTIONS WHERE QUESTION = ?"
        return self._dbreturn(query, (text,))[0][0]

    def course_id(self, code, sem):
        query = "SELECT COURSE_ID FROM COURSES WHERE CODE = ? AND SEM = ?"
        payload = (code, sem)
        return self._dbreturn(query, payload)[0][0]

    def survey_id(self, title, courseID):
        query = "SELECT SURVEY_ID FROM SURVEYS WHERE TITLE = ? AND COURSE_ID = ?"
        payload = (title, courseID)
        return self._dbreturn(query, payload)[0][0]

    def survey_questions(self, survey_id):
        query = "SELECT Q_ID FROM SURVEY_QUESTIONS WHERE SURVEY_ID = ?"
        return self._dbreturn(query, (survey_id,))

    def get_user(self, user_id):
        query = "SELECT HASHED_PASS, ROLE FROM USERS WHERE USER_ID = ?"
        return self._dbreturn(query, (user_id,))

    def get_enrolments(self, user_id):
        query = "SELECT COURSE_ID FROM ENROLMENTS WHERE USER_ID = ?"
        return self._dbreturn(query, (user_id,))

    def update_survey(self, s_id, status, q_list=None):
        query = "UPDATE SURVEYS SET OPEN = ? \
                 WHERE SURVEY_ID = ?"
        payload = (status, s_id)
        self._dbadd(query, payload)
        if q_list:
            for q in q_list:
                query = "INSERT INTO SURVEY_QUESTIONS (Q_ID, SURVEY_ID) \
                         VALUES (?, ?)"
                payload = (q, s_id)
                self._dbadd(query, payload)

    def add_completion(self, user_id, s_id):
        query = "INSERT INTO SURVEYS_COMPLETED (USER_ID, SURVEY_ID) \
                 VALUES (?, ?)"
        payload = (user_id, s_id)
        self._dbadd(query, payload)

    def check_completed(self, user_id, s_id):
        query = "SELECT * FROM SURVEYS_COMPLETED \
                 WHERE USER_ID = ? AND SURVEY_ID = ?"
        payload = (user_id, s_id)
        return self._dbreturn(query, payload)

    def get_guests(self):
        query = "SELECT USER_ID FROM GUEST_APPROVALS WHERE APPROVED = 0"
        return self._dbreturn(query, ())

    def approve_guest(self, user_id):
        query = "UPDATE GUEST_APPROVALS SET APPROVED = 1 \
                 WHERE USER_ID = ?"
        self._dbadd(query, (user_id,))

    def guest_approved(self, user_id):
        query = "SELECT APPROVED FROM GUEST_APPROVALS WHERE USER_ID = ?"
        return self._dbreturn(query, (user_id,))

    def add_time(self, s_id, timeobj):
        query = "INSERT INTO SURVEY_TIMES (SURVEY_ID, CLOSE_TIME) \
                 VALUES (?, ?)"
        payload = (s_id, timeobj)
        self._dbadd(query, payload)

    def get_time(self, s_id):
        query = "SELECT CLOSE_TIME FROM SURVEY_TIMES \
                 WHERE SURVEY_ID = ?"
        return self._dbreturn(query, (s_id,))

    def _dbreturn(self, query, payload):
        with DatabaseAccessor() as db:
            return [row for row in db.execute(query, payload)]

    def _dbadd(self, query, payload):
        with DatabaseAccessor() as db:
            db.execute(query, payload)


class DatabaseAccessor(object):

    def __enter__(self):
        self.connection = sqlite3.connect('library.db', detect_types=sqlite3.PARSE_DECLTYPES)
        self.cursor = self.connection.cursor()
        return self.cursor

    def __exit__(self, exception_type, exception_value, traceback):
        self.connection.commit()
        self.cursor.close()
