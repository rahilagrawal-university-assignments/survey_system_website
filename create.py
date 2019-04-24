import datetime as DT
from server import Question, Survey
from db_models import Controller
import functions as f
import server as s
import authenticate


def question(text, text_list, mandatory, mcq):
    # add question to course if not already there
    if text not in text_list and len(text) > 0:

        controller = Controller()
        controller.add_question(text, mandatory, mcq)

        new_key = controller.question_id(text)

        # create new question object
        new_q = Question(text, new_key, mandatory, mcq)
        s.questions_list[new_key] = new_q


def survey(q_list, code, sem, title, time):
    if q_list == []:
        raise AssertionError()
    controller = Controller()
    controller.add_survey(title, code, sem, q_list)
    link = controller.survey_id(title, code, sem)
    if time != "":
        controller.add_time(link, DT.datetime.now() + DT.timedelta(hours=time))

    # creates a new object using survey class
    new_survey = Survey(title, f.return_courseID(code, sem), code, sem, 2)

    # adds the checked questions to the survey questions list
    for i in q_list:
        question = f.find_question(i)
        new_survey.add_to_pool(question)

    new_survey.link = link
    # adds survey to the Global list of surveys
    s.surveys_list[link] = new_survey


def guest(username, password, code, sem):
    controller = Controller()
    controller.add_user(username, s.generate_password_hash(password), "guest")
    controller.add_guest(username, 0)
    controller.add_enrolment(username, f.return_courseID(code, sem))
    authenticate.get_user(username)


def approved_guest(username):
    controller = Controller()
    controller.approve_guest(username)


def finished_survey(sur, q_list):
    controller = Controller()
    for q in q_list:
        sur.add_to_pool(f.find_question(q))
    sur.status = 1
    controller.update_survey(sur.link, sur.status, q_list)

    return sur.link


def answers(user_id, link, answers):
    controller = Controller()
    controller.add_answer(link, answers)
    controller.add_completion(user_id, link)


def metrics(link):
    controller = Controller()
    user_ans = controller.retrieve_answers(link)
    dic = {}
    if user_ans:
        for i in range(len(user_ans[0])):
            dic[i+1] = [l[i] for l in user_ans]
    return dic


def close_survey(sur):
    sur.status = 0
    controller = Controller()
    controller.update_survey(sur.link, sur.status)


def check_survey_closed(sur):
    close_time = Controller().get_time(sur.link)
    try:
        close_time = close_time[0][0]
        if DT.datetime.today() >= close_time:
            close_survey(sur)
    except:
        pass    # No close time for this survey
