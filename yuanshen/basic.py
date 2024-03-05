#!/user/bin/env python3 -c
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

from enum import Enum
import weakref

class Ys_Elem_Type(Enum):
    HUO = "Pyro"
    SHUI = "Hydro"
    LEI = "Electro"
    BING = "Cryo"

    CAO = "Dendro"

    FENG = "Anemo"

    YAN = "Geo"
    WU_LI = "wu li"


class Ys_Attribute_Supplier:
    def __init__(self,
                 crit_rate=0.0, crit_damage=0.0,
                 hp_percent=0.0, hp=0,
                 atk_per=0.0, atk=0,
                 def_per=0.0, def_v=0,
                 elem_mastery=0, elem_bonus=0.0,
                 energy_recharge=0.0,

                 normal_a_bonus = 0.0,
                 charged_a_bonus = 0.0,
                 plunging_bonus = 0.0,
                 e_bonus = 0.0,
                 q_bonus = 0.0):
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

        self.normal_a_bonus = normal_a_bonus
        self.charged_a_bonus = charged_a_bonus
        self.plunging_bonus = plunging_bonus
        self.e_bonus = e_bonus
        self.q_bonus = q_bonus

    def apply_static_attributes(self, character):
        """
        设置没有和怪物进入战斗时的属性
        """
        pass

    def apply_combat_attributes(self, character):
        """
        设置和怪物进入战斗时的属性
        """
        pass

    def apply_passive(self, character, action_plan=None):
        """
        有些属性是有条件触发的, 例如芙芙专武需要扣血叠层

        action_plan 如果为 None，需要假设条件达成，对 character 直接进行属性设置
        """
        pass

    def __str__(self):
        attrs = []
        if self.crit_rate:
            attrs.append('cc:' + str(self.crit_rate))

        if self.crit_damage:
            attrs.append('cd:' + str(self.crit_damage))

        if self.hp_percent:
            attrs.append('hpp:' + str(self.hp_percent))

        if self.hp:
            attrs.append('hp:' + str(self.hp))

        if self.energy_recharge:
            attrs.append('re:' + str(self.energy_recharge))

        if self.atk_per:
            attrs.append('atkp:' + str(self.atk_per))

        if self.atk:
            attrs.append('atk:' + str(self.atk))

        if self.def_per:
            attrs.append('defp:' + str(self.def_per))

        if self.def_v:
            attrs.append('def:' + str(self.def_v))

        if self.elem_mastery:
            attrs.append('elem:' + str(self.elem_mastery))

        if self.elem_bonus:
            attrs.append('bonus:' + str(self.elem_bonus))

        return ", ".join(attrs)
    
    def __repr__(self) -> str:
        return self.__str__()


class Ys_Weapon(Ys_Attribute_Supplier):
    def __init_subclass__(cls, name, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.name = name
    
    def __init__(self, base_atk, jing_lian_rank=1, **kwargs):
        """
        owner: 持有者
        base_atk: 基础攻击力
        jing_lian_rank: 精炼等阶

        kwargs: 副词条及被动提供的相关**静态**属性
        """
        if jing_lian_rank not in [1, 2, 3, 4, 5]:
            raise Exception("精炼等阶只能是1, 2, 3, 4, 5")
        
        self.__owner = None
        self.base_atk = base_atk
        self.jing_lian_rank = jing_lian_rank

        super().__init__(**kwargs)

    def set_owner(self, owner):
        self.__owner = weakref.ref(owner)

    def get_owner(self):
        return self.__owner()

def ys_crit_damage(non_crit_damage, crit_damage):
    return int(non_crit_damage * (1 + crit_damage))

def ys_crit_damage_no_round(non_crit_damage, crit_damage):
    return non_crit_damage * (1 + crit_damage)

def ys_expect_damage(non_crit_damage, crit_rate, crit_damage):
    c = min(crit_rate, 1)
    return int(non_crit_damage * (1 + c * crit_damage))

def ys_expect_damage_no_round(non_crit_damage, crit_rate, crit_damage):
    c = min(crit_rate, 1)
    return non_crit_damage * (1 + c * crit_damage)
        



