def words_gen():  # открою текстовый файл и превращу его в список
    data = list(open('words.txt'))

    get_english_words_set = [
        i for i in data
    ]

    for index, item in enumerate(get_english_words_set):  # все элементы имеют \n поэтому уберем лишнее
        item_roster = list(item)
        if item.endswith('\n'):
            item_roster.remove('\n')
            item_put = ''.join(item_roster)
            get_english_words_set[index] = item_put

    return get_english_words_set  # из ти-икс-ти получил лист


if __name__ == '__main__':
    words_gen()
