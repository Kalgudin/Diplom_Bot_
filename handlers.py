# -*- coding: utf-8 -*-
#!/usr/bin/env  python3

'''Handler - функция, ктороая принимает на вход text и context (словарь), а возвращает Bool.
True, если шаг пройден, False если данные введены неверно'''
import re

from generate_ticket import generate_ticket

re_name = re.compile(r'^[\w\-\s]{3,40}$')
re_email = re.compile(r'\b(([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+)\b')

def handler_name(text, context):
    match = re.match(re_name, text)
    if match:
        context['name'] = match.group(0)
        return True
    else:
        return False

def handler_email(text, context):
    match = re.findall(re_email, text)
    if match:
        context['email'] = match[0][0]
        return True
    else:
        return False

def generate_ticket_handler(text, context):
    return generate_ticket(name=context['name'], email=context['email'])





