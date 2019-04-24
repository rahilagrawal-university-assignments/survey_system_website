import sqlite3
import csv
import sys
import time
import progressbar
from werkzeug.security import generate_password_hash, check_password_hash


def read_csv(file_name):
    r = csv.reader(open(file_name))
    return_list = [l for l in r]
    return return_list


def dbadd(query, payload=None):
    connection = sqlite3.connect('library.db')
    cursor = connection.cursor()
    try:
        if payload is None:
            cursor.execute(query)
        else:
            cursor.execute(query, payload)
        connection.commit()
    except:
        pass
    cursor.close()


def dbreturn(query, payload):
    connection = sqlite3.connect('library.db')
    cursor = connection.cursor()
    rows = cursor.execute(query, payload)
    results = [row for row in rows]
    connection.commit()
    cursor.close()
    return results


def add_course(code, sem):
    query = """INSERT INTO COURSES (CODE, SEM)
               VALUES (?, ?);"""
    payload = (code, sem)
    dbadd(query, payload)


def course_id(code, sem):
    query = """SELECT COURSE_ID FROM COURSES
               WHERE CODE = ? AND SEM = ?;"""
    payload = (code, sem)
    return dbreturn(query, payload)[0][0]


def add_user(user_id, password, role):
    query = """INSERT INTO USERS (USER_ID, HASHED_PASS, ROLE)
               VALUES (?, ?, ?);"""
    payload = (user_id, password, role)
    dbadd(query, payload)


def add_enrolment(user_id, course_id):
    query = """INSERT INTO ENROLMENTS (USER_ID, COURSE_ID)
               VALUES (?, ?);"""
    payload = (user_id, course_id)
    dbadd(query, payload)


def drop_tables():
    bar = progressbar.ProgressBar()
    for table in bar(("COURSES", "ENROLMENTS", "SURVEYS", "USERS", "METRICS",
                      "QUESTIONS", "SURVEY_QUESTIONS", "SURVEYS_COMPLETED",
                      "GUEST_APPROVALS", "SURVEY_TIMES")):
        dbadd("DROP TABLE {};".format(table))


def initialiseDB():
    courses = """CREATE TABLE COURSES
              (COURSE_ID INTEGER PRIMARY KEY AUTOINCREMENT,
              CODE varchar(8) NOT NULL, SEM varchar(4) NOT NULL);"""

    enrolments = """CREATE TABLE ENROLMENTS
                    (USER_ID TEXT NOT NULL, COURSE_ID INTEGER,
                    PRIMARY KEY (USER_ID, COURSE_ID));"""

    surveys = """CREATE TABLE SURVEYS
              (SURVEY_ID INTEGER PRIMARY KEY AUTOINCREMENT, TITLE TEXT NOT NULL,
              COURSE_ID INTEGER NOT NULL, OPEN INTEGER);"""

    metrics = """CREATE TABLE METRICS
              (ID INTEGER PRIMARY KEY AUTOINCREMENT,
              SURVEYID INTEGER NOT NULL, ANSWERS TEXT NOT NULL);"""

    users = """CREATE TABLE USERS
               (USER_ID TEXT PRIMARY KEY NOT NULL,
               HASHED_PASS TEXT NOT NULL, ROLE TEXT NOT NULL);"""

    questions = """CREATE TABLE QUESTIONS
                   (Q_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                   QUESTION TEXT NOT NULL, MANDATORY BOOLEAN NOT NULL,
                   MCQ BOOLEAN NOT NULL);"""

    survey_questions = """CREATE TABLE SURVEY_QUESTIONS
                          (Q_ID INTEGER, SURVEY_ID INTEGER,
                          PRIMARY KEY (Q_ID, SURVEY_ID));"""

    surveys_completed = """CREATE TABLE SURVEYS_COMPLETED
                          (USER_ID TEXT NOT NULL,
                          SURVEY_ID INTEGER NOT NULL,
                          PRIMARY KEY (USER_ID, SURVEY_ID));"""

    guest_approvals = """CREATE TABLE GUEST_APPROVALS
                         (USER_ID TEXT PRIMARY KEY NOT NULL,
                         APPROVED BOOLEAN NOT NULL);"""

    times = """CREATE TABLE SURVEY_TIMES
               (SURVEY_ID INTEGER,
               CLOSE_TIME timestamp,
               PRIMARY KEY (SURVEY_ID, CLOSE_TIME));"""

    bar = progressbar.ProgressBar()
    for query in bar((courses, enrolments, surveys, users, metrics, questions,
                      survey_questions, surveys_completed, guest_approvals, times)):
            dbadd(query)


def empty_tables(tables):
    bar = progressbar.ProgressBar()
    for table in bar(tables):
        dbadd("DELETE FROM {};".format(table))
        dbadd("DELETE FROM sqlite_sequence WHERE name='{}';".format(table))


def init_courses():
    bar = progressbar.ProgressBar()
    for line in bar(read_csv('csv/courses.csv')):
        add_course(line[0], line[1])


def init_users():

    users = {}
    for line in read_csv('csv/passwords.csv'):
        users[line[0]] = [line[1], line[2], []]
    for line in read_csv('csv/enrolments.csv'):
        users[line[0]][2].append(course_id(line[1], line[2]))

    bar = progressbar.ProgressBar()
    for user_id, info in bar(users.items()):
            add_user(user_id, generate_password_hash(info[0]), info[1])
            for course in info[2]:
                add_enrolment(user_id, course)


def init():
    print("creating tables ...")
    # time.sleep(1)
    initialiseDB()
    print("initialising courses (csv -> database) ...")
    # time.sleep(1)
    init_courses()
    print("initialising users (csv -> database) ...")
    # time.sleep(1)
    init_users()
