from typing import Self
import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))

from yuanshen.buff_manager import *
from yuanshen.character import Character
from yuanshen.monster import Monster
from yuanshen.action import Action, ActionPlan

def do_add_test1():
    class Creator1:
        pass

    class Creator2:
        pass

    class Buff_Lay_0_Co_f(Buff, attrs = BuffAttrs.CRIT_RATE):
        pass

    class Buff_Lay_0_Co_t(Buff, co_exist=True, attrs=BuffAttrs.CRIT_DAMAGE):
        pass

    class Buff_Lay_2_Co_f(MultiLayerBuff, max_layer=2, attrs = BuffAttrs.ATK_PER):
        def inc_layer(self, new_buff: Self):
            self.append_layer(new_buff)

    class Buff_Lay_2_Co_t(MultiLayerBuff, max_layer=2, co_exist=True, attrs = BuffAttrs.ELEM_MASTERY):
        def inc_layer(self, new_buff: Self):
            self.append_layer(new_buff)

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
    buff = Buff_Lay_0_Co_f(0, creator=creator1)
    new = buff_manager.add_buff(buff)
    assert new.buff is buff
    new_buff = Buff_Lay_0_Co_f(0, creator2)
    new = buff_manager.add_buff(new_buff)
    assert new is None
    assert is_same_lst(buff_manager.buff_lst, [new_buff])

    buff_manager = BuffManager()
    buff_manager.init(None)
    buff = Buff_Lay_0_Co_f(0, creator=creator1)
    new = buff_manager.add_buff(buff)
    assert new.buff is buff
    new_buff = Buff_Lay_0_Co_f(0, creator1)
    new = buff_manager.add_buff(new_buff)
    assert new is None
    assert is_same_lst(buff_manager.buff_lst, [new_buff])

    buff_manager = BuffManager()
    buff_manager.init(None)
    buff1 = Buff_Lay_0_Co_t(0, creator=creator1)
    buff2 = Buff_Lay_0_Co_t(0, creator=creator2)
    new = buff_manager.add_buff(buff1)
    assert new.buff is buff1
    new = buff_manager.add_buff(buff2)
    assert new.buff is buff2
    assert is_same_lst(buff_manager.buff_lst, [buff1, buff2])

    buff_manager = BuffManager()
    buff_manager.init(None)
    buff1 = Buff_Lay_0_Co_t(0, creator=creator1)
    buff2 = Buff_Lay_0_Co_t(0, creator=creator1)
    new = buff_manager.add_buff(buff1)
    assert new.buff is buff1
    new = buff_manager.add_buff(buff2)
    assert new is None
    assert is_same_lst(buff_manager.buff_lst, [buff2])

    buff_manager = BuffManager()
    buff_manager.init(None)
    buff1 = Buff_Lay_2_Co_f(0, creator=creator1)
    buff2 = Buff_Lay_2_Co_f(0, creator=creator1)
    new = buff_manager.add_buff(buff1)
    assert new.buff is buff1
    new = buff_manager.add_buff(buff2)
    assert new is None
    assert is_same_lst(buff_manager.buff_lst, [buff1])
    assert buff1.cur_layer(0) == 2

    buff_manager = BuffManager()
    buff_manager.init(None)
    buff1 = Buff_Lay_2_Co_f(0, creator=creator1)
    buff2 = Buff_Lay_2_Co_f(0, creator=creator2)
    new = buff_manager.add_buff(buff1)
    assert new.buff is buff1
    new = buff_manager.add_buff(buff2)
    assert new is None
    assert is_same_lst(buff_manager.buff_lst, [buff2])
    assert buff2.cur_layer(0) == 1

    buff_manager = BuffManager()
    buff_manager.init(None)
    buff1 = Buff_Lay_2_Co_t(0, creator=creator1)
    buff2 = Buff_Lay_2_Co_t(0, creator=creator1)
    new = buff_manager.add_buff(buff1)
    assert new.buff is buff1
    new = buff_manager.add_buff(buff2)
    assert new is None
    assert is_same_lst(buff_manager.buff_lst, [buff1])
    assert buff1.cur_layer(0) == 2

    buff_manager = BuffManager()
    buff_manager.init(None)
    buff1 = Buff_Lay_2_Co_t(0, creator=creator1)
    buff2 = Buff_Lay_2_Co_t(0, creator=creator2)
    new = buff_manager.add_buff(buff1)
    assert new.buff is buff1
    new = buff_manager.add_buff(buff2)
    assert new.buff is buff2
    assert is_same_lst(buff_manager.buff_lst, [buff1, buff2])
    assert buff1.cur_layer(0) == 1
    assert buff2.cur_layer(0) == 1

    buff_manager = BuffManager()
    buff_manager.init(None)
    buff1 = Buff_Lay_2_Co_t(0, creator=creator1)
    buff2 = Buff_Lay_2_Co_t(0, creator=creator2)
    buff3 = Buff_Lay_2_Co_t(0, creator=creator1)
    new = buff_manager.add_buff(buff1)
    assert new.buff is buff1
    new = buff_manager.add_buff(buff2)
    assert new.buff is buff2
    new = buff_manager.add_buff(buff3)
    assert new is None
    assert is_same_lst(buff_manager.buff_lst, [buff1, buff2])
    assert buff1.cur_layer(0) == 2
    assert buff2.cur_layer(0) == 1

    print("Add Test1 Passed")


class NaxiDa_Zhuan_Wu(Buff, attrs=BuffAttrs.ELEM_MASTERY):
    def on_update(self, buff_manager: BuffManager, plan: ActionPlan, cur_time, expired_layer):
        for ch in plan.characters:
            ch.buff_attrs.elem_mastery += 40


class NaXiDa_Q_Buff(Buff, attrs=BuffAttrs.ELEM_MASTERY, depend_attrs=BuffAttrs.ELEM_MASTERY, re_convertable=False):
    def __init__(self, start_time: float, q_em):
        super().__init__(start_time, end_time=start_time + 25.66)
        self.q_em = q_em

    def on_update(self, buff_manager: BuffManager, plan: ActionPlan, cur_time, expired_layer):
        for ch in plan.characters:
            if ch.is_in_foreground():
                ch.un_convertable_attrs.elem_mastery += self.q_em
                break

class NaXiDa_Q_Action(Action):
    def do(self, plan: ActionPlan):
        max_em = 0
        for ch in plan.characters:
            em = ch.get_elem_mastery(include_un_convertable=False)
            if em > max_em:
                max_em = em
       
        plan.buff_manager.add_buff(NaXiDa_Q_Buff(self.start_time, min(250, int(max_em / 4))))


class YeLan_E(MultiLayerBuff, max_layer=4, attrs=BuffAttrs.HP_PER):
    def inc_layer(self, new_buff: Self):
        self.append_layer(new_buff)

    def on_update(self, buff_manager: BuffManager, plan: ActionPlan, cur_time, expired_layer):
        cur_layer = self.cur_layer(cur_time)
        # print("cur_layer: ", cur_layer)
        for ch in plan.characters:
            ch.get_hp().buff_hp_per += cur_layer * 0.1


class YeLan_E_Action(Action):
    def do(self, plan: ActionPlan):
        plan.add_buff(YeLan_E(self.start_time, self.start_time + 25))


class Sheng_Xian(Buff, attrs=BuffAttrs.ELEM_MASTERY, 
                 depend_attrs=BuffAttrs.HP|BuffAttrs.HP_PER, 
                 re_convertable=False):
    def on_update(self, buff_manager: BuffManager, plan: ActionPlan, cur_time, expired_layer):
        owner: Character = self.creator
        owner_max_hp = owner.get_max_hp()
        # print(f"owner_max_hp: {owner_max_hp}, owner buff hp per:{owner.get_hp().buff_hp_per}")
        for ch in plan.characters:
            if ch is owner:
                ch.un_convertable_attrs.elem_mastery += int((0.12 * 3 + 0.2) / 100 * owner_max_hp)
            else:
                ch.un_convertable_attrs.elem_mastery += int(0.2 / 100 *  owner_max_hp)


class Wan_Ye_E(Buff, attrs=BuffAttrs.ELEM_BONUS, depend_attrs=BuffAttrs.ELEM_MASTERY, re_convertable=False):
    def __init__(self, start_time: float, bonus, wan_ye):
        super().__init__(start_time, end_time=start_time + 8, creator=wan_ye)
        self.bonus = bonus

    def on_update(self, buff_manager: BuffManager, plan: ActionPlan, cur_time, expired_layer):
        for ch in plan.characters:
            ch.un_convertable_attrs.elem_bonus += self.bonus


class Wan_Ye_E_Action(Action):
    def do(self, plan: ActionPlan):
        wan_ye = plan.get_p4()
        em = wan_ye.get_elem_mastery(include_un_convertable=False)
        bonus = em * 0.04 / 100
        plan.buff_manager.add_buff(Wan_Ye_E(self.start_time, bonus, wan_ye))


class Em_Provider(Buff, attrs=BuffAttrs.ELEM_MASTERY):
    def on_update(self, buff_manager: BuffManager, plan: ActionPlan, cur_time, expired_layer):
        for ch in plan.characters:
            ch.buff_attrs.elem_mastery += 100


class TestPrepareAction(Action):
    def do(self, plan: ActionPlan):
        buff_manager = plan.buff_manager
        buff_manager.add_buff(NaxiDa_Zhuan_Wu(0))
        buff_manager.add_buff(YeLan_E(1, 1 + 25))
        buff_manager.add_buff(YeLan_E(4, 4 + 25))
        buff_manager.add_buff(Sheng_Xian(7, 7 + 20, creator=plan.get_p3()))
        

class Em_Provider_Action(Action):
    def do(self, plan: ActionPlan):
        plan.buff_manager.add_buff(Em_Provider(12))


class Test2_Result_Checker(Action):
    def do(self, plan: ActionPlan):
        # for buff in plan.buff_manager.buff_lst:
        #     print(buff)
        #     print(buff.buff)
        #     print(buff.level)
        #     if buff.parents:
        #         print("parents:")
        #     for p in buff.parents:
        #         print("\t" + str(p))

        na_xi_da = plan.get_p1()
        # (645 + 40) + 250 + (42956 * 0.2 / 100) + 100
        assert na_xi_da.get_elem_mastery() == 1120 - 100
        assert round(na_xi_da.get_e_bonus(), 4) == round(0.4136, 4)

        ye_lan = plan.get_p2()
        assert ye_lan.get_max_hp() == 46235
        assert ye_lan.get_elem_mastery() == 225 - 100
        assert round(ye_lan.get_e_bonus(), 4) == round(0.4136, 4)

        a_ren = plan.get_p3()
        assert a_ren.get_max_hp() == 42956
        assert a_ren.get_elem_mastery() == 1169 - 100
        assert round(a_ren.get_e_bonus(), 4) == round(0.4136, 4)
        
        wan_ye = plan.get_p4()
        assert wan_ye.get_elem_mastery() == 1219 - 100
        assert round(wan_ye.get_e_bonus(), 4) == round(0.4136, 4)

        print("Test2 Passed")


def do_test2():
    na_xi_da = Character(elem_mastery=645)
    ye_lan = Character(base_hp=14450, max_hp=41900)
    a_ren = Character(base_hp=12289, max_hp=39270, elem_mastery=789)
    wan_ye = Character(elem_mastery=994)

    monster = Monster()

    plan = ActionPlan(characters=[na_xi_da, ye_lan, a_ren, wan_ye], monster=monster)
    assert plan.get_p1() is na_xi_da
    assert plan.get_p2() is ye_lan
    assert plan.get_p3() is a_ren
    assert plan.get_p4() is wan_ye

    with plan:
        plan.add_action(TestPrepareAction("测试准备",0))
        plan.add_switch_action(wan_ye, 8)
        plan.add_action(Wan_Ye_E_Action("万叶e", start_time=10))
        plan.add_switch_action(na_xi_da, 10.5)
        plan.add_action(NaXiDa_Q_Action("纳西妲Q", start_time=11))
        plan.add_action(YeLan_E_Action("夜兰e", start_time=13))
        # plan.add_action(Em_Provider_Action("其他精通", start_time=14))
        plan.add_action(Test2_Result_Checker("Test2结果检查", start_time=15))

        plan.run()


# Main body
if __name__ == '__main__':
    do_add_test1()
    do_test2()