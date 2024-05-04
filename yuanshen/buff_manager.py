#!/user/bin/env python3 -c
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

class Buff:
    def __init__(self, buff_type):
        self.buff_type = buff_type

    # buff 施加者
    def get_caster(self):
        return None

    # buff 层数
    def get_layer(self):
        return 1

    def get_duration(self):
        pass

    def get_start_time(self):
        return None
    
    def get_crit_rate(self, plan, target_character):
        return 0

    def get_crit_damage(self, plan, target_character):
        return 0

    def get_hp_percent(self, plan, target_character):
        return 0

    def get_hp(self, plan, target_character):
        return 0

    def get_atk_per(self, plan, target_character):
        return 0

    def get_atk(self, plan, target_character):
        return 0

    def get_def_per(self, plan, target_character):
        return 0

    def get_def(self, plan, target_character):
        return 0

    def get_elem_mastery(self, plan, target_character):
        return 0

    def get_elem_bonus(self, plan, target_character):
        return 0
    
    def get_healing_bonus(self, plan, target_character):
        return 0
    
    def get_incoming_healing_bonus(self, plan, target_character):
        return 0

    def get_energy_recharge(self, plan, target_character):
        return 0

    def get_normal_a_bonus(self, plan, target_character):
        return 0

    def get_charged_a_bonus(self, plan, target_character):
        return 0

    def get_plunging_bonus(self, plan, target_character):
        return 0

    def get_e_bonus(self, plan, target_character):
        return 0

    def get_q_bonus(self, plan, target_character):
        return 0

    def get_jian_kang(self, plan):
        return 0

    def get_jian_fang(self, plan):
        return 0

    def get_ignore_fang(self, plan):
        return 0


class BuffManager:
    def __init__(self):
        self.plan = None
        self.__buff_lst: list[Buff] = None

    def init(self, plan):
        self.plan = plan
        self.__buff_lst: list[Buff] = []

    def reset(self):
        self.plan = None
        self.__buff_lst = None

    def has_buff(self):
        return self.__buff_lst

    def add_buff(self, buff: Buff):
        if buff not in self.__buff_lst:
            self.__buff_lst.append(buff)

    def remove_buff(self, buff: Buff):
        self.__buff_lst.remove(buff)

    def get_crit_rate(self, ch):
        return sum([buff.get_crit_rate(self.plan, ch) for buff in self.__buff_lst])

    def get_crit_damage(self, ch):
        return sum([buff.get_crit_damage(self.plan, ch) for buff in self.__buff_lst])

    def get_max_hp(self, ch):
        extra_hp_per = sum([buff.get_hp_percent(self.plan, ch) for buff in self.__buff_lst])
        extra_hp = sum([buff.get_hp(self.plan, ch) for buff in self.__buff_lst])

        return extra_hp + ch.get_hp().get_base_hp() * extra_hp_per

    def get_atk(self, ch):
        extra_atk_per = sum([buff.get_atk_per(self.plan, ch) for buff in self.__buff_lst])
        extra_atk = sum([buff.get_atk(self.plan, ch) for buff in self.__buff_lst])

        return extra_atk + ch.get_base_atk() * extra_atk_per

    def get_defence(self, ch):
        extra_def_per = sum([buff.get_def_per(self.plan, ch) for buff in self.__buff_lst])
        extra_def = sum([buff.get_def(self.plan, ch) for buff in self.__buff_lst])

        return extra_def + ch.get_base_defence() * extra_def_per

    def get_elem_mastery(self, ch):
        return sum([buff.get_elem_mastery(self.plan, ch) for buff in self.__buff_lst])
    
    def get_healing_bonus(self, ch):
        return sum([buff.get_healing_bonus(self.plan, ch) for buff in self.__buff_lst])
    
    def get_incoming_healing_bonus(self, ch):
        return sum([buff.get_incoming_healing_bonus(self, ch) for buff in self.__buff_lst])

    def get_energy_recharge(self, ch):
        return sum([buff.get_energy_recharge(self.plan, ch) * 100 for buff in self.__buff_lst])

    def get_normal_a_bonus(self, ch):
        return sum([buff.get_elem_bonus(self.plan, ch) + buff.get_normal_a_bonus(self.plan, ch) for buff in self.__buff_lst])

    def get_charged_a_bonus(self, ch):
        return sum([buff.get_elem_bonus(self.plan, ch) + buff.get_charged_a_bonus(self.plan, ch) for buff in self.__buff_lst])

    def get_plunging_bonus(self, ch):
        return sum([buff.get_elem_bonus(self.plan, ch) + buff.get_plunging_bonus(self.plan, ch) for buff in self.__buff_lst])

    def get_e_bonus(self, ch):
        return sum([buff.get_elem_bonus(self.plan, ch) + buff.get_e_bonus(self.plan, ch) for buff in self.__buff_lst])

    def get_q_bonus(self, ch):
        return sum([buff.get_elem_bonus(self.plan, ch) + buff.get_q_bonus(self.plan, ch) for buff in self.__buff_lst])
    
    def get_jian_kang(self):
        return sum([buff.get_jian_kang(self.plan) for buff in self.__buff_lst])
    
    def get_jian_fang(self):
        return sum([buff.get_jian_fang(self.plan) for buff in self.__buff_lst])
    
    def get_ignore_fang(self):
        return sum([buff.get_ignore_fang(self.plan) for buff in self.__buff_lst])