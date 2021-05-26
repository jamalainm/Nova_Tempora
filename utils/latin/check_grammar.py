# file /mygame/utils/latin/check_grammar.py
from unidecode import unidecode

def check_case(caller, obj, args, case):
    """ Notify the caller if the target was found but the wrong case was specified """

    lower_case = [x.lower() for x in obj.db.formae[case]]

    lower_case = [unidecode(x) for x in lower_case]

    if unidecode(args.strip().lower()) not in lower_case:
        # make a list of possible forms
        if len(obj.db.formae[case]) == 1:
            caller.msg(f"(Did you mean '{obj.db.formae[case][0]}'?)")
        else:
            possible_forms = f"{obj.db.formae[case][0]}"
            for f in obj.db.formae[case][1:]:
                possible_forms += f" or {f}"

            caller.msg(f"Did you mean {possible_forms}?")
        return False
