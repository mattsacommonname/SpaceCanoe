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
from typing import Optional
from uuid import UUID

from database import User as UserModel


login_manager = LoginManager()


class User(UserMixin):
    """User object."""

    def __init__(self, user_id: UUID, name: str):
        """Constructor.

        :param user_id: The user's UUID.
        :param name: The user's name.
        """

        self.user_id = user_id
        self.name = name

    def get_id(self) -> str:
        """Get's the user's UUID as a string.

        :return: The user's UUID in a string format.
        """

        id_text: str = str(self.user_id)
        return id_text


def add_user(name: str, password: str) -> None:
    """Adds a user to the database.

    :param name: Name of the user.
    :param password: Plaintext password.
    """

    with db_session:
        # check if the user exists
        model: Optional[UserModel] = UserModel.get(name=name)
        if model:
            print(f'User "{name}" already exists.')
            return

        # create the user
        UserModel.build(name, password)


@login_manager.user_loader
def load_user(user_id: str) -> Optional[User]:
    """Login manager user loader callback. Attempts to find the user from the passed id.

    :param user_id: A string of a user ID. This will need to be parsable as a UUID.
    :return: The user if it's found. None if no matching user found.
    """

    user_uuid: UUID = UUID(user_id)

    with db_session:
        model: Optional[UserModel] = UserModel[user_uuid]
        if not model:
            return None  # no matching user found

        user: User = User(model.user_id, model.name)
        return user
