import datetime
from basic_actions import *
from tkinter import ttk

window = ttk.Style()


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

    returned = False
    while not returned:
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
                               '/back for back\n'
                               'Also /set for settings >>> ')
                if prompt == '/add':
                    friend_to_add = input('Type a nickname >>> ')
                    add_friend(user_login, friend_to_add)
                    break
                elif prompt == '/set':
                    settings(user_login)
                elif prompt == '/back':
                    returned = True
                    break
                else:
                    if prompt in chats_list_v:
                        if os.path.exists(os.path.join(os.path.abspath('chats'),
                                                       prompt + '.txt')):
                            print('Chat exists. Entering... ')
                        elif os.path.exists(os.path.abspath('chats')):
                            print('Some prick has deleted file, '
                                  'but we initialized empty chat '
                                  'with the same name')
                        else:
                            print('Some prick deleted the main folder chats, '
                                  'but we anticipated it')
                    else:
                        print('Creating chat...')
                        with open('chats.txt', 'a', encoding='utf-8') \
                                as chats_roster_write:
                            chats_roster_write.write(prompt + '\n')
                    chat(user_login, prompt)


def chat(logged_user: str, chat_name: str):
    if not os.path.exists(os.path.join(os.path.abspath('chats'),
                                       chat_name + '.txt')):
        os.mkdir('chats')
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
