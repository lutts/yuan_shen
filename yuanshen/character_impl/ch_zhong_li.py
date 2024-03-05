#!/user/bin/env python3 -tt
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

from action import Action, ActionPlan
from attribute_hub import ActionPlanAttributeSupplier
from character import Character

class ZhongLi_E_AttributeSupplier(ActionPlanAttributeSupplier):
    def __init__(self):
        self.end_time = None

    def get_e_action(self, name: str = None):
        return ZhongLi_E_Action(name, attr=self)

    def get_jian_kang(self, plan: ActionPlan):
        cur_time = plan.get_current_action_time()
        if cur_time <= self.end_time:
            return 0.2
        else:
            return 0

class ZhongLi_E_Action(Action):
    """
    注1: 不要直接创建这个 Action 的实例，使用ZhongLi_E_AttributeSupplier.get_e_action获取

    注2: plan.add_action时，min_t 和 max_t 使用钟离点按e时按钮变灰时的时间，实际减抗开始时间会自动计算
    """
    def __init__(self, name, attr: ZhongLi_E_AttributeSupplier):
        if not name:
            name = "钟离 e"
        super().__init__(name)
        
        self.__attr = attr

    def do_impl(self, plan: ActionPlan):
        jian_kang_start_time = self.get_timestamp + 1.15
        self.__attr.end_time = jian_kang_start_time + 20
        plan.add_extra_attr(self.__attr)
