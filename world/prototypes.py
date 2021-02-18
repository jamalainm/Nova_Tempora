# file mygame/world/prototypes.py
"""
Prototypes

A prototype is a simple way to create individualized instances of a
given `Typeclass`. For example, you might have a Sword typeclass that
implements everything a Sword would need to do. The only difference
between different individual Swords would be their key, description
and some Attributes. The Prototype system allows to create a range of
such Swords with only minor variations. Prototypes can also inherit
and combine together to form entire hierarchies (such as giving all
Sabres and all Broadswords some common properties). Note that bigger
variations, such as custom commands or functionality belong in a
hierarchy of typeclasses instead.

Example prototypes are read by the `@spawn` command but is also easily
available to use from code via `evennia.spawn` or `evennia.utils.spawner`.
Each prototype should be a dictionary. Use the same name as the
variable to refer to other prototypes.

Possible keywords are:
    prototype_parent - string pointing to parent prototype of this structure.
    key - string, the main object identifier.
    typeclass - string, if not set, will use `settings.BASE_OBJECT_TYPECLASS`.
    location - this should be a valid object or #dbref.
    home - valid object or #dbref.
    destination - only valid for exits (object or dbref).

    permissions - string or list of permission strings.
    locks - a lock-string.
    aliases - string or list of strings.

    ndb_<name> - value of a nattribute (the "ndb_" part is ignored).
    any other keywords are interpreted as Attributes and their values.

See the `@spawn` command and `evennia.utils.spawner` for more info.

"""
BAG = {
        "key":"saccus",
        "typeclass":"typeclasses.latin_clothing.Clothing",
        "formae": {"nom_sg":["saccus"],"gen_sg":["sacci"]},
        "sexus":"māre",
        "desc":"A bag",
        "genus_vestīmentōrum":"back",
        "can_hold":True,
        'physical':{"material":"linen","rigid":False,"volume":0.75,"mass":0.45},
        'container':{'max_vol':24,'rem_vol':24,"x":0.3,"y":0.4,"z":0.2}
        }
BANDEAU = {
        "key":"strophium",
        "typeclass":"typeclasses.latin_clothing.Clothing",
        "formae":{"nom_sg":["strophium"],"gen_sg":["strophii"]},
        "sexus":"neutrum",
        "desc":"A bandeau",
        "genus_vestīmentōrum":"undershirt",
        'physical':{"material":"linen","rigid":False,"volume":0.5,'mass':0.45}
        }

UNDERWEAR = {
        "key":"subligāculum",
        "typeclass":"typeclasses.latin_clothing.Clothing",
        "formae":{"nom_sg":["subligāculum"],"gen_sg":["subligāculī"]},
        "sexus":"neutrum",
        "desc":"Briefs",
        "genus_vestīmentōrum":"underpants",
        'physical':{"material":"linen","rigid":False,"volume":0.5,'mass':0.45}
        }

SWORD = {
        "key":"gladius",
        "typeclass":"typeclasses.rēs.Rēs",
        "formae":{"nom_sg":["gladius"],"gen_sg":["gladiī"]},
        "sexus":"māre",
        "desc":"A shortsword",
        "physical":{"material":"iron","rigid":True,"x":0.04,"y":0.65,"z":0.003,"mass":0.6,"volume":0.08},
        "damage":6
        }

WOOL = {
        "key":"lāna",
        "typeclass":"typeclasses.rēs.Rēs",
        "formae":{"nom_sg":["lāna"],"gen_sg":["lānae"]},
        "sexus":"muliebre",
        "desc":"A small bale of wool",
        'physical':{"material":"wool","rigid":False,"volume":23,"mass":3},
        }
CLOAK = {
        "key":"pallium",
        "typeclass":"typeclasses.latin_clothing.Clothing",
        "genus_vestīmentōrum":"cloak",
        "formae":{"nom_sg":["pallium"],"gen_sg":["palliī"]},
        "sexus":"neutrum",
        "desc":"A simple, well-woven cloth, to wrap about your top",
        "physical":{"material":"wool","rigid":False,"x":3.04,"y":1.52,"z":0.005,"mass":3,"volume":23}
        }
HAT = {
        "key":"petasus",
        "typeclass": "typeclasses.latin_clothing.Clothing",
        "genus_vestīmentōrum":"hat",
        "formae":{"nom_sg":["petasus"],"gen_sg":["petasī"]},
        "sexus":"māre",
        "desc":"A broad-brimmed, traveler's hat",
        "physical":{"material":"wool","rigid":False,"mass":0.17,"volume":2.21}
        }

SANDALS = {
        "key":"soleae",
        "typeclass":"typeclasses.latin_clothing.Clothing",
        "genus_vestīmentōrum":"shoes",
        "formae":{"nom_sg":["soleae"],"gen_sg":["soleārum"]},
        "sexus":"muliebre",
        "desc":"A pair of simple sandals",
        "physical":{"material":"leather","rigid":True,"x":0.107,"y":0.253,"z":0.0026,"mass":0.48,"volume":0.07}
        }

TUNIC = {
        "key":"tunica",
        "typeclass":"typeclasses.latin_clothing.Clothing",
        "genus_vestīmentōrum":"fullbody",
        "formae":{"nom_sg":["tunica"],"gen_sg":["tunicae"]},
        "sexus":"muliebre",
        "desc":"A sleeveless, knee-length tunic",
        "physical":{"material":"linen","rigid":False,"mass":1,"volume":2}
        }

LAMP = {
        "key":"lūmen",
        "typeclass":"typeclasses.rēs.Flammable",
        "formae":{"nom_sg":["lūmen"],"gen_sg":["lūminis"]},
        "sexus":"neutrum",
        "desc":"a small, simple, terracotta oil lamp",
        "physical":{"material":"clay","rigid":True,"mass":0.15,"volume":0.2,'x':0.05,'y':0.05,'z':0.08}
        }

VESTAL_HEARTH = {
        "key":"Focus Vestae",
#        "location":"#266",
        "typeclass":"typeclasses.rēs.Hearth",
        "formae":{"nom_sg":["focus"],"gen_sg":["focī"]},
        "sexus":"māre",
        "desc":"A large, marble hearth; it's diameter is nearly 1 |mpassus|n (pace).",
        "physical":{"material":"marble","rigid":True,"mass":8512,"volume":3140}
        }

PLAIN_HEARTH = {
        "key":"focus",
        "typeclass":"typeclasses.rēs.Hearth",
        "formae":{"nom_sg":["focus"],"gen_sg":["focī"]},
        "sexus":"māre",
        "desc":"A large hearth; it's diameter is nearly 1 |mpassus|n (pace).",
        "physical":{"material":"stone","rigid":True,"mass":8512,"volume":3140}
        }
# from random import randint
#
# GOBLIN = {
# "key": "goblin grunt",
# "health": lambda: randint(20,30),
# "resists": ["cold", "poison"],
# "attacks": ["fists"],
# "weaknesses": ["fire", "light"]
# }
#
# GOBLIN_WIZARD = {
# "prototype_parent": "GOBLIN",
# "key": "goblin wizard",
# "spells": ["fire ball", "lighting bolt"]
# }
#
# GOBLIN_ARCHER = {
# "prototype_parent": "GOBLIN",
# "key": "goblin archer",
# "attacks": ["short bow"]
# }
#
# This is an example of a prototype without a prototype
# (nor key) of its own, so it should normally only be
# used as a mix-in, as in the example of the goblin
# archwizard below.
# ARCHWIZARD_MIXIN = {
# "attacks": ["archwizard staff"],
# "spells": ["greater fire ball", "greater lighting"]
# }
#
# GOBLIN_ARCHWIZARD = {
# "key": "goblin archwizard",
# "prototype_parent" : ("GOBLIN_WIZARD", "ARCHWIZARD_MIXIN")
# }
