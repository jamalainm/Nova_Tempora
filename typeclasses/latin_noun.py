# file mygame/typeclasses/latin_noun.py

from evennia import DefaultObject
# adding the following for colors in names for pluralization
from evennia.utils import ansi
# adding the following for redefinition of 'return_appearance'
from collections import defaultdict
# from evennia.utils.utils import list_to_string

class LatinNoun(DefaultObject):

    def at_first_save(self):
        """
        This is called by the typeclass system whenever an instance of
        this class is saved for the first time. It is a generic hook
        for calling the startup hooks for the various game entities.
        When overloading you generally don't overload this but
        overload the hooks called by this method.

        """
        self.basetype_setup()
        # moving the below line to just before basetype_posthook
        # at the bottom of this defenitiion
        # self.at_object_creation()

        if hasattr(self, "_createdict"):
            # this will only be set if the utils.create function
            # was used to create the object. We want the create
            # call's kwargs to override the values set by hooks.
            cdict = self._createdict
            updates = []
            if not cdict.get("key"):
                if not self.db_key:
                    self.db_key = "#%i" % self.dbid
                    updates.append("db_key")
            elif self.key != cdict.get("key"):
                updates.append("db_key")
                self.db_key = cdict["key"]
            if cdict.get("location") and self.location != cdict["location"]:
                self.db_location = cdict["location"]
                updates.append("db_location")
            if cdict.get("home") and self.home != cdict["home"]:
                self.home = cdict["home"]
                updates.append("db_home")
            if cdict.get("destination") and self.destination != cdict["destination"]:
                self.destination = cdict["destination"]
                updates.append("db_destination")
            if updates:
                self.save(update_fields=updates)

            if cdict.get("permissions"):
                self.permissions.batch_add(*cdict["permissions"])
            if cdict.get("locks"):
                self.locks.add(cdict["locks"])
            if cdict.get("aliases"):
                self.aliases.batch_add(*cdict["aliases"])
            if cdict.get("location"):
                cdict["location"].at_object_receive(self, None)
                self.at_after_move(None)
            if cdict.get("tags"):
                # this should be a list of tags, tuples (key, category) or (key, category, data)
                self.tags.batch_add(*cdict["tags"])
            if cdict.get("attributes"):
                # this should be tuples (key, val, ...)
                self.attributes.batch_add(*cdict["attributes"])
            if cdict.get("nattributes"):
                # this should be a dict of nattrname:value
                for key, value in cdict["nattributes"]:
                    self.nattributes.add(key, value)

            del self._createdict

        self.at_object_creation()
        self.basetype_posthook_setup()

# adding the pluralization rules; so far they will only work for
# nominative plurals for when you look in a new room; not sure
# what to do with other plural functionality

    # redefine list_to_stringfor this function to use "et"

    def list_to_string(inlist, endsep="et", addquote=False):
        """
        This pretty-formats a list as string output, adding an optional
        alternative separator to the second to last entry.  If `addquote`
        is `True`, the outgoing strings will be surrounded by quotes.

        Args:
            inlist (list): The list to print.
            endsep (str, optional): If set, the last item separator will
                be replaced with this value.
            addquote (bool, optional): This will surround all outgoing
                values with double quotes.

        Returns:
            liststr (str): The list represented as a string.

        Examples:

            ```python
             # no endsep:
                [1,2,3] -> '1, 2, 3'
             # with endsep=='and':
                [1,2,3] -> '1, 2 and 3'
             # with addquote and endsep
                [1,2,3] -> '"1", "2" and "3"'
            ```

        """
        if not endsep:
            endsep = ","
        else:
            endsep = " " + endsep
        if not inlist:
            return ""
        if addquote:
            if len(inlist) == 1:
                return '"%s"' % inlist[0]
            return ", ".join('"%s"' % v for v in inlist[:-1]) + "%s %s" % (endsep, '"%s"' % inlist[-1])
        else:
            if len(inlist) == 1:
                return str(inlist[0])
            return ", ".join(str(v) for v in inlist[:-1]) + "%s %s" % (endsep, inlist[-1])

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
        visible = (con for con in self.contents if con != looker and con.access(looker, "view"))
        exits, users, things = [], [], defaultdict(list)
        # adjusted the exit name to take out the dbref so builders can
        # click on the exits to go there
        for con in visible:
            key = con.get_display_name(looker)
            if con.destination:
                exits.append(con.key)
            elif con.has_account:
                if con.db.ardēns:
                    users.append("|y(ardēns)|n |c%s|n" % key)
                else:
                    users.append("|c%s|n" % key)
            else:
                # things can be pluralized
                things[key].append(con)
        # get description, build string
        string = "|c%s|n\n" % self.get_display_name(looker)
        desc = self.db.desc
        # JI (12/7/9) Adding the following lines to accommodate clothing
        # Actually, added return_appearance to characters typeclass
        # and commenting this new section out
#        worn_string_list = []
#        clothes_list = get_worn_clothes(self, exclude_covered=True)
#        # Append worn, uncovered clothing to the description
#        for garment in clothes_list:
#            # if 'worn' is True, just append the name
#            if garment.db.worn is True:
#                # JI (12/7/19) append the accusative name to the description,
#                # since these will be direct objects
#                worn_string_list.append(garment.db.acc_sg)
#            # Otherwise, append the name and the string value of 'worn'
#            elif garment.db.worn:
#                worn_string_list.append("%s %s" % (garment.name, garment.db.worn))
        if desc:
            string += "%s" % desc
#        # Append worn clothes.
#        if worn_string_list:
#            string += "|/|/%s gerit: %s." % (self, list_to_string(worn_string_list))
#        else:
#            string += "|/|/%s nud%s est!" % (self, 'a' if self.db.gender == 1 else 'us')
#        return string
        # Thinking that the above, added for clothing, might need to only be in the
        # character typeclass
        if exits:
            # Changing this string so that exits appear green
            # string += "\n|wAd hos locos potes ire:|n\n " + LatinNoun.list_to_string(exits)
            colorful_exits = []
            for exit in exits:
                colorful_exits.append(f"|lc{exit}|lt|g{exit}|n|le")
            colorful_exits = sorted(colorful_exits)
            string += "\n|wAd hōs locōs potes īre:|n\n " + LatinNoun.list_to_string(colorful_exits)
        if users or things:
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

            string += "\n|wEcce:|n\n " + LatinNoun.list_to_string(users + thing_strings)

        return string

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
