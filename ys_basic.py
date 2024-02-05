#!/user/bin/env python3 -c
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

from enum import Enum

class Ys_Elem_Type(Enum):
    HUO = "Pyro"
    SHUI = "Hydro"
    LEI = "Electro"
    BING = "Cryo"

    CAO = "Dendro"

    FENG = "Anemo"

    YAN = "Geo"
    WU_LI = "wu li"


def ys_crit_damage(non_crit_damage, crit_damage):
    return round(non_crit_damage * (1 + crit_damage))

def ys_expect_damage(non_crit_damage, crit_rate, crit_damage):
    c = min(crit_rate, 1)
    return round(non_crit_damage * (1 + c * crit_damage))
        



