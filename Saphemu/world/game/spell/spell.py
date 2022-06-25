from peewee import Model, IntegerField, ForeignKeyField

from saphemu.world.game.character.character_data import CharacterData
from saphemu.db.database import DB


class Spell(Model):

    character      = ForeignKeyField(CharacterData)
    ident          = IntegerField()

    class Meta(object):
        database = DB
