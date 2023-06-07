from tkinter import *
import shift_gen
from os import path, startfile, listdir
import customtkinter
from PIL import Image, ImageTk
import database
from typing import Dict, Any, Tuple, AnyStr, List
import tkinter as tk
from tkinter import messagebox, filedialog
from time import sleep
from passwords import users
from copy import deepcopy
import importlib

WEEK = database.date_init()
DAYS_EDGE = (WEEK[0][0], WEEK[0][6])
MONTHS_EDGE = (WEEK[1][0], WEEK[1][6])

# init weekends from file
file_name = f'holidays-{DAYS_EDGE[0]}.{MONTHS_EDGE[0]}-' \
                f'{DAYS_EDGE[1]}.{MONTHS_EDGE[1]}.log'
dir_name = 'holidays'
database.restore_files(file_name=file_name, dir_name=dir_name)

# create a dir (if not exists) for compiled shifts templates
database.if_exists('templates')
database.if_exists('generation_configs')

# globals
weekends_values: Dict[str, Any] = {}
emps_dictionary: Dict[AnyStr, List] = database.database_init()[0]
shifts_dictionary: database.CustomListDict[int, List] = database.database_init()[1]
shifts_operable_dictionary: database.CustomListDict[int, List] = database.database_init()[1]
compiled_shifts_dictionary: database.CustomListDict[Tuple, List] = database.CustomListDict()
on_vals: 'database.CustomListDict' = database.CustomListDict()

# a default version of configs is a dict of NoneTypes
generation_configuration: Dict[int, None or AnyStr] = {
    number: "Пусто" for number in range(1, 8)
}
config_name = 'Без конфига'
force_quit = False

VERSION: str = database.fetch_version()
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
        self.title(f'Scheduler Bot v. {VERSION}')
        self.iconbitmap(path.abspath('Sport-table-tennis.ico'))
        self.geometry("400x250")
        self.eval('tk::PlaceWindow . center')

        # define images
        self.add_generation_image = ImageTk.PhotoImage(Image.open('genbot.png').resize((30, 30), Image.LANCZOS))
        self.add_settings_image = ImageTk.PhotoImage(Image.open('settings.png').resize((30, 30), Image.LANCZOS))
        self.add_employee_image = ImageTk.PhotoImage(Image.open('employee.png').resize((30, 30), Image.LANCZOS))
        self.add_shifts_image = ImageTk.PhotoImage(Image.open('schedule_shifts.png').resize((30, 30), Image.LANCZOS))
        self.add_history_image = ImageTk.PhotoImage(Image.open('history.png').resize((30, 30), Image.LANCZOS))
        self.add_folder_image = ImageTk.PhotoImage(Image.open('folder.png').resize((30, 30), Image.LANCZOS))
        self.add_weekend_image = ImageTk.PhotoImage(Image.open('weekend.png').resize((30, 30), Image.LANCZOS))
        self.compile_image = ImageTk.PhotoImage(Image.open('compiler_manual.png').resize((30, 30), Image.LANCZOS))

        # define buttons
        self.main_frame = customtkinter.CTkFrame(master=self,
                                                 width=400,
                                                 height=150,
                                                 bg_color='#1A1A1A',
                                                 fg_color='#1A1A1A'
                                                 )
        self.btn_gen = customtkinter.CTkButton(master=self.main_frame,
                                               image=self.add_generation_image,
                                               text='Генерировать',
                                               width=190,
                                               height=40,
                                               compound='left',
                                               command=launch_pre_gen)
        self.btn_set = customtkinter.CTkButton(master=self.main_frame,
                                               image=self.add_settings_image,
                                               text='Настройки генерации',
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
                                                  text='Столы',
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

        self.btn_add_weekends = customtkinter.CTkButton(master=self,
                                                        image=self.add_weekend_image,
                                                        text=f'Проставить выходные на '
                                                             f'{DAYS_EDGE[0]}.{MONTHS_EDGE[0]} - '
                                                             f'{DAYS_EDGE[1]}.{MONTHS_EDGE[1]}',
                                                        width=390,
                                                        height=40,
                                                        compound='left',
                                                        command=handle_weekends)

        self.btn_compile_shifts = customtkinter.CTkButton(master=self,
                                                          image=self.compile_image,
                                                          text=f'Пользовательская компоновка смен',
                                                          width=390,
                                                          height=40,
                                                          compound='left',
                                                          command=compile_shifts)

        # spawn items
        self.main_frame.grid(row=0, column=0)
        self.btn_gen.grid(row=0, column=0, padx=5, pady=5)
        self.btn_set.grid(row=1, column=0, padx=5, pady=5)
        self.btn_employees.grid(row=2, column=0, padx=5, pady=5)
        self.btn_shifts.grid(row=0, column=1, padx=5, pady=5)
        self.btn_open_logs.grid(row=1, column=1, padx=5, pady=5)
        self.btn_open_gen_folder.grid(row=2, column=1, padx=5, pady=5)
        self.btn_add_weekends.grid(row=1, column=0, pady=5)
        self.btn_compile_shifts.grid(row=2, column=0, pady=5)

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
        self.title('Редактировать столы')
        self.iconbitmap(path.abspath('Sport-table-tennis.ico'))
        self.geometry("180x450")

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
        global generation_configuration
        super().__init__()
        self.title('Настройки генерации')
        self.iconbitmap(path.abspath('Sport-table-tennis.ico'))
        self.geometry("730x230")

        self.save_image = ImageTk.PhotoImage(Image.open('save.png').resize((20, 20), Image.LANCZOS))
        self.load_image = ImageTk.PhotoImage(Image.open('load.png').resize((20, 20), Image.LANCZOS))

        self.title_label = customtkinter.CTkLabel(master=self,
                                                  text='Выберите каждую настройку для дня недели')
        self.days_of_week_configs_frame = customtkinter.CTkFrame(master=self,
                                                                 bg_color='#1A1A1A',
                                                                 fg_color='#1A1A1A'
                                                         )
        self.buttons_frame = customtkinter.CTkFrame(master=self,
                                                    bg_color='#1A1A1A',
                                                    fg_color='#1A1A1A'
                                                    )
        self.btn_load = customtkinter.CTkButton(master=self.buttons_frame,
                                                text='Загрузить конфиг',
                                                width=350,
                                                height=30,
                                                image=self.load_image,
                                                command=lambda: load_configs(self))
        self.btn_save = customtkinter.CTkButton(master=self.buttons_frame,
                                                text='Сохранить конфиг',
                                                width=350,
                                                height=30,
                                                image=self.save_image,
                                                command=lambda: save_configs(
                                                    window=self,
                                                    list_of_configs=self.list_of_option_box_objects
                                                ))

        # title
        self.title_label.grid(row=0, column=0, pady=10)

        # days_of_week_definitions
        days_of_week = {
            1: 'ПН',
            2: 'ВТ',
            3: 'СР',
            4: 'ЧТ',
            5: 'ПТ',
            6: 'СБ',
            7: 'ВС'
        }

        self.days_of_week_configs_frame.grid(row=1, column=0, pady=10)
        self.buttons_frame.grid(row=2, column=0, pady=30)

        self.list_of_option_box_objects = []
        for i in range(1, 8):
            # take names of all configs and put them into the list
            self.list_of_configs = [
                   item[0:-3]
                   for item in listdir('templates')
                   if item.endswith('.py')
            ]
            if generation_configuration[i] == 'Пусто':
                self.list_of_configs.insert(0, 'Пусто')
            else:
                self.list_of_configs.remove(generation_configuration[i])
                self.list_of_configs.insert(0, generation_configuration[i])
                self.list_of_configs.append('Пусто')



            self.day_label = customtkinter.CTkLabel(master=self.days_of_week_configs_frame,
                                                    text=f'{days_of_week[i]}')
            self.day_label.grid(row=0, column=i - 1, padx=5)

            self.config_choice_menu = customtkinter.CTkOptionMenu(master=self.days_of_week_configs_frame,
                                                                  values=self.list_of_configs,
                                                                  width=93)
            self.config_choice_menu.grid(row=1, column=i - 1, padx=5)
            self.list_of_option_box_objects.append(self.config_choice_menu)

        self.btn_save.grid(row=0, column=0, padx=5)
        self.btn_load.grid(row=0, column=1, padx=5)


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
        self.wm_attributes('-transparentcolor', '#ab23ff')
        for cell in schedule.init_layout():
            if cell.protected():
                if cell.get_y() == 0:
                    label = customtkinter.CTkLabel(master=self.weekends_upper_frame,
                                                   text=cell.get_info(), width=32,
                                                   font=('Arial', 12))
                    label.grid(column=cell.get_x(), row=cell.get_y(), padx=2, pady=2)
                else:
                    label = customtkinter.CTkLabel(master=self.weekends_scrollable_frame,
                                                   text=cell.get_info())
                    label.grid(column=cell.get_x(), row=cell.get_y(), padx=2, pady=2)
            else:
                try:
                    if weekends_values[f'{cell.get_x()};{cell.get_y()}'].get() == "on":
                        check_var = customtkinter.StringVar(value="on")
                        sign_var = ''
                    else:
                        check_var = customtkinter.StringVar(value="off")
                        sign_var = f'{WEEK[0][cell.get_x() - 1]}'
                except AttributeError:
                    if weekends_values[f'{cell.get_x()};{cell.get_y()}'] == 'on':
                        check_var = customtkinter.StringVar(value="on")
                        sign_var = ''
                    else:
                        check_var = customtkinter.StringVar(value="off")
                        sign_var = f'{WEEK[0][cell.get_x() - 1]}'
                except KeyError:
                    check_var = customtkinter.StringVar(value="off")
                    sign_var = f'{WEEK[0][cell.get_x() - 1]}'

                tick = customtkinter.CTkCheckBox(master=self.weekends_scrollable_frame,
                                                 text=f'',
                                                 variable=check_var,
                                                 onvalue="on",
                                                 offvalue="off",
                                                 width=30,
                                                 command=lambda: mute_weekends(f'{cell.get_x()};{cell.get_y()}'))

                tick_signing = customtkinter.CTkLabel(master=self.weekends_scrollable_frame,
                                                      text=sign_var,
                                                      fg_color='transparent',
                                                      font=('Arial', 10),
                                                      text_color='grey',
                                                      height=15,
                                                      width=15
                                                      )

                if cell.get_x() == 1 and cell.get_y() == len(schedule.emps) + 1:
                    pass
                else:
                    tick.grid(column=cell.get_x(), row=cell.get_y(), padx=2, pady=2)
                    tick_signing.place(in_=tick, relx=0.4, rely=0.7)
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


class CompilerWindow(customtkinter.CTkToplevel):
    """
    This window is designed for a manual shifts compilation.
    Here, you pick different shifts, get their description and,
    by clicking on them, you will have the chosen shift in the CTkLabel below
    """
    def __init__(self):
        super().__init__()
        self.title('Компоновка смен')
        self.iconbitmap(path.abspath('Sport-table-tennis.ico'))
        self.geometry("1140x400")

        # mark out layout
        self.suck_image = ImageTk.PhotoImage(Image.open('right_arrow.png').resize((20, 20), Image.LANCZOS))
        self.push_image = ImageTk.PhotoImage(Image.open('right_arrow_double.png').resize((20, 20), Image.LANCZOS))
        self.pull_image = ImageTk.PhotoImage(Image.open('minus.png').resize((20, 20), Image.LANCZOS))
        self.clear_image = ImageTk.PhotoImage(Image.open('erase.png').resize((20, 20), Image.LANCZOS))
        self.info_image = ImageTk.PhotoImage(Image.open('information.png').resize((20, 20), Image.LANCZOS))
        self.check_image = ImageTk.PhotoImage(Image.open('check.png').resize((20, 20), Image.LANCZOS))
        self.recovery_image = ImageTk.PhotoImage(Image.open('recover.png').resize((20, 20), Image.LANCZOS))
        self.save_image = ImageTk.PhotoImage(Image.open('save.png').resize((20, 20), Image.LANCZOS))
        self.load_image = ImageTk.PhotoImage(Image.open('load.png').resize((20, 20), Image.LANCZOS))

        self.left_frame = customtkinter.CTkFrame(master=self,
                                                 width=200,
                                                 height=200,
                                                 bg_color='#1A1A1A',
                                                 fg_color='#1A1A1A',
                                                 border_width=5,
                                                 border_color='#737373'
                                                 )
        self.center_frame = self.right_frame = customtkinter.CTkFrame(master=self,
                                                                      width=200,
                                                                      height=200,
                                                                      bg_color='#1A1A1A',
                                                                      fg_color='#1A1A1A',
                                                                      border_width=5,
                                                                      border_color='#737373'
                                                                      )
        self.right_frame = customtkinter.CTkFrame(master=self,
                                                  width=200,
                                                  height=200,
                                                  bg_color='#1A1A1A',
                                                  fg_color='#1A1A1A',
                                                  border_width=5,
                                                  border_color='#737373'
                                                  )

        self.center_upper_frame = customtkinter.CTkFrame(master=self.center_frame,
                                                         width=200,
                                                         height=200,
                                                         bg_color='#1A1A1A',
                                                         fg_color='#1A1A1A'
                                                         )

        self.center_middle_frame = customtkinter.CTkFrame(master=self.center_frame,
                                                          width=200,
                                                          height=200,
                                                          bg_color='#1A1A1A',
                                                          fg_color='#1A1A1A',
                                                          )
        self.center_lower_frame = customtkinter.CTkFrame(master=self.center_frame,
                                                         width=200,
                                                         height=200,
                                                         bg_color='#1A1A1A',
                                                         fg_color='#1A1A1A',
                                                         )

        self.left_frame_title = customtkinter.CTkLabel(master=self.left_frame, text='Доступные смены')
        self.center_frame_title = customtkinter.CTkLabel(master=self.center_frame, text='Предварительно')
        self.right_frame_title = customtkinter.CTkLabel(master=self.right_frame, text='Скомпилированные смены')

        self.preview_entry = customtkinter.CTkEntry(master=self.center_middle_frame,
                                                    width=238,
                                                    height=30,
                                                    font=("Arial", 12),
                                                    bg_color='#1A1A1A',
                                                    fg_color='#1A1A1A',
                                                    )

        self.btn_add_shift = customtkinter.CTkButton(master=self.center_middle_frame,
                                                     text='',
                                                     fg_color='#a6a6a6',
                                                     width=20,
                                                     height=30,
                                                     state='disabled',
                                                     image=self.suck_image,
                                                     command=lambda: expose(self.shifts_listbox,
                                                                            self.preview_entry,
                                                                            self))
        self.btn_remove_shift = customtkinter.CTkButton(master=self.center_middle_frame,
                                                        text='',
                                                        width=20,
                                                        height=30,
                                                        image=self.clear_image,
                                                        command=lambda: clear_entry(self.preview_entry, self))
        self.btn_load = customtkinter.CTkButton(master=self.center_lower_frame,
                                                text='Загрузить шаблон',
                                                width=350,
                                                height=30,
                                                image=self.load_image,
                                                command=lambda: load_compiled_templates(self))
        self.btn_reset_to_defaults = customtkinter.CTkButton(master=self.center_lower_frame,
                                                             text='Восстановить значения',
                                                             width=350,
                                                             height=30,
                                                             image=self.recovery_image,
                                                             command=lambda: reset_to_default(self))
        self.btn_save = customtkinter.CTkButton(master=self.center_lower_frame,
                                                text='Сохранить шаблон',
                                                width=350,
                                                height=30,
                                                image=self.save_image,
                                                command=lambda: save_compiled_templates(self))
        self.btn_push = customtkinter.CTkButton(master=self.center_middle_frame,
                                                text='',
                                                width=20,
                                                height=30,
                                                fg_color='#a6a6a6',
                                                state='disabled',
                                                image=self.push_image,
                                                command=lambda: add_to_compiled(
                                                    default_shifts_listbox=self.shifts_listbox,
                                                    compiled_shifts_listbox=self.compiled_shifts_listbox,
                                                    current_window=self
                                                ))
        self.btn_pull = customtkinter.CTkButton(master=self.center_middle_frame,
                                                text='',
                                                width=20,
                                                height=30,
                                                image=self.pull_image,
                                                state='disabled',
                                                fg_color='#a6a6a6',
                                                command=lambda: decompose(
                                                    window=self,
                                                )
                                                )
        self.pull_btn_title = customtkinter.CTkLabel(master=self.center_middle_frame,
                                                     text='Удалить компилированную смену >>>')
        self.btn_shift_info = customtkinter.CTkButton(master=self.center_upper_frame,
                                                      text='Информация о текущей смене',
                                                      width=350,
                                                      height=30,
                                                      image=self.info_image,
                                                      command=lambda: describe_current_choice(window=self))
        self.btn_check_shift = customtkinter.CTkButton(master=self.center_upper_frame,
                                                       text='Автоматическая проверка смены на пригодность',
                                                       width=350,
                                                       height=30,
                                                       image=self.check_image,
                                                       command=lambda: auto_check_by_bot(window=self))

        self.shifts_listbox = tk.Listbox(master=self.left_frame,
                                         highlightcolor='black',
                                         bg='#1A1A1A',
                                         foreground='grey',
                                         width=50,
                                         height=21,
                                         highlightbackground='black',
                                         highlightthickness=0)
        self.shifts_listbox.bind('<<ListboxSelect>>', func=self.change_color_of_add_button)

        self.compiled_shifts_listbox = tk.Listbox(master=self.right_frame,
                                                  highlightcolor='black',
                                                  bg='#1A1A1A',
                                                  foreground='grey',
                                                  width=50,
                                                  height=21,
                                                  highlightbackground='black',
                                                  highlightthickness=0)

        self.compiled_shifts_listbox.bind('<<ListboxSelect>>', func=self.change_color_of_pull_button)

        # grid

        # left frame
        self.left_frame.grid(row=0, column=0, pady=10, padx=10)
        self.left_frame_title.grid(row=0, column=0, pady=5)
        self.shifts_listbox.grid(row=1, column=0, pady=5)
        # center frame
        self.center_frame.grid(row=0, column=1, pady=10, padx=10)
        self.center_frame_title.grid(row=0, column=0, pady=5)
        # center upper
        self.center_upper_frame.grid(row=1, column=0, pady=5)
        self.btn_check_shift.grid(row=0, column=0, pady=5)
        self.btn_shift_info.grid(row=1, column=0, pady=5)
        # center middle
        self.center_middle_frame.grid(row=2, column=0, pady=5)
        self.btn_add_shift.grid(row=0, column=0, pady=10, padx=10)
        self.preview_entry.grid(row=0, column=1, pady=10, padx=10)
        self.btn_push.grid(row=0, column=2, pady=10, padx=10)
        self.btn_pull.grid(row=1, column=2, pady=10, padx=10)
        self.pull_btn_title.grid(row=1, column=1, pady=10, padx=10)
        self.btn_remove_shift.grid(row=1, column=0, pady=10, padx=10)
        # center lower
        self.center_lower_frame.grid(row=3, column=0, pady=5)
        self.btn_load.grid(row=0, column=0, pady=5)
        self.btn_save.grid(row=1, column=0, pady=5)
        self.btn_reset_to_defaults.grid(row=2, column=0, pady=5)

        # right frame
        self.right_frame.grid(row=0, column=2, pady=10, padx=10)
        self.right_frame_title.grid(row=0, column=0, pady=5)
        self.compiled_shifts_listbox.grid(row=1, column=0, pady=5)

    def refresh(self) -> None:
        self.destroy()
        self.__init__()
        self.mainloop()

    def change_color_of_add_button(self, *args) -> None:
        if self.shifts_listbox.get(ANCHOR):
            self.btn_add_shift.configure(state='enabled', fg_color='green')
        else:
            self.btn_add_shift.configure(state='disabled', fg_color='#a6a6a6')

    def change_color_of_push_button(self, *args) -> None:
        if self.preview_entry.get():
            self.btn_push.configure(state='enabled', fg_color='green')
        else:
            self.btn_push.configure(state='disabled', fg_color='#a6a6a6')

    def change_color_of_pull_button(self, *args) -> None:
        if self.compiled_shifts_listbox.get(ANCHOR):
            self.btn_pull.configure(state='enabled', fg_color='red')
        else:
            self.btn_pull.configure(state='disabled', fg_color='#a6a6a6')


class PreGenWindow(customtkinter.CTkToplevel):
    """
    A window that launches on press generate button
    """
    def __init__(self) -> None:
        super().__init__()
        self.configs = [
            config[0:-3] for config in listdir('generation_configs')
            if config.endswith('.py')
        ]

        self.title_frame = customtkinter.CTkFrame(
            master=self,
            width=200,
            height=40,
            bg_color='#1A1A1A',
            fg_color='#1A1A1A'
        )
        self.btn_frame = customtkinter.CTkFrame(
            master=self,
            width=200,
            height=40,
            bg_color='#1A1A1A',
            fg_color='#1A1A1A'
        )
        self.title_lbl = customtkinter.CTkLabel(
            master=self.title_frame,
            text='Выберите конфиг:'
        )
        self.choice_option_menu = customtkinter.CTkOptionMenu(
            master=self.title_frame,
            values=['Без конфига'] + self.configs
        )
        self.continue_btn = customtkinter.CTkButton(
            master=self.btn_frame,
            text='Подтвердить',
            command=lambda: generate_full(window=self)
        )
        self.quit_btn = customtkinter.CTkButton(
            master=self.btn_frame,
            text='Выйти',
            command=self.destroy
        )

        self.title_frame.pack(pady=10)
        self.btn_frame.pack(pady=10)
        self.title_lbl.pack(pady=5)
        self.choice_option_menu.pack(pady=5)
        self.continue_btn.grid(column=0, row=0, padx=10, pady=10)
        self.quit_btn.grid(column=1, row=0, padx=10, pady=10)


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


def generate_full(window: ['customtkinter.CTkToplevel']) -> None:
    """
    generates a full schedule for a week
    :return: None
    """
    global app
    global generation_configuration
    global config_name
    global force_quit

    force_quit = False
    config_name = window.choice_option_menu.get()

    if config_name == 'Без конфига':
        generation_configuration = {
            number: "Пусто" for number in range(1, 8)
    }
    else:
        module = importlib.import_module(name=f'generation_configs.{config_name}')
        generation_configuration = module.unpack()

    schedule = shift_gen.Schedule()
    for day in range(1, 8):
        schedule.generate_day(weekday=day,
                              config=generation_configuration[day])

    messagebox.showinfo(title='Информация', message='Успешно сгенерировано!')
    app.refresh()


def launch_pre_gen() -> None:
    """
    This window pops up before generation
    """
    window = PreGenWindow()
    window.mainloop()


def on_gen_closing(window: ['customtkinter.CTkToplevel'], out: bool) -> None:
    """
    function closes the window and, depending on what button has been pressed,
    decides whether to execute further code
    """
    global force_quit

    if out:
        force_quit = True

    window.destroy()


def settings_window() -> None:
    """
    This is a settings window func
    :return:
    """
    settings = Settings()
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
        file_write.flush()


def mute_shifts() -> None:
    """
    func-writer. I have this code repeat several times so that
    I decided to build it here
    :return: None
    """
    global shifts_dictionary
    with open('default_shifts.txt', 'w', encoding='utf-8') as file_write:
        for key, value in shifts_dictionary.items():
            for shift in value:
                file_write.write(f'{shift}-{key}\n')
            file_write.flush()


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
    global on_vals
    if any([len(list_of_on_vals) == 0 for list_of_on_vals in on_vals.values()]):
        messagebox.showwarning(title='Предупреждение',
                               message='У кого-то нет выходных. У каждого должен быть минимум один вых'
                                       'Вы можете продолжить, проигнорировав это сообщение')
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
            file_weekends.flush()
    context_window.destroy()


def mute_weekends(key: str) -> None:
    """
    Mutes a global variable dict weekends_values by key
    :return: None
    """
    global weekends_values
    global on_vals
    global emps_dictionary

    # takes out a warning window that warns that you cannot put more than
    # 2 weekends
    on_vals = database.CustomListDict()
    for coord, value in weekends_values.items():
        if int(coord.split(';')[1]) != len(emps_dictionary) + 1:
            on_vals[coord.split(';')[1]] = on_vals.get(coord.split(';')[1])
            if value.get() == 'on':
                on_vals[coord.split(';')[1]].append(value.get())
        print(on_vals)
        if any([len(list_of_on_vals) >= 3 for list_of_on_vals in on_vals.values()]):
            weekends_values[key].deselect()
            messagebox.showwarning(title='Предупреждение',
                                   message='Нельзя ставить больше 2-х выходных. '
                                           'Вы можете продолжить, проигнорировав это сообщение')
            return

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


def compile_shifts() -> None:
    """
    This function opens the window so user can compile shifts
    """
    global shifts_operable_dictionary
    global compiled_shifts_dictionary

    window = CompilerWindow()
    for hour, shift_list in shifts_operable_dictionary.items():
        for item in shift_list:
            window.shifts_listbox.insert(END, f'{item}-Старт в {hour}')
    for hour, shift_list in compiled_shifts_dictionary.items():
        for item in shift_list:
            window.compiled_shifts_listbox.insert(END, f'{item}-Старт в {hour}')
    window.mainloop()


def reset_to_default(window: ['customtkinter.CTkToplevel']) -> None:
    """
    This function takes a dictionary of default shifts and assigns it to the
    compiled_shifts dictionary
    """
    global shifts_dictionary
    global compiled_shifts_dictionary
    global shifts_operable_dictionary

    if messagebox.askokcancel(
            title="Восстановление по умолчанию",
            message="Вы уверены, что хотите вернуть смены по умолчанию?"
            ):
        shifts_operable_dictionary = deepcopy(shifts_dictionary)
        compiled_shifts_dictionary = database.CustomListDict()
        window.destroy()
        compile_shifts()

        return

    return


def expose(listbox: ['tk.Listbox'],
           entry: ['customtkinter.CTkEntry'],
           window: ['customtkinter.CTkToplevel']) -> None:
    """
    This function is designed for shifts compilation window. User's choice in
    listbox is becoming a Shift class and its name is inserted into entry. This
    is solely for preliminary addition, not for saving.
    """
    user_choice = listbox.get(ANCHOR)
    stripped_table = user_choice.split('-')[0] + '(' + (user_choice.split('-')[1]).split()[2] + ')'

    if entry.get():

        if entry.get().__contains__(stripped_table):
            messagebox.showwarning(title='Предупреждение',
                                   message=f'Стол "{stripped_table}" уже есть в выборке!')
            return
        if len(entry.get().split('/')) == 4:
            messagebox.showwarning(title='Где то плачет один бук',
                                   message=f'Нельзя ставить больше 4-х столов!')
            return

        entry.insert(END, f'/{stripped_table}')
        window.change_color_of_push_button()
        return
    entry.insert(END, stripped_table)


def decompose(window: ['customtkinter.CTkToplevel']) -> None:
    """
    This function does vice versa from the compiled shifts listbox:
    1. It takes the shift;
    2. It pops it from the listbox
    3. It adds the values back to the shifts listbox (left one)
    """
    global shifts_operable_dictionary  # left
    global compiled_shifts_dictionary  # right
    global shifts_dictionary  # FOR READ ONLY

    # delete from the compiled
    shift_str_to_delete = window.compiled_shifts_listbox.get(ANCHOR)
    tuple_of_items_listbox = window.compiled_shifts_listbox.get(0, END)
    window.compiled_shifts_listbox.delete(tuple_of_items_listbox.index(shift_str_to_delete))

    compiled_shifts_dictionary_copy = deepcopy(compiled_shifts_dictionary)
    for hour, list_of_shifts in compiled_shifts_dictionary_copy.items():
        for shift in list_of_shifts:
            if shift == shift_str_to_delete.split('-')[0]:
                compiled_shifts_dictionary[hour].remove(shift)
                if not compiled_shifts_dictionary[hour]:
                    compiled_shifts_dictionary.pop(hour)
                break
    # add back to the default
    list_of_names_str = (shift_str_to_delete.split('-')[0]).split('/')

    for hour, shifts_list in shifts_dictionary.items():
        for shift in shifts_list:
            if shift in list_of_names_str:
                shifts_operable_dictionary[hour] = shifts_operable_dictionary.get(hour)
                shifts_operable_dictionary[hour].append(shift)

    window.destroy()
    compile_shifts()


def from_entry(entry: ['customtkinter.CTkEntry']) -> ['shift_gen.Shift'] or None:
    """
    gets class instance from entry
    """
    text = entry.get()
    tables = []
    if text:
        for table in text.split('/'):
            table_name = table[0:table.index('(')]
            table_hour = int(table[table.index('(') + 1:len(table) - 1])
            tables.append(shift_gen.Shift(table_hour, table_name))

        init_instance = None
        for table in tables:
            if init_instance is None:
                init_instance = table
            else:
                init_instance += table

        return init_instance

    return None


def describe_current_choice(window: ['customtkinter.CTkToplevel']) -> None:
    """
    This function accepts the current entry, formulates a class out of tables
    and then calls a window where it passes its __str__ method
    """
    shift = from_entry(window.preview_entry)
    if shift is not None:
        messagebox.showinfo(title='Информация о смене',
                            message=shift.describe())
    else:
        messagebox.showinfo(title='Информация о смене',
                            message='Поле пустое!')


def clear_entry(entry: ['customtkinter.CTkEntry'],
                window: ['customtkinter.CTkToplevel']) -> None:
    """
    Function which just clears the field
    """
    entry.delete(0, END)
    window.change_color_of_push_button()


def auto_check_by_bot(window: ['customtkinter.CTkToplevel']) -> None:
    """
    This is an auto checker of shifts
    """
    shift = from_entry(window.preview_entry)

    if shift:
        if shift_gen.tables_suitable(shift):
            messagebox.showinfo(title='Проверка смены',
                                message='Я бы тоже такое поставил')

        else:
            messagebox.showinfo(title='Проверка смены',
                                message='Есть некоторые проблемы (см. Информацию о смене).'
                                        'Я бы такое не ставил. '
                                        'Но Вы можете проигнорировать это сообщение')
    else:
        messagebox.showinfo(title='Проверка смены',
                            message='Это сообщение выводится, значит что то не так\n\n\n\n'
                                    '(Это значит, ты хочешь проверить на правильность пустое поле, ай-яй-яй)')


def add_to_compiled(default_shifts_listbox: ['tk.Listbox'],
                    compiled_shifts_listbox: ['tk.Listbox'],
                    current_window: ['customtkinter.CTkToplevel']) -> None:
    """
    This function accepts arguments from window, mutes list boxes and
    global dictionaries
    Attributes:
        default_shifts_listbox: left list box (the one with default shifts)
        compiled_shifts_listbox: right list box (the one with those user compiled)
        current_window: a window itself
    """
    global shifts_operable_dictionary  # left
    global compiled_shifts_dictionary  # right
    current_shift = from_entry(current_window.preview_entry)

    if current_shift is None:
        messagebox.showwarning(title='Предупреждение',
                               message=f'Сюда нечего добавлять. Поле пустое')
        return
    if current_shift.get_inst() == 1:
        messagebox.showwarning(title='Предупреждение',
                               message=f'Одинарные смены не являются компонованными')
        return

    # compiled
    compiled_key = (current_shift.get_begin(), current_shift.get_end())
    compiled_value = current_shift.__str__()
    compiled_shifts_listbox.insert(END, f'{compiled_value}-С {compiled_key[0]} по {compiled_key[1]}')
    compiled_shifts_dictionary[compiled_key] = compiled_shifts_dictionary.get(compiled_key)
    compiled_shifts_dictionary[compiled_key].append(compiled_value)

    # operable
    # delete all occurrences
    shifts_operable_dictionary_copy = deepcopy(shifts_operable_dictionary)
    for hour, list_of_shifts in shifts_operable_dictionary_copy.items():
        for shift in list_of_shifts:
            if shift in compiled_value.split('/'):
                tuple_of_items_listbox = default_shifts_listbox.get(0, END)
                default_shifts_listbox.delete(tuple_of_items_listbox.index(f'{shift}-Старт в {hour}'))
                shifts_operable_dictionary[hour].remove(shift)
                if len(shifts_operable_dictionary[hour]) == 0:
                    shifts_operable_dictionary.pop(hour)

    clear_entry(current_window.preview_entry, current_window)
    current_window.change_color_of_push_button()


def save_compiled_templates(window: ['customtkinter.CTkToplevel']) -> None:
    """
    This function spawns templates of the compilations.
    It should open the window of how to call the file.
    """
    global shifts_operable_dictionary
    global compiled_shifts_dictionary
    file_to_save = custom_asksaveasfile(parent=window,
                                        initialdir=path.abspath('templates'),
                                        defaultextension='.py')

    if file_to_save is None:
        return

    file_to_save.write(f'def unpack():\n'
                       f'    operable = {shifts_operable_dictionary}\n'
                       f'    compiled = {compiled_shifts_dictionary}\n'
                       f'    return operable, compiled\n')
    file_to_save.flush()
    file_to_save.close()

    window.destroy()
    compile_shifts()


def load_compiled_templates(window: ['customtkinter.CTkToplevel']) -> None:
    """
    This function loads a template of the compilations as said by user.
    It should open the window of what file to load.
    """
    global shifts_operable_dictionary
    global compiled_shifts_dictionary
    file_to_open = custom_askopenfile(parent=window,
                                      initialdir=path.abspath('templates'),
                                      defaultextension='.py')

    if file_to_open is None:
        return

    filename = file_to_open.name.split('/')[-1][0:-3]
    file_to_open.close()

    module = importlib.import_module(name=f'templates.{filename}')
    shifts_operable_dictionary, compiled_shifts_dictionary = module.unpack()
    shifts_operable_dictionary = database.CustomListDict(shifts_operable_dictionary)
    compiled_shifts_dictionary = database.CustomListDict(compiled_shifts_dictionary)

    window.destroy()
    compile_shifts()


def custom_asksaveasfile(mode="w", **options):
    """
    Ask for a filename to save as, and returned the opened file.
    Taken from tkinter and changed encoding
    """

    filename = filedialog.SaveAs(**options).show()
    if filename:
        return open(filename, mode, encoding='utf-8')
    return None


def custom_askopenfile(mode="r", **options):
    """
    Ask for a filename to open, and returned the opened file
    """
    filename = filedialog.Open(**options).show()
    if filename:
        return open(filename, mode, encoding='utf-8')
    return None


def load_configs(window: ['customtkinter.CTkToplevel']) -> None:
    """
    This function loads configs from py file (dict) and mutes the
    generation_configuration
    """
    global generation_configuration
    global config_name
    file_to_open = custom_askopenfile(parent=window,
                                      initialdir=path.abspath('generation_configs'),
                                      defaultextension='.py')

    if file_to_open is None:
        return

    filename = file_to_open.name.split('/')[-1][0:-3]
    config_name = filename
    file_to_open.close()

    module = importlib.import_module(name=f'generation_configs.{filename}')
    generation_configuration = module.unpack()

    window.destroy()
    settings_window()


def save_configs(window: ['customtkinter.CTkToplevel'], list_of_configs: List['customtkinter.CTkOptionMenu']) -> None:
    """
    This function saves configs to py file (dict) using the
    generation_configuration dict
    """
    global generation_configuration
    global config_name

    for index, config in enumerate(list_of_configs):
        generation_configuration[index + 1] = config.get()

    file_to_save = custom_asksaveasfile(parent=window,
                                        initialdir=path.abspath('generation_configs'),
                                        defaultextension='.py')
    if file_to_save is None:
        return

    file_to_save.write(f'def unpack():\n'
                       f'    config = {generation_configuration}\n'
                       f'    return config\n')
    file_to_save.flush()
    config_name = file_to_save.name.split('/')[-1][0:-3]
    file_to_save.close()

    window.destroy()
    settings_window()


def on_closing(window: 'customtkinter.CTk') -> None:
    """
    Makes sure if user wants to close program. Is called on program closing
    :param window: a customtkinter.CTk instance (window)
    :return: None
    """
    if messagebox.askokcancel(
            title="Подтверждение выхода",
            message="Вы уверены, что хотите выйти?",
            parent=window
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
