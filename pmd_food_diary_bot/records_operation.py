import os
import time
import pandas as pd

class RecordsOperations(object):
    def __init__(self, config):
        self.config = config

    def load_records(self, chat_id):
        '''Load user records'''
        path = self.config.path
        param_dir = path['data_dir']
        param_name = f"{chat_id}.csv"
        param_path = os.path.join(param_dir, param_name)
        if os.path.isfile(param_path):
            with open(param_path, 'r') as fp:
                records = pd.read_csv(fp)
        else:
            records = None
        return records

    def save_records(self, chat_id, records):
        '''Save user records'''
        param_dir = self.config.path['data_dir']
        param_name = f"{chat_id}.csv"
        param_path = os.path.join(param_dir, param_name)
        with open(param_path, 'w') as fp:
            records.to_csv(fp, index=False)