import json
from os.path import join, isfile
import time

from pmd_food_diary_bot.output_text_operation import OutputTextOperation


class ParamsOperations(object):
    """Class to store user related technical params"""

    def __init__(self, config):
        self.def_params = {'last_time_message_sent': 0,
                           'add_record': {},
                           'user_settings': {
                               'timezone': 'Europe/Moscow',
                               'locale': 'ru',
                               'notification': {}}}
        self.config = config
        self.OTO = OutputTextOperation(config=config)

    def load_params(self, chat):
        """Load json with local parameters for the chat"""
        chat_id = chat.id
        chat_username = chat.username
        path = self.config.path
        param_dir = path['param_dir']
        param_name = f"{chat_id}_{chat_username}.json"
        param_path = join(param_dir, param_name)
        if isfile(param_path):
            with open(param_path, 'r') as fp:
                params = json.load(fp)
            if not isinstance(params, dict):
                error_text = f'''Loaded params object has type {type(params)} instead of {type(dict)}
    Debug info:
    \tChat id: {chat_id}'''
    # \tChat name: {chat_id} # Will be added in future
                raise TypeError(error_text)
        else:
            params = self.def_params
        return params

    def save_params(self, chat, params):
        """Save json with local parameters for the chat"""
        chat_id = chat.id
        chat_username = chat.username
        if not isinstance(params, dict):
            error_text = f'''Params object has type {type(params)} instead of {type(dict)}
    Debug info:
    \tChat id: {chat_id}'''
    # \tChat name: {chat_id} # Will be added in future
            raise TypeError(error_text)
        param_dir = self.config.path['param_dir']
        param_name = f"{chat_id}_{chat_username}.json"
        param_path = join(param_dir, param_name)
        with open(param_path, 'w') as fp:
            json.dump(params, fp)

    def check_param_keys(self, chat, add_only=True):
        params = self.load_params(chat)
        def_params = self.def_params

        for key in def_params.keys():
            if add_only:
                if not key in params.keys():
                    params[key] = def_params[key]
            else:
                params[key] = def_params[key]
        self.save_params(chat, params)


class UserSettings(ParamsOperations):
    """Class for user to change some settings"""

    def show_settings(self, chat):
        params = self.load_params(chat)
        settins_locale_map = self.OTO.get_user_settings_name(chat=chat)
        settings = params['user_settings']

        text = ""
        for setting, value in settings.items():
            text += f"{settins_locale_mapх[setting]} : {value}\n"

        return text