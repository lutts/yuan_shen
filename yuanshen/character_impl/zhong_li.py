#!/user/bin/env python3 -tt
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

from ..action import Action, ActionPlan
from ..buff_manager import Buff
from ..character import Character

class ZhongLi_E_AttributeSupplier(Buff):
    def __init__(self):
        self.end_time = None

    def get_e_action(self, name: str = None):
        return ZhongLi_E_Action(name, attr=self)

    def get_jian_kang(self, plan: ActionPlan):
        cur_time = plan.current_action_time
        if cur_time <= self.end_time:
            return 0.2
        else:
            return 0

class ZhongLi_E_Action(Action):
    def __init__(self, name, attr: ZhongLi_E_AttributeSupplier):
        if not name:
            name = "钟离 e"
        super().__init__(name)
        
        self.__attr = attr

    def do_impl(self, plan: ActionPlan):
        jian_kang_start_time = self.get_timestamp + 1.15
        self.__attr.end_time = jian_kang_start_time + 20
        plan.add_extra_attr(self.__attr)
