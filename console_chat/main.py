from typing import TextIO
import datetime
from friends import open_chats
import os


def welcome_menu():
    logged_in = False
    print('Messenger by Dmitry Goryachev. Welcome!')
    login = None
    while not logged_in:
        try:
            action = int(input('1. Log in\n2. Sign up.\n0. Quit\n>>> '))
        except ValueError:
            print('Enter a valid number of choice!')
        else:
            if action == 0:
                exit(0)
            elif action == 1:
                logged_in, login = ask_for_login()
            elif action == 2:
                ask_for_register()
            else:
                print('Enter a valid number of choice!')
    return login


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
        if char == char.upper():
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


def ask_for_register():
    while True:

        login = input('Create a login: ')
        if check_presence_of_user(login):
            print('User with such login already exists! Please log in')
            ask_for_login()
            break
        else:
            password = input('Create a password (at least 8 symbols, '
                             'a capital letter and number): ')
            if password_check(password):
                write_new_data(login, password)
                print('User created successfully! Now login!')
                break
            else:
                print('Password should contain at least 8 symbols, '
                      'a capital letter and number)')


def ask_for_login() -> tuple or bool:
    tries = 3

    login = input('Login >>> ')
    if check_presence_of_user(login) and \
            not blacklisted(login, 'r'):
        while tries != 0:
            password = input('Password >>> ')
            if password_check(password):
                print('Successfully logged in!')
                return True, login
            else:
                print('Access denied!')
                tries -= 1
        else:
            blacklisted(login, 'a')
    else:
        print('Login does not exist or the account was banned '
              'due to security rules violation. To unban, contact our support')
        return False, None


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


def settings(login_user: str):
    print('Settings')
    options = {1, 2, 3}
    while True:
        try:
            action = int(input('1. Remove/ban friend\n'
                               '2. Clear message history\n'
                               '3. Log out\n>>> '))
        except ValueError:
            print('Invalid input!')
        else:
            if action in options:
                if action == 1:
                    remove_friends(login_user)
                elif action == 2:
                    print('You cannot clear public chats)')
                else:
                    exit(0)
            else:
                print('Incorrect option')


def messenger(user_login: str):

    if user_login not in open_chats.keys():
        print('Nothing here yet. To start using app, add at least one friend.'
              'Type a nickname to add a friend:')
        while True:
            address = input('>>> ')

            if check_presence_of_user(address):
                add_friend(user_login, address)
                break
            else:
                print('No user found. Maybe he is not still with us? '
                      'Try typing something else')

    while True:
        print('Friends:')
        for index, friend in enumerate(open_chats[user_login]):
            print(f'{index + 1}. {friend}')
        print('Chats: ')

        with open('chats.txt', 'r', encoding='utf-8') as chats_roster:
            chats_list_v = []
            for index, chat_name in enumerate(chats_roster):
                chats_list_v.append(chat_name.rstrip())
                print(f'{index + 1}. {chat_name.rstrip()}')

            while True:
                prompt = input('Create a chat or '
                               'type /add to add friends.\n'
                               'Also /set for settings >>> ')
                if prompt == '/add':
                    friend_to_add = input('Type a nickname >>> ')
                    add_friend(user_login, friend_to_add)
                    break
                elif prompt == '/set':
                    settings(user_login)
                else:
                    if prompt in chats_list_v:
                        print('Chat exists. Entering... ')
                    else:
                        print('Creating chat...')
                        with open('chats.txt', 'a', encoding='utf-8') \
                                as chats_roster_write:
                            chats_roster_write.write(prompt + '\n')
                    chat(user_login, prompt)


def chat(logged_user: str, chat_name: str):
    path = os.path.join(os.path.abspath('chats'), chat_name + '.txt')
    with open(path, 'a', encoding='utf-8') as private_data:
        active = True
        while active:
            msg = input('Message (/back to back) >>> ')
            if msg == '/back':
                active = 0
            else:
                private_data.write(f'On {datetime.datetime.now().strftime("%d-%m-%Y %H:%M")}:'
                                   f' {logged_user} said: {msg}\n')


def show_chat():
    with open('chats.txt', 'r', encoding='utf-8') as chats_roster:
        chat_pick = input('Enter chat: ')
        if chats_roster.read().__contains__(chat_pick):
            with open(os.path.join(os.path.abspath('chats'), chat_pick), 'r',
                      encoding='utf-8') as correspondence:
                for line in correspondence:
                    print(line.rstrip())
        else:
            print('No such chat here. Maybe misprint?')


if __name__ == '__main__':
    user = welcome_menu()
    while True:
        try:
            choice = int(input('1. Chat with someone\n'
                               '2.Read some chats\n'
                               '0. Quit\n>>> '))
        except ValueError:
            print('Invalid input!')
        else:
            if choice == 1:
                messenger(user)
            elif choice == 2:
                show_chat()
            elif choice == 0:
                exit(0)
            else:
                print('Invalid number')
