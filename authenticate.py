from flask_login import login_user, current_user, login_required, logout_user
from server import User, users, login_manager
from db_models import Controller


def check_password(username, password):
    user = get_user(username)
    approved = True
    if user.role == "guest":
        approved = Controller().guest_approved(user.id)
    if user and user.check_password(password) and approved:
        login_user(user)
        return True
    return False


def check_user_type(u, p):
    return get_user(u).role if check_password(u, p) else False


@login_manager.user_loader
def get_user(user_id):
    if user_id not in users:
        controller = Controller()
        info = controller.get_user(user_id)
        enrolments = [t[0] for t in controller.get_enrolments(user_id)]
        if len(info) == 0:
            return None
        user = User(user_id, info[0][0], info[0][1],
                    enrolments)
        users[user_id] = user
        return user
    else:
        return users[user_id]
