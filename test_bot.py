
from unittest import TestCase, mock
from unittest.mock import patch, Mock

from vk_api.bot_longpoll import VkBotMessageEvent

from bot import Bot


class Test1(TestCase):
    RAW_EVENT = {
        'group_id': 212456808,
        'type': 'message_new',
        'event_id': 'f1e23ed6056f807da0a474f6a710299792acfcb6','v': '5.131',
        'object': {'message': {'date': 1649516237, 'from_id': 717559390, 'id': 162, 'out': 0,
                               'attachments': [], 'conversation_message_id': 153, 'fwd_messages': [],
                               'important': False, 'is_hidden': False,'peer_id': 717559390,
                               'random_id': 0, 'text': 'Прод'},
                'client_info': {'button_actions': ['text', 'vkpay', 'open_app', 'location',
                                                       'open_link', 'open_photo', 'callback',
                                                       'intent_subscribe','intent_unsubscribe'],
                'keyboard': True, 'inline_keyboard': True, 'carousel': True, 'lang_id': 0}}}

    def test_run(self):
        count = 5
        obj =  {'a': 1}
        events = [obj] * count
        long_poller_mock = Mock(return_value=events)
        long_poller_listen_mock = Mock()
        long_poller_listen_mock.listen = long_poller_mock

        with patch('bot.VkApi'):
            with patch('bot.VkBotLongPoll', return_value=long_poller_listen_mock):
                bot = Bot('', '')
                bot.on_event = Mock()
                bot.run()

                bot.on_event.assert_called()
                bot.on_event.assert_called_with(event=obj)
                assert bot.on_event.call_count == count

    def test_on_event(self):
        event = VkBotMessageEvent(raw=self.RAW_EVENT)
        send_mock = Mock()

        with patch('bot.VkApi'):
            with patch('bot.VkBotLongPoll'):
                bot = Bot('', '')
                bot.api = Mock()
                bot.api.messages.send = send_mock

                bot.on_event(event=event)

        send_mock.assert_called_once_with(
            message=self.RAW_EVENT['object']['message']['text'],
            random_id=mock.ANY,
            peer_id=self.RAW_EVENT['object']['message']['peer_id']
        )

    def test_reply_message(self):
        pass
