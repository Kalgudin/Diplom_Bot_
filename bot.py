# -*- coding: utf-8 -*-
#!/usr/bin/env  python3

from _token import TOKEN
from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id

GROUP_ID = '212456808'


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

    def on_event(self, event):
        if event.type == VkBotEventType.MESSAGE_NEW:
            self.message_text = event.message.text
            self.reply_message(event)

    def reply_message(self, event):
        message = f'Все говорят "{self.message_text}", а ты купи слона!'

        self.api.messages.send(message=message,
                               random_id=get_random_id(),
                               peer_id=event.object.message['from_id']
                               )
        self.message_text = None


if __name__ == '__main__':
    try:
        bot = Bot(group_id=GROUP_ID, token=TOKEN)
        bot.run()
    except Exception as exc:
        print(exc)