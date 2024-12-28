from os.path import join, isfile
import time
import json

# from pmd_food_diary_bot.params_operation import ParamsOperations
from pmd_food_diary_bot.bot_operation import BotOperations

class RecordsOperations(object):
    def __init__(self, bot, config):
        self.config = config
        self.def_records = []
        self.BO = BotOperations(bot=bot, config=config)

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
        record_dir = self.config.path['data_dir']
        record_name = f"{chat.id}_{chat.username}.json"
        record_path = join(record_dir, record_name)
        with open(record_path, 'w') as fp:
            json.dump(records, fp)
    def add_record(self, chat, record):
        records = self.load_records(chat)
        records.append(record)
        self.save_records(chat=chat, records=records)
    def initialize_add_record(self, message):
        chat = message.chat
        BO = self.BO
        record_fields_input = self.config.record_fields_input
        fields_readable = list(record_fields_input.values())
        fields_readable_s = '; '.join(fields_readable)
        message_text = f'''Введите следующие поля, разделённые точкой с запятой:
        {fields_readable_s}'''
        BO.send_message(chat_id=chat.id, text=message_text)
        BO.clear_step_handler(message)
        BO.register_next_step_handler(message, self.compose_record)
    def compose_record(self, message):
        chat = message.chat
        BO = self.BO
        record_fields = list(self.config.record_fields_input.keys())

        values_to_add = [x.strip() for x in message.split(';')]
        record = dict(zip(record_fields, values_to_add))
        self.add_record(chat=chat, record=record)
        message_text = 'Запись добавлена!'
        BO.send_message(chat_id=chat.id, text=message_text)
        BO.clear_step_handler(message)

# class AddRecord(object):
#     def __init__(self, config):
#         self.config = config
#         self.PO = ParamsOperations(config)
#         self.RO = RecordsOperations(config)
#     def generate_message(self, step):
#         if step == 1:
#             message_text = f'''Введите дату (ГГГГ ММ ДД Ч:М):'''
#         elif step == 2:
#             message_text = 'Введите запись:'
#         elif step == 3:
#             message_text = 'Вы собиратесь добавить следующую запись:'
#         else:
#             message_text = ''
#         return message_text
#     def add_record(self, chat, step, value):
#         PO = self.PO
#         RO = self.RO
#         config = self.config
#         params = PO.load_params(config, chat_id=chat.id)
#         record_to_add = params['record_to_add']
#         if step == 1:
#             record_to_add.clear()
#             record_to_add['date'] = value
#         elif step == 2:
#             record_to_add['record'] = value
#         elif step == 3:
#             pass
#

