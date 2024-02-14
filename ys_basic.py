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


class Ys_Attributes:
    def __init__(self,
                 crit_rate=0.0, crit_damage=0.0,
                 hp_percent=0.0, hp=0,
                 atk_per=0.0, atk=0,
                 def_per=0.0, def_v=0,
                 elem_mastery=0, elem_bonus=0.0,
                 energy_recharge=0.0):
        self.crit_rate = crit_rate
        self.crit_damage = crit_damage
        self.hp_percent = hp_percent
        self.hp = hp
        self.atk_per = atk_per
        self.atk = atk
        self.def_per = def_per
        self.def_v = def_v
        self.elem_mastery = elem_mastery
        self.elem_bonus = elem_bonus
        self.energy_recharge = energy_recharge

    def __str__(self):
        s = ""
        if self.crit_rate:
            s += 'cc:' + str(self.crit_rate)

        if self.crit_damage:
            s += ', cd:' + str(self.crit_damage)

        if self.hp_percent:
            s += ', hpp:' + str(self.hp_percent)

        if self.hp:
            s += ', hp:' + str(self.hp)

        if self.energy_recharge:
            s += ', re:' + str(self.energy_recharge)

        if self.atk_per:
            s += ', atkp:' + str(self.atk_per)

        if self.atk:
            s += ', atk:' + str(self.atk)

        if self.def_per:
            s += ', defp:' + str(self.def_per)

        if self.def_v:
            s += ', def:' + str(self.def_v)

        if self.elem_mastery:
            s += ', elem:' + str(self.elem_mastery)

        if self.elem_bonus:
            s += ', bonus:' + str(self.elem_bonus)

        return s
    
    def __repr__(self) -> str:
        return self.__str__()


def ys_crit_damage(non_crit_damage, crit_damage):
    return round(non_crit_damage * (1 + crit_damage))

def ys_crit_damage_no_round(non_crit_damage, crit_damage):
    return non_crit_damage * (1 + crit_damage)

def ys_expect_damage(non_crit_damage, crit_rate, crit_damage):
    c = min(crit_rate, 1)
    return round(non_crit_damage * (1 + c * crit_damage))

def ys_expect_damage_no_round(non_crit_damage, crit_rate, crit_damage):
    c = min(crit_rate, 1)
    return non_crit_damage * (1 + c * crit_damage)
        



