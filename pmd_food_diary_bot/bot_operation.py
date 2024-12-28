import time
from pmd_food_diary_bot.params_operation import ParamsOperations

class BotOperations(object):
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config
        self.PO = ParamsOperations(config)
    def send_message(self, chat_id, text, sleep=0.5, **kwargs):
        ''' Send a message with certain delay '''
        bot = self.bot
        PO = self.PO
        params = PO.load_params(chat_id=chat_id)
        interval = time.time() - params['last_time_message_sent']
        if (interval < sleep):
            time.sleep(sleep - interval)
        message = bot.send_message(chat_id, text, **kwargs)
        params['last_time_message_sent'] = time.time()
        PO.save_params(chat_id=chat_id, params=params)
        return message
    def clear_step_handler(self, message):
        self.bot.clear_step_handler(message)
    def register_next_step_handler(self, message, callback, *args, **kwargs):
        self.bot.register_next_step_handler(message, callback, *args, **kwargs)
