import sqlite3
import peewee
# peewee - хорошая ORM

from settings import DB_CONFIG_SL3

#
# conn = sqlite3.connect('bot.sl3') # создаем базу данных
# conn.text_factory = bytes  # указываем тип получаемых данных
# cursor = conn.cursor()  # Создадим курсор - специальный объект, с помощью которого мы сможем делать запросы к БД на языке запросов


db = peewee.SqliteDatabase("vk_chat_bot.sl3")
# db.bind(**DB_CONFIG_SL3)


class BaseTable(peewee.Model):
    # В подклассе Meta указываем подключение к той или иной базе данных
    class Meta:
        database = db

class UserState(BaseTable):
    '''Состояние пользователя в нутри сценария'''
    user_id = peewee.CharField(unique=True)
    scenario_name = peewee.CharField()
    step_name = peewee.CharField()
    context = peewee.TextField()

UserState.create_tables()


