import database
from random import shuffle, choice
import openpyxl
from datetime import datetime
from os import path, mkdir
from openpyxl.styles import Font, Alignment
from typing import List, Any, AnyStr, Tuple, NoReturn, Dict
from statistics import mean
import importlib
from copy import deepcopy


class Schedule:
    """
    This class is a schedule object that is a table-like data structure.

    Main class Schedule in the program creates instances of all other classes.
    However, it is not a superclass of any class.

    Below it will be explained how it works, but for now it is crucial to
    say that this class' first goal is to store, change, or delete,
    the information regarding its cells. It also works closely with openpyxl
    third-party lib and stores an Excel table object, to which it saves the
    comprehensive information it knows about its cells.

    Attributes:
        Although the schedule initiates with taking no arguments,
        it has a lot of attributes that vary depending on what is written
        in the files the Schedule commands to read. Visit database.py to see
        the funcs it calls.

        COLS: [int] COLS is a constant for this class only. It defines that the graph
        will always have 7 + 1 colons (1 colon reserved for naming rows and 7
        colons for each of the weekdays)

        WEEK: [tuple] WEEK attribute is a tuple of 2 lists that the Schedule commands
        database.date_init function object to fetch. WEEK is a constant for
        Schedule, first list in the tuple meaning 7 actual dates in the week,
        and the second one meaning 7 numeric orders for each day in the week,
        Read database.date_init docstring for more info.

        excel_object: [Workbook] This is an instance of the class openpyxl.Workbook.
        Initiates empty and stores Excel representation of Schedule

        sheet: [Workbook] A result of excel_object method 'active' and this sheet is
        already ready to be written and rewritten by the Schedule

        self.__emps_all: [dict] The dict, the key means the employee's name,
        the value means the working time diapason. One of the 2 dicts that the
        function database.database_init returned. Read its docstring for more.

        self.__shifts_all: [CustomListDict] The CustomListDict object, which is a dict. It
        stores the information about all the shifts meant to be further
        assigned to employees. One of the 2 dicts that the function
        database.database_init returned. Read its docstring for more.

        self.__emps: [list] Creates using string representation of employees and int
        representation of their working hours which it takes from self.__emps_all
        dict. A list of instances of class Employee.
        Read more in Employee docstring

        self.__shifts: [list] Creates using string representation of shifts and int
        representation of time when shift starts
        self.__shifts_all dict A list of instances of class Shift.
        Read more in Shift docstring

        self.__rows: [list] Unlike COLS, this value depends on something.
        This something is how many employees there are.

        self.__grid: [list] Is actually the list-like representation
        of graph's grid

    Methods (not including those of "__method__" format (magic)):
        __init_layout (private method), generate_day (public method).

    """
    COLS = 7
    WEEK: Tuple[List[int]] = database.date_init()

    excel_object: 'openpyxl.Workbook' = openpyxl.Workbook()
    sheet = excel_object.active

    def __init__(self) -> None:
        """
        All attributes the constructor creates are in the class description
        """
        self.__emps_all, self.__shifts_all = database.database_init()

        self.emps: List['Employee'] = [Employee(surname, occupation, index)
                                       for index, (surname, occupation)
                                       in enumerate(self.__emps_all.items())]

        self.__shifts: List['Shift'] = [
            Shift(hour, name)
            for hour, roster in self.__shifts_all.items() for name in roster
        ]

        self.rows: int = len(self.emps)
        self.__grid: List['Cell'] = [
            Cell(col, row) for col in range(self.COLS + 1)
            for row in range(self.rows + 1)
        ]
        self.init_layout()

    def __str__(self) -> str:
        """
        A method the schedule uses to show itself in a console
        :return: its name (str)
        """
        string = ''
        for item in self.__grid:
            string += item.__str__() + '\n'
        return string

    def init_layout(self) -> List['Cell']:
        """
        This method initiates an empty graph. It fills out the employees
        vertically and dates horizontally
        :return: List of cells for further use
        """

        for cell in self.__grid:
            if cell.get_x() in range(1, 8) and cell.get_y() == 0:
                day = self.WEEK[0][cell.get_x() - 1]
                month = self.WEEK[1][cell.get_x() - 1]
                cell.rename(f'{str(day)}.'
                            f'{"0" + str(month) if month < 10 else month}')
                self.sheet[cell.holler_ident()] = cell.get_info()
                self.sheet[cell.holler_ident()].font = Font(bold=True)
                self.sheet[cell.holler_ident()].alignment = Alignment(
                    horizontal='center', vertical='center'
                )
                self.sheet.column_dimensions[cell.holler_ident()[0]].width = 30
                cell.protect_from_change()
            elif cell.get_x() == 0 and cell.get_y() in range(1, self.rows + 1):
                cell.rename(f'{self.emps[cell.get_y() - 1].__str__()}')
                self.sheet[cell.holler_ident()] = cell.get_info()
                self.sheet.column_dimensions[cell.holler_ident()[0]].width = 15
                self.sheet[cell.holler_ident()].font = Font(bold=True)
                self.sheet[cell.holler_ident()].alignment = Alignment(
                    horizontal='center', vertical='center'
                )
                cell.protect_from_change()
            elif cell.get_x() == 0 and cell.get_y() == 0:
                cell.rename(f'График {self.WEEK[0][0]}-{self.WEEK[0][6]}')
                self.sheet[cell.holler_ident()] = cell.get_info()
                self.sheet[cell.holler_ident()].font = Font(bold=True, underline='single', italic=True)
                self.sheet.column_dimensions[cell.holler_ident()[0]].width = 15
                self.sheet[cell.holler_ident()].alignment = Alignment(
                    horizontal='center', vertical='center'
                )
                cell.protect_from_change()
            else:
                pass

        return self.__grid

    def generate_day(self, weekday: int,
                     config: AnyStr) -> None:
        """
        This method generates a schedule for the given weekday.
        Below in comments each action will be described
        :param weekday: int number from 1 to 7
        :param config: None or name of the file to initialize from (str).
        This config is user config.
        If None, the usual shifts roster will be used. Otherwise,
        list of single shifts + compiled shifts will be used
        :return: None
        """

        # first, on Monday the Schedule must clear the history of its actions,
        # if they were carried out 2 months ago and earlier
        if weekday == 1:
            database.clear_history()

        # weekends!
        addresses = []
        weekends_dir = 'holidays'
        weekends_file = f'holidays-{self.WEEK[0][0]}.'\
                        f'{self.WEEK[1][0]}-'\
                        f'{self.WEEK[0][6]}.'\
                        f'{self.WEEK[1][6]}.log'
        path_weekends = path.join(path.abspath(weekends_dir), weekends_file)
        if path.exists(path_weekends):
            with open(path_weekends, 'r', encoding='utf-8') as weekends_file:
                for line in weekends_file:
                    key_str = line.rstrip().split(':')[0]
                    val_str = line.rstrip().split(':')[1]
                    if int(key_str.split(';')[0]) == weekday and val_str == 'on':
                        addresses.append(int(key_str.split(';')[1]))

        # Local variables are created. They take only those cells from
        # self.__grid that belong to the current weekday and are
        # not in reader mode
        cells: List[Cell] = [
            cell for cell in self.__grid
            if cell.get_x() == weekday
            and not cell.protected()
        ]
        prev_day_cells: List[Cell] or List[str] = [
            cell for cell in self.__grid
            if cell.get_x() == weekday - 1
            and not cell.protected()
        ]

        # If prev_day_cells is empty, it is apparently Monday and the
        # Schedule must look up the needed data in logs
        if not prev_day_cells:
            # it takes the log from Sunday of the previous week
            day_curr = self.WEEK[0][weekday - 1]
            mo_curr = self.WEEK[1][weekday - 1]
            prev_day, prev_month = database.grab_last_week_sunday(day_curr, mo_curr)

            prev_data = database.extraction_action(path.join(
                path.abspath('history'), f"activity_for_{prev_day}."
                                         f"{prev_month if prev_month > 10 else str(0) + str(prev_month)}.log"
            ))

            if prev_data:
                # if there is such log, it fills out cells using it
                prev_day_cells = [
                    Cell(weekday, row) for row in range(1, len(cells) + 1)
                ]

                for cell, (name, value) in zip(prev_day_cells, prev_data):
                    if name != 'вых':
                        for name_shift in name.split('/'):
                            for basic_shift in self.__shifts:
                                if basic_shift.__str__() == name_shift:
                                    try:
                                        new_shift = cell.get_info() + basic_shift
                                    except TypeError:
                                        cell.rename(basic_shift)
                                    else:
                                        cell.rename(new_shift)
                    else:
                        cell.rename('вых')

            else:
                # if there is no data, it adds 'none' string values
                prev_day_cells = ['none' for _ in range(len(self.emps))]

        # in this block the bot shuffles cells and adjusts other lists so that
        # they are shuffled in strict correspondence with cells' order
        shuffle(cells)
        employees = [self.emps[cell.get_y() - 1] for cell in cells]
        if prev_day_cells:
            prev_day_cells = [prev_day_cells[cell.get_y() - 1] for cell in cells]

        # initialize dicts: single and compiled shifts. Do it from config param
        try:
            config_module = importlib.import_module(name=f'templates.{config}')
        except ModuleNotFoundError:
            config_module = None

        if not config_module:
            single_shifts, compiled_shifts = (deepcopy(self.__shifts_all), database.CustomListDict())
        else:
            single_shifts, compiled_shifts = config_module.unpack()

        # convert dicts into appropriate lists of Shift instances
        single_shifts_list: List['Shift'] = [
            Shift(hour, name)
            for hour, roster in single_shifts.items() for name in roster
        ]
        compiled_shifts_list: List['Shift'] = [
            Shift(hour[0], name, hour[1])
            for hour, roster in compiled_shifts.items() for name in roster
        ]

        shuffle(single_shifts_list),
        shuffle(compiled_shifts_list)

        # this algorythm implements the generation method.
        # It would not stop unless all shifts are given away
        # (shifts list is empty).
        while single_shifts_list:
            compare_shifts = single_shifts_list[:]
            # shifts assignment process
            for cell, employee, yesterday_cell in zip(cells, employees, prev_day_cells):
                if cell.get_y() in addresses and cell.get_y() != 0:
                    if not cell.tell_readiness():
                        cell.rename('вых')
                        self.sheet[cell.holler_ident()] = cell.get_info().__str__()
                        self.sheet[cell.holler_ident()].alignment = Alignment(
                            horizontal='center', vertical='center'
                        )
                        self.sheet.column_dimensions[cell.holler_ident()[0]].width = 30
                else:
                    aligned_to_yesterday = False
                    yesterday_info_end = None

                    if compiled_shifts_list:
                        compiled_choice = choice(compiled_shifts_list)
                        if compiled_choice.get_begin() not in employee.get_working_hours():
                            continue
                        cell.rename(compiled_choice)
                        self.sheet[cell.holler_ident()] = cell.get_info().__str__()
                        self.sheet[cell.holler_ident()].alignment = Alignment(
                            horizontal='center', vertical='center'
                        )
                        self.sheet.column_dimensions[cell.holler_ident()[0]].width = 30
                        compiled_shifts_list.remove(compiled_choice)
                        continue

                    for shift in single_shifts_list:
                        if cell.get_info() in ['None', 'none'] or not cell.get_info().if_compiled():
                            try:
                                candidate = cell.get_info() + shift
                            except TypeError:
                                candidate = shift

                            try:
                                yesterday_info_end = yesterday_cell.get_info().get_end()
                            except AttributeError:
                                pass
                            else:
                                aligned_to_yesterday = True
                            if tables_suitable(candidate) \
                                    and candidate.get_begin() in employee.get_working_hours():
                                if aligned_to_yesterday and yesterday_info_end - candidate.get_begin() <= 12:
                                    cell.rename(candidate)
                                    self.sheet[cell.holler_ident()] = cell.get_info().__str__()
                                    self.sheet[cell.holler_ident()].alignment = Alignment(
                                        horizontal='center', vertical='center'
                                    )
                                    single_shifts_list.remove(shift)
                                    break
                                elif aligned_to_yesterday:
                                    continue
                                else:
                                    cell.rename(candidate)
                                    self.sheet[cell.holler_ident()] = cell.get_info().__str__()
                                    self.sheet[cell.holler_ident()].alignment = Alignment(
                                        horizontal='center', vertical='center'
                                    )
                                    single_shifts_list.remove(shift)
                                    break
            # the block below is responsible for comparing if shifts list has changed since last iteration.
            # if there is no change, the bot enters remainders into the Excel
            if compare_shifts == single_shifts_list:
                self.sheet[choice(cells).holler_ident()[0] + str(len(self.emps) + 3)] = 'остатки'
                self.sheet[choice(cells).holler_ident()[0] + str(len(self.emps) + 3)].alignment = Alignment(
                                    horizontal='center', vertical='center'
                                )
                for index, shift in enumerate(single_shifts_list):
                    self.sheet[choice(cells).holler_ident()[0] + str(len(self.emps) + index + 4)] = shift.__str__()
                    self.sheet[choice(cells).holler_ident()[0] + str(len(self.emps) + index + 4)].alignment = \
                        Alignment(
                                    horizontal='center', vertical='center'
                                )
                    single_shifts_list.remove(shift)
        # Once the generation is ended, the bot finishes job and writes a table
        if weekday == 7:
            file_name = f'schedule-{self.WEEK[0][0]}-{self.WEEK[0][6]} of {self.WEEK[1][0]} ' \
                f'generated {datetime.now().strftime("%m_%d_%Y_%H_%M_%S")}.xlsx'
            path_to_file = path.abspath('gens')
            if not path.exists(path_to_file):
                mkdir('gens')
            self.excel_object.save(
                path.join(path_to_file, file_name)
            )

        database.log(grid_list=self.__grid, weekday=weekday, remainders=single_shifts_list, employees=self.emps)


class Cell:
    """
    Class Cell is a small part of Schedule's grid that builds it up.

    The cells are put into the schedule's grid simply using list.
    But they have their own unique features that help the Schedule class
    reorder them as fast and conveniently as it can be

    Acceptable params:
        coord_x: an integer value defining its x position in a grid
        coord_y: an integer value defining its y position in a grid
        contents: Any value that this cell carries("None by default")

    Attributes:
        self.letters: Capital letters in alphabetic order for further use with Excel
        self.__occupied: a bool value which defines if this cell has been
        muted or not
        self.__reader_mode: a bool value which is set True for those cells that are not subject to change.
        These are typically ones with names, dates and so on
        self.__x_pos, self.__y_pos: The values deriving from the coord_x and coord_y params this class accepts
        self.__info: This value derives from the param contents this class accepts
        self.__id_vertical: This is id for Excel (str)
        self.__id_horizontal: This is id for Excel (str)
        self.__ident: This is a string of type "A1" for  further use with Excel

    Methods:
        rename, clean, protect_from_change, get_x, get_y, tell_readiness,
        protected, get_info, holler_ident
    """
    def __init__(self, coord_x, coord_y, contents="None") -> None:
        self.letters: List = [
            chr(index)
            for index in range(ord('A'), ord('Z') + 1)
            if chr(index).upper() == chr(index)
        ]
        self.__occupied: bool = False
        self.__reader_mode: bool = False
        self.__x_pos: int = coord_x
        self.__y_pos: int = coord_y
        self.__info: Any = contents
        self.__id_vertical: AnyStr = str(coord_y + 1)
        self.__id_horizontal: AnyStr = self.letters[coord_x]
        self.__ident: AnyStr = f'{self.__id_horizontal}{self.__id_vertical}'

    def __str__(self) -> AnyStr:
        """
        This is an introduction for each cell.
        This method describes them to the console
        """
        return f'Клетка с координатой {str(self.__x_pos)}; {str(self.__y_pos)}: ' \
               f'Занята: {"да" if self.__occupied else "нет"}. ' \
               f'Содержание: {self.__info.__str__()} ' \
               f'Права на редактирование: ' \
               f'{"запрещены" if self.__reader_mode else "разрешены"}.' \
               f' Excel ID: {self.holler_ident()}'

    def rename(self, name) -> None:
        """
        This method renames the cell with what is passed here as
        an arg and sets occupied to True
        """
        self.__info = name
        self.__occupied = True

    def clean(self) -> None:
        """
        Restore cell to default
        """
        self.__info = 'None'
        self.__occupied = False

    def protect_from_change(self) -> None:
        """
        If you want to freeze this cell, use this method
        """
        self.__reader_mode = True

    def get_x(self) -> int:
        """
        Get x pos of this cell. Yes I know I should have used property,
        but I wrote it before I knew it, and the code
        is so big that I do not want to refactor everything
        """
        return self.__x_pos

    def get_y(self) -> int:
        """
        Get y pos of this cell
        """
        return self.__y_pos

    def tell_readiness(self) -> bool:
        """
        method makes sure if this cell is ready/filled
        """
        return self.__occupied

    def protected(self) -> bool:
        """
        If this cell is frozen
        """
        return self.__reader_mode

    def get_info(self) -> Any:
        """
        This method gets any info from this cell
        """
        return self.__info

    def holler_ident(self) -> AnyStr:
        """
        Get an Excel ID (A3 for example)
        """
        return self.__ident


class Shift:
    """
    Class Shift is a class that is responsible for everything that comes to
    working patterns that are assigned to the employees in the future

    Acceptable params:
        start_time: [int] is when the shift starts
        name: [str] is what the shift's name is

    Attributes:
        self.name: is taken from name param
        self.start_time: is taken from start_time param
        self.end_time: is taken from start time + 6 (tables last 6 hours)

    Methods:
        get_begin, get_end, get_daytime, get_duration, get_city, eval_shift,
        describe, get_inst, rearrange_time
    """
    def __init__(self, start_time: int,  name: str, end_time=None) -> None:
        self.name: AnyStr = name
        self.start_time: int = start_time
        if not end_time:
            self.end_time: int = start_time + 6
            self.compiled_beforehand = False
        else:
            self.compiled_beforehand = True
            self.end_time: int = end_time

    def __str__(self) -> AnyStr:
        """
        Tell its name
        """
        return f"{self.name}"

    def __add__(self, other) -> 'TwoTableShift' or None:
        """
        This method adds two tables and returns a TwoTableShift heir
        """
        if self != other:
            start_time, end_time = self.rearrange_time(other)
            return TwoTableShift(start_time,
                                 end_time,
                                 name="/".join([self.__str__(), other.__str__()]))
        else:
            return None

    def get_begin(self) -> int:
        """
        getter to get start time
        """
        return self.start_time

    def get_end(self) -> int:
        """
        getter to get end_time
        """
        return self.end_time

    def get_daytime(self) -> AnyStr:
        """
        Depending on when this shifts starts, this method returns its daytime
        """
        if self.start_time in range(0, 6):
            return 'ночь'
        elif self.start_time in range(6, 12):
            return 'утро'
        elif self.start_time in range(12, 17):
            return 'день'
        else:
            return 'вечер'

    def get_duration(self) -> int:
        """
        This method gets the shift duration
        """
        return abs(self.get_begin() - self.get_end())

    def get_city(self) -> List:
        """
        Method takes an identifier and compiles a list of cities,
        which comprise the shift
        """
        cities = list()
        if self.name.split('/'):
            for table in self.name.split('/'):
                try:
                    ident_num = int(table.split()[1])
                except ValueError:
                    if table.split()[1][0] in ['М', 'M']:
                        cities.append('Минск')
                    elif table.split()[1][0] == 'П':
                        cities.append('Польша польская')
                    else:
                        cities.append('Другая комбинация')
                else:
                    if ident_num in {1, 2, 6, 7}:
                        cities.append('Саранск')
                    elif ident_num in {3, 4, 8, 9}:
                        cities.append('Питер')
                    elif ident_num == 5:
                        cities.append('Уссурийск')
                    elif ident_num in {10, 11}:
                        cities.append('Ростов')
                    elif ident_num in {12, 13}:
                        cities.append('Марбелья')
                    else:
                        cities.append('Польша саранская')

        return cities

    def eval_shift(self) -> float or int:
        """
        This method estimates how this shift valuable is and returns pts.
        """
        scores = []
        for city in self.get_city():
            if city == 'Саранск':
                scores.append(10)
            elif city == 'Питер':
                scores.append(8)
            elif city == 'Минск':
                scores.append(6)
            elif city == 'Ростов':
                scores.append(4)
            elif city == 'Польша польская':
                scores.append(2)
            else:
                scores.append(1)

        return mean(scores)

    def describe(self):
        return f'Название смены: "{self.__str__()}"\n'\
               f'Время старта: {self.get_begin()} часов\n'\
               f'Время финиша: {self.get_end()} часов\n'\
               f'Длительность захода: {self.get_duration()} часов\n'\
               f'Время суток начала смены: {self.get_daytime()}\n'\
               f'Города: {", ".join(self.get_city())}\n'\
               f'Рейтинг смены : {self.eval_shift()}/10'

    def get_inst(self) -> int:
        """
        Method gets an int number of how much tables there are in the shift
        """
        if len(self.name.split('/')):
            return len(self.name.split('/'))
        else:
            return 1

    def rearrange_time(self, other) -> Tuple:
        """
        This method replaces times of start and end while the tables are added
        """
        if self.get_begin() < other.get_begin():
            start_time = self.get_begin()
            end_time = other.get_end()
        elif self.get_begin() > other.get_begin():
            start_time = other.get_begin()
            end_time = self.get_end()
        else:
            start_time = self.get_begin()
            end_time = self.get_end()

        return start_time, end_time

    def if_compiled(self) -> bool:
        """
        getter to know if the shift is compiled
        """
        return self.compiled_beforehand


class TwoTableShift(Shift):
    """
    Inherits from Shift and consists of two tables. Attributes and parameters
    are the same as those in parent class
    """
    def __init__(self, start_time: int, end_time: int, name: str):
        super().__init__(start_time, name)
        self.name: AnyStr = name
        self.start_time: int = start_time
        self.end_time: int = end_time

    def __str__(self):
        return f"{self.name}"

    def __add__(self, other):
        if other.get_inst() == 1:
            start_time, end_time = self.rearrange_time(other)
            if self.get_duration() == 9:
                return ThreeTableShift(start_time,
                                       end_time,
                                       name=f'{self.name}/{other.name}',
                                       definer=True)
            else:
                return ThreeTableShift(start_time,
                                       end_time,
                                       name=f'{self.name}/{other.name}')
        else:
            start_time, end_time = self.rearrange_time(other)
            return FourTableShift(start_time,
                                  end_time,
                                  name=f'{self.name}/{other.name}')


class ThreeTableShift(TwoTableShift):
    """
    Inherits from TwoTableShift and consists of 3 tables. Attributes and parameters
    are the same as those in parent class
    """
    def __init__(self, start_time: int, end_time: int, name: str, definer=False):
        super().__init__(start_time, end_time, name)
        self.name = name
        self.start_time = start_time
        self.end_time = end_time
        self.__definer = definer

    def __str__(self):
        return f"{self.name}"


class FourTableShift(TwoTableShift):
    """
    TInherits from TwoTableShift and consists of 4 tables. Attributes and parameters
    are the same as those in parent class
    """
    def __init__(self, start_time: int, end_time: int, name: str):
        super().__init__(start_time, end_time, name)
        self.name = name
        self.start_time = start_time
        self.end_time = end_time

    def __str__(self):
        return f"{self.name}"


class Employee:
    """
    Class Employee. This is a worker, who works with shifts

    Acceptable params:
        surname: string surname of worker
        working_hrs: a list of hours when the worker is available
        worker_id: integer ID of employee

    Attributes:
        self.__working_hrs: derives from param
        self.__surname: derives from param
        self.__id: derives from param + 1

    Methods:
        describe, add_wish, get_id, get_working_hours
    """

    def __init__(self, surname: str, working_hrs: list, worker_id: int) -> None:
        self.__working_hrs: List[int] = [hour for hour in range(int(working_hrs[0]), int(working_hrs[1]) + 1)]
        self.__surname: AnyStr = surname
        self.__id: int = worker_id + 1
        self.__wish = None

    def __str__(self) -> AnyStr:
        """
        Returns surname
        """
        return f'{self.__surname}'

    def describe(self):
        """
        Full description of instance
        """
        print(f'{self.__surname} работает в {self.get_working_hours()}. '
              f'Пожелание: {"Нет" if not self.__wish else {self.__wish}}. '
              f'ID: {self.get_id()}')

    def add_wish(self, wish) -> None or NoReturn:
        if not self.__wish:
            self.__wish = wish
        else:
            raise UserWarning(f'Wish already exists. Wish: {self.__wish}')
    pass

    def get_id(self) -> int:
        """
        id getter
        """
        return self.__id

    def get_working_hours(self) -> List:
        """
        working hours getter
        """
        return self.__working_hrs


def tables_suitable(shift: 'Shift') -> bool:
    """
    This function makes sure whether the added shift suits the requirements.
    They are:
        i) no less than 12 hours of break between days
        ii) no night runs
        iii) they should be of 6 to 12 hours long
    """
    type_shift: Dict[AnyStr, bool] = {
        'Is single': True if shift.get_inst() == 1 else False,
        'Is double': True if shift.get_inst() == 2 else False,
        'Is triple': True if shift.get_inst() == 3 else False,
        'Is quadruple': True if shift.get_inst() == 4 else False,
    }
    flags_shift: Dict[AnyStr, bool] = {
        'acceptable length': True if (type_shift['Is double'] and shift.get_duration() in {6, 7, 8, 9, 12})
        or (type_shift['Is triple'] and shift.get_duration() == 12)
        or (type_shift['Is quadruple'] and shift.get_duration() == 12)
        else False,

        'No night runs': False if shift.get_duration() == 12
        and shift.get_begin() not in range(6, 15)
        else True,

    }
    if type_shift['Is single']:
        return True
    return all(flags_shift.values())


def main_gen(shifts, init=False):
    """
    generator that actually filters all bad shifts
    """
    if init:
        for shift in shifts:
            yield shift
    else:
        for shift in shifts:
            if shift and tables_suitable(shift):
                yield shift


def tables_gen(all_shifts: list, param: int) -> List:
    """
    This function gets ALL variants of shifts that can be possibly combined
    from the list of shifts it accepts
    """
    length_shifts = len(all_shifts) - 1

    if param == 1:
        return [shift for shift in main_gen(all_shifts, init=True)]

    elif param == 2:
        shifts_double = [
            all_shifts[index_1] + all_shifts[index_2]
            for index_1 in range(length_shifts)
            for index_2 in range(length_shifts)
            if index_2 >= index_1
        ]
        return [shift for shift in main_gen(shifts_double)]

    elif param == 3:
        shifts_triple = [
            (shift_1 + shift_2) + shift_3
            for index_1, shift_1 in enumerate(all_shifts)
            for index_2, shift_2 in enumerate(all_shifts)
            for index_3, shift_3 in enumerate(all_shifts)
            if index_1 <= index_2 <= index_3
            and shift_2.__str__() not in shift_1.__str__().split('/')
            and shift_3.__str__() not in shift_2.__str__().split('/')
            ]
        return [shift for shift in main_gen(shifts_triple)]

    else:
        shifts_quadruple = [
                (shift_1 + shift_2) + (shift_3 + shift_4)
                for index_1, shift_1 in enumerate(all_shifts)
                for index_2, shift_2 in enumerate(all_shifts)
                for index_3, shift_3 in enumerate(all_shifts)
                for index_4, shift_4 in enumerate(all_shifts)
                if index_1 <= index_2 <= index_3 <= index_4
                and shift_2.__str__() not in shift_1.__str__().split('/')
                and shift_3.__str__() not in shift_2.__str__().split('/')
                and shift_4.__str__() not in shift_3.__str__().split('/')
                and abs((shift_1 + shift_2).get_begin() - (shift_3 + shift_4).get_begin()) == 6
                and abs((shift_1 + shift_2).get_end() - (shift_3 + shift_4).get_end()) == 6
        ]
        return [shift for shift in main_gen(shifts_quadruple)]
