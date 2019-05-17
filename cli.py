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


from click import Argument, Command

from feeds import check_for_updates
from login import add_user


def add_user_command(name, password):
    add_user(name, password)


arg = Argument(('name',))
params = [arg]
arg = Argument(('password',))
params.append(arg)
AddUserCommand = Command('au', callback=add_user_command, params=params)


def check_for_updates_command():
    check_for_updates()


UpdateCommand = Command('up', callback=check_for_updates_command)
