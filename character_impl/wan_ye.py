#!/user/bin/env python3 -c
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

import random
from ys_basic import Ys_Elem_Type
from ys_weapon import Ys_Weapon
from action import Action, ActionPlan
from attribute_hub import ActionPlanAttributeSupplier
from character import Character


class Wan_Ye_Ch(ActionPlanAttributeSupplier, Character, name="枫原万叶", 
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
    
    def get_elem_bonus(self, plan: ActionPlan, target_character):
        cur_time = plan.get_current_action_time()
        if cur_time > self.bonus_end_time:
            plan.debug("万叶增伤效果已经在{}消失".format(self.bonus_end_time))
            return 0
        
        return self.tian_fu_bonus

    def get_jian_kang(self, plan: ActionPlan):
        cur_time = plan.get_current_action_time()
        if cur_time > self.jian_kang_end_time:
            plan.debug(f"万叶减抗效果已经在{self.jian_kang_end_time}消失")
            return 0

        return 0.4
    
    def __add_kuo_san_action(self, plan: ActionPlan, t):
        action = WanYe_Kuo_San_Action(self)
        action.set_timestamp(t)
        plan.append_action(action)
    
    def do_e(self, plan: ActionPlan, base_time,
             switch_to_e_start=(0.2, 0.234),
             e_start_to_up_kuo_san=(0.216, 0.283),
             e_start_to_atk_button=(0.85, 0.885),
             atk_button_to_down_kuo_san=(0.184, 0.267),
             atk_button_to_switch=(0, 0)):
        """
        base_time: 切换到万叶的时间
        switch_to_e_start: 切万叶 -> 普攻按钮变为下落图标的时间，这个时间视为开始 e 的时间
        e_start_to_up_kuo_san: 开始 e -> e上升段触发扩散**出伤**时间
        e_start_to_atk_button: 开始 e -> 普攻按钮重新变为普攻图标的时间
        atk_button_to_down_kuo_san: 普攻下落 -> 扩散**出伤**时间
        atk_button_to_switch: 普攻下落 -> 切下一个角色的时间
        """
        plan.add_switch_action(self, base_time)

        e_start_time = base_time + random.uniform(*switch_to_e_start)
        up_kuo_san_time = e_start_time +  random.uniform(*e_start_to_up_kuo_san)
        self.__add_kuo_san_action(plan, up_kuo_san_time)

        atk_button_time = e_start_time + random.uniform(*e_start_to_atk_button)
        down_kuo_san_time = atk_button_time + random.uniform(*atk_button_to_down_kuo_san)
        self.__add_kuo_san_action(plan, down_kuo_san_time)

        switch_to_next_ch_time = atk_button_time + random.uniform(*atk_button_to_switch)
        return switch_to_next_ch_time

    def do_q(self, plan: ActionPlan, base_time,
             q_start_to_kuo_san=(1.466, 1.5),
             q_end_to_first_liu_feng=(0.733, 0.817),
             q_end_to_switch=(0, 0),
             liu_feng_interval=(1.966, 2.0),
             liu_feng_kuo_san_delay=(0.183, 0.217)):
        """
        q_start_to_kuo_san: 大招动画开始 -> 扩散出伤
        q_end_to_first_liu_feng: 大招动画结束 -> 第一次流风开始
        q_end_to_switch: 大招动画结束 -> 切人
        liu_feng_interval: 流风间隔
        liu_feng_kuo_san_delay: 流风开始 -> 流风扩散出伤
        """
        plan.add_switch_action(self, base_time)

        # 点按大招切万叶到万叶放大的时间基本是固定的
        q_start_time = base_time + 0.067
        plan.q_animation_start(self, self, q_start_time)

        # FIXME: 目前还没有手段能测出二命的200精通何时失效，目前观察到的数据大约是 11.6
        self.ming_2_end_time = q_start_time + 11.6

        q_kuo_san_time = q_start_time + random.uniform(*q_start_to_kuo_san)
        self.__add_kuo_san_action(plan, q_kuo_san_time)

        # 大招动画的时间也基本是固定的
        q_end_time = q_start_time + 1.55
        plan.q_animation_end(self, self, q_end_time)

        switch_to_next_ch_time = q_end_time + random.uniform(*q_end_to_switch)

        first_liu_feng_time = q_end_time + random.uniform(*q_end_to_first_liu_feng)
        first_liu_feng_kuo_san = first_liu_feng_time + random.uniform(*liu_feng_kuo_san_delay)
        self.__add_kuo_san_action(plan, first_liu_feng_kuo_san)

        last_liu_feng_time = first_liu_feng_time
        for _ in range(0, 4):
            liu_feng_time = last_liu_feng_time + random.uniform(*liu_feng_interval)
            if liu_feng_time - first_liu_feng_time > 8:
                liu_feng_time = first_liu_feng_time + 8

            liu_feng_kuo_san = liu_feng_time + random.uniform(*liu_feng_kuo_san_delay)
            self.__add_kuo_san_action(plan, liu_feng_kuo_san)
        
        return switch_to_next_ch_time
    

class WanYe_Kuo_San_Action(Action):
    def __init__(self, wan_ye: Wan_Ye_Ch):
        super().__init__("万叶触发扩散")
        self.wan_ye = wan_ye

    def do_impl(self, plan: ActionPlan):
        cur_time = self.get_timestamp()
        if not plan.monster.do_kuo_san(cur_time):
            return
        
        em = self.wan_ye.get_elem_mastery()
        if self.wan_ye.ming_zuo_num >= 2 and cur_time <= self.wan_ye.ming_2_end_time:
            em += 200

        self.wan_ye.bonus_end_time = cur_time + 8
        self.wan_ye.tian_fu_bonus = em * 0.04 / 100

        # 减抗需要万叶在前台
        if self.wan_ye.is_in_foreground():
            self.wan_ye.jian_kang_end_time = cur_time + 10

        plan.add_extra_attr(self.wan_ye)
