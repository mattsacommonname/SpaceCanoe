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
