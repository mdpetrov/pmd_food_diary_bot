import time
from pmd_food_diary_bot.params_operation import ParamsOperations
from telebot.util import quick_markup


class BotOperations(object):
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config
        self.PO = ParamsOperations(config)

    def send_message(self, chat, text, sleep=0.5, **kwargs):
        """ Send a message with certain delay """
        chat_id = chat.id
        bot = self.bot
        PO = self.PO
        params = PO.load_params(chat=chat)
        interval = time.time() - params['last_time_message_sent']
        if interval < sleep:
            time.sleep(sleep - interval)
        message = bot.send_message(chat_id, text, **kwargs)
        params['last_time_message_sent'] = time.time()
        PO.save_params(chat=chat, params=params)
        return message

    def edit_message(self, chat_id, message_id, text, **kwargs):
        return self.bot.edit_message_text(text=text, chat_id=chat_id, message_id=message_id, **kwargs)

    def delete_message(self, chat_id: int | str, message_id: int, timeout: int | None = None):
        return self.bot.delete_message(chat_id=chat_id, message_id=message_id, timeout=timeout)

    def clear_step_handler(self, message):
        self.bot.clear_step_handler(message)

    def clear_step_handler_by_chat_id(self, chat_id: int | str):
        self.bot.clear_step_handler_by_chat_id(chat_id=chat_id)

    def register_next_step_handler(self, message, callback, *args, **kwargs):
        self.bot.register_next_step_handler(message, callback, *args, **kwargs)

    def register_next_step_handler_by_chat_id(self, chat_id, callback, *args, **kwargs):
        self.bot.register_next_step_handler_by_chat_id(chat_id=chat_id, callback=callback, *args, **kwargs)

    @staticmethod
    def quick_markup(options: list, callback: list, row_width=2):
        if len(options) != len(callback):
            raise AttributeError('Length of options and callback must be equal')
        l = len(options)
        result = {}
        for i in range(l):
            result[options[i]] = {'callback_data': callback[i]}
        markup = quick_markup(result, row_width=row_width)
        return markup
