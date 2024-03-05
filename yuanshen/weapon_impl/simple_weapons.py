#!/user/bin/env python3 -c
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

from .context import Ys_Weapon
from .context import Character


class Yu_Huo(Ys_Weapon, name="渔获"):
    q_bonus = [
        16/100, 20/100, 24/100, 28/100, 32/100
    ]

    crit_rate_bonus = [
        6/100, 7.5/100, 9/100, 10.5/100, 12/100
    ]
    def apply_static_attributes(self, character: Character):
        character.add_energy_recharge(self.energy_recharge)
    
    def apply_passive(self, character: Character, action_plan=None):
        character.add_q_bonus(Yu_Huo.q_bonus[self.jing_lian_rank - 1])
        character.add_crit_rate(Yu_Huo.crit_rate_bonus[self.jing_lian_rank - 1])


class Tian_Kong_Zhi_Yi(Ys_Weapon, name="天空之翼"):
    crit_damage_bonus = [
        20/100, # 1
        25/100, # 2
        30/100, # 3
        35/100, # 4
        40/100, # 5
    ]

    def apply_static_attributes(self, character: Character):
        character.add_crit_rate(self.crit_rate)
        character.add_crit_damage(Tian_Kong_Zhi_Yi.crit_damage_bonus[self.jing_lian_rank - 1])


class Ji_Li_Sword(Ys_Weapon, name="祭礼剑"):
    def apply_static_attributes(self, character: Character):
        character.add_energy_recharge(self.energy_recharge)


class Wu_Qie_Zhi_Hui_Guang(Ys_Weapon, name="雾切之回光"):
    elem_bonus_bonus =  [
        12/100, 15/100, 18/100, 21/100, 24/100
    ]

    ba_yin_bonus = [
        (8/100, 16/100, 28/100), # 1
        (10/100, 20/100, 35/100), # 2
        (12/100, 24/100, 42/100), # 3
        (14/100, 28/100, 49/100), # 4
        (16/100, 32/100, 56/100), # 5
    ]
    def apply_static_attributes(self, character: Character):
        character.add_crit_damage(self.crit_damage)
        character.add_all_bonus(Wu_Qie_Zhi_Hui_Guang.elem_bonus_bonus[self.jing_lian_rank - 1])
    
    def apply_passive(self, character: Character, action_plan=None):
        # TODO: 绫华配戴时能完美吃到被动，别的角色如何处理？
        character.add_all_bonus(Wu_Qie_Zhi_Hui_Guang.ba_yin_bonus[self.jing_lian_rank - 1][2])


class Ruo_Shui_Arrow(Ys_Weapon, name="若水"):
    MAX_HP_BONUS = [16/100, 20/100, 24/100, 28/100, 32/100]
    DAMAGE_BONUS = [20/100, 25/100, 30/100, 35/100, 40/100]

    def apply_static_attributes(self, character: Character):
        character.add_crit_damage(self.crit_damage)
        character.get_hp().modify_max_hp_per(Ruo_Shui_Arrow.MAX_HP_BONUS[self.jing_lian_rank - 1])
        character.add_all_bonus(Ruo_Shui_Arrow.DAMAGE_BONUS[self.jing_lian_rank - 1])


