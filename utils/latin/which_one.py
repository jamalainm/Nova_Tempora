# file mygame/utils/latin/which_one.py
from unidecode import unidecode

def which_one(args, caller, stuff):
    """
    Bypass the native process for dealing with multiple items matching
    an argument, using a Latin interface instead.
    """

    # For specifying a particular item when there is more than one
    if '-' in args:
        thing = args.split('-')
        args = thing[-1].strip().lower()

        # collect objects that have the same name
        same = []
        for item in stuff:
            characteristics = item.aliases.all()
            [x.lower() for x in characteristics]

            characteristics = [unidecode(x) for x in characteristics]
            
            if unidecode(args) in characteristics:
                same.append(item)

        # if nothing was found, provide feedback
        if len(same) == 0:
            caller.msg("Nōn invēnistī!")
            return None, args

        # if fewer objects are found than specified, provide feedback
        if len(same) < int(thing[0]):
            caller.msg(f"Nōn sunt {thing[0].strip()}, sed {len(same)}!")
            return None, args

        # match the number with the item
        target = same[int(thing[0]) - 1]
        return target, args

    # If the user assumes there is only one of the particular type
    else: 
        same = []
        args = args.strip().lower()

        for item in stuff:
            characteristics = [item.key] + item.aliases.all()

            [x.lower() for x in characteristics]

            characteristics = [unidecode(x) for x in characteristics]

            if unidecode(args) in characteristics:
                same.append(item)

        # if nothing is found, provide feedback
        if len(same) == 0:
            caller.msg("Nōn invēnistī!")
            return None, args

        # if more than one item is found, provide feedback
        elif len(same) != 1:
            caller.msg(f"Sunt {len(same)}. Ecce:")
            for index, item in enumerate(same):
                caller.msg(f"{index +1}-{item}")
            return None, args

        # if the item is found and there's just the one, success!
        else:
            target = same[0]
            return target, args
