# Copyright 2019 Matthew Bishop
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


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


def add_user(name, password):
    with db_session:
        model = UserModel.get(name=name)
        if model:
            print(f'User "{name}" already exists.')
            return

        UserModel.build(name, password)


@login_manager.user_loader
def load_user(user_id):
    with db_session:
        model = UserModel[user_id]
        if not model:
            return None

        user = User(model.user_id, model.name)
        return user
