# file mygame/utils/latin/free_hands.py

"""
A helper function that returns the number of free
hands a character has.
"""

def free_hands(character,possessions):

    hands = ['sinistrā','dextrā']
    number_of_hands_free = 2
    held_items = []

    for possession in possessions:
        if possession.db.tenētur:
            if possession.db.tenētur in hands:
                number_of_hands_free -= 1
                hands.remove(possession.db.tenētur)
                held_items.append(possession)
            elif held == 'ambābus':
                number_of_hands_free -= 2
                held_items.append(possession)
                hands = []

    return [hands, number_of_hands_free]
