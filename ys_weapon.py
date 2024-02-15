#!/user/bin/env python3 -c
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

from ys_basic import Ys_Weapon
from character import Character

class Ti_Cao_Zhi_Dao_Guang(Ys_Weapon, name="薙草之稻光"):
    atk_per_multiplier = [
        28/100, # 1
        35/100, # 2
        42/100, # 3
        39/100, # 4
        56/100, # 5
    ]

    atk_per_max = [
        80/100, # 1
        90/100, # 2
        100/100, # 3
        110/100, # 4
        120/100, # 5
    ]

    energy_recharge_bonus = [
        30/100, # 1 
        35/100, # 2
        40/100, # 3
        45/100, # 4
        50/100, # 5
    ]

    def apply_static_attributes(self, character: Character, teammates=None):
        character.add_energy_recharge(self.energy_recharge)

    def get_atk_per_bonus(self, character: Character):
        energy_recharge = character.get_energy_recharge()
        return min(Ti_Cao_Zhi_Dao_Guang.atk_per_max[self.jing_lian_rank - 1],
                      (energy_recharge - 100) * Ti_Cao_Zhi_Dao_Guang.atk_per_multiplier[self.jing_lian_rank - 1] / 100)

    def apply_combat_attributes(self, character: Character, teammates=None):
        character.add_atk_per(self.get_atk_per_bonus(character))

    def apply_passive(self, character: Character, action_plan=None):
        old_atk_per = self.get_atk_per_bonus(character)
        character.add_energy_recharge(Ti_Cao_Zhi_Dao_Guang.energy_recharge_bonus[self.jing_lian_rank - 1])
        new_atk_per = self.get_atk_per_bonus(character)
        if new_atk_per > old_atk_per:
            character.add_atk_per(new_atk_per - old_atk_per)
        