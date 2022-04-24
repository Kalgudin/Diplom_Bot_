from copy import deepcopy
from unittest import TestCase, mock
from unittest.mock import patch, Mock

from pony.orm import db_session, rollback
from vk_api.bot_longpoll import VkBotMessageEvent

import settings
from bot import Bot

# запуск теста == python -m unittest
from generate_ticket import generate_ticket


def isolate_db(test_func):
    def wrapper(*args, **kwargs):
        with db_session:
            test_func(*args, **kwargs)
            rollback()
    return wrapper


class Test1(TestCase):
    RAW_EVENT = {
        'group_id': 212456808,
        'type': 'message_new',
        'event_id': 'f1e23ed6056f807da0a474f6a710299792acfcb6', 'v': '5.131',
        'object': {'message': {'date': 1649516237, 'from_id': 717559390, 'id': 162, 'out': 0,
                               'attachments': [], 'conversation_message_id': 153, 'fwd_messages': [],
                               'important': False, 'is_hidden': False, 'peer_id': 717559390,
                               'random_id': 0, 'text': 'Прод'},
                   'client_info': {'button_actions': ['text', 'vkpay', 'open_app', 'location',
                                                      'open_link', 'open_photo', 'callback',
                                                      'intent_subscribe', 'intent_unsubscribe'],
                                   'keyboard': True, 'inline_keyboard': True, 'carousel': True, 'lang_id': 0}}}

    def test_run(self):
        count = 5
        obj = {'a': 1}
        events = [obj] * count
        long_poller_mock = Mock(return_value=events)
        long_poller_listen_mock = Mock()
        long_poller_listen_mock.listen = long_poller_mock

        with patch('bot.VkApi'):
            with patch('bot.VkBotLongPoll', return_value=long_poller_listen_mock):
                bot = Bot('', '')
                bot.on_event = Mock()
                bot.send_image = Mock()
                bot.run()

                bot.on_event.assert_called()
                bot.on_event.assert_called_with(event=obj)
                assert bot.on_event.call_count == count

    INPUTS = [
        'Пgg',
        'А когда?',
        'Где пройдет',
        'Зарегистрируй',
        'Вениамин',
        'мой мейл rrr@kkkru', # False
        'rrr@kkk.ru',
    ]
    EXPECTED_OUTPUTS = [
        settings.DEFAULT_ANSWER,
        settings.INTENTS[0]['answer'],
        settings.INTENTS[1]['answer'],
        settings.SCENARIOS['registration']['steps']['step1']['text'],
        settings.SCENARIOS['registration']['steps']['step2']['text'],
        settings.SCENARIOS['registration']['steps']['step2']['failure_text'],
        settings.SCENARIOS['registration']['steps']['step3']['text'].format(name='Вениамин', email='rrr@kkk.ru')
    ]

    @isolate_db
    def test_run_ok(self):
        send_mock = Mock()
        api_mock = Mock()
        api_mock.messages.send = send_mock

        events = []
        for input_text in self.INPUTS:
            event = deepcopy(self.RAW_EVENT)
            event['object']['message']['text'] = input_text
            events.append(VkBotMessageEvent(event))

        long_poller_mock = Mock()
        long_poller_mock.listen = Mock(return_value=events)

        with patch('bot.VkBotLongPoll', return_value=long_poller_mock):
            bot = Bot('', '')
            bot.api = api_mock
            bot.send_image = Mock()
            bot.run()

        assert send_mock.call_count == len(self.INPUTS)
        real_outputs = []
        i = 0
        for call in send_mock.call_args_list:
            args, kwargs = call
            real_outputs.append(kwargs["message"])
        assert real_outputs == self.EXPECTED_OUTPUTS

    def test_generate_ticket(self):

        with open('files/ava.png', 'rb') as avatar_file:
            avatar_mock = Mock()
            avatar_mock.content = avatar_file.read()
        with patch('requests.get', return_value=avatar_mock):

            ticket_file = generate_ticket(name='Николай Калгудин', email='kalgudin@mail.ru')

        with open('files/expo_ticket.png', 'rb') as expected_file:
            expected_bytes = expected_file.read()
        assert ticket_file.read() == expected_bytes


