import logging
# import json
import os
# from telebot import types
# from telebot.util import quick_markup
# import random
# from dateutil import parser
import time

import telebot

# import numpy as np
# import re

logger = logging.getLogger(__name__)
logging.basicConfig(filename='./.secret/log/log.log', level=logging.INFO,
                    format='%(asctime)s. %(levelname)s %(module)s - %(funcName)s: %(message)s')

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Custom packages

from pmd_food_diary_bot.config import config
from pmd_food_diary_bot.params_operation import ParamsOperations
from pmd_food_diary_bot.log_operation import LogOperations
from pmd_food_diary_bot.bot_operation import BotOperations
from pmd_food_diary_bot.records_operation import RecordsOperations, AddRecord

# from pmd_food_diary_bot.output_text_operation import OutputTextOperation

path = config.path
# Open bot
with open(path['token'], 'rt', encoding='utf8') as fp:
    token = fp.read()

bot = telebot.TeleBot(token, threaded=False)

PO = ParamsOperations(config=config)
LO = LogOperations(config=config)
BO = BotOperations(bot=bot, config=config)
RO = RecordsOperations(config=config, bot=bot)
AR = AddRecord(config=config, bot=bot)


# OTO = OutputTextOperation(config=config)

@bot.message_handler(commands=['start'], chat_types=['private'], func=lambda m: (time.time() - m.date <= 10))
def get_message_start(message):
    PO.check_param_keys(chat=message.chat, add_only=True)
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


@bot.message_handler(chat_types=['private'], func=lambda m: (time.time() - m.date <= 5))
def get_message(message):
    PO.check_param_keys(chat=message.chat, add_only=True)
    if message.text == '/add_record':
        params = PO.load_params(message.chat)
        params['add_record'] = {}
        PO.save_params(chat=message.chat, params=params)
        AR.main(chat=message.chat)
    elif message.text == '/show_records':
        RO.show_records(chat=message.chat)


@bot.callback_query_handler(func=lambda call: (call.data.find('add_record_') >= 0) &
                                              (time.time() - call.message.date <= 60 * 60 * 24))
def callback_add_record(call):
    PO.check_param_keys(chat=call.message.chat, add_only=True)

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


if __name__ == '__main__':
    while True:
        try:
            logger.info('Restart the bot')
            bot.polling(none_stop=True, interval=1)  # обязательная для работы бота часть
        except Exception as e:
            logger.error('Error in execution')
            logging.error(e, exc_info=True)
            time.sleep(1 * 60)  # 1 minute
