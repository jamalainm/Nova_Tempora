# file mygame/utils/latin/adjective_agreement.py

from utils.latin.adjective_inflections import us_a_um_inflections

def us_a_um(case,gender):
    ending = us_a_um_inflections[case][gender]
    return ending
