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

def put_into_hand(recipient, target):
    """
    change status on <recipient.db.manibus_plēnīs> and <recipient.db.manibus_vacuīs> 
    and <target.db.tenētur>, preferring dominant hand.
    """

    if recipient.db.handedness == "dextrā":
        dom_hand = "dextrā"
        off_hand = "sinistrā"
    else:
        dom_hand = "sinistrā"
        off_hand = "dextrā"

    if dom_hand in recipient.db.manibus_vacuīs:
        target.db.tenētur = dom_hand
        recipient.db.manibus_vacuīs.remove(dom_hand)
        recipient.db.manibus_plēnīs.append(dom_hand)
    else:
        target.tenētur = off_hand
        recipient.db.manibus_vacuīs.remove(off_hand)
        recipient.db.manibus_vacuīs.append(off_hand)

def take_out_of_hand(loser, target):
    """
    change status on <loser.db.manibus_plēnīs> and <loser.db.manibus_vacuīs>
    and <target.db.tenētur>
    """

    holding_hand = target.db.tenētur
    loser.db.manibus_plēnīs.remove(holding_hand)
    loser.db.manibus_vacuīs.append(holding_hand)
    target.db.tenētur = False

