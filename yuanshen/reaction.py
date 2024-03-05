#!/user/bin/env python3 -c
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

from enum import Enum
from basic import Ys_Elem_Type
from character import Character
from monster import Monster

class Ys_Reaction:
    def __init__(self, ch: Character, monster: Monster):
        self.ch = ch
        self.monster = monster

    def do_damage(self, base_damage, bonus):
        pass


class Ys_No_Reaction(Ys_Reaction):
    def __init__(self, ch: Character, monster: Monster):
        super().__init__(ch, monster)

    def do_damage(self, base_damage, bonus):
        damage = base_damage * (1 + bonus)
        return self.monster.attacked(damage)


class Ys_Reaction_ZengFu(Ys_Reaction):
    def __init__(self, ch: Character, monster: Monster, extra_multiplier = 0):
        """
        extra_multiplier: 除基础、精通之外的额外反应加成，例如魔女4件套效果
        """
        self.validate_character(ch)
        super().__init__(ch, monster)
        self.extra_multiplier = extra_multiplier

    def do_damage(self, base_damage, bonus):
        elem_mastery = self.ch.get_elem_mastery()
        em_bonus = 2.78 * elem_mastery / (elem_mastery + 1400)
        base_multiplier = self.get_base_multiplier()

        damage = base_damage * base_multiplier * (1 + em_bonus + self.extra_multiplier)
        damage *= (1 + bonus)
        damage = self.monster.attacked(damage)
        return damage
    
    def validate_character(self, ch: Character):
        pass
    
    def get_base_multiplier(self):
        pass

class Ys_Reaction_ZhengFa(Ys_Reaction_ZengFu):
    def validate_character(self, ch: Character):
        if ch.elem_type not in [Ys_Elem_Type.SHUI, Ys_Elem_Type.HUO]:
            raise Exception("蒸发反应只有水和火")

    def get_base_multiplier(self):
        if self.ch.elem_type is Ys_Elem_Type.SHUI:
            return 2
        else:
            return 1.5

class Ys_Reaction_RongHua(Ys_Reaction_ZengFu):
    def validate_character(self, ch: Character):
        if ch.elem_type not in [Ys_Elem_Type.HUO, Ys_Elem_Type.BING]:
            raise Exception("融化反应只有火和冰")

    def get_base_multiplier(self):
        if self.ch.elem_type is Ys_Elem_Type.HUO:
            return 2
        else:
            return 1.5
        
class JiHua_Type(Enum):
    Chao_JiHua = "超激化"
    Man_JiHua = "蔓激化"

class Ys_Reaction_JiHua(Ys_Reaction):
    def __init__(self, ch: Character, monster: Monster, ji_hua_type: JiHua_Type, extra_multiplier = 0):
        """
        extra_multiplier: 除基础、精通之外的额外反应加成，例如魔女4件套效果
        """
        super().__init__(ch, monster)
        self.ji_hua_type = ji_hua_type
        self.extra_multiplier = extra_multiplier

    def do_damage(self, base_damage, bonus):
        # 注：只考虑90级，打激化反应请将角色升级到90级
        level_multiplier = 1446.85

        if self.ji_hua_type is JiHua_Type.Chao_JiHua:
            type_multiplier = 1.15
        else:
            type_multiplier = 1.25

        elem_mastery = self.ch.get_elem_mastery()
        em_bonus = 5 * elem_mastery / (elem_mastery + 1200)

        ji_hua_damage = level_multiplier * type_multiplier * (1 + em_bonus + self.extra_multiplier)

        damage = (base_damage + ji_hua_damage) * (1 + bonus)
        damage = self.monster.attacked(damage)

        return damage
