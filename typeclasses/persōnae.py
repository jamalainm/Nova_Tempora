# files mygame/typeclasses/persōnae.py

"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""
from evennia import DefaultCharacter
from typeclasses.rēs import Rēs
from utils.latin.adjective_agreement import us_a_um
from utils.latin.populate_forms import populate_forms
from utils.latin.latin_declension import DeclineNoun
from commands import default_cmdsets

# added to assign handedness
import random

# Adding next couple of lines to accommodate clothing
# from typeclasses import latin_clothing
# Adding so that some item is created with characters
from evennia.utils.create import create_object
# adding for combat
# from world.tb_basic import TBBasicCharacter
# from world.tb_basic import is_in_combat
import copy

class Persōna(Rēs,DefaultCharacter):
    """
    The Character defaults to reimplementing some of base Object's hook methods with the
    following functionality:

    at_basetype_setup - always assigns the DefaultCmdSet to this object type
                    (important!)sets locks so character cannot be picked up
                    and its commands only be called by itself, not anyone else.
                    (to change things, use at_object_creation() instead).
    at_after_move(source_location) - Launches the "look" command after every move.
    at_post_unpuppet(account) -  when Account disconnects from the Character, we
                    store the current location in the pre_logout_location Attribute and
                    move it to a None-location so the "unpuppeted" character
                    object does not need to stay on grid. Echoes "Account has disconnected"
                    to the room.
    at_pre_puppet - Just before Account re-connects, retrieves the character's
                    pre_logout_location Attribute and move it back on the grid.
    at_post_puppet - Echoes "AccountName has entered the game" to the room.

    """

    def at_object_creation(self):

        # Accommodoate and prefer the "Nomen"
        sexus = self.db.sexus

        # Decline object's primary name or praenomen
        nominative = self.db.formae['nom_sg'][0]
        genitive = self.db.formae['gen_sg'][0]
        populate_forms(self, nominative, genitive, sexus)

        # If there is a nōmen, decline it, also
        if self.db.nōmen:
            nom = self.db.formae['nom_sg'][1]
            gen = self.db.formae['gen_sg'][1]
            word = DeclineNoun(nom,gen,sexus)
            forms = word.make_paradigm()
            all_forms = forms
            forms = forms[2:]
            self.db.formae['dat_sg'].append(forms[0][1])
            self.db.formae['acc_sg'].append(forms[1][1])
            self.db.formae['abl_sg'].append(forms[2][1])
            self.db.formae['voc_sg'].append(forms[3][1])
            self.db.formae['nom_pl'].append(forms[4][1])
            self.db.formae['gen_pl'].append(forms[5][1])
            self.db.formae['dat_pl'].append(forms[6][1])
            self.db.formae['acc_pl'].append(forms[7][1])
            self.db.formae['abl_pl'].append(forms[8][1])
            self.db.formae['voc_pl'].append(forms[9][1])

            for form in all_forms:
                self.aliases.add(form[1])

                
        self.db.lang = 'latin'

        # assign handedness

        if random.random() >= 0.9:
            self.db.handedness = 'sinistrā'
        else:
            self.db.handedness = 'dextrā'

        # set 'manūs plēnae' and 'manūs vacuae'

        self.db.manibus_plēnīs = []
        self.db.manibus_vacuīs = ['dextrā','sinistrā']

        # Experiment with stats

        if not self.db.ingenia:
            statNums = [0,0,0,0,0,0]
            points = 27;
            while points > 0:
                index = random.randint(0,5)
                if statNums[index] < 5 and points > 0:
                    statNums[index] += 1
                    points -= 1
                elif statNums[index] in [5,6] and points > 1: 
                    statNums[index] += 1
                    points -= 2
            for index,value in enumerate(statNums):
                statNums[index] += 9

            self.db.ingenia = {'vīrēs':statNums[0],'pernīcitās':statNums[1],'valētūdō':statNums[2],'ratiō':statNums[3],'sapientia':statNums[4],'grātia':statNums[5]}

        # first calculate the bonus

        bonus = self.db.ingenia['valētūdō']
        bonus = (bonus - 11) if bonus % 2 else (bonus - 10)
        # 'pv' = 'puncta valētūdinis' (points of health)
        max_pv = (10 + bonus) if (10 + bonus) > 0 else 1
        self.db.pv = {'max':max_pv,"nunc":max_pv}

        strength = self.db.ingenia['vīrēs']
        # 'toll' < 'tollere' = to lift; 'fer' < 'ferre' = 'to bear'
        # '[persōna] impedīta' = [character] encumbered; impedītissima = v. encumbered
        # 'ferēns' = 'carrying'
        self.db.toll_fer = {'tollere': round(strength * 30 * 0.45,1), 'impedīta': round(strength * 5 * 0.45,1), 'impedītissima': round(strength * 10 * 0.45,1),'ferēns':0,'max':round(strength * 15 * 0.45,1)}

        # Add the following so players start with clothes
        underwear = create_object(
                typeclass = "typeclasses.vestīmenta.Vestīmentum",
                key = "subligāculum",
                location = self.dbref,
                attributes=[
                    ('sexus','neutrum'),
                    ('genus_vestīmentōrum','underpants'),
                    ('formae',{'nom_sg': ['subligāculum'], 'gen_sg': ['subligāculī']}),
                    ('geritur',True),
                    ('desc','Briefs'),
                    ('physical',{'material':'linen','rigid':False,'volume':0.5,'mass':0.45})
                    ]
                )

        if self.db.sexus == 'muliebre':
            bandeau = create_object(
                    typeclass = "typeclasses.vestīmenta.Vestīmentum",
                    key = "strophium",
                    location = self.dbref,
                    attributes=[
                        ('sexus','neutrum'),
                        ('genus_vestīmentōrum','undershirt'),
                        ('formae',{'nom_sg': ['strophium'], 'gen_sg': ['strophiī']}),
                        ('geritur',True),
                        ('desc','A bandeau'),
                        ('physical',{'material':'linen','rigid':False,'volume':0.5,'mass':0.45})
                        ]
                    )

        items_carried = self.contents
        mass_carried = 0
        for item in items_carried:
            mass_carried += item.db.physical['mass']
        self.db.toll_fer['ferēns'] = mass_carried

    # For turn-based battle
#    def at_before_move(self, destination):
#        """
#        Called just before starting to move this object to
#        destination.
#
#        Args:
#            destination (Object): The object we are moving to
#
#        Returns:
#            shouldmove (bool): If we should move or not.
#
#        Notes:
#            If this method returns False/None, the move is cancelled
#            before it is even started.
#
#        """
#        # Keep the character from moving if at 0 HP or in combat.
#        if is_in_combat(self):
#            self.msg("Tibi pugnantī exīre nōn licet!")
#            return False  # Returning false keeps the character from moving.
#        if self.db.pv['nunc'] <= 0:
#            self.msg(f"Tibi vict{us_a_um('dat_sg',self.db.sexus)} versārī nōn licet!")
#            return False
#        return True
#

    def basetype_setup(self):
        """
        Setup character-specific security.

        You should normally not need to overload this, but if you do,
        make sure to reproduce at least the two last commands in this
        method (unless you want to fundamentally change how a
        Character object works).

        """
        super().basetype_setup()
        self.locks.add(
            ";".join(["get:false()", "call:false()"])  # noone can pick up the character
        )  # no commands can be called on character from outside
        # add the default cmdset
        self.cmdset.add_default(default_cmdsets.PersōnaCmdSet, permanent=True)

    def at_after_move(self,source_location):
        super().at_after_move(source_location)

        if self.db.pv:
            prompt = f"\n|wVīta:{self.db.pv['nunc']}/{self.db.pv['max']})|n"

            self.msg(prompt)


