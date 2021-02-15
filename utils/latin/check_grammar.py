# file /mygame/utils/latin/check_grammar.py

def check_case(caller, obj, args, case):
    """ Notify the caller if the target was found but the wrong case was specified """

    lower_case = [x.lower() for x in obj.db.forms['acc_sg']]
    if args.strip().lower() not in lower_case:
        caller.msg(f"(Did you mean '{obj.db.forms['acc_sg'][0]}'?)")
        return False
