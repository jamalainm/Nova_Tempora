# files mygame/typeclasses/characters.py

"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""
# from evennia import DefaultCharacter
from evennia import DefaultRoom, DefaultCharacter
from evennia.contrib.ingame_python.typeclasses import EventCharacter
from utils.latin.latin_declension import DeclineNoun
from typeclasses.latin_noun import LatinNoun
from utils.latin.adjective_agreement import us_a_um

# adding next line for new at_say for the EventCharcter class
from evennia.utils.utils import inherits_from

# added to assign handedness
import random

# Commenting out and replacing DefaultCharacter so we can use ingame python
#
# class Character(DefaultCharacter):
#
# Adding next couple of lines to accommodate clothing
from typeclasses import latin_clothing
# Adding so that some item is created with characters
from evennia.utils.create import create_object
# adding for combat
from world.tb_basic import TBBasicCharacter
from world.tb_basic import is_in_combat
import copy

class Character(EventCharacter,LatinNoun,TBBasicCharacter):
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
        if self.db.praenōmen:
            genitive = self.db.formae['gen_sg'][0]
            gender = self.db.sexus
                
            praenomen = DeclineNoun(self.db.praenōmen,genitive,gender)
            praenomen_forms = praenomen.make_paradigm()
            self.db.formae['dat_sg'] = [praenomen_forms[2][1]]
            self.db.formae['acc_sg'] = [praenomen_forms[3][1]]
            self.db.formae['abl_sg'] = [praenomen_forms[4][1]]
            self.db.formae['voc_sg'] = [praenomen_forms[5][1]]
            self.db.formae['nom_pl'] = [praenomen_forms[6][1]]
            self.db.formae['gen_pl'] = [praenomen_forms[7][1]]
            self.db.formae['dat_pl'] = [praenomen_forms[8][1]]
            self.db.formae['acc_pl'] = [praenomen_forms[9][1]]
            self.db.formae['abl_pl'] = [praenomen_forms[10][1]]
            self.db.formae['voc_pl'] = [praenomen_forms[11][1]]

            # Add the variant forms to aliases for easy interaction
            for form in praenomen_forms:
                self.aliases.add(form[1])

            nomen = self.db.nōmen
            n_genitive = self.db.formae['gen_sg'][1]

            word = DeclineNoun(nomen,n_genitive,gender)
            forms = word.make_paradigm()
            self.db.formae['dat_sg'].append(forms[2][1])
            self.db.formae['acc_sg'].append(forms[3][1])
            self.db.formae['abl_sg'].append(forms[4][1])
            self.db.formae['voc_sg'].append(forms[5][1])
            self.db.formae['nom_pl'].append(forms[6][1])
            self.db.formae['gen_pl'].append(forms[7][1])
            self.db.formae['dat_pl'].append(forms[8][1])
            self.db.formae['acc_pl'].append(forms[9][1])
            self.db.formae['abl_pl'].append(forms[10][1])
            self.db.formae['voc_pl'].append(forms[11][1])

            # Add the variant forms to aliases for easy interaction
            for form in forms:
                self.aliases.add(form[1])

        # add all of the case endings to attributes

        else:
            word = DeclineNoun(self.db.nom_sg[0],self.db.gen_sg[0],self.db.gender)
            forms = word.make_paradigm()
            all_forms = forms
            forms = forms[2:]
            self.db.formae['dat_sg'] = [forms[0][1]]
            self.db.formae['acc_sg'] = [forms[1][1]]
            self.db.formae['abl_sg'] = [forms[2][1]]
            self.db.formae['voc_sg'] = [forms[3][1]]
            self.db.formae['nom_pl'] = [forms[4][1]]
            self.db.formae['gen_pl'] = [forms[5][1]]
            self.db.formae['dat_pl'] = [forms[6][1]]
            self.db.formae['acc_pl'] = [forms[7][1]]
            self.db.formae['abl_pl'] = [forms[8][1]]
            self.db.formae['voc_pl'] = [forms[9][1]]

            # Add the variant forms to aliases for easy interaction
            for form in all_forms:
                self.aliases.add(form[1])

        self.db.lang = 'latin'

        # assign handedness

        if random.random() >= 0.9:
            self.db.handedness = 'left'
        else:
            self.db.handedness = 'right'

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
        max_vp = (10 + bonus) if (10 + bonus) > 0 else 1
        self.db.vp = {'max':max_vp,"current":max_vp}

        strength = self.db.ingenia['vīrēs']
        # 'toll' < 'tollere' = to lift; 'fer' < 'ferre' = 'to bear'
        # '[persōna] impedīta' = [character] encumbered; impedītissima = v. encumbered
        # 'ferēns' = 'carrying'
        self.db.toll_fer = {'tollere': round(strength * 30 * 0.45,1), 'impedīta': round(strength * 5 * 0.45,1), 'impedītissima': round(strength * 10 * 0.45,1),'ferēns':0,'max':round(strength * 15 * 0.45,1)}

        # Add the following so players start with clothes
        underwear = create_object(
                typeclass = "typeclasses.latin_clothing.Clothing",
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
                    typeclass = "typeclasses.latin_clothing.Clothing",
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
    def at_before_move(self, destination):
        """
        Called just before starting to move this object to
        destination.

        Args:
            destination (Object): The object we are moving to

        Returns:
            shouldmove (bool): If we should move or not.

        Notes:
            If this method returns False/None, the move is cancelled
            before it is even started.

        """
        # Keep the character from moving if at 0 HP or in combat.
        if is_in_combat(self):
            self.msg("Tibi pugnantī exīre nōn licet!")
            return False  # Returning false keeps the character from moving.
        if self.db.pv['nunc'] <= 0:
            self.msg(f"Tibi vict{us_a_um('dat_sg',self.db.sexus)} versārī nōn licet!")
            return False
        return True


    #making a new get_display_name that is aware of case and not
    # dependent on the key of the object
    def get_display_name(self, looker, **kwargs):
        if not self.db.formae:
            if self.locks.check_lockstring(looker, "perm(Builder)"):
                return "{}(#{})".format(self.key, self.id)
            return self.key
        else:
            if self.locks.check_lockstring(looker, "perm(Builder)"):
                return "{}(#{})".format(self.key, self.id)
            return self.key

    def announce_move_from(self, destination, msg=None, mapping=None):
        """
        Called if the move is to be announced. This is
        called while we are still standing in the old
        location.

        Args:
            destination (Object): The place we are going to.
            msg (str, optional): a replacement message.
            mapping (dict, optional): additional mapping objects.

        You can override this method and call its parent with a
        message to simply change the default message.  In the string,
        you can use the following as mappings (between braces):
            object: the object which is moving.
            exit: the exit from which the object is moving (if found).
            origin: the location of the object before the move.
            destination: the location of the object after moving.

        """
        if not self.location:
            return

        # changing {origin} to {exit}
        string = msg or "{object} {exit} discessit." #, heading for {destination}."

        # Get the exit from location to destination
        location = self.location
        exits = [
            o for o in location.contents if o.location is location and o.destination is destination
        ]
        mapping = mapping or {}
        mapping.update({"character": self})

        if exits:
            exits[0].callbacks.call(
                "msg_leave", self, exits[0], location, destination, string, mapping
            )
            string = exits[0].callbacks.get_variable("message")
            mapping = exits[0].callbacks.get_variable("mapping")

        # If there's no string, don't display anything
        # It can happen if the "message" variable in events is set to None
        if not string:
            return

        super().announce_move_from(destination, msg=string, mapping=mapping)

    def announce_move_to(self, source_location, msg=None, mapping=None):
        """
        Called after the move if the move was not quiet. At this point
        we are standing in the new location.

        Args:
            source_location (Object): The place we came from
            msg (str, optional): the replacement message if location.
            mapping (dict, optional): additional mapping objects.

        You can override this method and call its parent with a
        message to simply change the default message.  In the string,
        you can use the following as mappings (between braces):
            object: the object which is moving.
            exit: the exit from which the object is moving (if found).
            origin: the location of the object before the move.
            destination: the location of the object after moving.

        """

        if not source_location and self.location.has_account:
            # This was created from nowhere and added to an account's
            # inventory; it's probably the result of a create command.
            string = "In manibus tuīs %s nunc est." % self.get_display_name(self.location)
            self.location.msg(string)
            return

        # added the line below because
        origin = source_location
        # error checking
        self.location.msg(source_location)
        if source_location:
            origin = source_location.db.abl_sg[0]
            string = msg or f"{self.key} ab {source_location.db.formae['abl_sg'][0]} venit."
        else:
            string = f"{character} venit."

        # adding '.db.abl_sg' to end of 'source_location' and moving from line below
        # up into the 'if source_location' conditional
        destination = self.location
        exits = []
        mapping = mapping or {}
        mapping.update({"character": self})

        if origin:
            exits = [
                o
                for o in destination.contents
                if o.location is destination and o.destination is origin
            ]
            if exits:
                exits[0].callbacks.call(
                    "msg_arrive", self, exits[0], origin, destination, string, mapping
                )
                string = exits[0].callbacks.get_variable("message")
                mapping = exits[0].callbacks.get_variable("mapping")

        # If there's no string, don't display anything
        # It can happen if the "message" variable in events is set to None
        if not string:
            return

        super().announce_move_to(source_location, msg=string, mapping=mapping)

    # This older 'at_say' is VERY different from the new EventCharacter ones.
    # commenting out to see what changes. EventCharacter say implements this
    # before executing its own things. Will incorporate new at_say event below
    def at_say(
        self,
        message,
        msg_self=None,
        msg_location=None,
        receivers=None,
        msg_receivers=None,
        **kwargs,
    ):
        """
        Display the actual say (or whisper) of self.

        This hook should display the actual say/whisper of the object in its
        location.  It should both alert the object (self) and its
        location that some text is spoken.  The overriding of messages or
        `mapping` allows for simple customization of the hook without
        re-writing it completely.

        Args:
            message (str): The message to convey.
            msg_self (bool or str, optional): If boolean True, echo `message` to self. If a string,
                return that message. If False or unset, don't echo to self.
            msg_location (str, optional): The message to echo to self's location.
            receivers (Object or iterable, optional): An eventual receiver or receivers of the message
                (by default only used by whispers).
            msg_receivers(str): Specific message to pass to the receiver(s). This will parsed
                with the {receiver} placeholder replaced with the given receiver.
        Kwargs:
            whisper (bool): If this is a whisper rather than a say. Kwargs
                can be used by other verbal commands in a similar way.
            mapping (dict): Pass an additional mapping to the message.

        Notes:


            Messages can contain {} markers. These are substituted against the values
            passed in the `mapping` argument.

                msg_self = 'You say: "{speech}"'
                msg_location = '{object} says: "{speech}"'
                msg_receivers = '{object} whispers: "{speech}"'

            Supported markers by default:
                {self}: text to self-reference with (default 'You')
                {speech}: the text spoken/whispered by self.
                {object}: the object speaking.
                {receiver}: replaced with a single receiver only for strings meant for a specific
                    receiver (otherwise 'None').
                {all_receivers}: comma-separated list of all receivers,
                                 if more than one, otherwise same as receiver
                {location}: the location where object is.

        """
        # Need to split the statement into two parts if there's more than 1 word
        # Having a problem with displaying speaker's name; changing 'object' to 'self.key'
        sentence = message.strip()
        words = sentence.split(' ')
        speeches = [f'"{words[0]}" inquis.',f'{self.key} "{words[0]}" inquit.']
        first = words[0]
        if len(words) > 1:
            rest = ' '.join(words[1:])
            speeches = [f'"{words[0]}" inquis "{rest}"',f'{self.key} "{words[0]}" inquit "{rest}"']    
        # Added the above on 11/24
        msg_type = "say"
        if kwargs.get("whisper", False):
            # whisper mode
            msg_type = "whisper"
            msg_self = (
                '{self} whisper to {all_receivers}, "{speech}"' if msg_self is True else msg_self
            )
            msg_receivers = msg_receivers or '{object} whispers: "{speech}"'
            msg_location = None
        else:
            # altering the commented out line immediately below to the line below that
            # msg_self = '{self} say, "{speech}"' if msg_self is True else msg_self
            msg_self = speeches[0] if msg_self is True else msg_self
            # altering the immediately below commented line
            # msg_location = msg_location or '{object} says, "{speech}"'
            msg_location = msg_location or speeches[1]
            msg_receivers = msg_receivers or message

        custom_mapping = kwargs.get("mapping", {})
        receivers = make_iter(receivers) if receivers else None
        location = self.location

        if msg_self:
            self_mapping = {
                "self": "You",
                "object": self.get_display_name(self),
                "location": location.get_display_name(self) if location else None,
                "receiver": None,
                "all_receivers": ", ".join(recv.get_display_name(self) for recv in receivers)
                if receivers
                else None,
                "speech": message,
            }
            self_mapping.update(custom_mapping)
            self.msg(text=(msg_self.format(**self_mapping), {"type": msg_type}), from_obj=self)

        if receivers and msg_receivers:
            receiver_mapping = {
                "self": "You",
                "object": None,
                "location": None,
                "receiver": None,
                "all_receivers": None,
                "speech": message,
            }
            for receiver in make_iter(receivers):
                individual_mapping = {
                    "object": self.get_display_name(receiver),
                    "location": location.get_display_name(receiver),
                    "receiver": receiver.get_display_name(receiver),
                    "all_receivers": ", ".join(recv.get_display_name(recv) for recv in receivers)
                    if receivers
                    else None,
                }
                receiver_mapping.update(individual_mapping)
                receiver_mapping.update(custom_mapping)
                receiver.msg(
                    text=(msg_receivers.format(**receiver_mapping), {"type": msg_type}),
                    from_obj=self,
                )

        if self.location and msg_location:
            location_mapping = {
                "self": "You",
                "object": self,
                "location": location,
                "all_receivers": ", ".join(str(recv) for recv in receivers) if receivers else None,
                "receiver": None,
                "speech": message,
            }
            location_mapping.update(custom_mapping)
            exclude = []
            if msg_self:
                exclude.append(self)
            if receivers:
                exclude.extend(receivers)
            self.location.msg_contents(
                text=(msg_location, {"type": msg_type}),
                from_obj=self,
                exclude=exclude,
                mapping=location_mapping,
            )

        location = getattr(self, "location", None)
        location = (
            location
            if location and inherits_from(location, "evennia.objects.objects.DefaultRoom")
            else None
        )

        if location and not kwargs.get("whisper", False):
            location.callbacks.call("say", self, location, message, parameters=message)

            # Call the other characters' "say" event
            presents = [
                obj
                for obj in location.contents
                if obj is not self
                and inherits_from(obj, "evennia.objects.objects.DefaultCharacter")
            ]
            for present in presents:
                present.callbacks.call("say", self, present, message, parameters=message)

# adding the following to accommodate clothing

    def return_appearance(self, looker, **kwargs):
        """
        # Lightly editing to change "You see" to "Ecce"
        # and 'Exits' to 'Ad hos locos ire potes:'
        This formats a description. It is the hook a 'look' command
        should call.

        Args:
            looker (Object): Object doing the looking.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).
        """


        if not looker:
            return ""
        # get and identify all objects
        # JI (12/7/19) Commenting out the following which probably shouldn't apply to characters.
#        visible = (con for con in self.contents if con != looker and con.access(looker, "view"))
#        exits, users, things = [], [], defaultdict(list)
#        for con in visible:
#            key = con.get_display_name(looker)
#            if con.destination:
#                exits.append(key)
#            elif con.has_account:
#                users.append("|c%s|n" % key)
#            else:
#                # things can be pluralized
#                things[key].append(con)
        # get description, build string
        string = "|c%s|n\n" % self.get_display_name(looker)
        desc = self.db.desc
        # JI (12/7/9) Adding the following lines to accommodate clothing
        worn_string_list = []
        clothes_list = latin_clothing.get_worn_clothes(self, exclude_covered=True)
        # Append worn, uncovered clothing to the description
        for garment in clothes_list:
            # if 'worn' is True, just append the name
            if garment.db.geritur is True:
                if garment.db.ardēns:
                    worn_string_list.append(f"|yard{'ēns' if garment.db.sexus == 'neutrm' else 'entem'}|n {garment.db.acc_sg[0]}")
                # JI (12/7/19) append the accusative name to the description,
                # since these will be direct objects
                else:
                    worn_string_list.append(garment.db.formae['acc_sg'][0])
            # Otherwise, append the name and the string value of 'worn'
            elif garment.db.geritur:
                worn_string_list.append("%s %s" % (garment.name, garment.db.geritur))
        # get held clothes
        possessions = self.contents
        held_list = []
        for possession in possessions:
            if possession.db.tenētur:
                if possession.db.ardēns:
                    held_list.append(f"|y(ard{'ēns' if possession.db.sexus == 'neutrum' else 'entem'})|n {possession.db.formae['acc_sg'][0]}")
                else:
                    held_list.append(possession.db.formae['acc_sg'][0])
        if desc:
            string += "%s" % desc
        # Append held items.
        if held_list:
            string += "|/|/%s tenet: %s." % (self, LatinNoun.list_to_string(held_list))
        # Append worn clothes.
        if worn_string_list:
            string += "|/|/%s gerit: %s." % (self, LatinNoun.list_to_string(worn_string_list))
        else:
            string += "|/|/%s nud%s est!" % (self, 'a' if self.db.sexus == 'muliebre' else 'us')
        return string
        # Thinking that the above, added for clothing, might need to only be in the
        # character typeclass
    def at_after_move(self,source_location):
        super().at_after_move(source_location)

#        origin = source_location
#        destination = self.location
#        Room = DefaultRoom
#        if isinstance(origin, Room) and isinstance(destination, Room):
#            self.callbacks.call("move", self, origin, destination)
#            destination.callbacks.call("move", self, origin, destination)
#
#            # Call the 'greet' event of characters in the location
#            for present in [
#                o for o in destination.contents if isinstance(o, DefaultCharacter) and o is not self
#            ]:
#                present.callbacks.call("greet", present, self)
#
#        target = self.location
#        self.msg((self.at_look(target), {"type": "look"}), options=None)

        if self.db.hp:
            prompt = "\n|wVita: %i/%i) |n" % (self.db.pv['nunc'],self.db.pv['max'])

            self.msg(prompt)
