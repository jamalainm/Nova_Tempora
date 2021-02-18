# file mygame/commands/iussa_latīna.py

"""
Iussa Latīna

Iussa Latīna describe the input the account can do to the game
as a player character. Iussa are added to the LatinCmdSet

"""

from utils.latin.adjective_agreement import us_a_um
from utils.latin.which_one import which_one
from utils.latin.check_grammar import check_case

from evennia import default_cmds
from evennia import CmdSet
from evennia.utils import create
from evennia.commands.default import muxcommand

from commands.command import Command

class MuxCommand(muxcommand.MuxCommand):
    """
    Right now all this does is display health status after changing
    clothes.
    """
    
    def at_post_cmd(self):
        """
        This hook is called after the command has finished executing
        (after self.func()).
        """
        caller = self.caller
        if caller.db.pv:
            prompt = "\n|wVita: %i/%i) |n" % (caller.db.pv['nunc'],caller.db.pv['max'])

            caller.msg(prompt)

class Creātur(Command):
    """
    Create an object with grammatical gender, a nominative singular,
    and a genitive singular form.

    Usage:
        creātur <nom_sg> <gen_sg> <gender> <typeclass>

    """

    key = "creātur"
    locks = "cmd:all()"
    help_category = "Iussa Administrātōrum"
    auto_help = True

    def parse(self):

        arglist = [arg.strip() for arg in self.args.split()]

        self.arglist = arglist

    def func(self):
        """
        Creates the object.
        """

        caller = self.caller

        # Make sure the proper number of arguments are used
        if not self.args or len(self.arglist) != 4:
            caller.msg("Scrībe: creātur <nōminātīvus cāsus> <genetīvus cāsus> <sexus> <genus>")
            return

        # Make sure a proper gender is accepted
        sexus = self.arglist[2]
        if sexus not in ['māre','muliebre','neutrum']:
            caller.msg("Estne sexus 'māre' an 'muliebre' an 'neutrum'?")
            return

        # Make sure an acceptable genitive is submitted
        genitive = self.arglist[1]
        if not genitive.endswith('ae') and not genitive.endswith('ī') and not genitive.endswith('is') and not genitive.endswith('ūs') and not genitive.endswith('um'):
            caller.msg("Eheu, ista forma cāsūs genitīvī nōn est accipienda.")
            return

        # create the object
        name = self.arglist[0]
#        typeclass = 'rēs'
        typeclass = f"typeclasses.rēs.{self.arglist[3]}"
        
        # create object (if not a valid typeclass, the default
        # object typeclass will automatically be used)
#        lockstring = self.new_obj_lockstring.format(id=caller.id)
        obj = create.create_object(
                typeclass,
                name,
                caller,
                home=caller,
#                locks=lockstring,
                report_to=caller,
                attributes=[
                    ('lang', 'latin'),
                    ('sexus', sexus),
                    ('formae',{'nom_sg': [name], 'gen_sg': [genitive]}),
                    ]
                )
        message = f"Ā tē nova {obj.typename} creāta est: {obj.name}."
        if not obj:
            return
        if not obj.db.desc:
            obj.db.desc = "Nihil ēgregiī vidēs."

        caller.msg(message)

class Relinque(Command):
    """
    Get rid of something
    
    Usage:
        relinque <rem>

    Lets you move an object from your inventory into the location
    that you currently occupy.
    """

    key = "relinque"
    locks = "cmd:all()"
    help_category = "Iussa Latīna"
    auto_help = True

    def parse(self):

        self.arglist = [arg.strip() for arg in self.args.split()]

    def func(self):
        """ Implement command """

        caller = self.caller
        if not self.arglist or len(self.arglist) != 1:
            caller.msg("Quid relinquere velis?")
            return

        # Ensure the intended object is targeted
        stuff = caller.contents
        obj, self.args = which_one(self.args, caller, stuff)
        if not obj:
            return

        # Check the grammar
        if check_case(caller, obj, self.args, 'acc_sg') == False:
            return

        # Call the object's scripts at_before_drop() method
        if not obj.at_before_drop(caller):
            return

        # Adding the following to deal with clothing:
        if obj.db.held:
            obj.db.held = False
        if obj.db.worn:
            obj.remove(caller,quiet=True)

        # Move object to caller's location
        obj.move_to(caller.location, quiet=True)
        # The below is for when we have encumberance implemented
#        caller.db.lift_carry['current'] -= obj.db.physical['mass']
        caller.msg(f"{obj.db.formae['acc_sg'][0]} relīquistī.")
        caller.location.msg_contents(f"{caller.name} {obj.db.formae['acc_sg'][0]} relīquit.", exclude=caller)

        # call the object script's at_drop() method.
        obj.at_drop(caller)

class IussaLatīnaCmdSet(default_cmds.CharacterCmdSet):
    """
    Command set for the Latin equivalents of default commands.
    """

    key = "DefaultCharacter"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        self.add(Relinque())

class IussaAdministrātōrumCmdSet(default_cmds.CharacterCmdSet):
    """
    Command set for building and creating Latin objects.
    """

    key = "DefaultCharacter"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        self.add(Creātur())
