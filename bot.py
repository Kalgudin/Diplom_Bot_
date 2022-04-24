# -*- coding: utf-8 -*-
#!/usr/bin/env  python3
import handlers
from models import UserState

try:
    import settings
except ImportError:
    exit('Do cp settings.py.default settings.py and set token!')

# import vk_api
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
# class UserState:
#     '''Состояние пользователя в нутри сценария'''
#     def __init__(self, scenario_name, step_name, context=None):
#         self.scenario_name = scenario_name
#         self.step_name = step_name
#         self.context = context or {}

class Bot:
    def __init__(self, group_id, token):
        self.group_id = group_id
        self.token = token
        self.vk = VkApi(token=token)
        self.long_poller = VkBotLongPoll(vk=self.vk, group_id=self.group_id)
        self.api = self.vk.get_api()
        self.message_text = None
        self.user_states = dict()

    def run(self):
        for event in self.long_poller.listen():
            # print(f'тестим ... {event}')
            try:
                self.on_event(event=event)
            except Exception as exc:
                print(f'exception - {exc}')
                log.exception(f'event processing error - {exc}')

    def on_event(self, event):
        if event.type != VkBotEventType.MESSAGE_NEW:
            log.info(f'I cant answer to this message - {event.type}') # raise ValueError('WHAT a FACK???????????????')
            return
        else:
            user_id = event.object['message']['peer_id']
            text = event.object['message']['text']
            log.info(f'text - {text}')
            log.info(f'user_id - {user_id}')
            if user_id in self.user_states:
                text_to_send = self.continue_scenario(user_id=user_id, text=text)
                log.info(f'continue scenario - text_to_send == {text_to_send}') # continue scenario
            else:
                log.info(f'serch intent  for  user_id - {user_id}') # serch intent
                for intent in settings.INTENTS:
                    if any(token in text.lower() for token in intent['tokens']):
                        if intent['answer']:
                            text_to_send = intent['answer']
                        else:
                            text_to_send = self.start_scenario(user_id, intent['scenario'])
                        break
                else:
                    text_to_send = settings.DEFAULT_ANSWER
                    log.info(f'settings.DEFAULT_ANSWER - {text_to_send}')
            self.message_text = text_to_send
            self.reply_message(user_id=user_id)

    def start_scenario(self, user_id, scenario_name):
        scenario = settings.SCENARIOS[scenario_name]
        first_step = scenario['first_step']
        step = scenario['steps'][first_step]
        text_to_send = step['text']
        self.user_states[user_id] = UserState(scenario_name=scenario_name, step_name=first_step, context={})
        return text_to_send

    def continue_scenario(self, user_id, text):
        state = self.user_states[user_id]
        steps = settings.SCENARIOS[state.scenario_name]['steps']
        step = steps[state.step_name]
        handler = getattr(handlers, step['handler'])
        if handler(text=text, context=state.context):
            log.info(f"next step  == {steps[step['next_step']]}") # next step
            log.info(f"text_to_send  == {steps[step['next_step']]['text']}") # next step
            next_step = steps[step['next_step']]
            text_to_send = next_step['text'].format(**state.context)
            if next_step['next_step']:
                # switch to next step
                state.step_name = step['next_step']
            else:
                # finish scenario
                self.user_states.pop(user_id)
                log.info('Спасибо за регистрацию, {name}! Мы отправили на {email}'.format(**state.context))
        else:
            # retry current step
            text_to_send = step['failure_text'].format(**state.context) # необязательно .format(**state.context)
        return text_to_send

    def reply_message(self, user_id):
        log.info('send answer from bot')

        # МОЙ ВАРИАНТ ОТВЕТА
        # message = f'Все говорят "{self.message_text}", а ты купи слона!'
        message = self.message_text
        self.api.messages.send(message=message,
                               random_id=get_random_id(),
                               peer_id=user_id
                               )
        self.message_text = None


if __name__ == '__main__':
    try:
        configure_logging()
        bot = Bot(group_id=GROUP_ID, token=TOKEN)
        bot.run()
    except Exception as exc:
        print(exc)