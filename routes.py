from flask import render_template, request, redirect, url_for
import datetime as DT
from server import app, Question, Course, Survey
from db_functions import init
from db_models import Controller, LibraryModel
import server as s
import functions as f
import create
from authenticate import *


@app.route('/', methods=["POST", "GET"])
@app.route('/login/<path:path>', methods=["POST", "GET"])
def index(path=None):
    valid, s.selected = True, ["", ""]
    s.current_guest = ["", ""]

    if current_user.is_authenticated:
        logout_user()

    if request.method == "POST":
        if "guest_bt" in request.form:
            return redirect(url_for('guest_registration'))
        username = request.form['username']
        password = request.form['password']
        valid = check_password(username, password)

        if valid:
            if current_user.role == "guest":
                survey = f.survey_from_course(s.courses_list[current_user.courses[0]].code,
                                              s.courses_list[current_user.courses[0]].sem)
                return redirect("survey={}".format(survey))
            elif path is None or path == "home":
                return redirect(url_for("%s_home" % current_user.role))
            else:
                return redirect(url_for(path))

    return render_template('login.html', valid=valid)


################
#    ADMIN     #
#   HOMEPAGE   #
################
@login_required
@app.route('/admin_home', methods=["POST", "GET"])
def admin_home():

    if not current_user.is_authenticated or current_user.role != "admin":
        return redirect('/login/home')

    guests = load_guests()

    if request.method == "POST":

        pages = ["add_questions", "active_surveys", "create_survey"]
        func = request.form.get('bt')

        if func == "options":
            return render_template('options.html',
                                   user=current_user)
        elif func == "preview":
            return redirect(url_for('preview', back=0))
        elif func in pages:
            return redirect(url_for(func))
        else:
            create.approved_guest(func)
            guests = load_guests()

    return render_template('admin_home.html',
                           user=current_user, guests=guests)


def load_guests():
    controller = Controller()
    return {user[0]: s.courses_list[controller.get_enrolments(user[0])[0][0]]
            for user in controller.get_guests()}


################
#    STAFF     #
#   HOMEPAGE   #
################
@login_required
@app.route('/staff_home', methods=["POST", "GET"])
def staff_home():

    if not current_user.is_authenticated or current_user.role != "staff":
        return redirect('/login/home')

    links = [[sur.title, sur.code, sur.sem, link] for link, sur in s.surveys_list.items()
             if sur.status == 2]

    return render_template('staff_home.html',
                           user=current_user,
                           surveys=links)


################
#    STUDENT   #
#   HOMEPAGE   #
################
@login_required
@app.route('/student_home', methods=["POST", "GET"])
def student_home():

    if not current_user.is_authenticated or current_user.role != "student":
        return redirect('/login/home')

    links = []

    if request.method == "POST" or s.chosen:
        s.chosen = request.form.get('course_selection')
        for link, sur in s.surveys_list.items():
            create.check_survey_closed(sur)
            not_completed = Controller().check_completed(current_user.id, sur.link)
            if not_completed and s.chosen and sur.status == 1 and sur.courseID == int(s.chosen):
                links.append([sur.title, sur.code, sur.sem, link])

    controller = Controller()
    enrolled_courses = {}
    for i in controller.get_enrolments(current_user.id):
        enrolled_courses[i[0]] = ' - '.join(controller.search_courses(i[0])[0])

    s.chosen = int(s.chosen) if s.chosen else s.chosen

    return render_template('student_home.html',
                           surveys=links, courses=enrolled_courses,
                           user=current_user, chosen=s.chosen)


@app.route('/guest_registration', methods=["POST", "GET"])
def guest_registration():

    registered = False

    if request.method == "POST":

        registered = get_selected()
        s.current_guest[0] = request.form['username']
        s.current_guest[1] = request.form['password']

        if "course_selection" in request.form:
            semester_fill(s.selected[0])

        if "register_bt" in request.form and registered:
            code, sem = s.selected[0], s.selected[1]
            if s.current_guest[0] == "" or s.current_guest[1] == "":
                registered = False
            else:
                create.guest(s.current_guest[0], s.current_guest[1], code, sem)
                s.current_guest = ["", ""]

    return render_template('guest_registration.html',
                           displays=[s.display_courses, s.display_sems],
                           values=s.selected, registered=registered,
                           current_guest=s.current_guest)


################
#    ADDING    #
#  QUESTIONS   #
################
@login_required
@app.route('/add_questions', methods=["POST", "GET"])
def add_questions():

    flag = False
    if not current_user.is_authenticated or current_user.role != "admin":
        return redirect('/login/add_questions')

    # triggers when the user presses a button
    # either 'add question' or 'preview questions'
    if request.method == "POST":

        # if user requests a preview of questions
        if "preview" in request.form:
            # redirect to preview page
            return redirect(url_for('preview', back=1,
                                    user=current_user))

        # if user has requested to add a question
        elif "question_bt" in request.form:
            text = request.form['question']
            notype1 = request.form.get('type1') is None
            notype2 = request.form.get('type1') is None
            if len(text) == 0 or notype1 or notype2:
                flag = True
            else:
                mandatory, mcq = request.form['type1'], request.form['type2']
                create.question(text, f.get_pool_text(), mandatory, mcq)

    # reload page retaining appropriate selected values
    return render_template('add.html',
                           user=current_user,
                           flag=flag)


################
#   VIEWING    #
#  QUESTIONS   #
################
@login_required
@app.route('/preview<back>')
def preview(back):

    if not current_user.is_authenticated:
        return redirect(url_for('index'))

    text = (current_user.role + "_home") if back == "0" else "add_questions"
    qs = [q.text for q in s.questions_list.values()]

    # display course and corresponding questions
    return render_template('preview.html',
                           questions=qs,
                           back=text,
                           user=current_user)


################
#   CREATING   #
#    SURVEY    #
################
@login_required
@app.route('/create_survey', methods=["POST", "GET"])
def create_survey():

    if not current_user.is_authenticated or current_user.role != "admin":
        return redirect('/login/create_survey')

    qs = {key: q.text for key, q in s.questions_list.items() if int(q.mandatory) == 1}

    created, exists = True, False

    if request.method == "POST":

        created = get_selected()

        # fills in semesters after code selection
        if "course_selection" in request.form:
            semester_fill(s.selected[0])

        if "create_survey_button" in request.form and created:
            code, sem = s.selected[0], s.selected[1]
            exists = f.survey_from_course(code, sem) != "not-found"
            q_list = request.form.getlist("available")
            title = request.form['title']
            time = request.form['time']
            correct_time = True
            try:
                time = int(time) if len(time) > 0 else time
            except:
                correct_time = False
            if not correct_time or len(q_list) <= 0 or not title:
                created = False
            elif not exists:
                create.survey(q_list, code, sem, title, time)

    # display course and corresponding questions
    return render_template('survey_creation.html',
                           user=current_user, values=s.selected,
                           displays=[s.display_courses, s.display_sems],
                           questions=qs, created=created,
                           exists=exists)


def get_selected():
    # the selected code and semester
    # s.selected[0] = code, s.selected[1] = semester
    s.selected[0] = request.form.get('course_selection')
    s.selected[1] = request.form.get('sem_selection')

    # checks whether they have actually been selected
    return False if s.selected[0] is None and s.selected[1] is None else True


def semester_fill(code_selected):
    s.display_sems = [course.sem for course in s.courses_list.values()
                      if course.code == code_selected]
    return True


################
#  COMPLETEING #
#    SURVEY    #
################
@app.route('/survey=<link>', methods=["POST", "GET"])
def do_survey(link):

    if not current_user.is_authenticated or current_user.role not in ("student", "guest"):
        return redirect('/login/active_surveys')

    if link != "not-found":
        completed = 0
        sur = f.find_survey(link)
        completed = Controller().check_completed(current_user.id, sur.link) is False
        create.check_survey_closed(sur)
        answers = []

        if (sur and sur.status in (0, 2)) and current_user.role == "student":
            return redirect(url_for('student_home'))

    if link == "not-found" or sur.status in (0, 2) or completed:
        return render_template('survey_completion.html',
                               user=current_user, not_found=True,
                               values=[s.courses_list[current_user.courses[0]].code,
                                       s.courses_list[current_user.courses[0]].sem])

    # Retreving answers from Form
    if request.method == "POST":
        if "submit_survey_bt" in request.form:
            completed = 1
            for q in sur.pool:
                if request.form.get(str(q.key)) is not None:
                    result = request.form[str(q.key)]
                    answers.append(result if len(result) > 0 else "NO ANSWER")
                elif q.mandatory == 1:
                    completed = 2
                    break
                else:
                    answers.append("NO ANSWER")
            if completed == 1:
                create.answers(current_user.id, link, answers)

    qs = {q.key: [q.text, q.mandatory, q.mcq] for q in sur.pool}

    # display course and corresponding questions
    return render_template('survey_completion.html',
                           questions=qs, not_found=False,
                           values=[sur.code, sur.sem, sur.title],
                           completed=completed, link=link,
                           user=current_user)


###############
#   ACTIVE    #
#   SURVEYS   #
###############
@login_required
@app.route('/active_surveys', methods=["POST", "GET"])
def active_surveys():

    if not current_user.is_authenticated or current_user.role != "admin":
        return redirect('/login/active_surveys')

    if request.method == "POST":
        if "close_survey" in request.form:
            survey = f.find_survey(request.form["close_survey"])
            create.close_survey(survey)

    active_surveys = [sur for sur in s.surveys_list.values()
                      if sur.status in (1, 2)]

    return render_template('active_surveys.html',
                           surveys=active_surveys,
                           user=current_user)


##############
#   SURVEY   #
#    VIEW    #
##############
@login_required
@app.route('/survey_overview/<link>')
def survey_overview(link):

    if not current_user.is_authenticated or current_user.role != "admin":
        return redirect(url_for('index'))

    sur = f.find_survey(link)
    qs = {q.key: [q.text, q.mandatory, q.mcq] for q in sur.pool}

    # metrics = {1: [ans1, ans2, ...], 2: [ans1, ans2, ...], ...}
    data = f.data_for_view(create.metrics(link))

    # display course and corresponding questions
    return render_template('metrics.html',
                           questions=qs, data=data,
                           values=[sur.code, sur.sem, sur.title],
                           link=link,
                           user=current_user)


@login_required
@app.route('/review_survey/<survey_link>', methods=["POST", "GET"])
def review_survey(survey_link):

    if not current_user.is_authenticated or current_user.role != "staff":
        return redirect('/login/review_survey')

    link = None

    qs = {key: q.text for key, q in s.questions_list.items() if int(q.mandatory) == 0}

    in_survey = [q.text for q in f.find_survey(survey_link).pool]

    if request.method == "POST":
        if "open_survey_bt" in request.form:
            q_list = request.form.getlist("available")
            link = create.finished_survey(f.find_survey(survey_link), q_list)
        return redirect(url_for('staff_home'))

    # display course and corresponding questions
    return render_template('survey_review.html',
                           questions=qs, in_survey=in_survey,
                           user=current_user, link=link)


##################
#     SERVER     #
# INITIALISATION #
##################

def init_DB():
    init()
    model = LibraryModel()

    # creates list of Course instances
    # also files in list of course codes to be chosen from
    for c in model.get_everything("COURSES"):
        new_course = Course(c[1], c[2], c[0])
        s.courses_list[c[0]] = new_course
        if new_course.code not in s.display_courses:
            s.display_courses.append(new_course.code)

    # initialises questions list
    for q in model.get_everything("QUESTIONS"):
        question = Question(q[1], q[0], q[2], q[3])
        s.questions_list[q[0]] = question

    # initialises list of surveys
    for sur in model.get_everything("SURVEYS"):
        c = model.search_courses(sur[2])[0]
        q_list = [f.find_question(e[0]) for e in model.survey_questions(sur[0])]
        survey = Survey(sur[1], sur[2], c[0], c[1], sur[3],
                        q_list, sur[0])
        s.surveys_list[sur[0]] = survey
