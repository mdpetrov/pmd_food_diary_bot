import pytz
import telebot
# from telebot import types
# from telebot.util import quick_markup
# import random
from datetime import datetime
from dateutil import parser
import time
# import json
import os
# import numpy as np
# import pandas as pd
# import re

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename='./.secret/log/log.log', level=logging.INFO,
                    format='%(asctime)s. %(levelname)s %(module)s - %(funcName)s: %(message)s')

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Custom packages

from pmd_food_diary_bot.config import config
from pmd_food_diary_bot.params_operation import ParamsOperations
from pmd_food_diary_bot.log_operation import LogOperations
from pmd_food_diary_bot.bot_operation import BotOperations
from pmd_food_diary_bot.records_operation import AddRecord

path = config.path
# Open bot
with open(path['token'], 'rt', encoding='utf8') as fp:
    token = fp.read()

bot = telebot.TeleBot(token, threaded=False)

PO = ParamsOperations(config=config)
LO = LogOperations(config=config)
BO = BotOperations(bot=bot, config=config)
# RO = RecordsOperations(config=config, bot=bot)
AR = AddRecord(config=config, bot=bot)


@bot.message_handler(commands=['start'], chat_types=['private'], func=lambda m: (time.time() - m.date <= 10))
def get_message_start(message):
    start_text = '''Дневник питания 
Список команд:
/start - Главное меню

Операции с записями:
/add_record - Добавить запись
/show_records - Вывести список записей

Настройки:
/settings - Настройки
'''
    BO.send_message(message.chat, text=start_text)


@bot.message_handler(commands=['add_record'], chat_types=['private'], func=lambda m: (time.time() - m.date <= 5))
def get_message_add_record(message):
    params = PO.load_params(message.chat)
    params['add_record'] = {}
    PO.save_params(chat=message.chat, params=params)

    AR.main(chat=message.chat)


@bot.message_handler(commands=['show_records'], chat_types=['private'], func=lambda m: (time.time() - m.date <= 5))
def get_message_show_records(message):
    params = PO.load_params(message.chat)
    tzinfo = params['timezone']
    records = AR.load_records(chat=message.chat)
    text_split = []

    for i, record in enumerate(records):
        if i == 0:
            text_split.append(['#', 'Время', 'Запись'])
        dt_base = parser.parse(record['datetime'])
        dt_local = dt_base.astimezone(pytz.timezone(tzinfo))

        record_corr = [str(i + 1), dt_local.strftime('%Y-%m-%d %H:%M'), record['user_record']]
        text_split.append(record_corr)
    text = '\n'.join(['\t\t'.join(x) for x in text_split])
    text = f"Список записей: \n{text}"
    BO.send_message(message.chat, text=text)


@bot.callback_query_handler(func=lambda call: (call.data.find('add_record_') >= 0) &
                                              (time.time() - call.message.date <= 60 * 60 * 24))
def callback_add_record(call):
    params = PO.load_params(call.message.chat)
    data_split = call.data.split('_')
    if data_split[2] == 'terminate':
        AR.terminate(chat=call.message.chat, message_text='')
        bot.answer_callback_query(call.id)

    if len(params['add_record']) == 0:
        BO.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        return None

    # step = int(data_split[data_split.index('step') + 1])
    step = params['add_record']['step']
    user_value = str(data_split[-1])
    params['add_record']['step'] = step + 1
    params['add_record']['user_value'] = user_value

    PO.save_params(chat=call.message.chat, params=params)

    AR.main(chat=call.message.chat)
    bot.answer_callback_query(call.id)


# @bot.callback_query_handler(func=lambda call: (call.data == 'add_record_terminate') &
#                                               (time.time() - call.message.date <= 60 * 60 * 24))
# def callback_add_record_terminate(call):
#     pass


if __name__ == '__main__':
    while True:
        try:
            logger.info('Restart the bot')
            bot.polling(none_stop=True, interval=1)  # обязательная для работы бота часть
        except Exception as e:
            logger.error('Error in execution')
            logging.error(e, exc_info=True)
            time.sleep(1 * 60)  # 1 minute
