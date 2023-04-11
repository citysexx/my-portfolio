from tkinter import *
import shift_gen
from os import path, startfile
import customtkinter
from PIL import Image, ImageTk
import database
from typing import Dict, Any, Tuple
import tkinter as tk
from tkinter import messagebox
from time import sleep
from passwords import users


WEEK = database.date_init()
DAYS_EDGE = (WEEK[0][0], WEEK[0][6])
MONTHS_EDGE = (WEEK[1][0], WEEK[1][6])

# init weekends from file
file_name = f'holidays-{DAYS_EDGE[0]}.{MONTHS_EDGE[0]}-' \
                f'{DAYS_EDGE[1]}.{MONTHS_EDGE[1]}.log'
dir_name = 'holidays'
database.restore_files(file_name=file_name, dir_name=dir_name)

# globals
weekends_values: Dict[str, Any] = {}
emps_dictionary = database.database_init()[0]
shifts_dictionary = database.database_init()[1]

USERS = users
AUTHORIZED = False


with open(path.join(path.abspath('holidays'), file_name), 'r', encoding='utf-8') as file:
    for line in file:
        if line.rstrip() == '':
            break
        else:
            weekends_values[line.rstrip().split(':')[0]] = line.rstrip().split(':')[1]


class App(customtkinter.CTk):
    """
    Main app window. There is no need to explain what every attribute means
    because they are all objects, and they are all called respectively with
    the function they carry out
    """
    def __init__(self):
        super().__init__()
        # define window size
        self.title('Scheduler Bot v 1.0 release')
        self.iconbitmap(path.abspath('Sport-table-tennis.ico'))
        self.geometry("400x200")
        self.eval('tk::PlaceWindow . center')

        # define images
        self.add_generation_image = ImageTk.PhotoImage(Image.open('genbot.png').resize((20, 20), Image.LANCZOS))
        self.add_settings_image = ImageTk.PhotoImage(Image.open('settings.png').resize((20, 20), Image.LANCZOS))
        self.add_employee_image = ImageTk.PhotoImage(Image.open('employee.png').resize((20, 20), Image.LANCZOS))
        self.add_shifts_image = ImageTk.PhotoImage(Image.open('schedule_shifts.png').resize((20, 20), Image.LANCZOS))
        self.add_history_image = ImageTk.PhotoImage(Image.open('history.png').resize((20, 20), Image.LANCZOS))
        self.add_folder_image = ImageTk.PhotoImage(Image.open('folder.png').resize((20, 20), Image.LANCZOS))
        self.add_weekend_image = ImageTk.PhotoImage(Image.open('weekend.png').resize((20, 20), Image.LANCZOS))

        # define buttons
        self.main_frame = customtkinter.CTkFrame(master=self, width=400, height=150)
        self.btn_gen = customtkinter.CTkButton(master=self.main_frame,
                                               image=self.add_generation_image,
                                               text='Генерировать',
                                               width=190,
                                               height=40,
                                               compound='left',
                                               command=generate_full)
        self.btn_set = customtkinter.CTkButton(master=self.main_frame,
                                               image=self.add_settings_image,
                                               text='Настройки',
                                               width=190,
                                               height=40,
                                               compound='left',
                                               command=settings_window)
        self.btn_employees = customtkinter.CTkButton(master=self.main_frame,
                                                     image=self.add_employee_image,
                                                     text='Сотрудники',
                                                     width=190,
                                                     height=40,
                                                     compound='left',
                                                     command=edit_employees_window)
        self.btn_shifts = customtkinter.CTkButton(master=self.main_frame,
                                                  image=self.add_shifts_image,
                                                  text='Смены',
                                                  width=190,
                                                  height=40,
                                                  compound='left',
                                                  command=edit_shifts_window)
        self.btn_open_logs = customtkinter.CTkButton(master=self.main_frame,
                                                     image=self.add_history_image,
                                                     text='История',
                                                     width=190,
                                                     height=40,
                                                     compound='left',
                                                     command=open_explorer_logs)
        self.btn_open_gen_folder = customtkinter.CTkButton(master=self.main_frame,
                                                           image=self.add_folder_image,
                                                           text='Графики',
                                                           width=190,
                                                           height=40,
                                                           compound='left',
                                                           command=open_explorer_schedules)

        # curr date

        self.btn_add_weekends = customtkinter.CTkButton(master=self,
                                                        image=self.add_weekend_image,
                                                        text=f'Проставить выходные на следующую '
                                                             f'неделю {DAYS_EDGE[0]}.{MONTHS_EDGE[0]} - '
                                                             f'{DAYS_EDGE[1]}.{MONTHS_EDGE[1]}',
                                                        width=390,
                                                        height=40,
                                                        compound='left',
                                                        command=handle_weekends)

        # spawn items
        self.main_frame.grid(row=0, column=0)
        self.btn_gen.grid(row=0, column=0, padx=5, pady=5)
        self.btn_set.grid(row=1, column=0, padx=5, pady=5)
        self.btn_employees.grid(row=2, column=0, padx=5, pady=5)
        self.btn_shifts.grid(row=0, column=1, padx=5, pady=5)
        self.btn_open_logs.grid(row=1, column=1, padx=5, pady=5)
        self.btn_open_gen_folder.grid(row=2, column=1, padx=5, pady=5)
        self.btn_add_weekends.grid(row=1, column=0, pady=5)

    def refresh(self):
        self.destroy()
        self.__init__()
        self.mainloop()


class FlexibleAddWindow(customtkinter.CTkToplevel):
    """
    This window is needed to add shifts or employees
    """
    def __init__(self, listbox: ['Listbox'],
                 window_belongs: str,
                 edit: bool = False) -> None:
        super().__init__()
        self.window_belongs = window_belongs
        if window_belongs == 'employees':
            self.old_name = None
            self.edit = edit
            self.listbox = listbox
            self.title('Добавить сотрудника')
            self.iconbitmap(path.abspath('Sport-table-tennis.ico'))
            self.geometry("500x150")

            self.upper_frame = customtkinter.CTkFrame(master=self,
                                                      width=200,
                                                      height=40,
                                                      bg_color='#1A1A1A',
                                                      fg_color='#1A1A1A')
            self.lower_frame = customtkinter.CTkFrame(master=self,
                                                      width=200,
                                                      height=40,
                                                      bg_color='#1A1A1A',
                                                      fg_color='#1A1A1A')

            self.label = customtkinter.CTkLabel(master=self.upper_frame,
                                                text=f'Укажите фамилию сотрудника и его начало и конец рабочих часов')

            self.entry_field = customtkinter.CTkEntry(master=self.upper_frame, width=400)
            self.begin_label_1 = customtkinter.CTkLabel(master=self.lower_frame, text='С')
            self.begin_label_2 = customtkinter.CTkLabel(master=self.lower_frame, text='часов')
            self.end_label_1 = customtkinter.CTkLabel(master=self.lower_frame, text='по')
            self.end_label_2 = customtkinter.CTkLabel(master=self.lower_frame, text='часов')
            self.begin_hour = customtkinter.CTkOptionMenu(master=self.lower_frame,
                                                          width=40,
                                                          height=20,
                                                          values=[str(i) for i in range(0, 25)])
            self.end_hour = customtkinter.CTkOptionMenu(master=self.lower_frame,
                                                        width=40,
                                                        height=20,
                                                        values=[str(i) for i in range(0, 25)])
            if self.edit:
                self.old_name = self.listbox.get(ANCHOR).split('-')[0]
                self.hours = self.listbox.get(ANCHOR).split('-')[1]
                self.hour_begin = self.hours.split()[2]
                self.hour_end = self.hours.split()[4]
                self.entry_field.insert(0, self.old_name)
                self.begin_hour = customtkinter.CTkOptionMenu(master=self.lower_frame,
                                                              width=40,
                                                              height=20,
                                                              values=[
                                                                  str(num)
                                                                  if index != 0
                                                                  else self.hour_begin
                                                                  for index, num
                                                                  in enumerate(range(0, 25))
                                                              ])

                self.end_hour = customtkinter.CTkOptionMenu(master=self.lower_frame,
                                                            width=40,
                                                            height=20,
                                                            values=[
                                                                str(num)
                                                                if index != 0
                                                                else self.hour_end
                                                                for index, num in
                                                                enumerate(range(0, 25))
                                                            ])

            else:
                self.begin_hour = customtkinter.CTkOptionMenu(master=self.lower_frame,
                                                              width=40,
                                                              height=20,
                                                              values=[str(i) for i in range(0, 25)])
                self.end_hour = customtkinter.CTkOptionMenu(master=self.lower_frame,
                                                            width=40,
                                                            height=20,
                                                            values=[str(i) for i in range(0, 25)])

            self.btn_confirm = customtkinter.CTkButton(master=self,
                                                       text='Подтвердить',
                                                       command=lambda: save_employees((
                                                           self,
                                                           self.entry_field,
                                                           self.begin_hour,
                                                           self.end_hour,
                                                           self.listbox
                                                       ),
                                                           edit))

            self.upper_frame.pack()
            self.lower_frame.pack(pady=5)
            self.label.grid(row=0, column=0)
            self.entry_field.grid(row=1, column=0, pady=5)
            self.begin_hour.grid(row=0, column=1, pady=5, padx=5)
            self.end_hour.grid(row=0, column=3, pady=5, padx=5)
            self.begin_label_1.grid(row=0, column=0, pady=5, padx=5)
            self.begin_label_2.grid(row=0, column=1, pady=5, padx=5)
            self.end_label_1.grid(row=0, column=2, pady=5, padx=5)
            self.end_label_2.grid(row=0, column=4, pady=5, padx=5)
            self.btn_confirm.pack(pady=5)

        elif window_belongs == 'shifts':
            self.title('Добавить смену')
            self.iconbitmap(path.abspath('Sport-table-tennis.ico'))
            self.geometry("400x200")
            self.old_name = None
            self.edit = edit
            self.listbox = listbox

            self.upper_frame = customtkinter.CTkFrame(master=self,
                                                      width=200,
                                                      height=40,
                                                      bg_color='#1A1A1A',
                                                      fg_color='#1A1A1A')
            self.lower_frame = customtkinter.CTkFrame(master=self,
                                                      width=200,
                                                      height=40,
                                                      bg_color='#1A1A1A',
                                                      fg_color='#1A1A1A')

            self.label = customtkinter.CTkLabel(master=self.upper_frame,
                                                text=f'Укажите название смены и ее начало')

            self.entry_field = customtkinter.CTkEntry(master=self.upper_frame, width=400)

            self.begin_hour = customtkinter.CTkOptionMenu(master=self.lower_frame,
                                                          width=40,
                                                          height=20,
                                                          values=[str(i) for i in range(0, 25)])

            if self.edit:
                self.old_name = self.listbox.get(ANCHOR).split('-')[0]
                self.hours = self.listbox.get(ANCHOR).split('-')[1]
                self.hour_begin = self.hours.split()[2]
                self.entry_field.insert(0, self.old_name)
                self.begin_hour = customtkinter.CTkOptionMenu(master=self.lower_frame,
                                                              width=40,
                                                              height=20,
                                                              values=[
                                                                  str(num)
                                                                  if index != 0
                                                                  else self.hour_begin
                                                                  for index, num
                                                                  in enumerate(range(0, 25))
                                                              ])

            else:
                self.begin_hour = customtkinter.CTkOptionMenu(master=self.lower_frame,
                                                              width=40,
                                                              height=20,
                                                              values=[str(i) for i in range(0, 25)])
                self.end_hour = customtkinter.CTkOptionMenu(master=self.lower_frame,
                                                            width=40,
                                                            height=20,
                                                            values=[str(i) for i in range(0, 25)])

            self.btn_confirm = customtkinter.CTkButton(master=self,
                                                       text='Подтвердить',
                                                       command=lambda: save_shifts((
                                                           self,
                                                           self.entry_field,
                                                           self.begin_hour,
                                                           self.listbox
                                                       ),
                                                           edit))

            self.upper_frame.pack()
            self.lower_frame.pack(pady=5)
            self.label.grid(row=0, column=0)
            self.entry_field.grid(row=1, column=0, pady=5)
            self.begin_hour.grid(row=0, column=0, pady=5, padx=5)
            self.btn_confirm.pack(pady=5)

        else:
            raise UserWarning('No target!')

    def refresh(self) -> None:
        self.destroy()
        self.__init__(listbox=self.listbox,
                      window_belongs=self.window_belongs,
                      edit=self.edit)
        self.mainloop()


class EmployeeWindow(customtkinter.CTkToplevel):
    """
    this window is needed to display employees
    """
    def __init__(self):
        super().__init__()
        self.title('Редактировать сотрудников')
        self.iconbitmap(path.abspath('Sport-table-tennis.ico'))
        self.geometry("245x450")

        self.addition_image = ImageTk.PhotoImage(Image.open('plus.png').resize((20, 20), Image.LANCZOS))
        self.subtraction_image = ImageTk.PhotoImage(Image.open('minus.png').resize((20, 20), Image.LANCZOS))
        self.edition_image = ImageTk.PhotoImage(Image.open('edit.png').resize((20, 20), Image.LANCZOS))

        self.buttons_frame = customtkinter.CTkFrame(master=self,
                                                    width=200,
                                                    height=40,
                                                    bg_color='#1A1A1A',
                                                    fg_color='#1A1A1A')
        self.btn_add_employee = customtkinter.CTkButton(master=self.buttons_frame,
                                                        text='',
                                                        width=20,
                                                        height=20,
                                                        image=self.addition_image,
                                                        command=lambda: add(self.employees_listbox,
                                                                            window_belongs='employees'))
        self.btn_remove_employee = customtkinter.CTkButton(master=self.buttons_frame,
                                                           text='',
                                                           width=20,
                                                           height=20,
                                                           image=self.subtraction_image,
                                                           command=lambda: delete(self.employees_listbox,
                                                                                  window_belongs='employees'))
        self.btn_edit_employee = customtkinter.CTkButton(master=self.buttons_frame,
                                                         text='',
                                                         width=20,
                                                         height=20,
                                                         image=self.edition_image,
                                                         command=lambda: add(self.employees_listbox,
                                                                             window_belongs='employees',
                                                                             edit=True))

        # define frames
        self.employees_listbox = tk.Listbox(master=self,
                                            highlightcolor='black',
                                            bg='#1A1A1A',
                                            foreground='grey',
                                            width=40,
                                            height=25,
                                            highlightbackground='black',
                                            highlightthickness=0)

        # grid
        self.employees_listbox.grid(row=0, column=0)
        self.buttons_frame.grid(row=1, column=0)
        self.btn_add_employee.grid(row=2, column=0, padx=2, pady=10)
        self.btn_remove_employee.grid(row=2, column=1, padx=2, pady=10)
        self.btn_edit_employee.grid(row=2, column=2, padx=2, pady=10)

    def refresh(self) -> None:
        self.destroy()
        self.__init__()
        self.mainloop()


class ShiftWindow(customtkinter.CTkToplevel):
    """
    this window is needed to display shifts
    """
    def __init__(self):
        super().__init__()
        self.title('Редактировать смены')
        self.iconbitmap(path.abspath('Sport-table-tennis.ico'))
        self.geometry("155x450")

        self.addition_image = ImageTk.PhotoImage(Image.open('plus.png').resize((20, 20), Image.LANCZOS))
        self.subtraction_image = ImageTk.PhotoImage(Image.open('minus.png').resize((20, 20), Image.LANCZOS))
        self.edition_image = ImageTk.PhotoImage(Image.open('edit.png').resize((20, 20), Image.LANCZOS))

        self.buttons_frame = customtkinter.CTkFrame(master=self,
                                                    width=200,
                                                    height=40,
                                                    bg_color='#1A1A1A',
                                                    fg_color='#1A1A1A')
        self.btn_add_shift = customtkinter.CTkButton(master=self.buttons_frame,
                                                     text='',
                                                     width=20,
                                                     height=20,
                                                     image=self.addition_image,
                                                     command=lambda: add(self.shifts_listbox,
                                                                         window_belongs='shifts'))
        self.btn_remove_shift = customtkinter.CTkButton(master=self.buttons_frame,
                                                        text='',
                                                        width=20,
                                                        height=20,
                                                        image=self.subtraction_image,
                                                        command=lambda: delete(self.shifts_listbox,
                                                                               window_belongs='shifts'))
        self.btn_edit_shift = customtkinter.CTkButton(master=self.buttons_frame,
                                                      text='',
                                                      width=20,
                                                      height=20,
                                                      image=self.edition_image,
                                                      command=lambda: add(self.shifts_listbox,
                                                                          window_belongs='shifts',
                                                                          edit=True))

        # define frames
        self.shifts_listbox = tk.Listbox(master=self,
                                         highlightcolor='black',
                                         bg='#1A1A1A',
                                         foreground='grey',
                                         width=25,
                                         height=25,
                                         highlightbackground='black',
                                         highlightthickness=0)

        # grid
        self.shifts_listbox.grid(row=0, column=0)
        self.buttons_frame.grid(row=1, column=0)
        self.btn_add_shift.grid(row=2, column=0, padx=2, pady=10)
        self.btn_remove_shift.grid(row=2, column=1, padx=2, pady=10)
        self.btn_edit_shift.grid(row=2, column=2, padx=2, pady=10)


class Settings(customtkinter.CTkToplevel):
    """
    Settings window
    """
    def __init__(self):
        super().__init__()
        self.title('Настройки')
        self.iconbitmap(path.abspath('Sport-table-tennis.ico'))
        self.geometry("400x150")
        # TODO настройки какие?


class WeekendsWindow(customtkinter.CTkToplevel):
    """
    Window that displays a table of weekends
    """
    def __init__(self):
        super().__init__()
        global weekends_values
        # create a new local instance of schedule
        schedule = shift_gen.Schedule()

        # Weekends graph window
        self.title(f'Выходные за {DAYS_EDGE[0]}.{MONTHS_EDGE[0]}-'
                   f'{DAYS_EDGE[1]}.{MONTHS_EDGE[1]}')
        self.iconbitmap(path.abspath('Sport-table-tennis.ico'))
        self.geometry("380x910")
        self.weekends_scrollable_frame = customtkinter.CTkScrollableFrame(master=self,
                                                                          width=350,
                                                                          height=800,
                                                                          bg_color='#1A1A1A',
                                                                          fg_color='#1A1A1A')
        self.weekends_upper_frame = customtkinter.CTkFrame(master=self,
                                                           width=500,
                                                           height=40,
                                                           bg_color='#1A1A1A',
                                                           fg_color='#1A1A1A')
        self.weekends_upper_frame.grid(row=0, column=0)
        self.weekends_scrollable_frame.grid(row=1, column=0)

        self.schedule_layout = schedule.init_layout()
        self.schedule_layout.append(shift_gen.Cell(1, len(schedule.emps) + 1))
        for cell in schedule.init_layout():
            if cell.protected():
                if cell.get_y() == 0:
                    label = customtkinter.CTkLabel(master=self.weekends_upper_frame, text=cell.get_info(), width=32)
                    label.grid(column=cell.get_x(), row=cell.get_y(), padx=2, pady=2)
                else:
                    label = customtkinter.CTkLabel(master=self.weekends_scrollable_frame, text=cell.get_info())
                    label.grid(column=cell.get_x(), row=cell.get_y(), padx=2, pady=2)
            else:
                try:
                    if weekends_values[f'{cell.get_x()};{cell.get_y()}'].get() == "on":
                        check_var = customtkinter.StringVar(value="on")
                    else:
                        check_var = customtkinter.StringVar(value="off")
                except AttributeError:
                    if weekends_values[f'{cell.get_x()};{cell.get_y()}'] == 'on':
                        check_var = customtkinter.StringVar(value="on")
                    else:
                        check_var = customtkinter.StringVar(value="off")
                except KeyError:
                    check_var = customtkinter.StringVar(value="off")

                tick = customtkinter.CTkCheckBox(master=self.weekends_scrollable_frame,
                                                 text='',
                                                 variable=check_var,
                                                 onvalue="on",
                                                 offvalue="off",
                                                 width=30,
                                                 command=lambda: mute_weekends(f'{cell.get_x()};{cell.get_y()}'))
                if cell.get_x() == 1 and cell.get_y() == len(schedule.emps) + 1:
                    pass
                else:
                    tick.grid(column=cell.get_x(), row=cell.get_y(), padx=2, pady=2)
                weekends_values[f'{cell.get_x()};{cell.get_y()}'] = tick
        self.btn_save = customtkinter.CTkButton(master=self,
                                                text='Сохранить текущий расклад на неделю',
                                                width=350,
                                                height=40,
                                                compound='left',
                                                command=ensure_save)
        self.btn_save.grid(row=2, column=0, pady=10)


class EnsureSaveWindow(customtkinter.CTkToplevel):
    """
    Are you sure you want to save something?
    """
    def __init__(self):
        super().__init__()
        self.title('Подтверждение')
        self.iconbitmap(path.abspath('Sport-table-tennis.ico'))
        self.geometry("1000x100")
        self.upper_frame = customtkinter.CTkFrame(master=self,
                                                  width=200,
                                                  height=50,
                                                  bg_color='#1A1A1A',
                                                  fg_color='#1A1A1A')
        self.lower_frame = customtkinter.CTkFrame(master=self,
                                                  width=200,
                                                  height=20,
                                                  bg_color='#1A1A1A',
                                                  fg_color='#1A1A1A')
        self.upper_frame.pack()
        self.lower_frame.pack()

        self.label = customtkinter.CTkLabel(master=self.upper_frame,
                                            text='Вы уверены? '
                                                 'Данные о выходных все равно будут автосохраняться, '
                                                 'но если вы закроете программу без ручного сохранения, '
                                                 'изменения не примутся!',
                                            width=1000)
        self.label.pack()
        self.btn_yes = customtkinter.CTkButton(master=self.lower_frame,
                                               text='Да',
                                               width=75,
                                               height=20,
                                               compound='left',
                                               anchor='s',
                                               command=lambda: save_weekends(self))
        self.btn_no = customtkinter.CTkButton(master=self.lower_frame,
                                              text='Нет',
                                              width=75,
                                              height=20,
                                              compound='left',
                                              command=self.destroy,
                                              anchor='s')
        self.btn_yes.grid(column=0, row=0, pady=20)
        self.btn_no.grid(column=1, row=0, pady=20)


class AuthorizationWindow(customtkinter.CTk):
    """
    login password window
    """
    def __init__(self):
        super().__init__()
        self.title('Авторизация')
        self.iconbitmap(path.abspath('Sport-table-tennis.ico'))
        self.geometry("215x145")
        self.eval('tk::PlaceWindow . center')

        self.frame = customtkinter.CTkFrame(master=self,
                                            width=200,
                                            height=40,
                                            bg_color='#1A1A1A',
                                            fg_color='#1A1A1A')
        self.login_label = customtkinter.CTkLabel(master=self.frame,
                                                  text='Логин:')
        self.password_label = customtkinter.CTkLabel(master=self.frame,
                                                     text='Пароль:')
        self.login_entry = customtkinter.CTkEntry(master=self.frame)
        self.password_entry = customtkinter.CTkEntry(master=self.frame, show="*")

        self._btn_confirm = customtkinter.CTkButton(master=self,
                                                    text='Войти',
                                                    command=lambda: check_user(window=self))

        self.frame.grid(row=0, column=0, pady=10)
        self._btn_confirm.grid(row=1, column=0, pady=5)
        self.login_label.grid(row=0, column=0, padx=5, pady=5)
        self.login_entry.grid(row=0, column=1, padx=5, pady=5)
        self.password_label.grid(row=1, column=0, padx=5, pady=5)
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)


def check_user(window: 'customtkinter.CTk()') -> None:
    """
    checks auth
    """
    global USERS
    global AUTHORIZED
    login = window.login_entry.get()
    password = window.password_entry.get()
    if login not in USERS or password != USERS[login]:
        sleep(2)
        messagebox.showwarning(title='Предупреждение',
                               message='Неверный логин или пароль!')
        return
    AUTHORIZED = True
    sleep(3)
    window.destroy()
    return


def generate_full() -> None:
    """
    generates a full schedule for a week
    :return: None
    """
    global app
    schedule = shift_gen.Schedule()
    for day in range(1, 8):
        schedule.generate_day(day)
    messagebox.showinfo(title='Информация', message='Успешно сгенерировано!')
    app.refresh()


def settings_window() -> None:
    """
    This is a settings window func
    :return:
    """
    settings = customtkinter.CTkToplevel(app)
    settings.mainloop()


def edit_shifts_window() -> None:
    """
    function makes it possible to work in the window with shifts.
    User can remove and add them
    :return: None
    """
    global shifts_dictionary
    shifts_window = ShiftWindow()
    # layout
    for hour, shift_list in shifts_dictionary.items():
        for item in shift_list:
            shifts_window.shifts_listbox.insert(END, f'{item}-Старт в {hour}')

    shifts_window.mainloop()


def edit_employees_window() -> None:
    """
    function makes it possible to work in the window with employees.
    User can remove and add them
    :return: None
    """
    global emps_dictionary

    # define layout
    employees_window = EmployeeWindow()

    # layout
    for employee, hour in emps_dictionary.items():
        employees_window.employees_listbox.insert(END, f'{employee}-Работает с {hour[0]} по {hour[-1]}')

    employees_window.mainloop()


def delete(listbox: ['Listbox'], window_belongs: str) -> None:
    """
    Func receives a structure of listbox instance and removes item from it
    :return: None
    """
    if window_belongs == 'employees':
        global emps_dictionary
        key = listbox.get(ANCHOR).split('-')[0]
        listbox.delete(ANCHOR)
        emps_dictionary.pop(key)
        mute_employees()
        return
    else:
        global shifts_dictionary
        name_half = listbox.get(ANCHOR).split('-')[0]
        time_half = listbox.get(ANCHOR).split('-')[1]
        key = int(time_half.split()[2])
        listbox.delete(ANCHOR)

        if len(shifts_dictionary[key]) > 1:
            shifts_dictionary[key].remove(name_half)
        else:
            shifts_dictionary.pop(key)

        print(shifts_dictionary)
        mute_shifts()
        return


def add(listbox: ['Listbox'], window_belongs: str, edit: bool = False) -> None:
    """
    Func receives a structure of listbox instance and adds item to it
    :param listbox: Listbox instance
    :param window_belongs: a string definer which window to operate with
    :param edit: an optional bool that, if True, edits info instead of adding it
    :return: None
    """
    window = FlexibleAddWindow(listbox=listbox,
                               window_belongs=window_belongs, edit=edit)
    window.mainloop()


def save_employees(
    widgets:
    Tuple['customtkinter.CTkToplevel()',
          'customtkinter.CTkEntry',
          'customtkinter.CTkOptionMenu',
          'customtkinter.CTkOptionMenu',
          'Listbox'
          ],
    edit:
    bool = False
) -> None:
    """
    This function takes info from the widgets, checks input and then rewrites 
    the file employees
    :param widgets: a list of CTk instances(widgets)
    :param edit: a bool that defines if we edit file
    muting itself
    :return: None
    """
    global emps_dictionary
    window = widgets[0]
    old_name = window.old_name
    target_index = None
    entered_name, entered_start, entered_end = widgets[1:4]
    listbox = widgets[4]
    name = entered_name.get().title()
    start = int(entered_start.get())
    end = int(entered_end.get())
    if not edit and name in emps_dictionary:
        messagebox.showwarning(title='Предупреждение', message='Такой сотрудник уже есть!')
        return
    if not name.isalpha():
        messagebox.showwarning(title='Предупреждение', message='Недопустимый ввод!')
        return
    if abs(start - end) < 6:
        messagebox.showwarning(title='Предупреждение', message='Человек должен работать минимум 6 часов!')
        return

    if edit:
        copy_dict = {}
        for index, (key, value) in enumerate(emps_dictionary.items()):
            copy_dict[key] = value
            if key == old_name:
                target_index = index
                copy_dict.update({name: [start, end]})
                copy_dict.pop(key)

        emps_dictionary = copy_dict
        mute_employees()
        listbox.delete(target_index, target_index)
        listbox.insert(target_index, f'{name}-Работает с {start} по {end}')
        window.destroy()
        return

    emps_dictionary[name] = [start, end]
    mute_employees()
    listbox.insert(END, f'{name}-Работает с {start} по {end}')
    window.destroy()
    return


def save_shifts(
    widgets:
    Tuple['customtkinter.CTkToplevel()',
          'customtkinter.CTkEntry',
          'customtkinter.CTkOptionMenu',
          'Listbox'
          ],
    edit:
    bool = False
) -> None:
    """
    This function takes info from the widgets, checks input and then rewrites 
    the file shifts
    :param widgets: a list of CTk instances(widgets)
    :param edit: a bool that defines if we edit file
    muting itself
    :return: None
    """
    global shifts_dictionary
    window = widgets[0]
    old_name = window.old_name
    target_index = 0

    entered_name, entered_start = widgets[1:3]
    listbox = widgets[3]

    name = entered_name.get()
    start = int(entered_start.get())
    if len(name.split()) != 2:
        messagebox.showwarning(title='Предупреждение',
                               message='Недопустимый ввод! Пример: Утро 5')
        return

    if not name.split()[0].isalpha():
        messagebox.showwarning(title='Предупреждение',
                               message='Название смены должно состоять только из букв!!')
        return

    if not edit:
        for val in shifts_dictionary.values():
            if name in val:
                messagebox.showwarning(title='Предупреждение',
                                       message='Такая смена уже есть!')
                return
    else:
        copy_dict = database.CustomListDict()
        index = 0
        for key, value in shifts_dictionary.items():
            for shift in value:
                copy_dict[key] = copy_dict.get(key)
                copy_dict[key].append(shift)
                if shift == old_name:
                    target_index = index
                    copy_dict[start] = copy_dict.get(start)
                    copy_dict[start].append(name)

                    if len(copy_dict[key]) > 1:
                        copy_dict[key].remove(shift)
                    else:
                        copy_dict.pop(key)
                index += 1

        shifts_dictionary = copy_dict
        mute_shifts()
        listbox.delete(target_index, target_index)
        listbox.insert(target_index, f'{name}-Старт в {start}')
        window.destroy()
        return

    shifts_dictionary[start] = shifts_dictionary.get(start)
    shifts_dictionary[start].append(name)
    print(shifts_dictionary)
    mute_shifts()
    listbox.insert(END, f'{name}-Старт в {start}')
    window.destroy()
    return


def mute_employees() -> None:
    """
    func-writer. I have this code repeat several times so that
    I decided to build it here
    :return: None
    """
    global emps_dictionary
    with open('emps.txt', 'w', encoding='utf-8') as file_write:
        for key, value in emps_dictionary.items():
            file_write.write(f'{key}-{value[0]} {value[1]}\n')


def mute_shifts() -> None:
    """
    func-writer. I have this code repeat several times so that
    I decided to build it here
    :return: None
    """
    global shifts_dictionary
    with open('shifts.txt', 'w', encoding='utf-8') as file_write:
        for key, value in shifts_dictionary.items():
            for shift in value:
                file_write.write(f'{shift}-{key}\n')


def open_explorer_logs() -> None:
    """
    Function allows user to access hist folder with explorer just from the GUI
    :return: None
    """
    startfile(path.abspath('history'))


def open_explorer_schedules() -> None:
    """
    Function allows user to access schedule folder with explorer just from the GUI
    :return: None
    """
    startfile(path.abspath('gens'))


def ensure_save() -> None:
    """
    are you sure to save?
    """
    context_window = EnsureSaveWindow()
    context_window.mainloop()


def save_weekends(context_window) -> None:
    """
    weekends saver
    """
    global weekends_values
    print(weekends_values)
    with open(path.join(path.abspath('holidays'), file_name), 'w', encoding='utf-8') as file_weekends:
        for key, value in weekends_values.items():
            file_weekends.write(f'{key}:{value.get()}\n')
    context_window.destroy()


def mute_weekends(key: str) -> None:
    """
    Mutes a global variable dict weekends_values by key
    :return: None
    """
    global weekends_values
    if weekends_values[key].get() == 'off':
        weekends_values[key].select()
    if weekends_values[key].get() == 'on':
        weekends_values[key].deselect()


def handle_weekends() -> None:
    """
    function calls a window where there is a grid graph, where he puts ticks
    and saves the changes
    :return: None
    """
    weekends_window = WeekendsWindow()
    weekends_window.mainloop()


def on_closing(window: 'customtkinter.CTk') -> None:
    """
    Makes sure if user wants to close program. Is called on program closing
    :param window: a customtkinter.CTk instance (window)
    :return: None
    """
    if messagebox.askokcancel(
            title="Подтверждение выхода",
            message="Вы уверены, что хотите выйти?"
            ):
        window.destroy()


# initialize color theme
customtkinter.set_appearance_mode('dark')
customtkinter.set_default_color_theme('dark-blue')

# authorization window
auth = AuthorizationWindow()
auth.protocol("WM_DELETE_WINDOW", lambda: on_closing(auth))
auth.mainloop()
# launch app
if AUTHORIZED:
    app = App()
    app.protocol("WM_DELETE_WINDOW", lambda: on_closing(app))
    app.mainloop()
