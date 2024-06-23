#!/user/bin/env python3 -c
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

from typing import Self
from enum import Flag, auto
from collections import deque


class BuffAttrs(Flag):
    CRIT_RATE = auto()
    CRIT_DAMAGE = auto()
    ATK_PER = auto()
    ATK = auto()
    DEF_PER = auto()
    DEF_V = auto()
    ELEM_MASTERY = auto()
    HEALING_BONUS = auto()
    INCOMING_HEALING_BONUS = auto()
    ENERGY_RECHARGE = auto()

    ELEM_BONUS = auto()
    NORMAL_A_BONUS = auto()
    CHARGED_A_BONUS = auto()
    PLUNGING_BONUS = auto()
    E_BONUS = auto()
    Q_BONUS = auto()

    HP_PER = auto()
    HP = auto()

    JIAN_KANG = auto()
    JIAN_FANG = auto()
    IGNORE_FANG = auto()


class Buff:
    def __init_subclass__(cls, max_layer=1, co_exist=False, re_convertable=True,
                          attrs: BuffAttrs = None, depend_attrs: BuffAttrs = BuffAttrs(0)) -> None:
        """
        * max_layer: 最大允许叠层

            * 注：如果 creator 不同，则还需要根据 co_exist 来判断是否允许重复存在

        * co_exist: 不同 creator 的相同 buff_type 是否允许同时存在（即：效果是否可叠加）, True 表示可叠加, False 表示不可叠加，
        仅在 creator 不为 None 时有效。默认不可叠加(False)

        * re_convertable: buff 提供的属性是否可以被二次转化，默认为可被二次转化(True), 不能二次转化的 buff 只能用于技能结算，不能被其他 buff 二次利用
        * attrs: buff 所提供的属性
        * depend_attrs:  buff 依赖的属性
        """
        super().__init_subclass__()

        cls.max_layer = max_layer
        cls.co_exist = co_exist
        cls.re_convertable = re_convertable
        if not attrs:
            raise Exception("Buff attrs must be specified")
        cls.attrs = attrs
        cls.depend_attrs = depend_attrs

    def __init__(self, start_time: float, end_time: float = None, creator=None):
        """
        start_time: buff 开始时间

        end_time: None表示永久

        creator: buff 施加者，可能是某个 Character, 也可能是某件武器，也可能是圣遗物效果
        """

        self.__start_time = start_time
        self.__end_time = end_time
        self.cur_layer = 1
        self.creator = creator

    @property
    def start_time(self):
        pass
    
    @property
    def end_time(self):
        pass

    def inc_layer(self, new_buff):
        if self.cur_layer < self.max_layer:
            self.cur_layer += 1
            self.__start_end_times.extend(new_buff.__start_end_times)

    def dec_layer(self):
        self.__start_end_times.pop()
        self.cur_layer -= 1

    def on_finish(self):
        pass

    def update(self, buff_manager, cur_time):
        pass


class BuffNode:
    def __init__(self, buff: Buff):
        self.buff = buff
        self.level = 0
        self.parents: list[Self] = []
        self.childs: list[Self] = []

class BuffManager:
    def __init__(self):
        self.plan = None
        self.__buff_lst: list[BuffNode] = None
        self.__root_node: BuffNode = None

    def init(self, plan):
        self.plan = plan
        self.__buff_lst: list[BuffNode] = []
        self.__root_node = BuffNode(None)

    def reset(self):
        self.plan = None
        self.__buff_lst = None

    def update(self, cur_time):
        for ch in self.plan.characters:
            ch.reset_attrs()
        self.plan.monster.buff_attrs.reset()

        invalid_buff = [buff for buff in self.__buff_lst 
                        if buff.buff.end_time is not None and buff.buff.end_time > cur_time]

        for buff in invalid_buff:
            self.__del_buff(buff)
            buff.buff.on_finish()

        self.__buff_lst.sort(key=lambda x: x.level)

        max_hp_may_changed = False
        for buff in self.__buff_lst:
            if buff.buff.start_time >= cur_time:
                continue

            buff.buff.update(self, cur_time)

            if not max_hp_may_changed and buff.buff.attrs & (BuffAttrs.HP_PER | BuffAttrs.HP):
                max_hp_may_changed = True

        if max_hp_may_changed:
            for ch in self.plan.characters:
                ch.get_hp().on_max_hp_changed()
                
    def __del_buff(self, buff: BuffNode):
        self.__buff_lst.remove(buff)

        parents = buff.parents
        if not parents:
            self.__root_node.childs.remove(buff)
        else:
            for p in parents:
                p.childs.remove(buff)

        for c in buff.childs:
            c.parents.remove(buff)
            for p in parents:
                if c.buff.depend_attrs & p.buff.attrs:
                    if c not in p.childs:
                        p.childs.append(c)
                        c.parents.append(p)
            self.__adjust_level(c)

    # NOTE: 这个函数也能检测循环依赖，有循环依赖的时候，这个函数会进入死循环
    def __adjust_level(self, buff: BuffNode):
        if not buff.parents:
            self.__root_node.childs.append(c)
            buff.level = 0
        else:
            if buff.level == 0:
                self.__root_node.childs.remove(buff)

            max_p_level = 0
            for p in buff.parents:
                if p.level > max_p_level:
                    max_p_level = p.level
            buff.level = max_p_level + 1

        for c in buff.childs:
            self.__adjust_level(c)

    def __add_buff(self, new_buff: BuffNode):
        self.__buff_lst.append(new_buff)
        # 大部分时候，buff 之间没有依赖关系
        self.__root_node.childs.append(new_buff)

        for buff in self.__buff_lst:
            if buff.buff.re_convertable and buff.buff.attrs & new_buff.buff.depend_attrs:
                buff.childs.append(new_buff)
                new_buff.parents.append(buff)
                self.__adjust_level(new_buff)
            elif buff.buff.depend_attrs & new_buff.buff.attrs:
                new_buff.childs.append(buff)
                buff.parents.append(new_buff)
                self.__adjust_level(buff)

    def add_buff(self, new_buff: Buff):
        same_type_buff_lst: list[BuffNode] = []
        for b in self.__buff_lst:
            if type(b.buff) is type(new_buff):
                same_type_buff_lst.append(b)

        if same_type_buff_lst:
            if new_buff.max_layer == 1:  # 不允许叠层
                if new_buff.co_exist:
                    # 不可重复，但不同 creator 允许同时存在
                    # 那么只需要替换掉 creator 相同的那个 old buff 即可
                    for old_buff in same_type_buff_lst:
                        if old_buff.buff.creator is new_buff.creator:
                            old_buff.buff = new_buff
                            return

                    # 没有 creator 相同的，作为新 buff 添加到列表
                    self.__add_buff(BuffNode(new_buff))
                else:
                    # 不可重复，而且不论 creator 是否相同都不可重复
                    assert len(same_type_buff_lst) == 1
                    old_buff = same_type_buff_lst[0]
                    old_buff.buff = new_buff
            else:   # 允许叠层
                if new_buff.co_exist:
                    # 允许叠层，并且不同 creator 是分别叠层的
                    # 找出 creator 相同的 old_buff，叠层加一
                    for old_buff in same_type_buff_lst:
                        if old_buff.buff.creator is new_buff.creator:
                            old_buff.buff.inc_layer(new_buff)
                            return

                    # 没有 creator 相同的，作为新 buff 添加到列表
                    self.__add_buff(BuffNode(new_buff))
                else:
                    # 允许叠层，但不同 creator 不允许共存
                    # 这意味着，只在 creator 相同时叠层，否则如果 creator 不同，new_buff 将替换掉 old_buff
                    assert len(same_type_buff_lst) == 1
                    old_buff = same_type_buff_lst[0]
                    if old_buff.buff.creator is new_buff.creator:
                        old_buff.buff.inc_layer(new_buff)
                    else:
                        old_buff.buff = new_buff
        else:
            self.__add_buff(BuffNode(new_buff))

    def remove_buff(self, buff: Buff):
        buff_node = None
        for bn in self.__buff_lst:
            if bn.buff is buff:
                buff_node = bn
                break

        if buff_node:
            self.__del_buff(buff_node)

    @property
    def buff_lst(self):
        """
        for test only!
        """
        return self.__buff_lst
