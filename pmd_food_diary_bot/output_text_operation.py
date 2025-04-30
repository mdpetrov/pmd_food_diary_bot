# from os.path import join, isfile
# import time
# import json
# from dateutil.relativedelta import relativedelta
# from datetime import datetime
# import pytz

from pmd_food_diary_bot.params_operation import ParamsOperations
# from pmd_food_diary_bot.bot_operation import BotOperations

class OutputTextOperation(object):
    def __init__(self, config):
        self.config = config
        self.PO = ParamsOperations(config=config)
    def get_record_steps_name(self, chat):
        params = self.PO.load_params(chat)
        locale = params['user_settings']['locale']
        record_steps_name_map = self.config.add_record_steps_translation[locale]
        return record_steps_name_map
    def get_user_settings_name(self, chat):
        params = self.PO.load_params(chat)
        locale = params['user_settings']['locale']
        user_settings_name_map = self.config.user_settings_translation[locale]
        return user_settings_name_map