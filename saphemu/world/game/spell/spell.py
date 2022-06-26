from peewee import ForeignKeyField, IntegerField, Model

from saphemu.db.database import DB
from saphemu.world.game.character.character_data import CharacterData


class Spell(Model):

    character = ForeignKeyField(CharacterData)
    ident = IntegerField()

    class Meta:
        database = DB
