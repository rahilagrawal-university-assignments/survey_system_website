from flask import Flask
import sqlite3
from flask_login import UserMixin, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from db_models import LibraryModel

app = Flask(__name__)
app.config['SECRET_KEY'] = '\xf7\xc9\x82\x96(b05\xb6D2;A\x15R\xe7\xbe\xcd'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


################
#    GLOBAL    #
#  VARIABLES   #
################

questions_list = {}
courses_list = {}
surveys_list = {}
display_courses = []
display_sems = []
selected = ["", ""]
current_guest = ["", ""]
chosen = 0
users = {}


#################
#     CLASS     #
#  DEFINITIONS  #
#################

class User(UserMixin):
    """
    User class

    ID: The user's id
        e.g. 103
    PASSWORD: The user's password
    ROLE: Staff / Admin / Student
    COURSES: If user is a student, list of course objects
    """

    __slots__ = ['_id', '_password', '_role', '_courses']

    def __init__(self, id, password, role, courses=None):
        self._id = id
        self._password = password
        self._role = role
        if courses is None:
            self._courses = []
        else:
            self._courses = courses

    def get_id(self):
        return self._id

    def check_password(self, password):
        return check_password_hash(self._password, password)

    def get_role(self):
        return self._role

    def add_course(self, course):
        self._courses.append(course)

    def get_courses(self):
        return self._courses

    id = property(get_id)
    role = property(get_role)
    courses = property(get_courses)


class Base(object):
    """
    Base class for Courses and Surveys

    CODE: The course code
          e.g. "COMP1531"
    SEM: The semester of the course
         e.g. "17s2"
    """

    __slots__ = ['_code', '_sem']

    def __init__(self, code, sem):
        self._code = code
        self._sem = sem

    def get_code(self):
        return self._code

    def set_code(self, code):
        self._code = code

    def get_sem(self):
        return self._sem

    def set_sem(self, sem):
        self._sem = sem

    code = property(get_code, set_code)
    sem = property(get_sem, set_sem)


class Question(object):
    """
    Each question created using add() is an object of the Question class

    TEXT: String of the question
          e.g. "Is the teaching quality in this course good?"
    KEY: Unique 5 character string that identifies the question
         used for effective storing of question data
         e.g. "A4jf5"
    """

    __slots__ = ['_text', '_key', '_mandatory', '_mcq']

    def __init__(self, text, key, mandatory, mcq):
        self._text = text
        self._key = key
        self._mandatory = int(mandatory)
        self._mcq = int(mcq)

    def get_text(self):
        return self._text

    def set_text(self, text):
        self._text = text

    def get_key(self):
        return self._key

    def set_key(self, key):
        self._key = key

    def get_mandatory(self):
        return self._mandatory

    def set_mandatory(self, mandatory):
        self._mandatory = int(mandatory)

    def get_mcq(self):
        return self._mcq

    def set_mcq(self, mcq):
        self._mcq = int(mcq)

    text = property(get_text, set_text)
    key = property(get_key, set_key)
    mandatory = property(get_mandatory, set_mandatory)
    mcq = property(get_mcq, set_mcq)


class Course(Base):
    """
    Courses are stored as objects of the Course class

    CODE: The course code
          e.g. "COMP1531"
    SEM: The semester of the course
         e.g. "17s2"
    """

    __slots__ = ['_id']

    def __init__(self, code, sem, ID):
        super(Course, self).__init__(code=code, sem=sem)
        self._id = ID

    def get_ID(self):
        return self._id

    ID = property(get_ID)


class Survey(Base):
    """
    Survey objects used to access survey data when a user goes to link

    LINK: Unique identification key used in published link to access survey
          e.g. "h2DG9"
          Usage: http://localhost:5000/survey=h2DG9
    COURSE: Course object for the course that the survey is for
            see Course class for attributes of this
    QUESTIONS: List of Question objects that are used in the survey
               see question class for attributes of each questions element
    """

    __slots__ = ['_title', '_courseID', '_status', '_pool', '_link']

    def __init__(self, title, courseID, code, sem, status, pool=None, link=None):
        super(Survey, self).__init__(code=code, sem=sem)
        self._title = title
        self._courseID = courseID
        self._status = status
        self._link = link
        if pool is None:
            self._pool = []
        else:
            self._pool = pool

    def get_title(self):
        return self._title

    def set_title(self, title):
        self._title = title

    def get_status(self):
        return self._status

    def set_status(self, status):
        self._status = status

    def get_pool(self):
        return self._pool

    def add_to_pool(self, q):
        self._pool.append(q)

    def get_link(self):
        return self._link

    def set_link(self, link):
        self._link = link

    def get_courseID(self):
        return self._courseID

    def set_courseID(self, ID):
        self._courseID = ID

    title = property(get_title, set_title)
    status = property(get_status, set_status)
    pool = property(get_pool)
    link = property(get_link, set_link)
    courseID = property(get_courseID)
