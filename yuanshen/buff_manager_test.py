from typing import Self
from buff_manager import *
from character import Character
from action import ActionPlan

def _do_test():
    class Creator1:
        pass

    class Creator2:
        pass

    class Buff_Lay_0_Co_f(Buff, attrs = BuffAttrs.CRIT_RATE):
        pass

    class Buff_Lay_0_Co_t(Buff, co_exist=True, attrs=BuffAttrs.CRIT_DAMAGE):
        pass

    class Buff_Lay_2_Co_f(Buff, max_layer=2, attrs = BuffAttrs.ATK_PER):
        pass

    class Buff_Lay_2_Co_t(Buff, max_layer=2, co_exist=True, attrs = BuffAttrs.ELEM_MASTERY):
        pass

    def is_same_lst(l1, l2):
        if len(l1) != len(l2):
            return False

        for b in l1:
            if b.buff not in l2:
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


class NaxiDa_Zhuan_Wu(Buff, attrs=BuffAttrs.ELEM_MASTERY):
    def update(self, buff_manager: BuffManager):
        plan: ActionPlan = buff_manager.plan
        for ch in plan.characters:
            ch.buff_attrs.elem_mastery += 40


class YeLan_E(Buff, max_layer=4, attrs=BuffAttrs.HP_PER):
    def __init__(self, start_time: float, end_time: float = None, creator=None):
        super().__init__(start_time, end_time, creator)

        self.layer_times = [(start_time, end_time)]

    def inc_layer(self, new_buff: Self):
        if self.cur_layer < self.max_layer:
            self.cur_layer += 1
            self.layer_times.extend(new_buff.layer_times)

    def update(self, buff_manager):
        plan: ActionPlan = buff_manager.plan
        

        for ch in plan.characters:
            ch.get_hp().buff_attrs.hp_per += self.cur_layer * 0.1

# Main body
if __name__ == '__main__':
    _do_test()