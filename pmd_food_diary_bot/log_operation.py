from os.path import join
from datetime import datetime

class LogOperations(object):
    def __init__(self, config):
        self.config = config
    def write_log(self, chat, text):
        path = self.config.path
        with open(join(path['log_dir'], f'{chat.id}_{chat.username}.log'), mode='a') as log_con:
            log_con.write(f'{datetime.now()}: {text}\n')