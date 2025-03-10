from os.path import join, isfile
import time
import json

from pmd_food_diary_bot.params_operation import ParamsOperations
from pmd_food_diary_bot.bot_operation import BotOperations


class RecordsOperations(object):
    def __init__(self, config, bot):
        self.config = config
        self.def_records = []
        self.BO = BotOperations(bot=bot, config=config)
        self.PO = ParamsOperations(config=config)

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
            json.dump(records, fp)


class AddRecord(RecordsOperations):
    def main(self, chat):
        chat_id = chat.id
        params = self.PO.load_params(chat.id)
        step = params['add_record'].setdefault('step', 0)
        step += 1
        params['add_record']['step'] = step
        # main_message_id = params['add_record'].setdefault('main_message_id', None)
        if step == 1:
            self.step1_pre(params, chat_id)
        elif step == 2:
            self.step1_action(params)
            self.step2_pre(params, chat_id)
            self.BO.register_next_step_handler(message=params['add_record']['main_message'], callback=self.step2_action, params=params)
        # elif step == 3:
            # self.step2_action(params)
            # self.step3_action(params)  # add save record

        self.PO.save_params(params, chat_id)

    def step1_pre(self, params, chat_id):
        step_name = self.config['add_record_steps'][0]
        main_message = params['add_record'].setdefault('main_message', None)
        if not isinstance(main_message, type(None)):
            self.BO.delete_message(chat_id, main_message.message_id)
        message_text = 'Добавление записи. Шаг 1. Выбери время'
        options_d = self.config['add_record_options'][step_name]
        options = list(options_d.values())
        callbacks = [f"add_record_step_1_{x}" for x in options_d.keys()]
        markup = self.BO.quick_markup(options, callbacks)
        message = self.BO.send_message(chat_id=chat_id, text=message_text, markup=markup)
        params['add_record']['main_message'] = message

    def step1_action(self, params):
        step_name = self.config['add_record_steps'][0]
        tmp_record = params['add_record'].setdefault('tmp_record', {})
        tmp_record[step_name] = params['add_record']['user_value']
        params['add_record']['tmp_record'] = tmp_record

    def step2_pre(self, params, chat_id):
        # step_name = self.config['add_record_steps'][1]
        main_message = params['add_record'].setdefault('main_message', None)
        message_text = 'Время зафиксировал! Теперь введи название записи:'
        if not isinstance(main_message, type(None)):
            self.BO.edit_message(chat_id=chat_id, message_id=main_message.message_id, text=message_text)
        else:
            raise NotImplementedError('Main message has not been found on step 2. Something is wrong')


    def step2_action(self, message, params):
        user_value = message.text
        params['add_record']['user_value'] = user_value

        step_name = self.config['add_record_steps'][1]
        tmp_record = params['add_record'].setdefault('tmp_record', {})
        tmp_record[step_name] = user_value
        params['add_record']['tmp_record'] = tmp_record
        self.step3_action(chat=message.chat, params=params)

    def step3_action(self, chat, params):
        records = self.load_records(chat=chat)
        tmp_record = params['add_record'].setdefault('tmp_record', {})
        records = records.append(tmp_record)
        self.save_records(chat=chat, records=records)
        params['add_record'] = {}
        self.PO.save_params(params, chat.id)
        self.BO.send_message(chat_id=chat.id,text='Успешно добавлено')
#
