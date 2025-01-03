import json
from os.path import join, isfile
import time

class ParamsOperations(object):
    """Class to store user related technical params"""
    def __init__(self, config):
        self.def_params = {'last_time_message_sent':0,
                           'record_to_add':{}}
        self.config = config

    def load_params(self, chat_id):
        '''Load json with local parameters for the chat'''
        path = self.config.path
        param_dir = path['param_dir']
        param_name = f"{chat_id}.json"
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

    def save_params(self, chat_id, params):
        '''Save json with local parameters for the chat'''
        if not isinstance(params, dict):
            error_text = f'''Params object has type {type(params)} instead of {type(dict)}
    Debug info:
    \tChat id: {chat_id}'''
    # \tChat name: {chat_id} # Will be added in future
            raise TypeError(error_text)
        param_dir = self.config.path['param_dir']
        param_name = f"{chat_id}.json"
        param_path = join(param_dir, param_name)
        with open(param_path, 'w') as fp:
            params = json.dump(params, fp)