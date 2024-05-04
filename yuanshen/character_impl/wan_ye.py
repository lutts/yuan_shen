#!/user/bin/env python3 -c
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

import random
from ..elem_type import Ys_Elem_Type
from ..weapon import Ys_Weapon
from ..action import Action, ActionPlan
from ..buff_manager import Buff
from ..character import Character

class Wan_Ye_Bonus_Buff(Buff):
    def get_elem_bonus(self, plan: ActionPlan, target_character):
        cur_time = plan.current_action_time()
        if cur_time > self.bonus_end_time:
            plan.debug("万叶增伤效果已经在{}消失".format(self.bonus_end_time))
            return 0
        
        return self.tian_fu_bonus

class Feng_Tao_Buff(Buff):
    def get_jian_kang(self, plan: ActionPlan):
        cur_time = plan.current_action_time()
        if cur_time > self.jian_kang_end_time:
            plan.debug(f"万叶减抗效果已经在{self.jian_kang_end_time}消失")
            return 0

        return 0.4
     
class Wan_Ye_Elem_Mastery_Buff(Buff):
    def get_elem_mastery(self, plan: ActionPlan, target_character):
        if self.ming_zuo_num < 2:
            return 0
        
        cur_time = plan.current_action_time()
        if self.ming_2_end_time and cur_time < self.ming_2_end_time:
            return 200
        else:
            return 0

class Wan_Ye_Ch(Buff, Character, name="枫原万叶", 
                elem_type=Ys_Elem_Type.FENG, ming_zuo_num=2, q_energy=60):
    def __init__(self, elem_mastery = 994, weapon: Ys_Weapon=None):
        """
        注意：如果传入的武器有精通属性，那么传给 elem_mastery 的值里需要减去武器的精通值
        """
        super().__init__(elem_mastery=elem_mastery, weapon=weapon)

        self.ming_2_end_time = 0
        self.bonus_end_time = 0
        self.tian_fu_bonus = 0

        self.jian_kang_end_time =0

    def get_e_bonus(self):
        return self.get_elem_mastery() * 0.04 / 100
    
    def get_q_bonus(self):
        em = self.get_elem_mastery()
        if self.ming_zuo_num >= 2:
            em += 200

        return em * 0.04 / 100    
            
    def __add_kuo_san_action(self, plan: ActionPlan, t):
        action = WanYe_Kuo_San_Action(self)
        action.set_timestamp(t)
        plan.append_action(action)

    def switch_to_e_interval(self):
        return random.uniform(0.167, 0.234)
    
    def do_e(self, plan: ActionPlan, t, down_kuo_san=True):
        """
        down_kuo_san: 如果 True, 则以下落触发的扩散为准，如果 False, 则以上升时触发的扩散为准
        """
        if not down_kuo_san:
            up_hit = t + 0.116
            self.__add_kuo_san_action(plan, up_hit)

        # atk_btn_again = t + random.uniform(0.85, 0.883)
        atk_btn_again = t + 0.867

        if down_kuo_san:
            down_hit = atk_btn_again + 0.083
            self.__add_kuo_san_action(plan, down_hit)

        # 切下一个角色的时间
        # TODO: eq连在考虑实现吗？
        switch_to_next_ch_time = atk_btn_again + random.uniform(0.366, 0.7)
        return switch_to_next_ch_time

    def do_q(self, plan: ActionPlan, t, add_all_liu_feng=False):
        """
        add_all_liu_feng: 如果为 False(默认), 则只添加最后一次流风的 action, 如果为 True, 则添加所有流风的 action
        """

        plan.q_animation_start(self, self, t)

        # FIXME: 目前还没有手段能测出二命的200精通何时失效，目前观察到的数据大约是 11.6
        self.ming_2_end_time = t + 11.6

        q_hit = t + 1.2
        self.__add_kuo_san_action(plan, q_hit)

        # 大招动画的时间也基本是固定的
        q_end_time = t + 1.55
        plan.q_animation_end(self, self, q_end_time)

        # TODO: 是否要考虑 qe 连招？
        switch_to_next_ch_time = t + random.uniform(1.767, 1.883)

        # 万叶 q 后续的流风有以下特性：
        # * 如果怪身上有元素附着，则先造成染伤，触发元素反应，再造成风伤，除非反应有元素残留，否则不会造成扩散
        # * 如果怪身上没有元素附着，则先造成风伤，后造成染伤，不会造成扩散

        first_liu_feng_hit = q_end_time + random.uniform(2.334, 2.434)
        max_liu_feng_hit = first_liu_feng_hit + 8

        if add_all_liu_feng:
            self.__add_kuo_san_action(plan, first_liu_feng_hit)

        last_liu_feng_hit = first_liu_feng_hit
        for _ in range(0, 4):
            liu_feng_hit  = last_liu_feng_hit + random.uniform(1.966, 2.033)
            if liu_feng_hit > max_liu_feng_hit:
                liu_feng_hit = max_liu_feng_hit

            if add_all_liu_feng:
                self.__add_kuo_san_action(plan, liu_feng_hit)

            last_liu_feng_hit = liu_feng_hit

        if not add_all_liu_feng:
            self.__add_kuo_san_action(plan, last_liu_feng_hit)
        
        return switch_to_next_ch_time


class WanYe_Kuo_San_Action(Action):
    def __init__(self, wan_ye: Wan_Ye_Ch):
        super().__init__("万叶触发扩散")
        self.wan_ye = wan_ye

    def do_impl(self, plan: ActionPlan):
        cur_time = self.get_timestamp()
        em = self.wan_ye.get_elem_mastery()
        if self.wan_ye.ming_zuo_num >= 2 and cur_time <= self.wan_ye.ming_2_end_time:
            em += 200

        self.wan_ye.bonus_end_time = cur_time + 8
        self.wan_ye.tian_fu_bonus = em * 0.04 / 100

        # 减抗需要万叶在前台
        if self.wan_ye.is_in_foreground():
            self.wan_ye.jian_kang_end_time = cur_time + 10

        plan.add_extra_attr(self.wan_ye)
