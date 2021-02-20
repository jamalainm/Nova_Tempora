# file mygame/typeclasses/rēs.py

"""
Object

The Object is the "naked" base class for things in the game world.

Note that the default Character, Room and Exit does not inherit from
this Object, but from their respective default implementations in the
evennia library. If you want to use this class as a parent to change
the other types, you can do so by adding this as a multiple
inheritance.

"""
# from evennia import DefaultObject
# from evennia.contrib.ingame_python.typeclasses import EventObject
from utils.latin.latin_declension import DeclineNoun
from utils.latin.populate_forms import populate_forms
from utils.latin.list_to_string import list_to_string
from utils.latin.adjective_agreement import us_a_um
from typeclasses.inflected_noun import InflectedNoun

from evennia.utils import ansi
from collections import defaultdict

# Commenting out to try and avoid circular loading?
from typeclasses import latin_clothing

#class Rēs(EventObject,LatinNoun):
class Rēs(InflectedNoun):
    """
    This is the root typeclass object, implementing an in-game Evennia
    game object, such as having a location, being able to be
    manipulated or looked at, etc. If you create a new typeclass, it
    must always inherit from this object (or any of the other objects
    in this file, since they all actually inherit from BaseObject, as
    seen in src.object.objects).

    The BaseObject class implements several hooks tying into the game
    engine. By re-implementing these hooks you can control the
    system. You should never need to re-implement special Python
    methods, such as __init__ and especially never __getattribute__ and
    __setattr__ since these are used heavily by the typeclass system
    of Evennia and messing with them might well break things for you.


    * Base properties defined/available on all Objects

     key (string) - name of object
     name (string)- same as key
     dbref (int, read-only) - unique #id-number. Also "id" can be used.
     date_created (string) - time stamp of object creation

     account (Account) - controlling account (if any, only set together with
                       sessid below)
     sessid (int, read-only) - session id (if any, only set together with
                       account above). Use `sessions` handler to get the
                       Sessions directly.
     location (Object) - current location. Is None if this is a room
     home (Object) - safety start-location
     has_account (bool, read-only)- will only return *connected* accounts
     contents (list of Objects, read-only) - returns all objects inside this
                       object (including exits)
     exits (list of Objects, read-only) - returns all exits from this
                       object, if any
     destination (Object) - only set if this object is an exit.
     is_superuser (bool, read-only) - True/False if this user is a superuser

    * Handlers available

     aliases - alias-handler: use aliases.add/remove/get() to use.
     permissions - permission-handler: use permissions.add/remove() to
                   add/remove new perms.
     locks - lock-handler: use locks.add() to add new lock strings
     scripts - script-handler. Add new scripts to object with scripts.add()
     cmdset - cmdset-handler. Use cmdset.add() to add new cmdsets to object
     nicks - nick-handler. New nicks with nicks.add().
     sessions - sessions-handler. Get Sessions connected to this
                object with sessions.get()
     attributes - attribute-handler. Use attributes.add/remove/get.
     db - attribute-handler: Shortcut for attribute-handler. Store/retrieve
            database attributes using self.db.myattr=val, val=self.db.myattr
     ndb - non-persistent attribute handler: same as db but does not create
            a database entry when storing data

    * Helper methods (see src.objects.objects.py for full headers)

     search(ostring, global_search=False, attribute_name=None,
             use_nicks=False, location=None, ignore_errors=False, account=False)
     execute_cmd(raw_string)
     msg(text=None, **kwargs)
     msg_contents(message, exclude=None, from_obj=None, **kwargs)
     move_to(destination, quiet=False, emit_to_obj=None, use_destination=True)
     copy(new_key=None)
     delete()
     is_typeclass(typeclass, exact=False)
     swap_typeclass(new_typeclass, clean_attributes=False, no_default=True)
     access(accessing_obj, access_type='read', default=False)
     check_permstring(permstring)

    * Hooks (these are class methods, so args should start with self):

     basetype_setup()     - only called once, used for behind-the-scenes
                            setup. Normally not modified.
     basetype_posthook_setup() - customization in basetype, after the object
                            has been created; Normally not modified.

     at_object_creation() - only called once, when object is first created.
                            Object customizations go here.
     at_object_delete() - called just before deleting an object. If returning
                            False, deletion is aborted. Note that all objects
                            inside a deleted object are automatically moved
                            to their <home>, they don't need to be removed here.

     at_init()            - called whenever typeclass is cached from memory,
                            at least once every server restart/reload
     at_cmdset_get(**kwargs) - this is called just before the command handler
                            requests a cmdset from this object. The kwargs are
                            not normally used unless the cmdset is created
                            dynamically (see e.g. Exits).
     at_pre_puppet(account)- (account-controlled objects only) called just
                            before puppeting
     at_post_puppet()     - (account-controlled objects only) called just
                            after completing connection account<->object
     at_pre_unpuppet()    - (account-controlled objects only) called just
                            before un-puppeting
     at_post_unpuppet(account) - (account-controlled objects only) called just
                            after disconnecting account<->object link
     at_server_reload()   - called before server is reloaded
     at_server_shutdown() - called just before server is fully shut down

     at_access(result, accessing_obj, access_type) - called with the result
                            of a lock access check on this object. Return value
                            does not affect check result.

     at_before_move(destination)             - called just before moving object
                        to the destination. If returns False, move is cancelled.
     announce_move_from(destination)         - called in old location, just
                        before move, if obj.move_to() has quiet=False
     announce_move_to(source_location)       - called in new location, just
                        after move, if obj.move_to() has quiet=False
     at_after_move(source_location)          - always called after a move has
                        been successfully performed.
     at_object_leave(obj, target_location)   - called when an object leaves
                        this object in any fashion
     at_object_receive(obj, source_location) - called when this object receives
                        another object

     at_traverse(traversing_object, source_loc) - (exit-objects only)
                              handles all moving across the exit, including
                              calling the other exit hooks. Use super() to retain
                              the default functionality.
     at_after_traverse(traversing_object, source_location) - (exit-objects only)
                              called just after a traversal has happened.
     at_failed_traverse(traversing_object)      - (exit-objects only) called if
                       traversal fails and property err_traverse is not defined.

     at_msg_receive(self, msg, from_obj=None, **kwargs) - called when a message
                             (via self.msg()) is sent to this obj.
                             If returns false, aborts send.
     at_msg_send(self, msg, to_obj=None, **kwargs) - called when this objects
                             sends a message to someone via self.msg().

     return_appearance(looker) - describes this object. Used by "look"
                                 command by default
     at_desc(looker=None)      - called by 'look' whenever the
                                 appearance is requested.
     at_get(getter)            - called after object has been picked up.
                                 Does not stop pickup.
     at_drop(dropper)          - called when this object has been dropped.
     at_say(speaker, message)  - by default, called if an object inside this
                                 object speaks

     """
    """
    This is my solution to populating all of the inflected forms of
    Latin nouns on creation
    """

    def at_object_creation(self):

        # add all of the case endings to attributes

        nominative = self.db.formae['nom_sg'][0]
        genitive = self.db.formae['gen_sg'][0]
        sexus = self.db.sexus

        populate_forms(self, nominative, genitive, sexus)

        self.db.lang = 'latin'

    #making a new get_display_name that is aware of case and not
    # dependent on the key of the object
    # Copied the below from typeclasses/characters.py
    def get_display_name(self, looker, **kwargs):
        if not self.db.formae:
            if self.locks.check_lockstring(looker, "perm(Builder)"):
                return "{}(#{})".format(self.key, self.id)
            return self.key
        else:
            if self.locks.check_lockstring(looker, "perm(Builder)"):
                return "{}(#{})".format(self.key, self.id)
            return self.key
#    def get_display_name(self, looker, **kwargs):
#        if self.locks.check_lockstring(looker, "perm(Builder)"):
#            return "{}(#{})".format(self.db.formae['nom_sg'][0], self.id)
#        return self.db.formae['nom_sg'][0]

    def get_numbered_name(self, count, looker, **kwargs):
        """ 
        Return the numbered (Singular, plural) forms of this object's key.
        This is by default called by return_appearance and is used for
        grouping multiple same-named of this object. Note that this will
        be called on *every* member of a group even though the plural name
        will be only shown once. Also the singular display version, such as
        'an apple', 'a tree' is determined from this method.

        Args:
            count (int): Number of objects of this type
            looker (Object): Onlooker. Not used by default
        Kwargs:
            key (str): Optional key to pluralize, if given, use this instead of
            the object's key
        Returns:
            singular (str): The singular form to display
            plural (str): The determined plural form of the key, including count.
        """
        key = kwargs.get("key", self.key)
        key = ansi.ANSIString(key) # This is needed to allow inflection of colored names
        if self.db.formae:
            plural = self.db.formae['nom_pl'][0]
        else:
            plural = self.key
        plural = "%s %s" % (count, plural)
        if self.db.formae:
            singular = self.key
        else:
            singular = self.key
        if not self.aliases.get(plural, category="plural_key"):
            # We need to wipe any old plurals/an/a in case key changed in the interim
            self.aliases.clear(category="plural_key")
            self.aliases.add(plural, category="plural_key")
            # save the singular form as an alias here too so we can display "an egg"
            # and also look at "an egg".
            self.aliases.add(singular, category="plural_key")
        return singular, plural

    def return_appearance(self, looker, **kwargs):
        """ Adapting to Latin grammar """

        """
        This formats a description. It is the hook a 'look' command
        should call.

        Args:
            looker (Object): Object doing the looking.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default)
        """

        if not looker:
            return ""

        # get and identify all objects
        visible = (con for con in self.contents if con != looker and con.access(looker, "view"))
        exits, users, things = [], [], defaultdict(list)

        # adjusted the exit name to take out the dbref so builders can
        # click on the exits to traverse them
        for con in visible:
            key = con.get_display_name(looker)
            if con.destination:
                exits.append(con.key)
            elif con.has_account:
                if con.db.ardēns:
                    users.append(f"|y(ardēns)|n |c{key}|n")
                else:
                    users.append(f"|c{key}|n")
            else:
                # things can be pluralized
                things[key].append(con)

        # get description, build string
        string = f"|c{self.get_display_name(looker)}|n\n"
        desc = self.db.desc

        # adding the following to accommodate clothing
        worn_string_list = []
        clothes_list = latin_clothing.get_worn_clothes(self, exclude_covered=True)

        # append worn, uncovered clothing to the description
        for garment in clothes_list:

            # append accusative of garment since these are direct objects
            if garment.db.ardēns:
                worn_string_list.append(
                        f"|y(ard{'ēns' if garment.db.sexus == 'neutrum' else 'entem'})|n {garment.db.formae['acc_sg'][0]}"
                        )
            else:
                worn_string_list.append(garment.db.formae['acc_sg'][0])

            # Otherwise, append the name and the string value of 'geritur' ('worn')
            # Honestly, I have no idea what these lines are for (2/19/21)
#            elif garment.db.geritur:
#                worn_string_list.append(garment.name)

        # get held clothes
        possessions = self.contents
        held_list = []
        for possession in possessions:
            possession_sexus = possession.db.sexus
            if possession.db.tenētur:
                if possession.db.ardēns:
                    held_list.append(
                            f"|y(ard{'ēns' if possession.db.sexus == 'neutrum' else 'entem'})|n {possession.db.formae['acc_sg'][0]}"
                            )
                else:
                    held_list.append(possession.db.key)

        # Compile text of what looker sees
        if desc:
            string += desc

        # Append held items
        if held_list:
            string += f"|/|/{self} tenet: {list_to_string(held_list)}"

        # Append worn items
        if worn_string_list:
            string += f"|/|/{self} gerit: {list_to_string(worn_string_list)}"
        else:
            string += f"|/|/{self} nūd{us_a_um('nom_sg',self.db.sexus)} est!"

        if exits:
            # Changing this string so that exits appear green
            # string += "\n|wAd hos locos potes ire:|n\n " + LatinNoun.list_to_string(exits)
            colorful_exits = []
            for exit in exits:
                colorful_exits.append(f"|lc{exit}|lt|g{exit}|n|le")
            colorful_exits = sorted(colorful_exits)
            string += "\n|wAd hōs locōs potes īre:|n\n " + list_to_string(colorful_exits)
        if users or things:
            self.msg("Sorting through things.")
            # handle pluralization of things (never pluralize users)
            thing_strings = []
            for key, itemlist in sorted(things.items()):
                nitem = len(itemlist)
                if nitem == 1:
                    key, _ = itemlist[0].get_numbered_name(nitem, looker, key=key)
                    if itemlist[0].db.is_burning:
                        key = "|y(ardēns)|n " + key
                else:
                    key = [item.get_numbered_name(nitem, looker, key=key)[1] for item in itemlist][
                        0
                    ]
                thing_strings.append(key)

            string += "\n|wEcce:|n\n " + list_to_string(users + thing_strings)

        return string

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
        if msg:
            string = msg
        else:
            string = "{object} {exit} discēdit."

        # Get the exit from location to destination
        location = self.location
        exits = [
            o for o in location.contents if o.location is location and o.destination is destination
        ]
        if not mapping:
            mapping = {}

        mapping.update(
                {
                    "object": self,
                    "exit": exits[0] if exits else "somewhere",
                    "origin": location or "nowhere",
                    "destination": destination or "nowhere",
                    }
                )

        location.msg_contents(string, exclude=(self,), mapping=mapping)

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
            string = "You now have %s in your possession." % self.get_display_name(self.location)
            self.location.msg(string)
            return

        if source_location:
            if msg:
                string = msg
            else:
                string = "{object} ad {ad_locum} ab {ab_loco} vēnit."
        else:
            string = "{object} ad {ad_locum} vēnit."

        origin = source_location
        destination = self.location
        exits = []
        if origin:
            exits = [
                o
                for o in destination.contents
                if o.location is destination and o.destination is origin
            ]

        if not mapping:
            mapping = {}

        # Implementing some Latin awareness
        if source_location:
            if source_location.db.formae:
                ab_loco = source_location.db.formae['abl_sg'][0]
            else:
                ab_loco = source_location

        if self.location.db.formae:
            ad_locum = self.location.db.formae['acc_sg'][0]
        else:
            ad_locum = self.location

        mapping.update(
            {
                "object": self,
                "exit": exits[0] if exits else "somewhere",
                "origin": origin or "nowhere",
                "destination": destination or "nowhere",
                "ab_loco": ab_loco,
                "ad_locum": ad_locum,
            }
        )

        destination.msg_contents(string, exclude=(self,), mapping=mapping)

    # adjusting the 'at_before_say' and 'at_say' hooks for Latin
    def at_before_say(self, message, **kwargs):
        """
        Before the object says something.

        This hook is by default used by the 'say' and 'whisper'
        commands as used by this command it is called before the text
        is said/whispered and can be used to customize the outgoing
        text from the object. Returning `None` aborts the command.

        Args:
            message (str): The suggested say/whisper text spoken by self.
        Keyword Args:
            whisper (bool): If True, this is a whisper rather than
                a say. This is sent by the whisper command by default.
                Other verbal commands could use this hook in similar
                ways.
            receivers (Object or iterable): If set, this is the target or targets for the say/whisper.

        Returns:
            message (str): The (possibly modified) text to be spoken.

        """
        return message

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
        Keyword Args:
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
        msg_type = "say"
        if kwargs.get("whisper", False):
            # whisper mode
            msg_type = "whisper"
            msg_self = (
                '{self} whisper to {all_receivers}, "|n{speech}|n"'
                if msg_self is True
                else msg_self
            )
            msg_receivers = msg_receivers or '{object} whispers: "|n{speech}|n"'
            msg_location = None
        else:
            # split "message" into two parts if possible
            two_part_speech = False
            speech_list = message.split(' ')
            speech_one = speech_list[0]
            speech_two = ""
            if len(speech_list) > 1:
                speech_two = (' ').join(speech_list[1:])
                two_part_speech = True

            if two_part_speech:
                msg_self = '"|n{speech_one}|n" inquis "|n{speech_two}|n"'
                msg_location = '{object} "|n{speech_one}|n" inquit "|n{speech_two}|n"'
                msg_receivers = '{object} tibi "|n{speech_one}|n" inquit "|n{speech_two}|n"'
            else:
                msg_self = '"|n{speech_one}|n" inquis.'
                msg_location = '{object} "|n{speech_one}|n" inquit.'
                msg_receivers = '{object} tibi "|n{speech_one}|n" inquit.'

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
                "speech_one": speech_one,
                "speech_two": speech_two,
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
                "speech_one": speech_one,
                "speech_two": speech_two,
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

class Flammable(Rēs):

    def at_object_creation(self):

        nom = self.db.formae['nom_sg'][0]
        gen = self.db.formae['gen_sg'][0]
        gender = self.db.sexus

        populate_forms(self,nom,gen,gender)

        self.db.flammable = True
        self.db.ardēns = False

        self.db.lang = 'latin'

class Hearth(Rēs):

    def at_object_creation(self):

        nom = self.db.formae['nom_sg'][0]
        gen = self.db.formae['gen_sg'][0]
        gender = self.db.sexus

        populate_forms(self,nom,gen,gender)

        self.db.flammable = True
        self.db.ardēns = True

        self.db.lang = 'latin'
