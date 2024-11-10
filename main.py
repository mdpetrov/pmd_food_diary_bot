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

# from pmd_daubi_bot.config import config
# from pmd_daubi_bot.params_operation import ParamsOperations
# from pmd_daubi_bot.log_operation import LogOperations
# from pmd_daubi_bot.bot_operation import BotOperations
# from pmd_daubi_bot.phrase_operation import PhraseOperations

# path = config.path
# Open bot
with open(path['token'], 'rt', encoding='utf8') as fp:
	token = fp.read()

bot = telebot.TeleBot(token, threaded=False)

# PO = ParamsOperations(config=config)
# LO = LogOperations(config=config)
# BO = BotOperations(bot=bot)
# PhO = PhraseOperations(config=config)



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
    BO.send_message(message.chat.id, text=start_text, params=local_params)
    PO.save_params(message.chat.id, local_params)

@bot.message_handler(commands=['add_phrase'], chat_types=['private'], func=lambda m: (time.time() - m.date <= 5))
def get_message_add_phrase(message):
    local_params = PO.load_params(message.chat.id)
    BO.send_message(message.chat.id, text='''Ты можешь добавить новую фразу в генератор ответов. 
Фразы добавляются анонимно. 
Введи фразу:''', params=local_params)
    bot.register_next_step_handler(message, check_phrase)
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