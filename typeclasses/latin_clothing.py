# file mygame/typeclasses/latin_clothing.py
"""
Clothing - Provides a typeclass and commands for wearable clothing,
which is appended to a character's description when worn.

Evennia contribution - Tim Ashley Jenkins 2017

Clothing items, when worn, are added to the character's description
in a list. For example, if wearing the following clothing items:

    a thin and delicate necklace
    a pair of regular ol' shoes
    one nice hat
    a very pretty dress

A character's description may look like this:

    Superuser(#1)
    This is User #1.

    Superuser is wearing one nice hat, a thin and delicate necklace,
    a very pretty dress and a pair of regular ol' shoes.

Characters can also specify the style of wear for their clothing - I.E.
to wear a scarf 'tied into a tight knot around the neck' or 'draped
loosely across the shoulders' - to add an easy avenue of customization.
For example, after entering:

    wear scarf draped loosely across the shoulders

The garment appears like so in the description:

    Superuser(#1)
    This is User #1.

    Superuser is wearing a fanciful-looking scarf draped loosely
    across the shoulders.

- JI (12/7/19): I think I'll disable this functionality to start with

Items of clothing can be used to cover other items, and many options
are provided to define your own clothing types and their limits and
behaviors. For example, to have undergarments automatically covered
by outerwear, or to put a limit on the number of each type of item
that can be worn. The system as-is is fairly freeform - you
can cover any garment with almost any other, for example - but it
can easily be made more restrictive, and can even be tied into a
system for armor or other equipment.

To install, import this module and have your default character
inherit from ClothedCharacter in your game's characters.py file:

    from evennia.contrib.clothing import ClothedCharacter

    class Character(ClothedCharacter):

And then add ClothedCharacterCmdSet in your character set in your
game's commands/default_cmdsets.py:

    from evennia.contrib.clothing import ClothedCharacterCmdSet

    class CharacterCmdSet(default_cmds.CharacterCmdSet):
         ...
         at_cmdset_creation(self):

             super().at_cmdset_creation()
             ...
             self.add(ClothedCharacterCmdSet)    # <-- add this

From here, you can use the default builder commands to create clothes
with which to test the system:

    @create a pretty shirt : evennia.contrib.clothing.Clothing
    @set shirt/genus_vestīmentōrum = 'top'
    wear shirt

"""
# JI (12/7/19) Adding the following line to change inheritance
# of new typeclass Clothing
from typeclasses.rēs import Rēs
from evennia import DefaultObject
from evennia import DefaultCharacter

from typeclasses.latin_noun import LatinNoun

# Options start here.
# Maximum character length of 'wear style' strings, or None for unlimited.
WEARSTYLE_MAXLENGTH = 50

# The rest of these options have to do with clothing types. Clothing types are optional,
# but can be used to give better control over how different items of clothing behave. You
# can freely add, remove, or change clothing types to suit the needs of your game and use
# the options below to affect their behavior.

# The order in which clothing types appear on the description. Untyped clothing or clothing
# with a type not given in this list goes last.
CLOTHING_TYPE_ORDER = [
    "hat",
    "cloak",
    "jewelry",
    "top",
    "undershirt",
    "gloves",
    "fullbody",
    "shoulder",
    "bottom",
    "underpants",
    "socks",
    "shoes",
    "accessory",
]
# The maximum number of each type of clothes that can be worn. Unlimited if untyped or not specified.
CLOTHING_TYPE_LIMIT = {"hat": 1, "gloves": 1, "socks": 1, "shoes": 1, "cloak": 1, "undershirt": 1, "bottom": 1, "underpants": 1, "fullbody":2, "shoulder":2}
# The maximum number of clothing items that can be worn, or None for unlimited.
CLOTHING_OVERALL_LIMIT = 20
# What types of clothes will automatically cover what other types of clothes when worn.
# Note that clothing only gets auto-covered if it's already worn when you put something
# on that auto-covers it - for example, it's perfectly possible to have your underpants
# showing if you put them on after your pants!
CLOTHING_TYPE_AUTOCOVER = {
    "top": ["undershirt"],
    "bottom": ["underpants"],
    "fullbody": ["undershirt", "underpants"],
    "shoes": ["socks"],
}
# Types of clothes that can't be used to cover other clothes.
CLOTHING_TYPE_CANT_COVER_WITH = ["jewelry"]


# HELPER FUNCTIONS START HERE

def order_clothes_list(clothes_list):
    """
    Orders a given clothes list by the order specified in CLOTHING_TYPE_ORDER.

    Args:
        clothes_list (list): List of clothing items to put in order

    Returns:
        ordered_clothes_list (list): The same list as passed, but re-ordered
                                     according to the hierarchy of clothing types
                                     specified in CLOTHING_TYPE_ORDER.
    """
    ordered_clothes_list = clothes_list
    # For each type of clothing that exists...
    for current_type in reversed(CLOTHING_TYPE_ORDER):
        # Check each item in the given clothes list.
        for clothes in clothes_list:
            # If the item has a clothing type...
            if clothes.db.genus_vestīmentōrum:
                item_type = clothes.db.genus_vestīmentōrum
                # And the clothing type matches the current type...
                if item_type == current_type:
                    # Move it to the front of the list!
                    ordered_clothes_list.remove(clothes)
                    ordered_clothes_list.insert(0, clothes)
    return ordered_clothes_list


def get_worn_clothes(character, exclude_covered=False):
    """
    Get a list of clothes worn by a given character.

    Args:
        character (obj): The character to get a list of worn clothes from.

    Kwargs:
        exclude_covered (bool): If True, excludes clothes covered by other
                                clothing from the returned list.

    Returns:
        ordered_clothes_list (list): A list of clothing items worn by the
                                     given character, ordered according to
                                     the CLOTHING_TYPE_ORDER option specified
                                     in this module.
    """
    clothes_list = []
    for thing in character.contents:
        # If uncovered or not excluding covered items
        if not thing.db.covered_by or exclude_covered is False:
            # If 'worn' is True, add to the list
            if thing.db.geritur:
                clothes_list.append(thing)
    # Might as well put them in order here too.
    ordered_clothes_list = order_clothes_list(clothes_list)
    return ordered_clothes_list


def clothing_type_count(clothes_list):
    """
    Returns a dictionary of the number of each clothing type
    in a given list of clothing objects.

    Args:
        clothes_list (list): A list of clothing items from which
                             to count the number of clothing types
                             represented among them.

    Returns:
        types_count (dict): A dictionary of clothing types represented
                            in the given list and the number of each
                            clothing type represented.
    """
    types_count = {}
    for garment in clothes_list:
        if garment.db.genus_vestīmentōrum:
            type = garment.db.genus_vestīmentōrum
            if type not in list(types_count.keys()):
                types_count[type] = 1
            else:
                types_count[type] += 1
    return types_count


def single_type_count(clothes_list, type):
    """
    Returns an integer value of the number of a given type of clothing in a list.

    Args:
        clothes_list (list): List of clothing objects to count from
        type (str): Clothing type to count

    Returns:
        type_count (int): Number of garments of the specified type in the given
                          list of clothing objects
    """
    type_count = 0
    for garment in clothes_list:
        if garment.db.genus_vestīmentōrum:
            if garment.db.genus_vestīmentōrum == type:
                type_count += 1
    return type_count

# JI (12/7/19) Inheriting from new object class; maybe that's crazy
# Inheriting from new Latin typeclass 'Rēs'; had been 'Object'
class Clothing(Rēs):
# class Clothing(DefaultObject):
    def wear(self, wearer, wearstyle, quiet=False):
        """
        Sets clothes to 'geritur' (worn) and optionally echoes to the room.

        Args:
            wearer (obj): character object wearing this clothing object
            wearstyle (True or str): string describing the style of wear or True for none

        Kwargs:
            quiet (bool): If false, does not message the room

        Notes:
            Optionally sets db.geritur with a 'wearstyle' that appends a short passage to
            the end of the name  of the clothing to describe how it's worn that shows
            up in the wearer's desc - I.E. 'around his neck' or 'tied loosely around
            her waist'. If db.worn is set to 'True' then just the name will be shown.
        """
        # Set clothing as worn
        # JI (12/7/19) Chaging to "True" to disable "wearstyle" at least to start with
        self.db.geritur = True
        # Auto-cover appropirate clothing types, as specified above
        to_cover = []
        # JI (12/7/19) list to hold ablative forms
        to_cover_ablative = []
        if self.db.genus_vestīmentōrum and self.db.genus_vestīmentōrum in CLOTHING_TYPE_AUTOCOVER:
            for garment in get_worn_clothes(wearer):
                if (
                    garment.db.genus_vestīmentōrum
                    and garment.db.genus_vestīmentōrum in CLOTHING_TYPE_AUTOCOVER[self.db.genus_vestīmentōrum]
                ):
                    to_cover.append(garment)
                    # JI (12/7/19) list of ablative forms
                    to_cover_ablative.append(garment.db.formae['abl_sg'][0])
                    garment.db.covered_by = self
        # Return if quiet
        if quiet:
            return
        # Echo a message to the room
        # JI (12/7/19) Translated message for putting something on. 
        # But this returns the same message to caller and room
        message = "%s %s induit" % (wearer, self.db.formae['acc_sg'][0])
        if wearstyle is not True:
            message = "%s wears %s %s" % (wearer, self.name, wearstyle)
        if to_cover:
            # JI (12/7/19) Translated message for covering something
            message = message + ", %s tect%s" % (LatinNoun.list_to_string(to_cover_ablative), 'īs' if len(to_cover) > 1 else 'ā' if to_cover[0].db.sexus == 'muliebre' else 'ō')
        wearer.location.msg_contents(message + ".", exclude=wearer)
        wearer.msg(f"{self.db.formae['acc_sg'][0]} induistī.")

        self.db.tenētur = False

    def remove(self, wearer, quiet=False):
        """
        Removes worn clothes and optionally echoes to the room.

        Args:
            wearer (obj): character object wearing this clothing object

        Kwargs:
            quiet (bool): If false, does not message the room
        """
        # See if wearer's hands are full:
        possessions = wearer.contents
        hands = ['dextrā','sinistrā']
        held_items = []
        full_hands = 0
        for possession in possessions:
            if possession.db.tenētur:
                if possession.db.tenētur in hands:
                    held_items.append(possession)
                    full_hands += 1
                elif possession.db.tenētur == 'ambābus':
                    held_items.append(possession)
                    full_hands += 2

        if full_hands >= 2:
            wearer.msg("Manūs tuae sunt plēnae!")
            return

        self.db.geritur = False
        # JI (12/7/2019) Translated Message to Latin
        remove_message = "%s %s exuit." % (wearer, self.db.formae['acc_sg'][0])
        uncovered_list = []
        # JI (12/7/19) List to hold ablative forms
        uncovered_list_ablative = []

        # Check to see if any other clothes are covered by this object.
        for thing in wearer.contents:
            # If anything is covered by
            if thing.db.covered_by == self:
                thing.db.covered_by = False
                # JI (12/9/19) changing the following from thing.name to thing
                uncovered_list.append(thing)
                # JI (12/7/19) Add to list of ablative forms
                uncovered_list_ablative.append(thing.db.formae['abl_sg'][0])
        if len(uncovered_list) > 0:
            # JI (12/7/2019) Translated message to Latin
            remove_message = "%s %s exuit, %s apert%s." % (
                wearer,
                self.db.formae['acc_sg'][0],
                # JI (12/7/19) changed list to ablative forms
                LatinNoun.list_to_string(uncovered_list_ablative),
                # JI (12/7/19) select the proper ending for "having been revealed"
                'īs' if len(uncovered_list) > 1 else 'ā' if uncovered_list[0].db.sexus == 'muliebre' else 'ō',
            )
        # Echo a message to the room
        if not quiet:
            wearer.location.msg_contents(remove_message, exclude=wearer)
            wearer.msg(f"{self.db.formae['acc_sg'][0]} exuistī.")

        if held_items:
            hands.remove(held_items[0].db.tenētur)
            self.db.tenētur = hands[0]
        else:
            self.db.tenētur = wearer.db.handedness

    def at_get(self, getter):
        """
        Makes absolutely sure clothes aren't already set as 'worn'
        when they're picked up, in case they've somehow had their
        location changed without getting removed.
        """
        self.db.geritur = False


class ClothedCharacter(DefaultCharacter):
    """
    Character that displays worn clothing when looked at. You can also
    just copy the return_appearance hook defined below to your own game's
    character typeclass.
    """

    def return_appearance(self, looker):
        """
        This formats a description. It is the hook a 'look' command
        should call.

        Args:
            looker (Object): Object doing the looking.

        Notes:
            The name of every clothing item carried and worn by the character
            is appended to their description. If the clothing's db.worn value
            is set to True, only the name is appended, but if the value is a
            string, the string is appended to the end of the name, to allow
            characters to specify how clothing is worn.
        """
        if not looker:
            return ""
        # get description, build string
        string = "|c%s|n\n" % self.get_display_name(looker)
        desc = self.db.desc
        worn_string_list = []
        clothes_list = get_worn_clothes(self, exclude_covered=True)
        # Append worn, uncovered clothing to the description
        for garment in clothes_list:
            # If 'worn' is True, just append the name
            if garment.db.geritur is True:
                # JI (12/7/19) append the accusative name to the description,
                # since these will be direct objects
                worn_string_list.append(garment.db.formae['acc_sg'][0])
            # Otherwise, append the name and the string value of 'worn'
            elif garment.db.geritur:
                worn_string_list.append("%s %s" % (garment.name, garment.db.geritur))
        if desc:
            string += "%s" % desc
        # Append worn clothes.
        if worn_string_list:
            string += "|/|/%s gerit: %s." % (self, LatinNoun.list_to_string(worn_string_list))
        else:
            string += "|/|/%s nūd%s est!" % (self, 'a' if self.db.sexus == 'muliebre' else 'us' if self.db.sexus == 'māre' else 'um')
        return string
