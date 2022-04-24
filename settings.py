# -*- coding: utf-8 -*-
#!/usr/bin/env  python3

GROUP_ID = '212456808'
TOKEN = ''

INTENTS = [
    {
        'name': 'Дата проведения',
        'tokens': ('когда', 'сколько', 'скольки', 'дату', 'дата', 'скольки', 'спрашиваю', ),
        'scenario': None,
        'answer': 'Конференция проводится 3 июля, регистрация начнется в 10 утра'
    },
    {
        'name': 'Место проведения',
        'tokens': ('где', 'место', 'локация', 'адрес', 'метро', ),
        'scenario': None,
        'answer': 'Конференция пройдет в павельене 18г в Экспоцентре'
    },
    {
        'name': 'Регистрация',
        'tokens': ('регист', 'добав', 'давай',),
        'scenario': 'registration',
        'answer': None
    },
    {
        'name': ' Приветствие',
        'tokens': ('прив', 'добрый', 'хай', 'здравств', 'здров',  ),
        'scenario': None,
        'answer': 'Здравствуйте, чем я могу вам помочь?'
    },
    {
        'name': 'Благодарность',
        'tokens': ('спасиб', 'благодар', 'спс'),
        'scenario': None,
        'answer': 'Всегда пожалуйста, приходите ещё!'
    },
    {
        'name': 'Прощание',
        'tokens': ('досвид', 'всего', 'пока', 'порщай', 'лихом'),
        'scenario': None,
        'answer': 'Всегда пожалуйста, приходите ещё!'
    },
]
SCENARIOS = {
    'registration': {
        "first_step": 'step1',
        "steps": {
            'step1': {
                'text': 'Чтобы зарегистрироваться, введите ваше имя. Оно будет написано на бэйдике.',
                'failure_text': 'Имя должно состоять из 3-40 букв и дефиса. Попробуйте еще раз.',
                'handler': 'handler_name',
                'next_step': 'step2'
            },
            'step2': {
                'text': 'Введите email. Мы отправим на него все данные.',
                'failure_text': 'Во введенном адресе ошибка. Попробуйте ещё раз',
                'handler': 'handler_email',
                'next_step': 'step3'
            },
            'step3': {
                'text': 'Спасибо за регистрацию, {name}! Мы отправили на {email} билет, распечатайте его.',
                'failure_text': None,
                'handler': None,
                'next_step': None
            }
        }
    }

}
DEFAULT_ANSWER = 'Не знаю, как на это ответить. Могу сказать когда и где пройдет конференция, а также ' \
                 'зарегистрировать вас. Просто спросите. '

DB_CONFIG = dict(
    provider='postgres',
    user='postgres',
    host='localhost',
    database='vk_chat_bot'
)