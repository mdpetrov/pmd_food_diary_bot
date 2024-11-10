import telebot
from telebot import types 
from telebot.util import quick_markup
import random
import datetime
import time
import json
import os
import numpy as np
import pandas as pd
import re

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Custom packages

from pmd_daubi_bot.config import config
from pmd_daubi_bot.params_operation import ParamsOperations
from pmd_daubi_bot.log_operation import LogOperations
from pmd_daubi_bot.bot_operation import BotOperations
from pmd_daubi_bot.records_operation import RecordsOperations

path = config.path
# Open bot
with open(path['token'], 'rt', encoding='utf8') as fp:
	token = fp.read()

bot = telebot.TeleBot(token, threaded=False)

PO = ParamsOperations(config=config)
LO = LogOperations(config=config)
BO = BotOperations(bot=bot)
RO = RecordsOperations(config=config)



# if not os.path.isfile(path['text_phrases']):
    # raise OSError('text_phrases not found')


random.seed(datetime.datetime.now().timestamp())

    
    

@bot.message_handler(commands=['start'], chat_types=['private'], func=lambda m: (time.time() - m.date <= 10))
def get_message_start(message):
    local_params = PO.load_params(message.chat.id)
    # BO.send_message(message.chat.id, text='ДАУБИ БОТ', params=local_params)
    start_text = '''Дневник еды 
Список команд:
    /start - вывести стартовое сообщение
    /add_record - добавить запись
    /show_records - вывести список записей (пока не работает)
'''
    records = RO.load_records(chat_id=message.chat.id)
    if records:
        start_text = f'''{start_text}
Список записей:
{[f"\t{'\t'.join(x[1:])}" for x in records.itertuples()])}'''

    BO.send_message(message.chat.id, text=start_text, params=local_params)
    PO.save_params(message.chat.id, local_params)

@bot.message_handler(commands=['add_record'], chat_types=['private'], func=lambda m: (time.time() - m.date <= 5))
def get_message_add_record(message):
    local_params = PO.load_params(message.chat.id)
    add_record(message)
    PO.save_params(message.chat.id, local_params)
    
def add_record(message, step=1, send_message_only=False)
    local_params = PO.load_params(message.chat.id)
    add_record_state = local_params['add_record_state']
    if not message.text:
        # add_record(message, step=step-1, send_message_only=True)
        # bot.register_next_step_handler(message, add_record, step=step-1, message_prev=message_prev)
        # return None
        step -= 1
    add_record_state.update({'step':step})
    text_main = f'''Режим добавления записи 
Шаг {step}/(tbd). '''
    if step == 1:
        text_add = f'''Введите дату (ГГГГ ММ ДД Ч:М):'''
    elif step == 2:
        text_add = 'Введите запись:'
        if message.text:
            record_date_input = message.text
            record_date_output = record_date_input
            add_record_state.update({'date':record_date_output})
    elif step == 3:
        text_add = 'Вы собиратесь добавить следующую запись:'
        if message.text:
            record = message.text
            add_record_state.update('record':record)
            text_add = f"{add_record_state['date']}\t{record}"

    text = f"{text_main}\n{text_add}"
    message_sent = BO.send_message(message.chat.id, text=text, params=local_params)
    bot.register_next_step_handler(message_sent, add_record, step=step+1)
    PO.save_params(message.chat.id, local_params)

        
if __name__ == '__main__':
    while True:
        try:
            LO.write_log(0, 'Restart the bot')
            bot.polling(none_stop=True, interval=1) #обязательная для работы бота часть
        except Exception as e:
            LO.write_log(0, 'Error in execution')
            LO.write_log(0, e)
            time.sleep(1*60) # 1 minute