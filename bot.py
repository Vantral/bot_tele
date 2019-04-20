import telebot
import requests
import re

bot = telebot.TeleBot('')


def find_room(text):
    pattern = '<h4>.*?Режим работы</h4>(?:\s\s<p>(.*?)</p>.*?)(?:\s\s<p>(.*?)</p>.*?)?(?:\s\s<p>(.*?)</p>.*?)?'
    working_hours = re.findall(pattern, text, flags=re.DOTALL)
    if working_hours == []:
        working_hours = ['Время работы неизвестно.']

    pattern = '<h4>.*?Меню</h4>.*?<a.*? href="(.*?)".*?>(.*?)</a>'
    menu_ref = re.findall(pattern, text, flags=re.DOTALL)
    if menu_ref == []:
        menu_ref = ['Меню нет']

    pattern = '<h4>.*?Где находится</h4>\s\s<p>(.*?)</p>'
    placement1 = re.findall(pattern, text, flags=re.DOTALL)
    if placement1 == []:
        placement = ['К сожалению, местоположение еще не описано']
    else:
        placement = []
        for l in placement1:
            placement.append(l.replace('&nbsp;', ' ').replace('&laquo;', '«').replace('&raquo;', '»'))

    pattern = '<h4>.*?Специальное меню</h4>(?:(?:\s)*?<p>(.*?)</p>)\n\n\t<'
    special1 = re.findall(pattern, text, flags=re.DOTALL)
    special = []
    if special1 == []:
        special = ['Специального меню пока нет. Ждите праздников']
    else:
        for l in special1:
            special.append(l.replace('&nbsp;', ' ').replace('<strong>', '').replace('</strong>', ''))

    return placement, working_hours, menu_ref, special


def read_url(filename):

    response = requests.get(filename)
    html = response.text
    return html


def find_info(num, filename, index=0):
    f = read_url(filename)
    info = find_room(f)
    #print(info[num])
    if num == 3 or num == 0:
        return info[num][index]
    if num == 2:
        x = 'https://www.hse.ru' + info[num][index][0] + '\n' + info[num][0][1]
        return x
    else:
        return '\n'.join(info[num][0])

def data(filename, index=0):
    @bot.message_handler(regexp='Расположение в корпусе')
    def loc(message):
        x = find_info(0, filename, index)
        bot.send_message(message.chat.id, x)
    @bot.message_handler(regexp='Часы работы')
    def time(message):
        x = find_info(1, filename, index)
        bot.send_message(message.chat.id, x)
    @bot.message_handler(regexp='Специальное меню')
    def time(message):
        x = find_info(3, filename, index)
        bot.send_message(message.chat.id, x)
    @bot.message_handler(regexp='Меню')
    def time(message):
        x = find_info(2, filename, index)
        bot.send_message(message.chat.id, x)


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет! Введите /corpus, чтобы увидеть список корпусов')

@bot.message_handler(commands=['corpus'])
def choose_korp1(message):
    item = telebot.types.ReplyKeyboardMarkup()
    item.row('М.Гнездниковский пер., д.4', 'Кирпичная, 33')
    item.row('Кочновский проезд., 3', 'Мясницкая, 11')
    item.row('Мясницкая, 20')
    bot.send_message(message.chat.id, 'Какой корпус вам интересен?', reply_markup=item)
    bot.send_message(message.chat.id, 'Другой /corpus2')

@bot.message_handler(commands=['corpus2'])
def choose_korp2(message):
    item = telebot.types.ReplyKeyboardMarkup()
    item.row('М.Ордынка, 17', 'Б.Переяславская ул., д.50')
    item.row('М.Пионерская ул., 12/4', 'Потаповский пер., д.16, стр.10')
    item.row('Старая Басманная,  21/4')

    bot.send_message(message.chat.id, 'Какой корпус вам интересен?', reply_markup=item)
    bot.send_message(message.chat.id, 'Другой /corpus3')

@bot.message_handler(commands=['corpus3'])
def choose_korp3(message):
    item = telebot.types.ReplyKeyboardMarkup()
    fg = telebot.types.KeyboardButton('hello')
    item.row('М.Гнездниковский пер., д.4', 'Таллинская ул., д.34')
    item.row('Б.Трехсвятительский пер., 3', 'М.Трехсвятительский пер., 8/2, стр.1')
    item.row('М.Гнездниковский пер., д.4', 'Трифоновская ул., д.57')
    bot.send_message(message.chat.id, 'Какой корпус вам интересен?', reply_markup=item)
    bot.send_message(message.chat.id, 'Другое /corpus4')

@bot.message_handler(commands=['corpus4'])
def choose_korp4(message):
    item = telebot.types.ReplyKeyboardMarkup()
    item.row('Усачева, 6', 'Хитровский пер., 2/8, стр.5')
    item.row('Шаболовка, 26, стр. 4', 'Шаболовка, 28/11, стр.2')

    bot.send_message(message.chat.id, 'Выберите корпус', reply_markup=item)

@bot.message_handler(regexp='М.Гнездниковский пер., д.4')
def make_schoice(message):
    item = telebot.types.ReplyKeyboardMarkup()
    item.row('Расположение в корпусе', 'Часы работы')
    item.row('Меню', 'Специальное меню')
    bot.send_message(message.chat.id, 'Что вы хотите узнать?', reply_markup=item)
    data('https://www.hse.ru/buildinghse/dining/mgnezdn')


# @bot.message_handler(regexp='Кирпичная, 33')
# def make_schoice(message):
#     choice = telebot.types.ReplyKeyboardMarkup()
#     choice.row('Столовая', 'Буфет', 'Киоск')
#     bot.send_message(message.chat.id, 'О чём вы хотите узнать?', reply_markup=choice)
#     @bot.message_handler(regexp='Столовая')
#     def a(message):
#         item = telebot.types.ReplyKeyboardMarkup()
#         item.row('Расположение в корпусе', 'Часы работы')
#         item.row('Меню', 'Специальное меню')
#         bot.send_message(message.chat.id, 'Что вы хотите узнать?', reply_markup=item)
#         data('https://www.hse.ru/buildinghse/dining/kirpich', index=0)
#     @bot.message_handler(regexp='Буфет')
#     def b(message):
#         item = telebot.types.ReplyKeyboardMarkup()
#         item.row('Расположение в корпусе', 'Часы работы')
#         item.row('Меню', 'Специальное меню')
#         bot.send_message(message.chat.id, 'Что вы хотите узнать?', reply_markup=item)
#         @bot.message_handler(regexp='Меню')
#         def ab(message):
#             bot.send_message(message.chat.id, 'Нет данных на сайте', reply_markup=item)
#         data('https://www.hse.ru/buildinghse/dining/kirpich', index=1)
#     @bot.message_handler(regexp='Киоск')
#     def c(message):
#         item = telebot.types.ReplyKeyboardMarkup()
#         item.row('Расположение в корпусе', 'Часы работы')
#         item.row('Меню', 'Специальное меню')
#         bot.send_message(message.chat.id, 'Что вы хотите узнать?', reply_markup=item)
#         @bot.message_handler(regexp='Меню')
#         def ab(message):
#             bot.send_message(message.chat.id, 'Нет данных на сайте', reply_markup=item)
#         data('https://www.hse.ru/buildinghse/dining/kirpich', index=2)

@bot.message_handler(regexp='Кочновский проезд., 3')
def make_schoice(message):
    item = telebot.types.ReplyKeyboardMarkup()
    item.row('Расположение в корпусе', 'Часы работы')
    item.row('Меню', 'Специальное меню')
    bot.send_message(message.chat.id, 'Что вы хотите узнать?', reply_markup=item)
    data('http://www.hse.ru/buildinghse/dining/kochn')

@bot.message_handler(regexp='Мясницкая, 11')
def make_schoice(message):
    item = telebot.types.ReplyKeyboardMarkup()
    item.row('Расположение в корпусе', 'Часы работы')
    item.row('Меню', 'Специальное меню')

    bot.send_message(message.chat.id, 'Что вы хотите узнать?', reply_markup=item)

@bot.message_handler(regexp='Мясницкая, 20')
def make_schoice(message):
    item = telebot.types.ReplyKeyboardMarkup()
    item.row('Расположение в корпусе', 'Часы работы')
    item.row('Меню', 'Специальное меню')

    bot.send_message(message.chat.id, 'Что вы хотите узнать?', reply_markup=item)

@bot.message_handler(regexp='М.Ордынка, 17')
def make_schoice(message):
    item = telebot.types.ReplyKeyboardMarkup()
    item.row('Расположение в корпусе', 'Часы работы')
    item.row('Меню', 'Специальное меню')
    bot.send_message(message.chat.id, 'Что вы хотите узнать?', reply_markup=item)
    data('https://www.hse.ru/buildinghse/dining/mordinka')

@bot.message_handler(regexp='Б.Переяславская ул., д.50')
def make_schoice(message):
    item = telebot.types.ReplyKeyboardMarkup()
    item.row('Расположение в корпусе', 'Часы работы')
    item.row('Меню', 'Специальное меню')

    bot.send_message(message.chat.id, 'Что вы хотите узнать?', reply_markup=item)
    data('http://www.hse.ru/buildinghse/dining/pereyasl')

@bot.message_handler(regexp='М.Пионерская ул., 12/4')
def make_schoice(message):
    item = telebot.types.ReplyKeyboardMarkup()
    item.row('Расположение в корпусе', 'Часы работы')
    item.row('Меню', 'Специальное меню')

    bot.send_message(message.chat.id, 'Что вы хотите узнать?', reply_markup=item)
    data('https://www.hse.ru/buildinghse/dining/mpion')

@bot.message_handler(regexp='Потаповский пер., д.16, стр.10')
def make_schoice(message):
    item = telebot.types.ReplyKeyboardMarkup()
    item.row('Расположение в корпусе', 'Часы работы')
    item.row('Меню', 'Специальное меню')

    bot.send_message(message.chat.id, 'Что вы хотите узнать?', reply_markup=item)
    data('https://www.hse.ru/buildinghse/dining/potap')

@bot.message_handler(regexp='Старая Басманная,  21/4 стр.5')
def make_schoice(message):
    item = telebot.types.ReplyKeyboardMarkup()
    item.row('Расположение в корпусе', 'Часы работы')
    item.row('Меню', 'Специальное меню')

    bot.send_message(message.chat.id, 'Что вы хотите узнать?', reply_markup=item)

@bot.message_handler(regexp='Таллинская ул., д.34')
def make_schoice(message):
    item = telebot.types.ReplyKeyboardMarkup()
    item.row('Расположение в корпусе', 'Часы работы')
    item.row('Меню', 'Специальное меню')

    bot.send_message(message.chat.id, 'Что вы хотите узнать?', reply_markup=item)

@bot.message_handler(regexp='Шаболовка, 28/11, стр.2')
def make_schoice(message):
    item = telebot.types.ReplyKeyboardMarkup()
    item.row('Расположение в корпусе', 'Часы работы')
    item.row('Меню', 'Специальное меню')

    bot.send_message(message.chat.id, 'Что вы хотите узнать?', reply_markup=item)

    data('https://www.hse.ru/buildinghse/dining/shabolovka28')

@bot.message_handler(regexp='Б.Трехсвятительский пер., 3')
def make_schoice(message):
    item = telebot.types.ReplyKeyboardMarkup()
    item.row('Расположение в корпусе', 'Часы работы')
    item.row('Меню', 'Специальное меню')

    bot.send_message(message.chat.id, 'Что вы хотите узнать?', reply_markup=item)

@bot.message_handler(regexp='М.Трехсвятительский пер., 8/2, стр.1')
def make_schoice(message):
    item = telebot.types.ReplyKeyboardMarkup()
    item.row('Расположение в корпусе', 'Часы работы')
    item.row('Меню', 'Специальное меню')

    bot.send_message(message.chat.id, 'Что вы хотите узнать?', reply_markup=item)

    data('https://www.hse.ru/buildinghse/dining/mt')

@bot.message_handler(regexp='Шаболовка, 26, стр.4')
def make_schoice(message):
    item = telebot.types.ReplyKeyboardMarkup()
    item.row('Расположение в корпусе', 'Часы работы')
    item.row('Меню', 'Специальное меню')

    bot.send_message(message.chat.id, 'Что вы хотите узнать?', reply_markup=item)

@bot.message_handler(regexp='Большая Ордынка, 47/7')
def make_schoice(message):
    item = telebot.types.ReplyKeyboardMarkup()
    item.row('Расположение в корпусе', 'Часы работы')
    item.row('Меню', 'Специальное меню')

    bot.send_message(message.chat.id, 'Что вы хотите узнать?', reply_markup=item)

    data('https://www.hse.ru/buildinghse/dining/bordinka')

@bot.message_handler(regexp='Трифоновская ул., д.57')
def make_schoice(message):
    item = telebot.types.ReplyKeyboardMarkup()
    item.row('Расположение в корпусе', 'Часы работы')
    item.row('Меню', 'Специальное меню')

    bot.send_message(message.chat.id, 'Что вы хотите узнать?', reply_markup=item)

    data('https://www.hse.ru/buildinghse/dining/trifon')

@bot.message_handler(regexp='Усачева, 6')
def make_schoice(message):
    item = telebot.types.ReplyKeyboardMarkup()
    item.row('Расположение в корпусе', 'Часы работы')
    item.row('Меню', 'Специальное меню')

    bot.send_message(message.chat.id, 'Что вы хотите узнать?', reply_markup=item)

    data('https://www.hse.ru/buildinghse/dining/usacheva')

@bot.message_handler(regexp='Хитровский пер., 2/8, стр.5')
def make_schoice(message):
    item = telebot.types.ReplyKeyboardMarkup()
    item.row('Расположение в корпусе', 'Часы работы')
    item.row('Меню', 'Специальное меню')

    bot.send_message(message.chat.id, 'Что вы хотите узнать?', reply_markup=item)

    data('https://www.hse.ru/buildinghse/dining/khitr')



bot.polling()
