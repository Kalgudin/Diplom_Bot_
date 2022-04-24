# -*- coding: utf-8 -*-
#!/usr/bin/env  python3
import requests
from pony.orm import db_session

import handlers
from models_pony import UserState, Registration

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

    @db_session
    def on_event(self, event):
        if event.type != VkBotEventType.MESSAGE_NEW:
            log.debug(f'I cant answer to this message - {event.type}') # raise ValueError('WHAT a FACK???????????????')
            return
        user_id = event.object['message']['peer_id']
        text = event.object['message']['text']
        log.info(f'message from user {user_id} == {text}')
        state = UserState.get(user_id=str(user_id))

        log.debug(f'text - {text}')
        log.debug(f'user_id - {user_id}')
        if state is not None:
            self.continue_scenario(text=text, state=state, user_id=user_id)
            log.info('continue scenario - text_to_send ==>') # continue scenario
        else:
            log.debug(f'serch intent  for  user_id - {user_id}') # serch intent
            for intent in settings.INTENTS:
                if any(token in text.lower() for token in intent['tokens']):
                    if intent['answer']:
                        self.send_text(text_to_send=intent['answer'], user_id=user_id)

                    else:
                        self.start_scenario(user_id, intent['scenario'], text)
                    break
            else:
                text_to_send = settings.DEFAULT_ANSWER
                log.debug(f'settings.DEFAULT_ANSWER - {text_to_send}')
                self.send_text(text_to_send=text_to_send, user_id=user_id)

    def send_text(self, text_to_send, user_id):
        log.info(f'send answer from bot == {text_to_send}')
        self.api.messages.send(message=text_to_send,
                               random_id=get_random_id(),
                               peer_id=user_id
                               )

    def send_image(self, image, user_id):
        upload_url = self.api.photos.getMessagesUploadServer()['upload_url']
        upload_data = requests.post(url=upload_url, files={'photo': ('image.png', image, 'image/png')}).json()
        image_data = self.api.photos.saveMessagesPhoto(**upload_data)
        owner_id = image_data[0]['owner_id']
        media_id = image_data[0]['id']
        attachment = f'photo{owner_id}_{media_id}'
        self.api.messages.send(attachment=attachment,
                               random_id=get_random_id(),
                               peer_id=user_id
                               )

    def send_step(self, step, user_id, text, context):
        if 'text' in step:
            self.send_text(step['text'].format(**context), user_id)
        if 'image' in step:
            handler = getattr(handlers, step['image'])
            image = handler(text, context)
            self.send_image(image, user_id)

    def start_scenario(self, user_id, scenario_name, text):
        scenario = settings.SCENARIOS[scenario_name]
        first_step = scenario['first_step']
        step = scenario['steps'][first_step]
        self.send_step(step, user_id, text, context={})
        UserState(user_id=str(user_id), scenario_name=scenario_name, step_name=first_step, context={})

    def continue_scenario(self, text, state, user_id):
        steps = settings.SCENARIOS[state.scenario_name]['steps']
        step = steps[state.step_name]
        handler = getattr(handlers, step['handler'])
        if handler(text=text, context=state.context):
            log.debug(f"next step  == {steps[step['next_step']]}") # next step
            log.debug(f"text_to_send  == {steps[step['next_step']]['text']}") # next step
            next_step = steps[step['next_step']]
            self.send_step(next_step, user_id, text, state.context)
            if next_step['next_step']:
                # switch to next step
                state.step_name = step['next_step']
            else:
                # finish scenario
                log.info('Спасибо за регистрацию, {name}! Мы отправили на {email}'.format(**state.context))
                Registration(name=state.context['name'], email=state.context['email'])
                state.delete()
        else:
            # retry current step
            self.send_text(step['failure_text'].format(**state.context), user_id)


if __name__ == '__main__':
    try:
        configure_logging()
        bot = Bot(group_id=GROUP_ID, token=TOKEN)
        bot.run()
    except Exception as exc:
        print(exc)
