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


class Wan_Ye_Ch(Buff, Character, name="枫原万叶", 
                elem_type=Ys_Elem_Type.FENG, ming_zuo_num=2, q_energy=60):
    def __init__(self, elem_mastery = 994, weapon: Ys_Weapon=None):
        """
        注意：如果传入的武器有精通属性，那么传给 elem_mastery 的值里需要减去武器的精通值
        """
        super().__init__(elem_mastery=elem_mastery, weapon=weapon)

    def get_tian_fu_bonus(self):
        return self.get_elem_mastery() * 0.04 / 100
            
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

        # 二命的结束时间无法准确测量，目前观测到的数据显示第五次流风之后 1.5 秒效果消失
        ming_2_buff = Wan_Ye_Ming_2_Buff("wan ye 2 ming", t, last_liu_feng_hit + 1.5, self)
        plan.buff_mamager.add_buff(ming_2_buff)
        
        return switch_to_next_ch_time


class Wan_Ye_Bonus_Buff(Buff):
    def get_elem_bonus(self, plan: ActionPlan, target_character):
        wan_ye: Wan_Ye_Ch = self.creator
        return wan_ye.get_tian_fu_bonus()
        

class Feng_Tao_Buff(Buff):
    def get_jian_kang(self, plan: ActionPlan):
        return 0.4


class Wan_Ye_Ming_2_Buff(Buff):
    def get_elem_mastery(self, plan: ActionPlan, target_character: Character):
        if target_character.is_in_foreground() or target_character is self.creator:
            # 万叶自身及前台能吃到二命加成
            return 200
        
        return 0


class WanYe_Kuo_San_Action(Action):
    def __init__(self, wan_ye: Wan_Ye_Ch):
        super().__init__("万叶触发扩散")
        self.wan_ye = wan_ye

    def do_impl(self, plan: ActionPlan):
        cur_time = self.get_timestamp()
        bonus_buf = Wan_Ye_Bonus_Buff("wan ye bonus", cur_time, cur_time + 8, creator=self.wan_ye)
        plan.buff_mamager.add_buff(bonus_buf)

        # 减抗需要万叶在前台
        if self.wan_ye.is_in_foreground():
            feng_tao_buff = Feng_Tao_Buff("feng tao", cur_time, cur_time + 10)
            plan.buff_mamager.add_buff(feng_tao_buff)
