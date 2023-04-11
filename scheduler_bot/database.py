from custom_list_dict import CustomListDict
from datetime import datetime
from os import path, walk, curdir, mkdir, remove
from typing import AnyStr, Tuple, Dict


# initialize the current time and put its values to the appropriate variables
curr_date: [object] = datetime
YEAR, MONTH, DAY = curr_date.timetuple(curr_date.now())[:3]
WEEKDAY: int = curr_date.date(datetime.now()).weekday()


def database_init() -> Tuple[Dict, CustomListDict]:
    """
    This function accepts no arguments. It reads the shifts.txt and emps.txt.
    Then it converts this information to tuple of 2 dicts, the second dict is
    custom. See custom_list_dict.py for more information
    :return: Tuple[Dict, CustomListDict]
    """
    # init shifts with their time of begin, each key being the hour of begin,
    # each value being the list of shifts starting this time
    with open('shifts.txt', 'r', encoding='utf-8') as shifts:
        all_shifts = CustomListDict()
        for line in shifts:
            key = int(line.rstrip().split('-')[1])
            val = line.rstrip().split('-')[0]
            all_shifts[key] = all_shifts.get(key)
            all_shifts[key].append(val)

    # init employees with their time intervals
    emps_names = {
        line.split('-')[0].rstrip(): line.split('-')[1].split() for line in open(
            'emps.txt', 'r', encoding='utf-8'
        )
    }

    return emps_names, all_shifts


def grab_last_week_sunday(day: int, month: int) -> Tuple[int, int]:
    """
    This function accepts monday day and month and returns a proper
    date tuple for further use.
    :param day: int meaning day of Monday
    :param month: int meaning month when is day monday
    :return: tuple
    """
    global YEAR
    year = YEAR

    day -= 1
    if day == 0:
        day = 1
        month -= 1
        if month == 0:
            month = 12

        i = 1
        while True:
            try:
                datetime(year, month, day + i)
            except ValueError:
                day = i
                break
            else:
                i += 1
    return day, month


def seek_week(weekday, day, month, year) -> Tuple:
    """
    this func seeks for the next week first day
    """
    while weekday < 7:
        try:
            day += 1
            weekday += 1
            datetime(year, month, day)
        except ValueError:
            day = 1
            if month == 12:
                year += 1
                month = 1
            else:
                month += 1

    return day, month


def prep_week(day, month) -> Tuple:
    """
    this func compiles the next week
    """
    global YEAR
    days = list()
    months = list()
    occasions = 0
    for i in range(7):
        try:
            datetime(YEAR, month, day + i)
        except ValueError:
            occasions += 1
            days.append(occasions)
            months.append(month + 1)
        else:
            days.append(day + i)
            months.append(month)

    return days, months


def date_init():
    """
    e.g. if you call it on the 18th of May (Thursday),
        it will return you the following week from Monday to Sunday
        ([22, 23, 24, 25, 26, 27, 28], [5, 5, 5, 5, 5, 5, 5])
    :return:
    """
    monday_day, month = seek_week(
        weekday=WEEKDAY,
        day=DAY,
        month=MONTH,
        year=YEAR
    )

    return prep_week(monday_day, month)


def restore_files(file_name: str, dir_name: str) -> None:
    """
    a magic function that automatically creates the files and folders needed
    for the correct work of the program (if there's not any)
    """
    for root, catalog, file in walk(curdir):
        if dir_name in root:
            if file_name in file:
                break
            else:
                open(path.join(root, file_name), 'x')
    else:
        if not path.exists(dir_name):
            mkdir(dir_name)
            restore_files(file_name=file_name, dir_name=dir_name)


def extraction_action(path_to_file: AnyStr) -> None or Tuple:
    """
    This generator function accepts the log file, checks if it exists.
    If so, it reads it and returns a dict
    :param path_to_file: a path to file of .log format
    :return: dict of keys and values for further use in generation methods
    """
    if not path.exists(path_to_file) or not path_to_file.endswith('.log'):
        return None

    with open(path_to_file, 'r', encoding='utf-8') as log_data:
        for line in log_data:
            clear_line = line.rstrip()
            str_to_add = ''
            for index, item in enumerate(clear_line.split('_')):
                if index == 9:
                    str_to_add += item
                if index == 14:
                    str_to_add += '+' + item
                    tuple_of_data = tuple(str_to_add.split('+'))
                    yield tuple_of_data


def clear_history() -> None:
    """
    a short function used to clear history of activity if older than two months
    :return: None
    """
    global MONTH
    global DAY
    for root, dirs, files in walk('history'):
        for file in files:
            file_month = int(file.split('_')[2].split('.')[1])
            file_date = int(file.split('_')[2].split('.')[0])
            if MONTH - file_month + file_month >= 2 and file_date <= DAY:
                remove(path.join(root, file))


def log(grid_list: list, weekday: int, remainders: list, employees: list) -> None:
    """
    function that keeps track of the bot activity and writes it into the log file
    :param grid_list: list of schedule's layout
    :param weekday: current day of week in iteration (int)
    :param remainders: shifts that have not meet bot conditions and left to
    assign manually by a human
    :param employees: list of all employees
    :return: None
    """
    days, months = date_init()
    log_file_name = f"activity_for_{days[weekday - 1]}." \
                    f"{months[weekday - 1] if months[weekday - 1] > 10 else str(0) + str(months[weekday - 1])}.log"
    restore_files(file_name=log_file_name, dir_name='history')
    # write
    with open(path.join(path.abspath('history'), log_file_name), 'w', encoding='utf-8') as log_file:
        for cell in grid_list:
            if cell.get_x() == weekday and not cell.protected():
                if not isinstance(cell.get_info(), str):
                    time_begin = cell.get_info().get_begin()
                    time_end = cell.get_info().get_end()
                else:
                    time_begin = time_end = "none"
                log_file.write(f'<action_on_{datetime.now().strftime("%m_%d_%Y_%H_%M_%S")}>_'
                               f'Assigned_{cell.get_info().__str__()}_'
                               f'employee_{employees[cell.get_y() - 1]}_'
                               f'starts_at_{time_begin}'
                               f'_finishes_at_{time_end}\n')
        if remainders:
            log_file.write('----------------------------------------------\n')
            for item in remainders:
                log_file.write(f'<action_on_{datetime.now().strftime("%m_%d_%Y_%H_%M_%S")}> '
                               f'shift_left={item.__str__()}\n')
