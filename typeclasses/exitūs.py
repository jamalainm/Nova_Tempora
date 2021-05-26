"""
Exits

Exits are connectors between Rooms. An exit always has a destination property
set and has a single command defined on itself with the same name as its key,
for allowing Characters to traverse the exit to its destination.

"""
from evennia import DefaultExit

class Exitus(DefaultExit):
    """
    Exits are connectors between rooms. Exits are normal Objects except
    they defines the `destination` property. It also does work in the
    following methods:

     basetype_setup() - sets default exit locks (to change, use `at_object_creation` instead).
     at_cmdset_get(**kwargs) - this is called when the cmdset is accessed and should
                              rebuild the Exit cmdset along with a command matching the name
                              of the Exit object. Conventionally, a kwarg `force_init`
                              should force a rebuild of the cmdset, this is triggered
                              by the `@alias` command when aliases are changed.
     at_failed_traverse() - gives a default error message ("You cannot
                            go there") if exit traversal fails and an
                            attribute `err_traverse` is not defined.

    Relevant hooks to overload (compared to other types of Objects):
        at_traverse(traveller, target_loc) - called to do the actual traversal and calling of the other hooks.
                                            If overloading this, consider using super() to use the default
                                            movement implementation (and hook-calling).
        at_after_traverse(traveller, source_loc) - called by at_traverse just after traversing.
        at_failed_traverse(traveller) - called by at_traverse if traversal failed for some reason. Will
                                        not be called if the attribute `err_traverse` is
                                        defined, in which case that will simply be echoed.
    """
#    def at_object_creation(self):
#        self.db.formae = {'acc_sg':[self.key]}
#        self.db.desc = self.destination

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

#        # get and identify all objects
#        visible = (con for con in self.contents if con != looker and con.access(looker, "view"))
#        exits, users, things = [], [], defaultdict(list)
#
#        # adjusted the exit name to take out the dbref so builders can
#        # click on the exits to traverse them
#        for con in visible:
#            key = con.get_display_name(looker)
#            if con.destination:
#                exits.append(con.key)
#            elif con.has_account:
#                if con.db.ardēns:
#                    users.append(f"|y(ardēns)|n |c{key}|n")
#                else:
#                    users.append(f"|c{key}|n")
#            else:
#                # things can be pluralized
#                things[key].append(con)
#
#        # get description, build string
        string = f"|c{self.get_display_name(looker)}|n\n"
#        desc = self.db.desc
#
#        # adding the following to accommodate clothing
#        worn_string_list = []
#        clothes_list = latin_clothing.get_worn_clothes(self, exclude_covered=True)
#
#        # append worn, uncovered clothing to the description
#        for garment in clothes_list:
#
#            # append accusative of garment since these are direct objects
#            if garment.db.ardēns:
#                worn_string_list.append(
#                        f"|y(ard{'ēns' if garment.db.sexus == 'neutrum' else 'entem'})|n {garment.db.formae['acc_sg'][0]}"
#                        )
#            else:
#                worn_string_list.append(garment.db.formae['acc_sg'][0])
#
#            # Otherwise, append the name and the string value of 'geritur' ('worn')
#            # Honestly, I have no idea what these lines are for (2/19/21)
##            elif garment.db.geritur:
##                worn_string_list.append(garment.name)
#
#        # get held clothes
#        possessions = self.contents
#        held_list = []
#        for possession in possessions:
#            possession_sexus = possession.db.sexus
#            if possession.db.tenētur:
#                if possession.db.ardēns:
#                    held_list.append(
#                            f"|y(ard{'ēns' if possession.db.sexus == 'neutrum' else 'entem'})|n {possession.db.formae['acc_sg'][0]}"
#                            )
#                else:
#                    held_list.append(possession.db.formae['acc_sg'][0])
#
#        # Compile text of what looker sees
#        if desc:
#            string += "%s" % desc
#
#        # Append held items
#        if held_list:
#            string += f"|/|/{self} tenet: {list_to_string(held_list)}"
#
#        # Append worn items
#        if self.is_typeclass("typeclasses.persōnae.Persōna", exact=False):
#            if worn_string_list:
#                string += f"|/|/{self} gerit: {list_to_string(worn_string_list)}"
#            else:
#                string += f"|/|/{self} nūd{us_a_um('nom_sg',self.db.sexus)} est!"
#
#        if users or things:
#            # handle pluralization of things (never pluralize users)
#            thing_strings = []
#            for key, itemlist in sorted(things.items()):
#                nitem = len(itemlist)
#                if nitem == 1:
#                    key, _ = itemlist[0].get_numbered_name(nitem, looker, key=key)
#                    if itemlist[0].db.ardēns:
#                        key = "|y(ardēns)|n " + key
#                else:
#                    key = [item.get_numbered_name(nitem, looker, key=key)[1] for item in itemlist][
#                        0
#                    ]
#                thing_strings.append(key)
#        
#        if exits:
#            # Changing this string so that exits appear green
#            # string += "\n|wAd hos locos potes ire:|n\n " + LatinNoun.list_to_string(exits)
#            colorful_exits = []
#            for exit in exits:
#                colorful_exits.append(f"|lc{exit}|lt|g{exit}|n|le")
#            colorful_exits = sorted(colorful_exits)
#            string += "\n|wAd hōs locōs potes īre:|n\n " + list_to_string(colorful_exits)
#
#            if len(things) > 0 and len(users) > 0:
#                string += "\n|wEcce:|n\n " + list_to_string(users + thing_strings)
#            elif len(users) > 0:
#                string += "\n|wEcce:|n\n " + list_to_string(users)
#            elif len(things) > 0:
#                string += "\n|wEcce:|n\n " + list_to_string(thing_strings)
#
        string += f"\n{self.destination}"
        return string


