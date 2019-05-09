from flask_login import LoginManager, UserMixin
from pony.orm import db_session
from uuid import UUID

from database import User as UserModel


login_manager = LoginManager()


class User(UserMixin):
    def __init__(self, user_id: UUID, name: str):
        self.user_id = user_id
        self.name = name

    def get_id(self):
        id_text = str(self.user_id)
        return id_text


@login_manager.user_loader
def load_user(user_id):
    with db_session:
        model = UserModel[user_id]
        if not model:
            return None

        user = User(model.user_id, model.name)
        return user
