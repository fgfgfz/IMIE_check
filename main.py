from re import compile
from json import dumps
from json import loads

from telebot import TeleBot
from requests import post

from config import URL
from config import TOKEN
from config import API_TOKEN


MESSAGES = {
    'start':
        'Введите Ваш IMEI:',
}

ERRORS = {
    'validation':
        '<b>Некорректный IMEI!</b>',

    'not_text':
        '<b>Это не IMEI!</b>',

    'not_in_white_list':
        '<b>К сожалению, у Вас нет прав на это :(</b>',
}


bot = TeleBot(TOKEN, parse_mode='html')


# Белый список сохранил в txt, т.к можно добавить возможность вносить и удалять пользователей в/из него
def get_white_list():
    with open('white_list.txt', 'r') as file:
        lines = file.readlines()
        users_id = [int(line.replace('\n', '')) for line in lines]
        return users_id


# Для данного тестового API токена доступны только 4 сервиса: 12, 13, 14, 15
def get_imei_info(imei):
    headers = {
        'Authorization': 'Bearer ' + API_TOKEN,
        'Content-Type': 'application/json'
    }
    data = dumps({
        "deviceId": imei,
        "serviceId": 12
    })

    response = post(URL, headers=headers, data=data)
    imei_info = loads(response.text)
    answer = dumps(imei_info, indent=4)
    return answer


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, MESSAGES['start'])


@bot.message_handler(content_types=['audio', 'photo', 'voice', 'video', 'document', 'location', 'contact', 'sticker'])
def not_text_error(message):
    bot.send_message(message.chat.id, ERRORS['not_text'])


@bot.message_handler(content_types=['text'])
def processing_imei(message):
    global white_list
    pattern = compile(r'\d{15}')
    match = pattern.fullmatch(message.text)

    if message.from_user.id not in white_list:
        bot.send_message(message.chat.id, ERRORS['not_in_white_list'])
    elif match:
        imei_info = get_imei_info(message.text)
        bot.send_message(message.chat.id, imei_info)
    else:
        bot.send_message(message.chat.id, ERRORS['validation'])


white_list = get_white_list()
bot.infinity_polling()
