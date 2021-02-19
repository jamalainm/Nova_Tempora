"""
Room

Rooms are simple containers that has no location of their own.

"""

# from evennia import DefaultRoom
from evennia.contrib.ingame_python.typeclasses import EventRoom
from utils.latin.latin_declension import DeclineNoun
from utils.latin.populate_forms import populate_forms
from typeclasses.latin_noun import LatinNoun

# Commenting out and changing inherit to EventRoom for ingame python
# class Room(DefaultRoom):
#
class Room(EventRoom,LatinNoun):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See examples/object.py for a list of
    properties and methods available on all Objects.
    """

    def at_object_creation(self):

        # add all of the case endings to attributes

        nom = self.db.formae['nom_sg'][0]
        gen = self.db.formae['gen_sg'][0]
        sexus = self.db.sexus

        populate_forms(self, nom, gen, sexus)

        self.db.lang = 'latin'
