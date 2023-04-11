from typing import Tuple
import os


def filtering(index: int, pack: Tuple) -> bool:
    roster_of_errors = [True, True, True, True]
    dict_of_names_errors = {
        IndexError: 'НЕ присутствуют все три поля: IndexError.',
        NameError: 'Поле «Имя» содержит НЕ только буквы: NameError.',
        SyntaxError: 'Поле «Имейл» НЕ содержит @ и точку: SyntaxError.',
        ValueError: 'Поле «Возраст» НЕ представляет число от 10 до 99: '
                    'ValueError.'
    }

    if len(pack) < 3:
        roster_of_errors[0] = False
    else:
        if not pack[0].isalpha():
            roster_of_errors[1] = False
        if not pack[1].__contains__('@' and '.'):
            roster_of_errors[2] = False
        try:
            if int(pack[2]) not in range(10, 100):
                roster_of_errors[3] = False
        except ValueError:
            roster_of_errors[3] = False

    with open('registrations_bad.log', 'a', encoding='utf-8') as bad_try:
        count = 0
        for boolean_value, (type_of_error, error_name) in \
                zip(roster_of_errors, dict_of_names_errors.items()):
            try:
                if not boolean_value:
                    raise type_of_error

            except type_of_error:
                bad_try.write(f'In line {index + 1} '
                              f'("{" ".join(pack)}"): {error_name}\n')

            else:
                count += 1
        else:
            if count == 4:
                return True


def main():
    paths = (
        os.path.abspath('registrations_bad.log'),
        os.path.abspath('registrations_good.log')
    )

    for path in paths:
        if os.path.exists(path):
            os.remove(path)

    with open('registrations.txt', 'r', encoding='utf-8') as database_raw, \
            open('registrations_good.log', 'a', encoding='utf-8') as nice_try:
        for index, line in enumerate(database_raw):
            data_pack = tuple(line.rstrip().split())
            if filtering(index, data_pack):
                nice_try.write(' '.join(data_pack) + '\n')


if __name__ == '__main__':
    main()
