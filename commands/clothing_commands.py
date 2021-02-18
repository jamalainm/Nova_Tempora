# file mygame/commands/clothing_commands.py
#
# Heavliy based on Tim Ashley Jenkins 2017 Evennia contribution
#
# Moved from the 'latin_clothing' typeclass file for consistency's sake
#
# COMMANDS START HERE

from commands.iussa_latīna import MuxCommand
from evennia import default_cmds
from evennia.utils import evtable
from utils.latin.which_one import which_one
from typeclasses.latin_clothing import CLOTHING_TYPE_LIMIT, CLOTHING_OVERALL_LIMIT, get_worn_clothes, single_type_count

CLOTHING_TYPE_LIMIT = {"hat": 1, "gloves": 1, "socks": 1, "shoes": 1, "cloak": 1, "undershirt": 1, "bottom": 1, "underpants": 1, "fullbody":2, "shoulder":2}

CLOTHING_OVERALL_LIMIT = 20

class CmdWear(MuxCommand):
    """
    Puts on an item of clothing you are holding.

    Usage:
      indue <rem> 

    Examples:
      indue tunicam

    All the clothes you are wearing are appended to your description.
    If you provide a 'wear style' after the command, the message you
    provide will be displayed after the clothing's name.
    """

    # JI (12/17/19) changing key to 'indue' and help category to 
    # 'Iussa Latīna'
    key = "indue"
    help_category = "Iussa Latīna"

    def func(self):
        """
        This performs the actual command.
        """
        if not self.args:
            # JI (12/17/19) adapting for Latin commands, removing "wear style"
            self.caller.msg("Usage: indue <rem>")
            return
        # JI (12/7/19) Commenting out following line, adding my which_one function
        # and copying the commented out line with self.arglist[0] replaced by target
        # clothing = self.caller.search(self.arglist[0], candidates=self.caller.contents)
        stuff = self.caller.contents
        target, self.args = which_one(self.args,self.caller,stuff)
        # JI (12/7/19) Going to see about bypassing the following in preference of the above
        # clothing = self.caller.search(target, candidates=self.caller.contents)
        clothing = target
        wearstyle = True
        if not clothing:
            # JI (12/7/19) changing to Latin
            self.caller.msg("Non in manibus habes.")
            return
        if not clothing.is_typeclass("typeclasses.latin_clothing.Clothing", exact=False):
            # JI (12/7/19) adapting to Latin
            self.caller.msg("Ill%s non est vestis!" % ('a' if clothing.db.sexus == 'muliebre' else 'e' if clothing.db.sexus == 'māre' else 'ud'))
            return

        # Enforce overall clothing limit.
        if CLOTHING_OVERALL_LIMIT and len(get_worn_clothes(self.caller)) >= CLOTHING_OVERALL_LIMIT:
            # JI (12/7/19) Adapting to Latin
            self.caller.msg("Plūra vestīmenta gerere nōn potes!")
            return

        # Apply individual clothing type limits.
        if clothing.db.genus_vestīmentōrum and not clothing.db.geritur:
            type_count = single_type_count(get_worn_clothes(self.caller), clothing.db.genus_vestīmentōrum)
            if clothing.db.genus_vestīmentōrum in list(CLOTHING_TYPE_LIMIT.keys()):
                if type_count >= CLOTHING_TYPE_LIMIT[clothing.db.genus_vestīmentōrum]:
                    self.caller.msg("Vestīmenta huius generis plūra gerere nōn potes!")
                            # JI (12/7/19) Adapting to Latin
#                        "You can't wear any more clothes of the type '%s'."
#                        % clothing.db.genus_vestīmentōrum
#                    )

                    return

        if clothing.db.geritur and len(self.arglist) == 1:
            # JI (12/7/19) Adapting to Latin
            self.caller.msg("Iam %s geris!" % clothing.db.formae['acc_sg'][0])
            return
        if len(self.arglist) > 1:  # If wearstyle arguments given
            wearstyle_list = self.arglist  # Split arguments into a list of words
            del wearstyle_list[0]  # Leave first argument (the clothing item) out of the wearstyle
            wearstring = " ".join(
                str(e) for e in wearstyle_list
            )  # Join list of args back into one string
            if (
                WEARSTYLE_MAXLENGTH and len(wearstring) > WEARSTYLE_MAXLENGTH
            ):  # If length of wearstyle exceeds limit
                self.caller.msg(
                    "Please keep your wear style message to less than %i characters."
                    % WEARSTYLE_MAXLENGTH
                )
            else:
                wearstyle = wearstring
        # JI (12/7/19) Make sure grammar happens:
        lower_case = [x.lower() for x in clothing.db.formae['acc_sg']]
        if self.args not in lower_case:
            self.caller.msg(f"(Did you mean '{clothing.db.formae['acc_sg']}')")
            return
        clothing.wear(self.caller, wearstyle)


class CmdRemove(MuxCommand):
    """
    Takes off an item of clothing.

    Usage:
       exue <rem>

    Removes an item of clothing you are wearing. You can't remove
    clothes that are covered up by something else - you must take
    off the covering item first.
    """

    key = "exue"
    help_category = "Iussa Latīna"

    def func(self):
        """
        This performs the actual command.
        """
        # JI (12/7/19) Like with CmdWear above, adding the which_one function
        # to deal with Latin issues. Commenting out original and adapting by
        # changing self.args to target.
        # clothing = self.caller.search(self.args, candidates=self.caller.contents)
        stuff = self.caller.contents
        target, self.args = which_one(self.args,self.caller,stuff)
        # JI (12/7/9) commenting out the below in preference of the above
        # clothing = self.caller.search(target, candidates=self.caller.contents)
        clothing = target
        if not clothing:
            # JI (12/7/19) Adapted to Latin
            self.caller.msg("Non geritur.")
            return
        if not clothing.db.geritur:
            # JI (12/7/19) Adapted to Latin
            self.caller.msg("Non geritur!")
            return
        if clothing.db.covered_by:
            # adapted to Latin
            self.caller.msg("prius tibi est necesse %s exuere." % clothing.db.covered_by.db.formae['acc_sg'][0])
            return
        # JI (12/7/19) Ensure proper grammer
        lower_case = [x.lower() for x in clothing.db.formae['acc_sg']]
        if self.args.lower() not in lower_case:
            self.caller.msg(f"(Did you mean '{clothing.db.formae['acc_sg']}'?)")
            return
        clothing.remove(self.caller)


class CmdCover(MuxCommand):
    # JI 12/7/19
    # I think the syntax for adapting this command could take a while:
    # since there are multiple arguments we want to accept either word
    # order and if I remember from the 'give' command adaptation, that
    # was a failry involved process
    """
    Covers a worn item of clothing with another you're holding or wearing.

    Usage:
        cover <obj> [with] <obj>

    When you cover a clothing item, it is hidden and no longer appears in
    your description until it's uncovered or the item covering it is removed.
    You can't remove an item of clothing if it's covered.
    """

    key = "cover"
    help_category = "clothing"

    def func(self):
        """
        This performs the actual command.
        """

        if len(self.arglist) < 2:
            self.caller.msg("Usage: cover <worn clothing> [with] <clothing object>")
            return
        # Get rid of optional 'with' syntax
        if self.arglist[1].lower() == "with" and len(self.arglist) > 2:
            del self.arglist[1]
        to_cover = self.caller.search(self.arglist[0], candidates=self.caller.contents)
        cover_with = self.caller.search(self.arglist[1], candidates=self.caller.contents)
        if not to_cover or not cover_with:
            return
        if not to_cover.is_typeclass("typeclasses.latin_clothing.Clothing", exact=False):
            self.caller.msg("%s isn't clothes!" % to_cover.name)
            return
        if not cover_with.is_typeclass("typeclasses.latin_clothing.Clothing", exact=False):
            self.caller.msg("%s isn't clothes!" % cover_with.name)
            return
        if cover_with.db.genus_vestīmentōrum:
            if cover_with.db.genus_vestīmentōrum in CLOTHING_TYPE_CANT_COVER_WITH:
                self.caller.msg("You can't cover anything with that!")
                return
        if not to_cover.db.geritur:
            self.caller.msg("You're not wearing %s!" % to_cover.name)
            return
        if to_cover == cover_with:
            self.caller.msg("You can't cover an item with itself!")
            return
        if cover_with.db.covered_by:
            self.caller.msg("%s is covered by something else!" % cover_with.name)
            return
        if to_cover.db.covered_by:
            self.caller.msg(
                "%s is already covered by %s." % (cover_with.name, to_cover.db.covered_by.name)
            )
            return
        if not cover_with.db.geritur:
            cover_with.wear(
                self.caller, True
            )  # Put on the item to cover with if it's not on already
        self.caller.location.msg_contents(
            "%s covers %s with %s." % (self.caller, to_cover.name, cover_with.name)
        )
        to_cover.db.covered_by = cover_with


class CmdUncover(MuxCommand):
    # JI (12/7/19) Since I'll be omitting cover for the time being, 
    # let's disable this command, too
    """
    Reveals a worn item of clothing that's currently covered up.

    Usage:
        uncover <obj>

    When you uncover an item of clothing, you allow it to appear in your
    description without having to take off the garment that's currently
    covering it. You can't uncover an item of clothing if the item covering
    it is also covered by something else.
    """

    key = "uncover"
    help_category = "clothing"

    def func(self):
        """
        This performs the actual command.
        """

        if not self.args:
            self.caller.msg("Usage: uncover <worn clothing object>")
            return

        to_uncover = self.caller.search(self.args, candidates=self.caller.contents)
        if not to_uncover:
            return
        if not to_uncover.db.geritur:
            self.caller.msg("You're not wearing %s!" % to_uncover.name)
            return
        if not to_uncover.db.covered_by:
            self.caller.msg("%s isn't covered by anything!" % to_uncover.name)
            return
        covered_by = to_uncover.db.covered_by
        if covered_by.db.covered_by:
            self.caller.msg("%s is under too many layers to uncover." % (to_uncover.name))
            return
        self.caller.location.msg_contents("%s uncovers %s." % (self.caller, to_uncover.name))
        to_uncover.db.covered_by = None


class CmdDrop(MuxCommand):
    """
    drop something

    Usage:
      relinque <rem>

    Lets you drop an object from your inventory into the
    location you are currently in.
    """

    key = "relinque"
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def func(self):
        """Implement command"""

        caller = self.caller
        if not self.args:
            caller.msg("Quid velis relinquere?")
            return

        # Because the DROP command by definition looks for items
        # in inventory, call the search function using location = caller
        obj = caller.search(
            self.args,
            location=caller,
            # JI (12/7/19) Adapting the following to Latin
            nofound_string="Non habes.",
            multimatch_string="Tot habes!",
        )
        if not obj:
            return

        # This part is new!
        # You can't drop clothing items that are covered.
        if obj.db.covered_by:
            caller.msg("You can't drop that because it's covered by %s." % obj.db.covered_by)
            return
        # JI (12/7/19) Make sure grammar is followed
        lower_case = [x.lower() for x in obj.db.formae['acc_sg']]
        if self.args.lower() not in lower_case:
            caller.msg(f"(Did you mean '{obj.db.formae['acc_sg'][0]}'?)")
            return
        # Remove clothes if they're dropped.
        if obj.db.geritur:
            obj.remove(caller, quiet=True)

        obj.move_to(caller.location, quiet=True)
        # JI (12/7/19) Adapting to Latin
        caller.msg("%s reliquisti." % (obj.db.formae['acc_sg'][0],))
        caller.location.msg_contents("%s %s reliquit." % (caller.db.form['nom_sg'][0], obj.db.formae['acc_sg'][0]), exclude=caller)
        # Call the object script's at_drop() method.
        obj.at_drop(caller)


class CmdGive(MuxCommand):
    """
    give away something to someone

    Usage:
      give <inventory obj> = <target>

    Gives an items from your inventory to another character,
    placing it in their inventory.
    """

    key = "give"
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def func(self):
        """Implement give"""

        caller = self.caller
        if not self.args or not self.rhs:
            caller.msg("Usage: give <inventory object> = <target>")
            return
        to_give = caller.search(
            self.lhs,
            location=caller,
            nofound_string="You aren't carrying %s." % self.lhs,
            multimatch_string="You carry more than one %s:" % self.lhs,
        )
        target = caller.search(self.rhs)
        if not (to_give and target):
            return
        if target == caller:
            caller.msg("You keep %s to yourself." % to_give.key)
            return
        if not to_give.location == caller:
            caller.msg("You are not holding %s." % to_give.key)
            return
        # This is new! Can't give away something that's worn. 
        # JI (12/7/19) I think I might just
        # add this last part to the already latinified give command
        if to_give.db.covered_by:
            caller.msg(
                "You can't give that away because it's covered by %s." % to_give.db.covered_by
            )
            return
        # Remove clothes if they're given.
        if to_give.db.geritur:
            to_give.remove(caller)
        to_give.move_to(caller.location, quiet=True)
        # give object
        caller.msg("You give %s to %s." % (to_give.key, target.key))
        to_give.move_to(target, quiet=True)
        target.msg("%s gives you %s." % (caller.key, to_give.key))
        # Call the object script's at_give() method.
        to_give.at_give(caller, target)


class CmdInventory(MuxCommand):
    """
    view inventory

    Usage:
      inventory
      inv

    Shows your inventory.
    """

    # Alternate version of the inventory command which separates
    # worn and carried items.

    key = "habeō"
    locks = "cmd:all()"
    arg_regex = r"$"
    help_category = 'Iussa Latīna'

    def func(self):
        """check inventory"""
        if not self.caller.contents:
            # JI (12/7/19) Adapted to Latin
            self.caller.msg("Res neque habes neque geris.")
            return

        items = self.caller.contents

        carry_table = evtable.EvTable(border="header")
        wear_table = evtable.EvTable(border="header")
        for item in items:
            if not item.db.geritur:
                if item.db.is_burning:
                    glowing = f"|y(ard{'ēns' if item.db.sexus == 'neutrum' else 'entem'})|n |C{item.db.formae['acc_sg'][0]}|n"
                    carry_table.add_row(f"{ardēns} {'(dextrā)' if item.db.tenētur == 'dextrā' else '(sinistrā)'} {item.db.desc or ''}")
                else:
                    carry_table.add_row("|C%s|n" % item.db.formae['acc_sg'][0], '(dextrā)' if item.db.tenētur == 'dextrā' else '(sinistrā)', item.db.desc or "")
        if carry_table.nrows == 0:
            carry_table.add_row("|CNihil.|n", "")
        string = "|wTenēs:\n%s" % carry_table
        for item in items:
            if item.db.geritur:
                wear_table.add_row("|C%s|n" % item.db.formae['acc_sg'][0], item.db.desc or "")
        if wear_table.nrows == 0:
            wear_table.add_row("|CNihil.|n", "")
        string += "|/|wGeris:\n%s" % wear_table
        self.caller.msg(string)


class ClothedCharacterCmdSet(default_cmds.CharacterCmdSet):
    """
    Command set for clothing, including new versions of 'give' and 'drop'
    that take worn and covered clothing into account, as well as a new
    version of 'inventory' that differentiates between carried and worn
    items.
    """

    key = "DefaultCharacter"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #
        self.add(CmdWear())
        self.add(CmdRemove())
#        self.add(CmdCover())
#        self.add(CmdUncover())
#        self.add(CmdGive())
#        self.add(CmdDrop())
        self.add(CmdInventory())

