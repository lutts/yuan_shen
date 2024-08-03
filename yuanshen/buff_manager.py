#!/user/bin/env python3 -c
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

from typing import Self, NewType
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


BuffManager = NewType("BuffManager", None)


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
        # if not attrs:
        #     raise Exception("Buff attrs must be specified")
        cls.attrs = attrs
        cls.depend_attrs = depend_attrs

    def __init__(self, start_time: float, end_time: float = 10000, creator=None):
        """
        start_time: buff 开始时间

        end_time: 默认是一个很大的值，一场战斗不会持续这么长时间，因此默认的值可视为永久 buff

        creator: buff 施加者，可能是某个 Character, 也可能是某件武器，也可能是圣遗物效果
        """

        self.__start_time = start_time
        self.__end_time = end_time
        self.creator = creator
        self.__need_update = True

    def start_time(self):
        return self.__start_time
    
    def end_time(self):
        return self.__end_time
    
    def cur_layer(self, cur_time):
        return 1
    
    def prepare_update(self, plan, cur_time):
        """
        prepare update

        return: need update or not
        """
        
        nu = self.__need_update and self.__start_time <= cur_time
        self.__need_update = False
        return nu

    def update(self, buff_manager: BuffManager, plan, cur_time):
        if cur_time < self.start_time():
            return
        
        self.on_update(buff_manager, plan, cur_time)

    def on_finish(self):
        pass

    def on_update(self, buff_manager: BuffManager, plan, cur_time):
        pass


class MultiLayerBuff(Buff):
    def __init__(self, start_time: float, end_time: float = 10000, creator=None):
        """
        start_time: buff 开始时间

        end_time: 默认是一个很大的值，一场战斗不会持续这么长时间，因此默认的值可视为永久 buff

        creator: buff 施加者，可能是某个 Character, 也可能是某件武器，也可能是圣遗物效果
        """

        self.__start_end_times = deque([(start_time, end_time)])
        self.creator = creator
        self.__cur_layer = 0

    def start_time(self):
        return self.__start_end_times[0][0]
    
    def end_time(self):
        return self.__start_end_times[-1][1]
    
    def cur_layer(self, cur_time):
        layer = 0
        for start_time, end_time in self.__start_end_times:
            if cur_time <= end_time and start_time <= cur_time:
                # NOTE: 首先检查 end_time，方便快速过滤超时的 layer
                layer += 1
                if layer == self.max_layer:
                    break
                
        return layer

    def remove_expired_layer(self, cur_time):
        while self.__start_end_times:
            end_time = self.__start_end_times[0][1]
            if end_time < cur_time:
                self.__start_end_times.popleft()
            else:
                break
    
    def prepare_update(self, plan, cur_time):
        self.remove_expired_layer(cur_time)

        if cur_time < self.start_time():
            return False

        prev_layer = self.__cur_layer
        self.__cur_layer = self.cur_layer(cur_time)
        return prev_layer != self.__cur_layer

    def inc_layer(self, new_buff: Self, cur_time):
        self.__start_end_times.extend(new_buff.__start_end_times)


class BuffNode:
    def __init__(self, buff: Buff):
        self.buff = buff
        self.level = 0
        self.parents: list[Self] = []
        self.childs: list[Self] = []


class BuffManager:
    def __init__(self):
        self.__buff_lst: list[BuffNode] = None
        self.__root_node: BuffNode = None

    def init(self, plan):
        self.__buff_lst: list[BuffNode] = []
        self.__root_node = BuffNode(None)

    def reset(self):
        self.__buff_lst = None
        self.__root_node = None

    def update(self, plan, cur_time):
        need_update = False

        idx = 0
        while idx < len(self.__buff_lst):
            buff = self.__buff_lst[idx]
            if buff.buff.end_time() < cur_time:
                self.__del_buff(buff)
                buff.buff.on_finish()
                need_update = True
            else:
                idx += 1
                nu = buff.buff.prepare_update(plan, cur_time)
                need_update = need_update or nu

        if not need_update:
            return

        # print(f"update buff @{cur_time}")
        for ch in plan.characters:
            ch.reset_attrs()
        plan.monster.buff_attrs.reset()

        for buff in self.__buff_lst:
            buff.buff.update(self, plan, cur_time)
                
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
            self.__root_node.childs.append(buff)
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
        # 大部分时候，buff 之间没有依赖关系
        self.__root_node.childs.append(new_buff)

        for buff in self.__buff_lst:
            if buff.buff.re_convertable and buff.buff.attrs & new_buff.buff.depend_attrs:
                buff.childs.append(new_buff)
                new_buff.parents.append(buff)
                self.__adjust_level(new_buff)
            elif new_buff.buff.re_convertable and buff.buff.depend_attrs & new_buff.buff.attrs:
                new_buff.childs.append(buff)
                buff.parents.append(new_buff)
                self.__adjust_level(buff)

        self.__buff_lst.append(new_buff)
        
    def add_buff(self, new_buff: Buff, cur_time=None):
        """
        * 返回值: 如果新增了 buff, 则返回相应的 BuffNode, 如果是替换了旧的或增加了叠层，则返回 None
        """
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
                    new_buff_node = BuffNode(new_buff)
                    self.__add_buff(new_buff_node)
                else:
                    # 不可重复，而且不论 creator 是否相同都不可重复
                    assert len(same_type_buff_lst) == 1
                    old_buff = same_type_buff_lst[0]
                    old_buff.buff = new_buff
                    return
            else:   # 允许叠层
                if new_buff.co_exist:
                    # 允许叠层，并且不同 creator 是分别叠层的
                    # 找出 creator 相同的 old_buff，叠层加一
                    for old_buff in same_type_buff_lst:
                        if old_buff.buff.creator is new_buff.creator:
                            old_buff.buff.inc_layer(new_buff, cur_time)
                            return

                    # 没有 creator 相同的，作为新 buff 添加到列表
                    new_buff_node = BuffNode(new_buff)
                    self.__add_buff(new_buff_node)
                else:
                    # 允许叠层，但不同 creator 不允许共存
                    # 这意味着，只在 creator 相同时叠层，否则如果 creator 不同，new_buff 将替换掉 old_buff
                    assert len(same_type_buff_lst) == 1
                    old_buff = same_type_buff_lst[0]
                    if old_buff.buff.creator is new_buff.creator:
                        old_buff.buff.inc_layer(new_buff, cur_time)
                    else:
                        old_buff.buff = new_buff
                    return
        else:
            new_buff_node = BuffNode(new_buff)
            self.__add_buff(new_buff_node)

        if new_buff_node.childs:
            print("===sort")
            self.__buff_lst.sort(key=lambda x: x.level)

        return new_buff_node

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
    