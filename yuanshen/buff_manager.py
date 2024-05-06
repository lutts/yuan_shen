#!/user/bin/env python3 -c
# -*- coding: utf-8 -*-
"""
Module documentation.
"""


class Buff:
    def __init_subclass__(cls, max_layer=0, co_exist=False) -> None:
        """
        max_layer: 最大允许叠层, 0 表示不允许重复存在(即: 后来的 buff_type 相同的会覆盖旧的), 默认不可重复存在(0)

            * 注：如果 creator 不同，则还需要根据 co_exist 来判断是否允许重复存在

        co_exist: 不同 creator 的相同 buff_type 是否允许同时存在（即：效果是否可叠加）, True 表示可叠加, False 表示不可叠加，
        仅在 creator 不为 None 时有效。默认不可叠加(False)
        """
        super().__init_subclass__()

        cls.max_layer = max_layer
        cls.co_exist = co_exist

    def __init__(self, start_time: float, end_time: float = None, creator=None):
        """
        start_time: buff 开始时间

        end_time: None表示永久
        
        creator: buff 施加者，可能是某个 Character, 也可能是某件武器，也可能是圣遗物效果
        """

        self.start_time = start_time
        self.end_time = end_time
        self.cur_layer = 1
        self.creator = creator

    def inc_layer(self, new_buff):
        if self.cur_layer < self.max_layer:
            self.cur_layer += 1

    def get_crit_rate(self, plan, target_character):
        return 0

    def get_crit_damage(self, plan, target_character):
        return 0

    def get_hp_percent(self, plan, target_character):
        return 0

    def get_hp(self, plan, target_character):
        return 0

    def get_atk_per(self, plan, target_character):
        return 0

    def get_atk(self, plan, target_character):
        return 0

    def get_def_per(self, plan, target_character):
        return 0

    def get_def(self, plan, target_character):
        return 0

    def get_elem_mastery(self, plan, target_character):
        return 0

    def get_elem_bonus(self, plan, target_character):
        return 0

    def get_healing_bonus(self, plan, target_character):
        return 0

    def get_incoming_healing_bonus(self, plan, target_character):
        return 0

    def get_energy_recharge(self, plan, target_character):
        return 0

    def get_normal_a_bonus(self, plan, target_character):
        return 0

    def get_charged_a_bonus(self, plan, target_character):
        return 0

    def get_plunging_bonus(self, plan, target_character):
        return 0

    def get_e_bonus(self, plan, target_character):
        return 0

    def get_q_bonus(self, plan, target_character):
        return 0

    def get_jian_kang(self, plan):
        return 0

    def get_jian_fang(self, plan):
        return 0

    def get_ignore_fang(self, plan):
        return 0


class BuffManager:
    def __init__(self):
        self.plan = None
        self.__buff_lst: list[Buff] = None

    def init(self, plan):
        self.plan = plan
        self.__buff_lst: list[Buff] = []

    def reset(self):
        self.plan = None
        self.__buff_lst = None

    def update(self, cur_time):
        # TODO: notify buff on finish?
        new_lst = [buff for buff in self.__buff_lst if buff.end_time is not None and buff.end_time >= cur_time]
        self.__buff_lst = new_lst

    def add_buff(self, new_buff: Buff):
        same_type_buff_lst: list[Buff] = []
        for b in self.__buff_lst:
            if type(b) is type(new_buff):
                same_type_buff_lst.append(b)

        if same_type_buff_lst:
            if new_buff.max_layer == 0: # 不允许叠层
                if new_buff.co_exist: 
                    # 不可重复，但不同 creator 允许同时存在
                    # 那么只需要替换掉 creator 相同的那个 old buff 即可
                    added = False
                    for old_buff in same_type_buff_lst:
                        if old_buff.creator is new_buff.creator:
                            self.__buff_lst.remove(old_buff)
                            self.__buff_lst.append(new_buff)
                            added = True
                            break # 后面不会再有 creator 相同的了

                    if not added:
                        # 没有 creator 相同的，作为新 buff 添加到列表
                        self.__buff_lst.append(new_buff)
                else:
                    # 不可重复，而且不论 creator 是否相同都不可重复
                    assert len(same_type_buff_lst) == 1
                    old_buff = same_type_buff_lst[0]
                    self.__buff_lst.remove(old_buff)
                    self.__buff_lst.append(new_buff)
            else:   # 允许叠层
                if new_buff.co_exist:
                    # 允许叠层，并且不同 creator 是分别叠层的
                    # 找出 creator 相同的 old_buff，叠层加一
                    added = False
                    for old_buff in same_type_buff_lst:
                        if old_buff.creator is new_buff.creator:
                            old_buff.inc_layer(new_buff)
                            added = True
                            break

                    if not added:
                        # 没有 creator 相同的，作为新 buff 添加到列表
                        self.__buff_lst.append(new_buff)
                else:
                    # 允许叠层，但不同 creator 不允许共存
                    # 这意味着，只在 creator 相同时叠层，否则如果 creator 不同，new_buff 将替换掉 old_buff
                    assert len(same_type_buff_lst) == 1
                    old_buff = same_type_buff_lst[0]
                    if old_buff.creator is new_buff.creator:
                        old_buff.inc_layer(new_buff)
                    else:
                        self.__buff_lst.remove(old_buff)
                        self.__buff_lst.append(new_buff)
        else:
            self.__buff_lst.append(new_buff)

    def remove_buff(self, buff: Buff):
        self.__buff_lst.remove(buff)

    @property
    def buff_lst(self):
        """
        for test only!
        """
        return self.__buff_lst

    def get_crit_rate(self, ch):
        return sum([buff.get_crit_rate(self.plan, ch) for buff in self.__buff_lst])

    def get_crit_damage(self, ch):
        return sum([buff.get_crit_damage(self.plan, ch) for buff in self.__buff_lst])

    def get_max_hp(self, ch):
        extra_hp_per = sum([buff.get_hp_percent(self.plan, ch)
                           for buff in self.__buff_lst])
        extra_hp = sum([buff.get_hp(self.plan, ch)
                       for buff in self.__buff_lst])

        return extra_hp + ch.get_hp().get_base_hp() * extra_hp_per

    def get_atk(self, ch):
        extra_atk_per = sum([buff.get_atk_per(self.plan, ch)
                            for buff in self.__buff_lst])
        extra_atk = sum([buff.get_atk(self.plan, ch)
                        for buff in self.__buff_lst])

        return extra_atk + ch.get_base_atk() * extra_atk_per

    def get_defence(self, ch):
        extra_def_per = sum([buff.get_def_per(self.plan, ch)
                            for buff in self.__buff_lst])
        extra_def = sum([buff.get_def(self.plan, ch)
                        for buff in self.__buff_lst])

        return extra_def + ch.get_base_defence() * extra_def_per

    def get_elem_mastery(self, ch):
        return sum([buff.get_elem_mastery(self.plan, ch) for buff in self.__buff_lst])

    def get_healing_bonus(self, ch):
        return sum([buff.get_healing_bonus(self.plan, ch) for buff in self.__buff_lst])

    def get_incoming_healing_bonus(self, ch):
        return sum([buff.get_incoming_healing_bonus(self, ch) for buff in self.__buff_lst])

    def get_energy_recharge(self, ch):
        return sum([buff.get_energy_recharge(self.plan, ch) * 100 for buff in self.__buff_lst])

    def get_normal_a_bonus(self, ch):
        return sum([buff.get_elem_bonus(self.plan, ch) + buff.get_normal_a_bonus(self.plan, ch) for buff in self.__buff_lst])

    def get_charged_a_bonus(self, ch):
        return sum([buff.get_elem_bonus(self.plan, ch) + buff.get_charged_a_bonus(self.plan, ch) for buff in self.__buff_lst])

    def get_plunging_bonus(self, ch):
        return sum([buff.get_elem_bonus(self.plan, ch) + buff.get_plunging_bonus(self.plan, ch) for buff in self.__buff_lst])

    def get_e_bonus(self, ch):
        return sum([buff.get_elem_bonus(self.plan, ch) + buff.get_e_bonus(self.plan, ch) for buff in self.__buff_lst])

    def get_q_bonus(self, ch):
        return sum([buff.get_elem_bonus(self.plan, ch) + buff.get_q_bonus(self.plan, ch) for buff in self.__buff_lst])

    def get_jian_kang(self):
        return sum([buff.get_jian_kang(self.plan) for buff in self.__buff_lst])

    def get_jian_fang(self):
        return sum([buff.get_jian_fang(self.plan) for buff in self.__buff_lst])

    def get_ignore_fang(self):
        return sum([buff.get_ignore_fang(self.plan) for buff in self.__buff_lst])


def _do_test():
    class Creator1:
        pass

    class Creator2:
        pass

    class Buff_Lay_0_Co_f(Buff):
        pass

    class Buff_Lay_0_Co_t(Buff, co_exist=True):
        pass

    class Buff_Lay_2_Co_f(Buff, max_layer=2):
        pass

    class Buff_Lay_2_Co_t(Buff, max_layer=2, co_exist=True):
        pass

    def is_same_lst(l1, l2):
        if len(l1) != len(l2):
            return False
        
        for b in l1:
            if b not in l2:
                return False
            
        return True
    
    creator1 = Creator1()
    creator2 = Creator2()

    buff_manager = BuffManager()
    buff_manager.init(None)
    buff_manager.add_buff(Buff_Lay_0_Co_f(0, creator=creator1))
    new_buff = Buff_Lay_0_Co_f(0, creator2)
    buff_manager.add_buff(new_buff)
    assert is_same_lst(buff_manager.buff_lst, [new_buff])

    buff_manager = BuffManager()
    buff_manager.init(None)
    buff_manager.add_buff(Buff_Lay_0_Co_f(0, creator=creator1))
    new_buff = Buff_Lay_0_Co_f(0, creator1)
    buff_manager.add_buff(new_buff)
    assert is_same_lst(buff_manager.buff_lst, [new_buff])

    buff_manager = BuffManager()
    buff_manager.init(None)
    buff1 = Buff_Lay_0_Co_t(0, creator=creator1)
    buff2 = Buff_Lay_0_Co_t(0, creator=creator2)
    buff_manager.add_buff(buff1)
    buff_manager.add_buff(buff2)
    assert is_same_lst(buff_manager.buff_lst, [buff1, buff2])

    buff_manager = BuffManager()
    buff_manager.init(None)
    buff1 = Buff_Lay_0_Co_t(0, creator=creator1)
    buff2 = Buff_Lay_0_Co_t(0, creator=creator1)
    buff_manager.add_buff(buff1)
    buff_manager.add_buff(buff2)
    assert is_same_lst(buff_manager.buff_lst, [buff2])

    buff_manager = BuffManager()
    buff_manager.init(None)
    buff1 = Buff_Lay_2_Co_f(0, creator=creator1)
    buff2 = Buff_Lay_2_Co_f(0, creator=creator1)
    buff_manager.add_buff(buff1)
    buff_manager.add_buff(buff2)
    assert is_same_lst(buff_manager.buff_lst, [buff1])
    assert buff1.cur_layer == 2

    buff_manager = BuffManager()
    buff_manager.init(None)
    buff1 = Buff_Lay_2_Co_f(0, creator=creator1)
    buff2 = Buff_Lay_2_Co_f(0, creator=creator2)
    buff_manager.add_buff(buff1)
    buff_manager.add_buff(buff2)
    assert is_same_lst(buff_manager.buff_lst, [buff2])
    assert buff2.cur_layer == 1

    buff_manager = BuffManager()
    buff_manager.init(None)
    buff1 = Buff_Lay_2_Co_t(0, creator=creator1)
    buff2 = Buff_Lay_2_Co_t(0, creator=creator1)
    buff_manager.add_buff(buff1)
    buff_manager.add_buff(buff2)
    assert is_same_lst(buff_manager.buff_lst, [buff1])
    assert buff1.cur_layer == 2

    buff_manager = BuffManager()
    buff_manager.init(None)
    buff1 = Buff_Lay_2_Co_t(0, creator=creator1)
    buff2 = Buff_Lay_2_Co_t(0, creator=creator2)
    buff_manager.add_buff(buff1)
    buff_manager.add_buff(buff2)
    assert is_same_lst(buff_manager.buff_lst, [buff1, buff2])
    assert buff1.cur_layer == 1
    assert buff2.cur_layer == 1

    buff_manager = BuffManager()
    buff_manager.init(None)
    buff1 = Buff_Lay_2_Co_t(0, creator=creator1)
    buff2 = Buff_Lay_2_Co_t(0, creator=creator2)
    buff3 = Buff_Lay_2_Co_t(0, creator=creator1)
    buff_manager.add_buff(buff1)
    buff_manager.add_buff(buff2)
    buff_manager.add_buff(buff3)
    assert is_same_lst(buff_manager.buff_lst, [buff1, buff2])
    assert buff1.cur_layer == 2
    assert buff2.cur_layer == 1
# Main body
if __name__ == '__main__':
    _do_test()