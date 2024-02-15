#!/user/bin/env python3 -c
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

from action import Action, ActionPlan, ActionPlanAttributes
from character import Character

WAN_YE_ELEM_MASTERY = 994
WAN_YE_MING_ZUO_NUM = 2


def get_wan_ye_elem_bonus(elem_mastery=WAN_YE_ELEM_MASTERY):
    return elem_mastery * 0.04 / 100


def get_wan_ye_q_bonus(elem_mastery=WAN_YE_ELEM_MASTERY):
    if WAN_YE_MING_ZUO_NUM >= 2:
        elem_mastery += 200

    return get_wan_ye_elem_bonus(elem_mastery)


def get_wan_ye_e_bonus(elem_mastery=WAN_YE_ELEM_MASTERY):
    return get_wan_ye_elem_bonus(elem_mastery)


class WanYeAttributes(ActionPlanAttributes):
    def __init__(self, elem_mastery=WAN_YE_ELEM_MASTERY, ming_zuo_num=WAN_YE_MING_ZUO_NUM):
        self.elem_mastery = elem_mastery
        self.ming_zuo_num = ming_zuo_num
        self.bonus_end_time = None
        self.jian_kang_end_time = None
        self.q_end_time = None
        self.elem_bonus = get_wan_ye_elem_bonus(elem_mastery)

    def set_bonus_end_time(self, et):
        if self.bonus_end_time is None:
            self.bonus_end_time = et
        elif et > self.bonus_end_time:
            self.bonus_end_time = et

    def set_jian_kang_end_time(self, et):
        if self.jian_kang_end_time is None:
            self.jian_kang_end_time = et
        elif et > self.jian_kang_end_time:
            self.jian_kang_end_time = et

    def set_q_end_time(self, et):
        self.q_end_time = et

    def get_elem_bonus(self, plan: ActionPlan, target_character):
        cur_time = plan.get_current_action_time()
        if cur_time > self.bonus_end_time:
            return 0

        if self.ming_zuo_num >= 2 and self.q_end_time and cur_time < self.q_end_time:
            return get_wan_ye_elem_bonus(self.elem_mastery + 200)
        else:
            return self.elem_bonus

    def get_jian_kang(self, plan: ActionPlan):
        cur_time = plan.get_current_action_time()
        if cur_time > self.jian_kang_end_time:
            return 0

        return 0.4

    def create_e_action(self):
        return WanYe_E_Action(self)

    def create_q_action(self):
        return WanYe_Q_Action(self)


class WanYe_E_Action(Action):
    def __init__(self, attr: WanYeAttributes):
        self.attr = attr
        super().__init__("万叶E")

    def do_impl(self, plan: ActionPlan):
        self.attr.set_bonus_end_time(self.get_timestamp() + 8)
        self.attr.set_jian_kang_end_time(self.get_timestamp() + 10)
        plan.add_extra_attr(self.attr)


class WanYe_Q_Action(Action):
    def __init__(self, attr: WanYeAttributes):
        self.attr = attr
        super().__init__("万叶Q")

    def do_impl(self, plan: ActionPlan):
        cur_time = self.get_timestamp()
        self.attr.set_bonus_end_time(cur_time + 8 + 8)
        self.attr.set_jian_kang_end_time(cur_time + 10)
        self.attr.set_q_end_time(cur_time + 8)
        plan.add_extra_attr(self.attr)
