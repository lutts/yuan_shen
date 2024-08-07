#!/user/bin/env python3 -tt
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

from yuanshen.buff_manager import BuffManager
from ..elem_type import Ys_Elem_Type
from ..action import Action, ActionPlan
from ..buff_manager import Buff, BuffAttrs
from ..character import Character


class Zhong_Li_Ch(Character, name="钟离", elem_type=Ys_Elem_Type.YAN):
    def do_e(self, plan: ActionPlan, t):
        jian_kang_start = t + 1.034
        jian_kang_action = Zhong_Li_Jian_Kang_Action(jian_kang_start)


class Zhong_Li_Jian_Kang_Buff(Buff, attrs=BuffAttrs.JIAN_KANG):
    def on_update(self, buff_manager: BuffManager, plan: ActionPlan, cur_time):
        plan.monster.add_jian_kang(0.2)


class Zhong_Li_Jian_Kang_Action(Action):
    def __init__(self, start_time):
        super().__init__("钟离e", start_time)

    def do(self, plan: ActionPlan):
        buff = Zhong_Li_Jian_Kang_Buff(start_time=self.start_time, duration=20.722)
        plan.add_buff(buff)
