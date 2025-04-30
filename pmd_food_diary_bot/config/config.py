path = {"token": "./.secret/token/.token",
        "log_dir": "./.secret/log",
        "record_dir": "./.secret/record",
        "param_dir": "./.secret/param"}
record_fields_input = {'date': 'Дата (ГГГГ-ММ-ДД Ч:М)',
                       'record': 'Запись'}

add_record_steps = ['datetime', 'user_record', 'tags']
add_record_steps_translation = {'ru': {'datetime': 'Время',
                                       'user_record': 'Запись',
                                       'tags': 'Теги'}}
add_record_options = {'datetime': {0: 'Прямо сейчас',
                                   10: '10 минут назад',
                                   30: '30 минут назад',
                                   60: '1 час назад',
                                   120: '2 часа назад',
                                   180: '3 часа назад',
                                   240: '4 часа назад', }
                      }
user_settings_translation = {'ru': {'locale': 'Язык',
                                    'timezone': 'Часовой пояс',
                                    'notification': 'Уведомления'}
                             }
