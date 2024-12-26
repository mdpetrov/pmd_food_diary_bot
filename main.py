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

from pmd_food_diary_bot.config import config
from pmd_food_diary_bot.params_operation import ParamsOperations
from pmd_food_diary_bot.log_operation import LogOperations
from pmd_food_diary_bot.bot_operation import BotOperations
from pmd_food_diary_bot.records_operation import RecordsOperations

path = config.path
# Open bot
with open(path['token'], 'rt', encoding='utf8') as fp:
    token = fp.read()

bot = telebot.TeleBot(token, threaded=False)

PO = ParamsOperations(config=config)
LO = LogOperations(config=config)
BO = BotOperations(bot=bot)
RO = RecordsOperations(config=config)

    

@bot.message_handler(commands=['start'], chat_types=['private'], func=lambda m: (time.time() - m.date <= 10))
def get_message_start(message):
    start_text = '''Дневник еды 
Список команд:
    /start - вывести стартовое сообщение
    /add_record - добавить запись
    /show_records - вывести список записей
'''
    BO.send_message(message.chat.id, text=start_text)

@bot.message_handler(commands=['add_record'], chat_types=['private'], func=lambda m: (time.time() - m.date <= 5))
def get_message_add_record(message):
    RO.initialize_add_record(message)

        
if __name__ == '__main__':
    while True:
        try:
            LO.write_log(0, 'Restart the bot')
            bot.polling(none_stop=True, interval=1) #обязательная для работы бота часть
        except Exception as e:
            LO.write_log(0, 'Error in execution')
            LO.write_log(0, e)
            time.sleep(1*60) # 1 minute