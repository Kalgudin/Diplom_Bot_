# -*- coding: utf-8 -*-
#!/usr/bin/env  python3

try:
    import settings
except ImportError:
    exit('Do cp settings.py.default settings.py and set token!')

from _token import TOKEN, GROUP_ID
from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
import logging

log = logging.getLogger('bot')


def configure_logging():
    log.setLevel(logging.DEBUG)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter('%(levelname)s %(message)s'))
    stream_handler.setLevel(logging.INFO)
    log.addHandler(stream_handler)
    datefmt = '%d/%m/%Y %H:%M'
    file_fandler = logging.FileHandler('bot.log')
    file_fandler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt=datefmt))
    file_fandler.setLevel(logging.DEBUG)
    log.addHandler(file_fandler)


class Bot:
    def __init__(self, group_id, token):
        self.group_id = group_id
        self.token = token
        self.vk = VkApi(token=token)
        self.long_poller = VkBotLongPoll(vk=self.vk, group_id=self.group_id)
        self.api = self.vk.get_api()
        self.message_text = None

    def run(self):
        for event in self.long_poller.listen():
            try:
                self.on_event(event=event)
            except Exception as exc:
                print(f'exception - {exc}')
                log.exception(f'event processing error - {exc}')

    def on_event(self, event):
        if event.type == VkBotEventType.MESSAGE_NEW:
            self.message_text = event.message.text
            self.reply_message(event)
        else:
            log.debug(f'I cant answer to this message - {event.type}')
            # raise ValueError('WHAT a FACK???????????????')

    def reply_message(self, event):
        log.info('send answer from bot')
        message = f'Все говорят "{self.message_text}", а ты купи слона!'

        self.api.messages.send(message=message,
                               random_id=get_random_id(),
                               peer_id=event.object.message['from_id']
                               )
        self.message_text = None


if __name__ == '__main__':
    try:
        configure_logging()
        bot = Bot(group_id=GROUP_ID, token=TOKEN)
        bot.run()
    except Exception as exc:
        print(exc)