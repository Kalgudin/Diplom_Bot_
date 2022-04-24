from pony.orm import Database, Required, Json
# peewee - хорошая ORM

from settings import DB_CONFIG

db = Database()
db.bind(**DB_CONFIG)

class UserState(db.Entity):
    '''Состояние пользователя в нутри сценария'''
    scenario_name = Required(str)
    step_name = Required(str)
    context = Required(Json)
