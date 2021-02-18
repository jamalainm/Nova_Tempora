# file mygame/utils/latin/populate_forms.py

from utils.latin.latin_declension import DeclineNoun

def populate_forms(self,nom,gen,gender):
    """
    A helper function for at_object_creation of Latin nouns
    """

    word = DeclineNoun(nom,gen,gender)
    forms = word.make_paradigm()
    all_forms = forms
    forms = forms[2:]
    self.db.formae['dat_sg'] = [forms[0][1]]
    self.db.formae['acc_sg'] = [forms[1][1]]
    self.db.formae['abl_sg'] = [forms[2][1]]
    self.db.formae['voc_sg'] = [forms[3][1]]
    self.db.formae['nom_pl'] = [forms[4][1]]
    self.db.formae['gen_pl'] = [forms[5][1]]
    self.db.formae['dat_pl'] = [forms[6][1]]
    self.db.formae['acc_pl'] = [forms[7][1]]
    self.db.formae['abl_pl'] = [forms[8][1]]
    self.db.formae['voc_pl'] = [forms[9][1]]

    for form in all_forms:
        self.aliases.add(form[1])
