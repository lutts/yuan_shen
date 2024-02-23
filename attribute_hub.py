#!/user/bin/env python3 -c
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

from monster import Monster

class ActionPlanAttributeSupplier:
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


class AttributeHub:
    def __init__(self, plan):
        self.plan = plan
        self.__extra_attrs: list[ActionPlanAttributeSupplier] = []

    def has_extra_attr(self):
        return self.__extra_attrs

    def add_extra_attr(self, attr: ActionPlanAttributeSupplier):
        if attr not in self.__extra_attrs:
            self.__extra_attrs.append(attr)

    def remove_extra_attr(self, attr: ActionPlanAttributeSupplier):
        self.__extra_attrs.remove(attr)

    def get_crit_rate(self, ch):
        return sum([attr.get_crit_rate(self.plan, ch) for attr in self.__extra_attrs])

    def get_crit_damage(self, ch):
        return sum([attr.get_crit_damage(self.plan, ch) for attr in self.__extra_attrs])

    def get_max_hp(self, ch):
        extra_hp_per = sum([attr.get_hp_percent(self.plan, ch) for attr in self.__extra_attrs])
        extra_hp = sum([attr.get_hp(self.plan, ch) for attr in self.__extra_attrs])

        return extra_hp + ch.get_hp().get_base_hp() * extra_hp_per

    def get_atk(self, ch):
        extra_atk_per = sum([attr.get_atk_per(self.plan, ch) for attr in self.__extra_attrs])
        extra_atk = sum([attr.get_atk(self.plan, ch) for attr in self.__extra_attrs])

        return extra_atk + ch.get_base_atk() * extra_atk_per

    def get_defence(self, ch):
        extra_def_per = sum([attr.get_def_per(self.plan, ch) for attr in self.__extra_attrs])
        extra_def = sum([attr.get_def(self.plan, ch) for attr in self.__extra_attrs])

        return extra_def + ch.get_base_defence() * extra_def_per

    def get_elem_mastery(self, ch):
        return sum([attr.get_elem_mastery(self.plan, ch) for attr in self.__extra_attrs])

    def get_energy_recharge(self, ch):
        return sum([attr.get_energy_recharge(self.plan, ch) * 100 for attr in self.__extra_attrs])

    def get_normal_a_bonus(self, ch):
        return sum([attr.get_elem_bonus(self.plan, ch) + attr.get_normal_a_bonus(self.plan, ch) for attr in self.__extra_attrs])

    def get_charged_a_bonus(self, ch):
        return sum([attr.get_elem_bonus(self.plan, ch) + attr.get_charged_a_bonus(self.plan, ch) for attr in self.__extra_attrs])

    def get_plunging_bonus(self, ch):
        return sum([attr.get_elem_bonus(self.plan, ch) + attr.get_plunging_bonus(self.plan, ch) for attr in self.__extra_attrs])

    def get_e_bonus(self, ch):
        return sum([attr.get_elem_bonus(self.plan, ch) + attr.get_e_bonus(self.plan, ch) for attr in self.__extra_attrs])

    def get_q_bonus(self, ch):
        return sum([attr.get_elem_bonus(self.plan, ch) + attr.get_q_bonus(self.plan, ch) for attr in self.__extra_attrs])

    def get_kang_xin_multiplier(self, monster: Monster):
        extra_jian_kang = sum([attr.get_jian_kang(self.plan) for attr in self.__extra_attrs])
        return monster.get_jian_kang_bonus(extra_jian_kang)

    def get_fang_yu_multiplier(self, monster: Monster):
        extra_jian_fang = sum([attr.get_jian_fang(self.plan) for attr in self.__extra_attrs])
        extra_ignore_def = sum([attr.get_ignore_fang(self.plan) for attr in self.__extra_attrs])
        return monster.get_fang_yu_xi_shu(extra_jian_fang=extra_jian_fang,
                                                extra_ignore_defence_ratio=extra_ignore_def)