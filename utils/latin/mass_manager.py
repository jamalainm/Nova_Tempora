# file mygame/utils/latin/mass_manager.py
"""
Some helper functions to add and remove an object's mass from
a character's current load
"""

def add_mass(recipient, target):
    recipient.db.toll_fer['ferēns'] += target.db.physical['mass']

def remove_mass(recipient, target):
    recipient.db.toll_fer['ferēns'] -= target.db.physical['mass']
