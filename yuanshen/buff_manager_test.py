from buff_manager import *

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


# Main body
if __name__ == '__main__':
    _do_test()