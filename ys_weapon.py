#!/user/bin/env python3 -c
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

from ys_basic import Ys_Weapon
from character import Character, Character_HP_Change_Data
from action import Action, ActionPlan

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

    def apply_static_attributes(self, character: Character):
        character.add_energy_recharge(self.energy_recharge)

    def get_atk_per_bonus(self, character: Character):
        energy_recharge = character.get_energy_recharge()
        return min(Ti_Cao_Zhi_Dao_Guang.atk_per_max[self.jing_lian_rank - 1],
                      (energy_recharge - 100) * Ti_Cao_Zhi_Dao_Guang.atk_per_multiplier[self.jing_lian_rank - 1] / 100)

    def apply_combat_attributes(self, character: Character):
        character.add_atk_per(self.get_atk_per_bonus(character))

    def apply_passive(self, character: Character, action_plan=None):
        old_atk_per = self.get_atk_per_bonus(character)
        character.add_energy_recharge(Ti_Cao_Zhi_Dao_Guang.energy_recharge_bonus[self.jing_lian_rank - 1])
        new_atk_per = self.get_atk_per_bonus(character)
        if new_atk_per > old_atk_per:
            character.add_atk_per(new_atk_per - old_atk_per)
        

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


class Jing_Shui_Liu_Yong_Zhi_Hui(Ys_Weapon, name="静水流涌之辉"):
    E_BONUS_MULTIPLIER = [8/100, 10/100, 12/100, 14/100, 16/100]
    HP_BONUS_MULTIPLIER = [14/100, 17.5/100, 21/100, 24.5/100, 28/100]

    def __init__(self, base_atk, jing_lian_rank=1, **kwargs):
        super().__init__(base_atk, jing_lian_rank=jing_lian_rank, **kwargs)

        self.__e_bonus_level = 0
        self.__e_bonus_last_change_time = 0

        self.__hp_bonus_level = 0
        self.__hp_bonus_last_change_time = 0

    @property
    def e_bonus_level(self):
        return self.__e_bonus_level
    
    @property
    def hp_bonus_level(self):
        return self.__hp_bonus_level
    
    def apply_static_attributes(self, character: Character):
        character.add_crit_damage(0.882)
    
    def apply_passive(self, character: Character, action_plan: ActionPlan=None):
        if not action_plan:
            character.add_e_bonus(Jing_Shui_Liu_Yong_Zhi_Hui.E_BONUS_MULTIPLIER[self.jing_lian_rank - 1])
            character.get_hp().modify_max_hp_per(Jing_Shui_Liu_Yong_Zhi_Hui.HP_BONUS_MULTIPLIER[self.jing_lian_rank - 1])
        else:
            action_plan.add_consume_hp_callback(self.on_hp_changed)
            action_plan.add_regenerate_hp_callback(self.on_hp_changed)

    def on_hp_changed(self, plan: ActionPlan, source: Character, targets_with_data: list[Character_HP_Change_Data]):
        teammate_processed = False
        owner = self.get_owner()
        for tdata in targets_with_data:
            if tdata.character is owner:
                self.increase_e_bonus_level(plan)
            elif not teammate_processed:
                self.increase_hp_bonus_level(plan)
                teammate_processed = True

        if self.__hp_bonus_level >= 2 and self.__e_bonus_level >= 3:
            plan.remove_consume_hp_callback(self.on_hp_changed)
            plan.remove_regenerate_hp_callback(self.on_hp_changed)
                      
    def increase_e_bonus_level(self, plan: ActionPlan):
        if self.__e_bonus_level >= 3:
            return
        
        cur_time = plan.get_current_action_time()

        if self.__e_bonus_last_change_time and (cur_time - self.__e_bonus_last_change_time < 0.2):
            return

        self.__e_bonus_last_change_time = cur_time
        self.__e_bonus_level += 1

        action = Increase_JingShui_E_Bonus_Level_Action(self)
        action.set_timestamp(cur_time + plan.get_effective_delay())
        plan.insert_action_runtime(action)

    def increase_hp_bonus_level(self, plan: ActionPlan):
        if self.__hp_bonus_level >= 2:
            return
        
        cur_time = plan.get_current_action_time()

        if self.__hp_bonus_last_change_time and (cur_time - self.__hp_bonus_last_change_time < 0.2):
            # 有0.2秒的CD
            return

        self.__hp_bonus_last_change_time = cur_time
        self.__hp_bonus_level += 1

        action = Increase_JingShui_Hp_Level_Action(self)
        action.set_timestamp(cur_time + plan.get_effective_delay())
        plan.insert_action_runtime(action)
    
class Increase_JingShui_Hp_Level_Action(Action):
    def __init__(self, supervisor: Jing_Shui_Liu_Yong_Zhi_Hui):
        super().__init__("静水流涌之辉生命值叠层")
        self.supervisor = supervisor

    def do_impl(self, plan: ActionPlan):
        owner: Character = self.supervisor.owner
        multiplier = Jing_Shui_Liu_Yong_Zhi_Hui.HP_BONUS_MULTIPLIER[self.supervisor.jing_lian_rank - 1]
        owner.get_hp().modify_max_hp_per(multiplier)
        self.debug("静水流涌之辉生命叠一层，目前层数: %d",  self.supervisor.hp_bonus_level)
        if Action.enable_record:
            plan.damage_record_hp()


class Increase_JingShui_E_Bonus_Level_Action(Action):
    def __init__(self, supervisor: Jing_Shui_Liu_Yong_Zhi_Hui):
        super().__init__("静水流涌之辉战技增伤叠层")
        self.supervisor = supervisor

    def do_impl(self, plan: ActionPlan):
        owner: Character = self.supervisor.owner
        multiplier = Jing_Shui_Liu_Yong_Zhi_Hui.E_BONUS_MULTIPLIER[self.supervisor.jing_lian_rank - 1]
        owner.add_e_bonus(multiplier)
        self.debug("静水流涌之辉战技叠一层，目前层数: %d", self.supervisor.e_bonus_level)
        # FIXME:
        # plan.damage_record_bonus()