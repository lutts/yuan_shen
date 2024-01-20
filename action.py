#!/user/bin/env python3 -tt
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

import logging
import typing
import random

from monster import Monster

ActionPlan = typing.NewType("ActionPlan", None)

class ActionTimestampException(Exception):
    """ Action time already setted """


class Action:
    def __init__(self, name):
        self.name = name
        self.done = False
        # timestamp是动态计算出来的，这里只是放一个占位符
        self.__timestamp = 0

    def set_done(self):
        self.done = True

    def set_timestamp(self, t):
        # 时间戳只允许设置一次，这样做是为了防止将同一个action实例插入到 action_list
        if self.__timestamp:
            raise ActionTimestampException(
                "Action timestamp already setted, can not change")

        self.__timestamp = t

    def get_timestamp(self):
        return self.__timestamp
    
    def __debug(self, fmt_str, *args, **kwargs):
        fmt_str = str(round(self.__timestamp, 3)) + ": " + fmt_str
        logging.debug(fmt_str, *args, **kwargs)
    
    def debug(self, fmt_str, *args, **kwargs):
        pass
        # self.__debug(fmt_str, *args, **kwargs)
        
    def damage_record(self,  prefix, bei_lv_str, bonus, monster: Monster, other_bonus=0):
        s = [prefix, bei_lv_str]
        s.append(str(round(bonus, 3)))
        s.append(str(round(monster.kang_xin_xi_su, 3)))
        s.append(str(round(monster.fang_yu_xi_shu, 3)))
        if other_bonus:
            s.append(str(other_bonus))
        logging.debug(" * ".join(s))

    def damage_record_hp(self, bei_lv_str, bonus, monster: Monster, other_bonus=0):
        pass
        # self.damage_record("damage += cur_hp", bei_lv_str, bonus, monster, other_bonus)

    def do(self, plan: ActionPlan, data=None, index=-1):
        if self.done:
            return None

        return self.do_impl(plan, data, index)

    def do_impl(self, plan: ActionPlan, data, index):
        """
        * plan: 此Action所在的ActionPlan的实例
        * data: 相关数据
        * index: 在action_list中的位置，某些action可能需要知道自已所有位置以方便”往前看“或”往后看“
                 index小于0表示不在action_list中
        """
        pass


class ActionPlan:
    def __init__(self):
        self.__current_action_time = 0
        self.action_list: list[Action] = []

    def get_current_action_time(self):
        return self.__current_action_time

    ##################################################

    def __debug(self, fmt_str, *args, **kwargs):
        fmt_str = str(round(self.get_current_action_time(), 3)) + ": " + fmt_str
        logging.debug(fmt_str, *args, **kwargs)

    def debug(self, fmt_str, *args, **kwargs):
        pass
        # self.__debug(fmt_str, *args, **kwargs)

    def sort_action(self):
        self.action_list.sort(key=lambda a: a.get_timestamp())

    def add_action(self, name, cls, min_t, max_t, base_action=None, negative=False, effective_delay=0, **kwargs):
        action = cls(name, **kwargs)
        base_time = 0
        if base_action:
            base_action_found = False
            for a in self.action_list:
                if a.name == base_action:
                    base_time = a.get_timestamp()
                    base_action_found = True
                    break

            if not base_action_found:
                raise Exception("base action " + base_action + " not found!")

        t = random.randint(round(min_t * 1000), round(max_t * 1000)) / 1000
        if negative:
            timestamp = base_time - t
        else:
            timestamp = base_time + t
        action.set_timestamp(timestamp + effective_delay)

        self.action_list.append(action)

    def find_first_action(self, action_name) -> Action:
        for t in self.action_list:
            if t.name == action_name:
                return t
            
    def insert_action(self, action, re_sort=False):
        self.action_list.append(action)
        if re_sort:
            self.sort_action()
            
    def insert_action_runtime(self, action, re_sort=True):
        if action.get_timestamp() < self.__current_action_time:
            raise Exception("action timestamp small than current action time")
        
        self.insert_action(action, re_sort)
        

    def run(self):
        self.sort_action()

        index = 0
        while index < len(self.action_list):
            action = self.action_list[index]
            self.__current_action_time = action.get_timestamp()
            action.do(self, index=index)

            index += 1