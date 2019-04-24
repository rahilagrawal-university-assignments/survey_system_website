import csv
import string
import random
import datetime
import server as s


# 2D LIST OF ROWS AND COLUMNS
def read_csv(file_name):
    r = csv.reader(open(file_name))
    return_list = [l for l in r]
    return return_list


# GENERATE RANDOM IDENTIFICATION KEY
def generate_key():
    possible = string.ascii_letters + string.digits
    return ''.join(random.choice(possible) for i in range(5))


def data_for_view(answers):

    def in_list(l, ans):
        for item in l:
            if item[0] == ans:
                return True
        return False

    data = {}
    for key, items in answers.items():
        data[key] = []
        for ans in items:
            if ans is not None and not in_list(data[key], ans):
                data[key].append([ans, 1])
            else:
                for i in data[key]:
                    if i[0] == ans:
                        i[1] += 1
                        break
    return data


#################
#     CLASS     #
#   FUNCTIONS   #
#################

def get_pool_text():
    return [q.text for q in s.questions_list.values()]


def find_question(key):
    try:
        return s.questions_list[int(key)]
    except:
        return None


def find_survey(link):
    try:
        return s.surveys_list[int(link)]
    except:
        return None


def return_courseID(code, sem):
    for ID, course in s.courses_list.items():
        if course.code == code and course.sem == sem:
            return ID
    return None


def keys(q_list):
    return [str(q.key) for q in q_list]


def survey_from_course(code, sem):
    for link, sur in s.surveys_list.items():
        closed = sur.status == 0
        if sur.code == code and sur.sem == sem and not closed:
            return link
    return "not-found"
