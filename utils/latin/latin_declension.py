class DeclineNoun:
    def __init__(self,nom,gen,gender,irregular=False):
        self.nom = nom
        self.gen = gen
        self.gender = gender
        self.irregular = irregular

    def id_declension(self):

        if self.gen[-2:] == "ae":
            return [1, self.gen[:-2]]
        elif self.gen[-2:] == "is":
            return [3, self.gen[:-2]]
        elif self.gen[-2:] == "us":
            return [4, self.gen[:-2]]
        elif self.nom[-2:] == "ēs":
            return [5, self.gen[:-1]]
        elif self.gen[-2:] == "um":
            if self.nom[-2:] == "ae":
                return [6, self.nom[:-2]]
            elif self.nom[-1] == "ī":
                return [7, self.nom[:-1]]
            elif self.nom[-1] == "a":
                return [8, self.nom[:-1]]
        else:
            return [2, self.gen[:-1]]

    def first_declension(self):

        base = DeclineNoun.id_declension(self)[1] 

        endings = ['ae', 'am', 'ā', 'a', 'ae', 'ārum', 'īs', 'ās', 'īs', 'ae']

        forms = [self.nom, self.gen]

        for i in endings:
            forms.append(base + i)

        return forms

    def second_declension(self):

        base = DeclineNoun.id_declension(self)[1] 

        endings = ['ō', 'um','ō','e','ī','ōrum','īs','ōs','īs','ī']

        forms = [self.nom,self.gen]

        for i in endings:
            forms.append(base + i)

        if base[-1] == 'r':
            forms[5] = self.nom
        elif base[-1] == 'i':
            forms[5] = base[:-1] + 'ī'

        if int(self.gender) == 3:
            forms[3] = self.nom
            forms[5] = self.nom
            forms[6] = base + 'a'
            forms[9] = base + 'a'
            forms[11] = base + 'a'

        return forms

    def third_declension(self):

        from cltk.stem.latin.syllabifier import Syllabifier

        syllabifier = Syllabifier()

        vowels = ['a','e','i','o','u','a','e','i','o','u']

        base = DeclineNoun.id_declension(self)[1]

        forms = [self.nom,self.gen]

        endings = ['ī','em','e','blah','ēs','um','ibus','ēs','ibus','ēs']

        for i in endings:
            forms.append(base + i)

        forms[5] = self.nom

        nom_syllable = len(syllabifier.syllabify(self.nom))
        gen_syllable = len(syllabifier.syllabify(self.gen))

        i_stem = False

        if nom_syllable == gen_syllable:
            if self.nom[-2:] in ['is', 'es']:
                i_stem = True
        elif self.nom[-1] in ['x', 's']:
             if base[-1] not in vowels and base[-2] not in vowels:
                 i_stem = True

        if i_stem == True:

            forms[7] = forms[7][:-2] + 'i' + forms[7][-2:]

        if int(self.gender) == 3:
            forms[5] = self.nom
            forms[3] = self.nom
            forms[6] = base + 'a'
            forms[9] = base + 'a'
            forms[11] = base + 'a'
            if self.nom[-1] == 'e' or self.nom[-2:] in ['al','ar']:
                forms[4] = base + 'ī'
                forms[6] = base + 'ia'
                forms[7] = base + 'ium'
                forms[9] = base + 'ia'
                forms[11] = base + 'ia'
        return forms


    def fourth_declension(self):

        base = DeclineNoun.id_declension(self)[1]

        endings = ['uī','um','ū','us','ūs','uum','ibus','ūs','ibus','ūs']

        forms = [self.nom,self.gen]

        for i in endings:
            forms.append(base + i)

        if int(self.gender) == 3:
            forms[3] = self.nom
            forms[2] = base + 'u'
            forms[5] = self.nom
            forms[6] = base + 'ua'
            forms[9] = base + 'ua'
            forms[11] = base + 'ua'

        return forms

    def fifth_declension(self):

        base = DeclineNoun.id_declension(self)[1] 

        base = base[:-1] + "e"

        endings = ['i', 'm', '', 's', 's', 'rum', 'bus', 's', 'bus', 's']

        forms = [self.nom,self.gen]

        for i in endings:
            forms.append(base + i)

        forms[3] = forms[3][:-2] + 'em'

        if base[-2] != 'i':
            forms[1] = forms[1][:-2] + 'ei'
            forms[2] = forms[2][:-2] + 'ei'

        return forms

    def first_plural(self):

        base = DeclineNoun.id_declension(self)[1]

        endings = ['ae','arum','is','as','is','ae','ae','arum','is','as','is','ae']

        forms = []

        for i in endings:
            forms.append(base + i)

        return forms

    def second_plural_masc(self):

        base = DeclineNoun.id_declension(self)[1]

        endings = ['i','orum','is','os','is','i','i','orum','is','os','is','i']

        forms = []

        for i in endings:
            forms.append(base + i)

        return forms

    def second_plural_neut(self):

        base = DeclineNoun.id_declension(self)[1]

        endings = ['a','orum','is','a','is','a','a','orum','is','a','is','a']

        forms = []

        for i in endings:
            forms.append(base + 1)

        return forms

    def make_paradigm(self):
        
        labels = ['nom_sg','gen_sg','dat_sg','acc_sg','abl_sg','voc_sg','nom_pl','gen_pl','dat_pl','acc_pl','abl_pl','voc_pl']

        forms = []

        if DeclineNoun.id_declension(self)[0] == 1:
            forms = self.first_declension()
        elif DeclineNoun.id_declension(self)[0] == 2:
            forms = DeclineNoun.second_declension(self)
        elif DeclineNoun.id_declension(self)[0] == 3:
            forms = DeclineNoun.third_declension(self)
        elif DeclineNoun.id_declension(self)[0] == 4:
            forms = DeclineNoun.fourth_declension(self)
        elif DeclineNoun.id_declension(self)[0] == 5:
            forms = DeclineNoun.fifth_declension(self)
        elif DeclineNoun.id_declension(self)[0] == 6:
            forms = DeclineNoun.first_plural(self)
        elif DeclineNoun.id_declension(self)[0] == 7:
            forms = DeclineNoun.second_plural_masc(self)
        else:
            forms = DeclineNoun.second_plural_neut(self)

        declension = []
        for index,value in enumerate(labels):
            declension.append((value,forms[index]))

        return declension
