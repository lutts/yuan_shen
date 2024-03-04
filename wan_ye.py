#!/user/bin/env python3 -c
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

from ys_basic import Ys_Elem_Type
from ys_weapon import Ys_Weapon
from action import Action, ActionPlan
from attribute_hub import ActionPlanAttributeSupplier
from character import Character

class Wan_Ye_Ch(Character, name="枫原万叶", elem_type=Ys_Elem_Type.FENG, ming_zuo_num=2, q_energy=60):
    def __init__(self, elem_mastery = 994, weapon: Ys_Weapon=None):
        super().__init__(elem_mastery=elem_mastery, weapon=weapon)

    def get_e_bonus(self):
        return self.get_elem_mastery() * 0.04 / 100
    
    def get_q_bonus(self):
        em = self.get_elem_mastery()
        if self.ming_zuo_num >= 2:
            em += 200

        return em * 0.04 / 100
    
    def get_e_action(self):
        return super().get_e_action()
    
    def get_q_action(self):
        return super().get_q_action()



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


class WanYeAttributes(ActionPlanAttributeSupplier):
    def __init__(self, elem_mastery=WAN_YE_ELEM_MASTERY, ming_zuo_num=WAN_YE_MING_ZUO_NUM):
        self.elem_mastery = elem_mastery
        self.ming_zuo_num = ming_zuo_num

        self.__bonus_end_time = None
        self.jian_kang_end_time = None
        self.q_end_time = None

        self.elem_bonus = get_wan_ye_elem_bonus(elem_mastery)
        self.ming_2_bonus = get_wan_ye_elem_bonus(elem_mastery + 200)

    # 大招增伤时间能持续到大招结束后8秒，如果大招结束前e，大概率是不能延长增伤持续时间的，只会刷新风套减抗时间
    def set___bonus_end_time(self, et):
        if self.__bonus_end_time is None:
            self.__bonus_end_time = et
        elif et > self.__bonus_end_time:
            self.__bonus_end_time = et

    def set_q_end_time(self, et):
        self.q_end_time = et

    def get_elem_bonus(self, plan: ActionPlan, target_character):
        cur_time = plan.get_current_action_time()
        if cur_time > self.__bonus_end_time:
            plan.debug("万叶增伤效果已经在{}消失".format(self.__bonus_end_time))
            return 0

        if self.ming_zuo_num >= 2 and self.q_end_time and cur_time < self.q_end_time:
            return self.ming_2_bonus
        else:
            return self.elem_bonus

    def get_jian_kang(self, plan: ActionPlan):
        cur_time = plan.get_current_action_time()
        if cur_time > self.jian_kang_end_time:
            plan.debug(f"万叶减抗效果已经在{self.jian_kang_end_time}消失")
            return 0

        return 0.4

    def create_e_action(self, use_e_start_time=False):
        """
        如果 plan.add_action时使用的时间是点按e后普攻键变下落图标的时间，则 use_e_start_time 传 True
        """
        return WanYe_E_Action(self)

    def create_q_action(self):
        return WanYe_Q_Action(self)


class WanYe_E_Action(Action):
    """
    注：不要直接创建这个类的实例
    """
    def __init__(self, attr: WanYeAttributes):
        self.attr = attr
        self.__use_e_start_time = False

        super().__init__("万叶E扩散")

    def use_e_start_time(self):
        self.__use_e_start_time = True

    def set_timestamp(self, t):
        if self.__use_e_start_time:
            pass
        else:
            pass

        super().set_timestamp(t)



    def do_impl(self, plan: ActionPlan):
        self.attr.set_bonus_end_time(self.get_timestamp() + 8)
        self.attr.jian_kang_end_time = self.get_timestamp() + 10
        plan.add_extra_attr(self.attr)


class WanYe_Q_Action(Action):
    """
    注：不要直接创建这个类的实例
    """
    def __init__(self, attr: WanYeAttributes):
        self.attr = attr
        super().__init__("万叶Q扩散")

    def do_impl(self, plan: ActionPlan):
        cur_time = self.get_timestamp()
        # 增伤持续到大招结束后 8 秒
        self.attr.set_bonus_end_time(cur_time + 8 + 8)
        self.attr.jian_kang_end_time = cur_time + 10
        self.attr.q_end_time = cur_time + 8
        plan.add_extra_attr(self.attr)
