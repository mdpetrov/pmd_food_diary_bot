from os.path import join, isfile
import time
import json

from dateutil.relativedelta import relativedelta
from dateutil import parser
from datetime import datetime
import pytz

import pandas as pd
from tabulate import tabulate

from pmd_food_diary_bot.params_operation import ParamsOperations
from pmd_food_diary_bot.bot_operation import BotOperations
from pmd_food_diary_bot.output_text_operation import OutputTextOperation


class RecordsOperations(object):
    def __init__(self, config, bot):
        self.config = config
        self.def_records = []
        self.BO = BotOperations(bot=bot, config=config)
        self.PO = ParamsOperations(config=config)
        self.OTO = OutputTextOperation(config=config)

    def load_records(self, chat):
        """Load user records"""
        path = self.config.path
        record_dir = path['record_dir']
        record_name = f"{chat.id}_{chat.username}.json"
        record_path = join(record_dir, record_name)
        if isfile(record_path):
            with open(record_path, 'r') as fp:
                records = json.load(fp)
        else:
            records = self.def_records
        return records

    def save_records(self, chat, records):
        """Save user records"""
        record_dir = self.config.path['record_dir']
        record_name = f"{chat.id}_{chat.username}.json"
        record_path = join(record_dir, record_name)
        with open(record_path, 'w') as fp:
            json.dump(obj=records, fp=fp)

    def show_records(self, chat):
        params = self.PO.load_params(chat)
        tzinfo = params['user_settings']['timezone']
        column_locale_map = self.OTO.get_record_steps_name(chat=chat)

        records = self.load_records(chat=chat)
        records_df = pd.DataFrame.from_dict(records)
        records_df['datetime'] = records_df.apply(self._set_local_timezone, axis=1, tzinfo=tzinfo)
        records_df.sort_values(['datetime'], ascending=[True], inplace=True)

        records_df.index = records_df.index.map(lambda x: x + 1)
        records_df.columns = records_df.columns.map(column_locale_map)

        records_tab = tabulate(records_df, headers=records_df.columns)
        text = f"Список записей: \n\n{records_tab}"
        self.BO.send_message(chat=chat, text=text)

    @staticmethod
    def _set_local_timezone(row, tzinfo):
        dt_base = parser.parse(row['datetime'])
        dt_local = dt_base.astimezone(pytz.timezone(tzinfo))
        return dt_local.strftime('%Y-%m-%d %H:%M')

class AddRecord(RecordsOperations):
    def main(self, chat):
        chat_id = chat.id
        params = self.PO.load_params(chat)
        step = params['add_record'].setdefault('step', 1)
        # step += 1
        # params['add_record']['step'] = step
        # main_message_id = params['add_record'].setdefault('main_message_id', None)
        if step == 1:
            self.step1_pre(params, chat)
        elif step == 2:
            self.step1_action(params, chat=chat)
            self.step2_pre(params, chat=chat)
            self.BO.register_next_step_handler_by_chat_id(chat_id=chat.id, callback=self.step2_action)
        # elif step == 3:
        # self.step2_action(params)
        # self.step3_action(params)  # add save record

        self.PO.save_params(params=params, chat=chat)

    def step1_pre(self, params, chat):
        chat_id = chat.id
        step_name = self.config.add_record_steps[0]
        main_message_id = params['add_record'].setdefault('main_message_id', 0)
        if main_message_id > 0:
            self.BO.delete_message(chat_id, main_message_id)
        message_text = 'Добавление записи. Выбери время'
        options_d = self.config.add_record_options[step_name]
        options = list(options_d.values())
        callbacks = [f"add_record_step_1_{x}" for x in options_d.keys()]
        options.append('Отменить'), callbacks.append('add_record_terminate')

        markup = self.BO.quick_markup(options, callbacks)
        message = self.BO.send_message(chat=chat, text=message_text, reply_markup=markup)
        params['add_record']['main_message_id'] = message.id

    def step1_action(self, params, chat):
        tzinfo = params['user_settings']['timezone']
        step_name = self.config.add_record_steps[0]
        tmp_record = params['add_record'].setdefault('tmp_record', {})
        main_message_id = params['add_record']['main_message_id']

        current_time = datetime.now().astimezone(pytz.utc)
        minutes_back = int(params['add_record']['user_value'])
        interval = current_time - relativedelta(minutes=minutes_back)
        user_time = interval.strftime('%Y-%m-%d %H:%M %Z')

        user_time_local = interval.astimezone(pytz.timezone(tzinfo)).strftime('%Y-%m-%d %H:%M')
        tmp_record[step_name] = user_time

        markup = self.BO.quick_markup(options=['Отменить'], callback=['add_record_terminate'])
        self.BO.edit_message(chat_id=chat.id, message_id=main_message_id, text=f'Зафиксировал время {user_time_local}',
                             reply_markup=markup)

        params['add_record']['tmp_record'] = tmp_record

    def step2_pre(self, params, chat):
        main_message_id = params['add_record'].setdefault('main_message_id', 0)
        message_text = 'Теперь введи название записи:'
        self.BO.send_message(chat=chat, text=message_text)

    def step2_action(self, message):
        """ This method handles the message that comes after the step 2 (pre)"""
        params = self.PO.load_params(message.chat)
        user_value = message.text
        if user_value[0] == '/':
            message_text = 'Название записи не может начинаться с технических символов'
            self.terminate(chat=message.chat, message_text=message_text)
            return None
        params['add_record']['user_value'] = user_value

        step_name = self.config.add_record_steps[1]
        tmp_record = params['add_record'].setdefault('tmp_record', {})
        tmp_record[step_name] = user_value
        params['add_record']['tmp_record'] = tmp_record
        self.BO.clear_step_handler_by_chat_id(message.chat.id)
        self.step_final_action(chat=message.chat, params=params)

    def step_final_action(self, chat, params):
        records = self.load_records(chat=chat)
        tmp_record = params['add_record'].setdefault('tmp_record', {})
        records.append(tmp_record)
        self.save_records(chat=chat, records=records)
        params['add_record'] = {}
        self.PO.save_params(params=params, chat=chat)
        self.BO.send_message(chat=chat, text='Успешно добавлено')

    def terminate(self, chat, message_text=''):
        params = self.PO.load_params(chat=chat)
        main_message_id = params['add_record'].setdefault('main_message_id', 0)
        if main_message_id > 0:
            self.BO.delete_message(chat_id=chat.id, message_id=main_message_id)
        params['add_record'] = {}

        self.PO.save_params(params=params, chat=chat)
        message_text = f"Операция отменена. {message_text}"
        self.BO.send_message(chat=chat, text=message_text)
        self.BO.clear_step_handler_by_chat_id(chat.id)
