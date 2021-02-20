# file /mygame/utils/latin/check_grammar.py

def check_case(caller, obj, args, case):
    """ Notify the caller if the target was found but the wrong case was specified """

    lower_case = [x.lower() for x in obj.db.formae[case]]
    caller.msg(f"For {case} there are this many things: {len(obj.db.formae[case])}")
    if args.strip().lower() not in lower_case:
        caller.msg(f"(Did you mean '{obj.db.formae[case][0]}'?)")
        return False
