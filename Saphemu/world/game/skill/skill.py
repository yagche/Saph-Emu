from peewee import Model, IntegerField, ForeignKeyField

from saphemu.world.game.character.character_data import CharacterData
from saphemu.db.database import DB


class Skill(Model):

    character      = ForeignKeyField(CharacterData)
    ident          = IntegerField()
    level          = IntegerField(default = 0)
    stat_level     = IntegerField(default = 0)

    class Meta(object):
        database = DB
