from typing import TextIO
from friends import open_chats
import os


def password_check(password: str) -> bool:
    flags = {
        'len_str_8': False,
        'capitals': False,
        'numbers': False
    }
    nums = [
        chr(index) for index in range(ord('0'), ord('9') + 1)
    ]
    if len(password) >= 8:
        flags['len_str_8'] = True

    for char in password:
        if char in nums:
            flags['numbers'] = True
        elif char == char.upper():
            flags['capitals'] = True

    return False not in flags.values()


def generate_dict(file: TextIO) -> dict:
    return {
            line.split(':')[0]: line.split(':')[1].rstrip() for line in file
        }


def check_presence_of_user(login: str) -> bool:
    with open('login.txt', 'r', encoding='utf-8') as login_data:
        dict_data = generate_dict(login_data)
        return login in dict_data.keys()


def check_password_user(password: str) -> bool:
    with open('login.txt', 'r', encoding='utf-8') as login_data:
        dict_data = generate_dict(login_data)
        return password in dict_data.values()


def write_new_data(login: str, password: str):
    with open('login.txt', 'a', encoding='utf-8') as login_write_data:
        login_write_data.write(f'{login}:{password}\n')


def blacklisted(login: str, mode: str):
    if mode == 'r':
        with open('ban_list.txt', mode, encoding='utf-8') as ban_check:
            return ban_check.read().__contains__(login)
    else:  # if mode == 'a'
        with open('ban_list.txt', mode, encoding='utf-8') as ban_addition:
            ban_addition.write(f"{login}\n")


def add_friend(active_user, added_user):
    with open('friends.py', 'w', encoding='utf-8') as friends_file:
        if active_user not in open_chats.keys():
            open_chats[active_user] = [added_user]
            friends_file.write(f'open_chats = {str(open_chats)}\n')
        elif check_presence_of_user(added_user) and \
                added_user not in open_chats[active_user]:
            open_chats[active_user].append(added_user)
            friends_file.write(f'open_chats = {str(open_chats)}\n')
        else:
            print('Cannot add friend. Either he is already friends, or is '
                  'not a user of our chat yet')


def remove_friends(active_user):
    with open('friends.py', 'w', encoding='utf-8') as friends_file:
        active = True
        while active:
            friend = input('Who to delete? >>> ')
            if check_presence_of_user(friend) \
                    and friend in open_chats[active_user]:
                open_chats[active_user].remove(friend)
                friends_file.write(f'open_chats = {str(open_chats)}\n')
            active = int(input('0-quit 1-continue >>> '))


def change_password(login: str):
    tries = 3
    while tries != 0:
        password_old = input('Old password >>> ')
        if check_password_user(password_old):
            break
        else:
            tries -= 1
            print(f'Wrong password! If you do it {tries} more time(s), '
                  f'we will ban you!')
    else:
        print('We warned you. You are a fraudster trying to hack '
              'the real user! Bye!')
        blacklisted(login, 'a')
        exit(0)

    while True:
        password_new = input('Enter a new password >>> ')
        if password_check(password_new):
            password_repeat = input('Repeat a password >>> ')
            if password_repeat == password_new:
                break
            else:
                print('Passwords do not coincide! Retry! ')
        else:
            print('Password should contain at least 8 symbols, '
                  'a capital letter and number)')

    with open('login.txt', 'r', encoding='utf-8') as database:
        dictionary = generate_dict(database)
        dictionary[login] = password_new
    with open('login.txt', 'w', encoding='utf-8') as database_write:  # rewrite login
        passing_str = ''
        for key, value in dictionary.items():
            passing_str += f'{key}:{value}\n'
        database_write.write(passing_str)


def settings(login_user: str):
    print('Settings')
    options = {1, 2, 3, 4}
    while True:
        try:
            action = int(input('1. Remove/ban friend\n'
                               '2. Clear message history\n'
                               '3. Change your password\n'
                               '4. Log out\n>>> '))
        except ValueError:
            print('Invalid input!')
        else:
            if action in options:
                if action == 1:
                    remove_friends(login_user)
                elif action == 2:
                    print('You cannot clear public chats)')
                elif action == 3:
                    change_password(login_user)
                else:
                    exit(0)
            else:
                print('Incorrect option')


def show_chat():
    with open('chats.txt', 'r', encoding='utf-8') as chats_roster:
        chat_pick = input('Enter chat: ')
        if chats_roster.read().__contains__(chat_pick):
            with open(os.path.join(os.path.abspath('chats'),
                                   chat_pick + '.txt'), 'r',
                      encoding='utf-8') as correspondence:
                for line in correspondence:
                    print(line.rstrip())
        else:
            print('No such chat here. Maybe misprint?')
