#!/user/bin/env python3 -c
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

import random
from ..elem_type import Ys_Elem_Type
from ..weapon import Ys_Weapon
from ..action import Action, ActionPlan
from ..buff_manager import Buff, BuffAttrs, BuffManager
from ..character import Character


class Wan_Ye_Ch(Character, name="枫原万叶", 
                elem_type=Ys_Elem_Type.FENG, ming_zuo_num=2, q_energy=60):
    @staticmethod
    def create_instance(elem_mastery = 994, weapon: Ys_Weapon = None):
        if weapon:
            elem_mastery -= weapon.get_elem_mastery()
        return Wan_Ye_Ch(base_hp=13348, base_atk=297, base_defence=807,
                         elem_mastery=elem_mastery, weapon=weapon)

    def get_tian_fu_bonus(self):
        return self.get_elem_mastery(False) * 0.04 / 100
            
    def __add_kuo_san_action(self, plan: ActionPlan, start_time):
        action = WanYe_Kuo_San_Action(self, start_time)
        plan.add_action(action)

    def __do_raw_e(self, plan: ActionPlan, t, down_kuo_san=True):
        if not down_kuo_san:
            up_hit = t + 0.116
            self.__add_kuo_san_action(plan, up_hit)

        # atk_btn_again = t + random.uniform(0.85, 0.883)
        atk_btn_again = t + 0.867

        if down_kuo_san:
            down_hit = atk_btn_again + 0.083
            self.__add_kuo_san_action(plan, down_hit)

        return atk_btn_again
    
    def do_e(self, plan: ActionPlan, t, down_kuo_san=True):
        """
        * t: 切万叶出来的时间

        * down_kuo_san: 如果 True, 则以下落触发的扩散为准，如果 False, 则以上升时触发的扩散为准

        * 返回值：切下一个角色的时间
        """
        plan.add_switch_action(self, t)

        e_start = t + random.uniform(0.167, 0.234)

        atk_btn_again = self.__do_raw_e(plan, e_start, down_kuo_san)

        # 切下一个角色的时间
        switch_to_next_ch_time = atk_btn_again + random.uniform(0.366, 0.7)
        return switch_to_next_ch_time

    def __do_raw_q(self, plan: ActionPlan, q_start_time):
        plan.q_animation_start(self, self, q_start_time)

        q_hit = q_start_time + 1.2
        q_kuo_san = q_hit + 0.2
        self.__add_kuo_san_action(plan, q_kuo_san)

        # 大招动画的时间也基本是固定的(TODO：在按钮变亮前就会受伤，0.2是预估的，需要实测)
        q_end_time = q_start_time + 1.55 - 0.2
        plan.q_animation_end(self, self, q_end_time)

        # 万叶 q 后续的流风有以下特性：
        # * 如果怪身上有元素附着，则先造成染伤，触发元素反应，再造成风伤，除非反应有元素残留，否则不会造成扩散
        # * 如果怪身上没有元素附着，则先造成风伤，后造成染伤，不会造成扩散

        liu_feng_hit = q_start_time + random.uniform(2.334, 2.434)
        max_liu_feng_hit = liu_feng_hit + 8

        self.__add_kuo_san_action(plan, liu_feng_hit)

        for _ in range(0, 5):
            liu_feng_hit += random.uniform(1.966, 2.033)
            if liu_feng_hit > max_liu_feng_hit:
                liu_feng_hit = max_liu_feng_hit

            self.__add_kuo_san_action(plan, liu_feng_hit)

        # 二命的结束时间无法准确测量，目前观测到的数据显示第五次流风之后 1.5 秒效果消失
        ming_2_buff = Wan_Ye_Ming_2_Buff(q_start_time, liu_feng_hit + 1.5, self)
        plan.add_buff(ming_2_buff)

    def do_q(self, plan: ActionPlan, t):
        """
        * t: 切万叶出来的时间
        * ignore_liu_feng: 是否忽略五次流风扩散，如果能确定五次流风期间万叶都不会切到前台来，则可以忽略，否则不能忽略
        * 返回值：切下一个角色的时机
        """
        t = self.q_switch(plan, t)

        self.__do_raw_q(plan, t)

        # TODO: 是否要考虑 qe 连招？
        switch_to_next_ch_time = t + random.uniform(1.767, 1.883)
        return switch_to_next_ch_time
    
    def do_eq(self, plan: ActionPlan, t):
        pass

    def do_qe(self, plan: ActionPlan, t):
        pass


class Wan_Ye_Bonus_Buff(Buff, attrs=BuffAttrs.ELEM_BONUS, depend_attrs=BuffAttrs.ELEM_MASTERY, re_convertable=False):
    def __init__(self, start_time: float, bonus, wan_ye):
        super().__init__(start_time, duration=8, creator=wan_ye)
        self.bonus = bonus
    
    def on_update(self, buff_manager: BuffManager, plan: ActionPlan, cur_time, expired_layer):
        for ch in plan.characters:
            ch.un_convertable_attrs.elem_bonus += self.bonus
        

class Feng_Tao_Buff(Buff, attrs=BuffAttrs.JIAN_KANG):
    def on_update(self, buff_manager: BuffManager, plan: ActionPlan, cur_time, expired_layer):
        plan.monster.buff_attrs.jian_kang += 0.4


class Wan_Ye_Ming_2_Buff(Buff, attrs=BuffAttrs.ELEM_MASTERY):
    def on_update(self, buff_manager: BuffManager, plan: ActionPlan, cur_time, expired_layer):
        for ch in plan.characters:
            if ch.is_in_foreground():
                ch.buff_attrs.elem_mastery += 200
            elif ch is self.creator:
                ch.buff_attrs.elem_mastery += 200


class WanYe_Kuo_San_Action(Action):
    def __init__(self, wan_ye: Wan_Ye_Ch, start_time):
        super().__init__("万叶触发扩散", start_time)
        self.wan_ye = wan_ye

    def do(self, plan: ActionPlan):
        cur_time = self.start_time

        # 增伤可以后台触发
        bonus = self.wan_ye.get_tian_fu_bonus()
        plan.add_buff(Wan_Ye_Bonus_Buff(cur_time, bonus, self.wan_ye))

        # 减抗需要万叶在前台
        if self.wan_ye.is_in_foreground():
            feng_tao_buff = Feng_Tao_Buff(cur_time, cur_time + 10)
            plan.add_buff(feng_tao_buff)
