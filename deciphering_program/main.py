from english_words import words_gen  # импортируем словарь распространенных англ слов, оставляю задел на будущее:
# добавить несколько языков, например
from message import string_gen  # импорт строки из другого файла с целью ненагруженности кода
import time as t


def decipher(string, swing):  # генерирую строку, подается инит строка и сдвиг
    list_of_strings = [
        chr(ord(letter) + swing) if letter != ' ' else ' ' for letter in string
    ]

    string = ''.join(list_of_strings)

    return string


def proper_string(string):  # здесь питон пытается найти верный сдвиг и строку,
    # возвращает стрингу
    eng_words_list = words_gen()
    string_list = string.split()
    swing = 0
    match = []

    try:  # пробуем пойти со сдвигом назад
        print('Trying back Unicodes...')
        t.sleep(2)
        while len(match) / len(string_list) < 0.1:  # питон остановит поиск, в случае если в списке совпадений
            # элементов строки и списком слов англ языка будет хотя бы 10 процентов элементов от длины элементов строки
            #  так питон узнает, когда текст станет более менее читаемым

            string_list = decipher(string, swing).split()
            match = [
                item for item in string_list if item in eng_words_list
            ]
            swing -= 1

        else:
            print('String found...')
            t.sleep(0.3)

    except TypeError:  # если словили такой эксепшен, смысла двигать назад нет, двинем вперед
        print('Could not search coincidences in behind. Going forward...')
        t.sleep(2)
        swing = 0
        while len(match) / len(string_list) < 0.1:

            string_list = decipher(string, swing).split()
            match = [
                item for item in string_list if item in eng_words_list
            ]
            swing += 1

        else:
            print('String found...')
            t.sleep(0.3)

    except UnicodeError or UnicodeEncodeError:  # если и вперед не нашел, значит по кр мере такого шифра в стринге нет,
        # а это просто набор символов
        print('Could not decypher. Sorry.')
        t.sleep(2)
        return None

    finally:  # в любом случае питон говорит что прога поработала
        print('Decyphering done!')
        t.sleep(0.3)

    return ' '.join(string_list)


def message_decode(data):  # расшифровываем строку, уже конкретную
    print('Your possible string: {}'.format(''.join(data)))
    print('Decyphering...')
    t.sleep(3)
    list_of_msg = data.split()
    trial_word = list_of_msg[0]
    swing = 0

    for index in range(len(trial_word)):  # для начала установим, какой сдвиг присутствует в первом слове, изначальный
        list_chars = list(trial_word)

        if trial_word in words_gen():
            swing = len(trial_word) - index
            break

        else:
            swing += 1
            list_chars.append(list_chars[0])
            list_chars.remove(list_chars[0])
            trial_word = ''.join(list_chars)

    for index, item in enumerate(list_of_msg):  # сдвигаем все слова
        list_item = list(item)
        little_swing = swing
        if little_swing >= len(list_item):
            while little_swing >= len(list_item):
                little_swing -= len(list_item)
            else:
                list_of_msg[index] = list_item[len(list_item) - little_swing:] +\
                                     list_item[:len(list_item) - little_swing]
        else:
            list_of_msg[index] = list_item[len(list_item) - swing:] + list_item[:len(list_item) - swing]
        if '.' in list_item:
            swing += 1
    final_list = [
        ''.join(item) for item in list_of_msg
    ]

    return ' '.join(final_list)


def main():
    print('Generating string...')
    t.sleep(1)
    string = string_gen()
    print('Starting...')
    t.sleep(1)
    data = proper_string(string)

    if type(data) is not None:
        print('Message:\n{string}'.format(
            string=message_decode(data).replace('. ', '\n')
        ))


if __name__ == '__main__':
    main()
