from pony.orm import Database, Required, Json
# peewee - хорошая ORM
# вариант  pony + sqlite, postgreSQL не получилось
from settings import DB_CONFIG_SL3

db = Database()
db.bind(**DB_CONFIG_SL3)


class UserState(db.Entity):
    '''Состояние пользователя в нутри сценария'''
    user_id = Required(str, unique=True)
    scenario_name = Required(str)
    step_name = Required(str)
    context = Required(Json)

class Registration(db.Entity):
    '''Заявка на регистрацию'''
    name = Required(str)
    email = Required(str)


db.generate_mapping(create_tables=True)