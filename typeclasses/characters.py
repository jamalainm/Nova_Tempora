# files mygame/typeclasses/characters.py

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

class Character(Rēs,DefaultCharacter):
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

        # set hands as empty

        self.db.right_hand = False
        self.db.left_hand = False

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
# Added the following to typeclasses.rēs.Rēs to consolidate
#
#
#    #making a new get_display_name that is aware of case and not
#    # dependent on the key of the object
#    def get_display_name(self, looker, **kwargs):
#        if not self.db.formae:
#            if self.locks.check_lockstring(looker, "perm(Builder)"):
#                return "{}(#{})".format(self.key, self.id)
#            return self.key
#        else:
#            if self.locks.check_lockstring(looker, "perm(Builder)"):
#                return "{}(#{})".format(self.key, self.id)
#            return self.key
#
# Adding the following move function to typeclasses.rēs.Rēs in order to consolodite
#
#    def announce_move_from(self, destination, msg=None, mapping=None):
#        """
#        Called if the move is to be announced. This is
#        called while we are still standing in the old
#        location.
#
#        Args:
#            destination (Object): The place we are going to.
#            msg (str, optional): a replacement message.
#            mapping (dict, optional): additional mapping objects.
#
#        You can override this method and call its parent with a
#        message to simply change the default message.  In the string,
#        you can use the following as mappings (between braces):
#            object: the object which is moving.
#            exit: the exit from which the object is moving (if found).
#            origin: the location of the object before the move.
#            destination: the location of the object after moving.
#
#        """
#        if not self.location:
#            return
#        if msg:
#            string = msg
#        else:
#            string = "{object} {exit} discēdit."
#
#        # Get the exit from location to destination
#        location = self.location
#        exits = [
#            o for o in location.contents if o.location is location and o.destination is destination
#        ]
#        if not mapping:
#            mapping = {}
#
#        mapping.update(
#                {
#                    "object": self,
#                    "exit": exits[0] if exits else "somewhere",
#                    "origin": location or "nowhere",
#                    "destination": destination or "nowhere",
#                    }
#                )
#
#        location.msg_contents(string, exclude=(self,), mapping=mapping)
#
#    def announce_move_to(self, source_location, msg=None, mapping=None):
#        """
#        Called after the move if the move was not quiet. At this point
#        we are standing in the new location.
#
#        Args:
#            source_location (Object): The place we came from
#            msg (str, optional): the replacement message if location.
#            mapping (dict, optional): additional mapping objects.
#
#        You can override this method and call its parent with a
#        message to simply change the default message.  In the string,
#        you can use the following as mappings (between braces):
#            object: the object which is moving.
#            exit: the exit from which the object is moving (if found).
#            origin: the location of the object before the move.
#            destination: the location of the object after moving.
#
#        """
#
#        if not source_location and self.location.has_account:
#            # This was created from nowhere and added to an account's
#            # inventory; it's probably the result of a create command.
#            string = "You now have %s in your possession." % self.get_display_name(self.location)
#            self.location.msg(string)
#            return
#
#        if source_location:
#            if msg:
#                string = msg
#            else:
#                string = "{object} ad {ad_locum} ab {ab_loco} vēnit."
#        else:
#            string = "{object} ad {ad_locum} vēnit."
#
#        origin = source_location
#        destination = self.location
#        exits = []
#        if origin:
#            exits = [
#                o
#                for o in destination.contents
#                if o.location is destination and o.destination is origin
#            ]
#
#        if not mapping:
#            mapping = {}
#
#        # Implementing some Latin awareness
#        if source_location:
#            if source_location.db.formae:
#                ab_loco = source_location.db.formae['abl_sg'][0]
#            else:
#                ab_loco = source_location
#
#        if self.location.db.formae:
#            ad_locum = self.location.db.formae['acc_sg'][0]
#        else:
#            ad_locum = self.location
#
#        mapping.update(
#            {
#                "object": self,
#                "exit": exits[0] if exits else "somewhere",
#                "origin": origin or "nowhere",
#                "destination": destination or "nowhere",
#                "ab_loco": ab_loco,
#                "ad_locum": ad_locum,
#            }
#        )
#
#        destination.msg_contents(string, exclude=(self,), mapping=mapping)


# Trying to move this object hook into typeclasses.rēs.Rēs
#
#    def return_appearance(self, looker, **kwargs):
#        """
#        # Lightly editing to change "You see" to "Ecce"
#        # and 'Exits' to 'Ad hos locos ire potes:'
#        This formats a description. It is the hook a 'look' command
#        should call.
#
#        Args:
#            looker (Object): Object doing the looking.
#            **kwargs (dict): Arbitrary, optional arguments for users
#                overriding the call (unused by default).
#        """
#
#
#        if not looker:
#            return ""
#        # get and identify all objects
#        # JI (12/7/19) Commenting out the following which probably shouldn't apply to characters.
##        visible = (con for con in self.contents if con != looker and con.access(looker, "view"))
##        exits, users, things = [], [], defaultdict(list)
##        for con in visible:
##            key = con.get_display_name(looker)
##            if con.destination:
##                exits.append(key)
##            elif con.has_account:
##                users.append("|c%s|n" % key)
##            else:
##                # things can be pluralized
##                things[key].append(con)
#        # get description, build string
#        string = "|c%s|n\n" % self.get_display_name(looker)
#        desc = self.db.desc
#        # JI (12/7/9) Adding the following lines to accommodate clothing
#        worn_string_list = []
#        clothes_list = latin_clothing.get_worn_clothes(self, exclude_covered=True)
#        # Append worn, uncovered clothing to the description
#        for garment in clothes_list:
#            # if 'worn' is True, just append the name
#            if garment.db.geritur is True:
#                if garment.db.ardēns:
#                    worn_string_list.append(f"|yard{'ēns' if garment.db.sexus == 'neutrm' else 'entem'}|n {garment.db.acc_sg[0]}")
#                # JI (12/7/19) append the accusative name to the description,
#                # since these will be direct objects
#                else:
#                    worn_string_list.append(garment.db.formae['acc_sg'][0])
#            # Otherwise, append the name and the string value of 'worn'
#            elif garment.db.geritur:
#                worn_string_list.append("%s %s" % (garment.name, garment.db.geritur))
#        # get held clothes
#        possessions = self.contents
#        held_list = []
#        for possession in possessions:
#            if possession.db.tenētur:
#                if possession.db.ardēns:
#                    held_list.append(f"|y(ard{'ēns' if possession.db.sexus == 'neutrum' else 'entem'})|n {possession.db.formae['acc_sg'][0]}")
#                else:
#                    held_list.append(possession.db.formae['acc_sg'][0])
#        if desc:
#            string += "%s" % desc
#        # Append held items.
#        if held_list:
#            string += "|/|/%s tenet: %s." % (self, LatinNoun.list_to_string(held_list))
#        # Append worn clothes.
#        if worn_string_list:
#            string += "|/|/%s gerit: %s." % (self, LatinNoun.list_to_string(worn_string_list))
#        else:
##            string += "|/|/%s nūd%s est!" % (self, 'a' if self.db.sexus == 'muliebre' else 'us' if self.db.sexus == 'māre' else 'um')
#            string += f"|/|/{self.key} nūd{us_a_um('nom_sg',self.db.sexus)} est!"
#        return string
#        # Thinking that the above, added for clothing, might need to only be in the
#        # character typeclass
    def at_after_move(self,source_location):
        super().at_after_move(source_location)

        if self.db.pv:
            prompt = f"\n|wVīta:{self.db.pv['nunc']}/{self.db.pv['max']})|n"

            self.msg(prompt)


