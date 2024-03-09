#!/user/bin/env python3 -tt
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

import logging
import typing
import copy
import itertools
import random
from collections.abc import Callable

from yuanshen.elem_type import Ys_Elem_Type
from yuanshen.utils import ys_expect_damage
from yuanshen.syw_finder import ShengYiWu, ShengYiWu_Score, calculate_score, Syw_Combine_Desc, find_syw_combine, set_qualifier_threshold
from yuanshen.character import Character, Character_HP_Change_Data
from yuanshen.monster import Monster
from yuanshen.action import Action, ActionPlan
from yuanshen.attribute_hub import ActionPlanAttributeSupplier
from yuanshen.weapon_impl.jing_shui_liu_yong_zhi_hui import Jing_Shui_Liu_Yong_Zhi_Hui


enable_debug = True
enable_record = False
MAX_RUN_NUM = 1


def randtime(t_min, t_max):
    return random.randint(t_min, t_max) / 1000


class Character_FuFu(Character, name="furina", elem_type=Ys_Elem_Type.SHUI, ming_zuo_num=6, 
                     e_level=13, q_level=13, q_energy=60):
    # 最小技能等级 8 级， 如果要设置 8 级以下的技能等级，请自行在下面的 MULTIPLIER 里添加 8 级以下的倍率系数
    MIN_SKILL_LEVEL = 8

    BASE_HP = 15307
    HEI_DAO_MULTIPLIER = 18/100
    BAI_DAO_MULTIPLIER = (18 + 25)/100

    E_MULTIPLIER = [12.6/100, 13.4/100, 14.2/100, 14.9/100, 15.7/100, 16.7/100]
    FU_REN_MULTIPLIER = [5.17/100, 5.49/100, 5.82/100, 6.14/100, 6.46/100, 6.87/100]
    XUN_JUE_MULTIPLIER = [9.54/100, 10.13/100, 10.73/100, 11.32/100, 11.92/100, 12.67/100]
    PANG_XIE_MULTIPLIER = [13.26/100, 14.09/100, 14.92/100, 15.75/100, 16.58/100, 17.61/100]
    GE_ZHE_HEAL_MULTIPLIER = [(7.68/100, 867), (8.16/100, 940), (8.64/100, 1017), 
                              (9.12/100, 1098), (9.60/100, 1183), (10.20/100, 1271)]
    
    Q_MULTIPLIER = [18.3/100, 19.4/100, 20.5/100, 21.7/100, 22.8/100, 24.2/100]

    QI_BONUS_MULTIPLIER = [0.21/100, 0.23/100, 0.25/100, 0.27/100, 0.29/100, 0.31/100]
    QI_HEAL_MULTIPLIER = [0.08/100, 0.09/100, 0.10/100, 0.11/100, 0.12/100, 0.13/100]

    def __init__(self, weapon, ming_zuo_num=6):
        """
        * ming_zuo_num: 命座数
        """
        super().__init__(base_hp=Character_FuFu.BASE_HP, weapon=weapon, crit_rate=0.242)
        super().set_ming_zuo_num(ming_zuo_num)

        if ming_zuo_num >= 1:
            self.BASE_QI_FEN_ZHI = 150
            self.MAX_QI_FEN_ZHI = 400
        else:
            self.BASE_QI_FEN_ZHI = 0
            self.MAX_QI_FEN_ZHI = 300

        if ming_zuo_num >= 2:
            self.QI_INCREASE_MULTIPLIER = 3.5
            self.QI_HP_MULTIPLIER = 0.0035
            self.MING_2_QI_FEN_ZHI = 800
        else:
            self.QI_INCREASE_MULTIPLIER = 1
            self.QI_HP_MULTIPLIER = 0
            self.MING_2_QI_FEN_ZHI = self.MAX_QI_FEN_ZHI

        # self.bei_lv_to_salon_member_name = {
        #     self.FU_REN_MULTIPLIER: "夫人",
        #     self.XUN_JUE_MULTIPLIER: "勋爵",
        #     self.PANG_XIE_MULTIPLIER: "螃蟹"
        # }

        # self.bei_lv_to_str = {
        #     self.FU_REN_MULTIPLIER: "fufu.FU_REN_MULTIPLIER / 100",
        #     self.XUN_JUE_MULTIPLIER: "fufu.XUN_JUE_MULTIPLIER / 100",
        #     self.PANG_XIE_MULTIPLIER: "fufu.PANG_XIE_MULTIPLIER / 100"
        # }
            
    @classmethod
    def create_with_zhuan_wu(cls, ming_zuo_num = 6):
        weapon = Jing_Shui_Liu_Yong_Zhi_Hui(base_atk=542, crit_damage=0.882)
        return Character_FuFu(weapon=weapon, ming_zuo_num=ming_zuo_num)

    def qi_fen_zhi_to_elem_bonus(self, qi):
        return qi * self.QI_BONUS_MULTIPLIER[self.q_level]
    
    def qi_fen_zhi_to_healing_bonus(self, qi):
        return qi * self.QI_HEAL_MULTIPLIER[self.q_level]
    
    def gu_you_tian_fu_2_bonus(self, max_hp):
        return min(max_hp / 1000 * 0.007, 0.28)
    
    def get_ge_zhe_cure_num(self, plan: ActionPlan):
        multiplier = Character_FuFu.GE_ZHE_HEAL_MULTIPLIER[self.e_level - 1]
        return round(self.get_hp().get_max_hp() * multiplier[0] + multiplier[1])
    
    def add_q_damage(self, plan: ActionPlan):
        multiplier = Character_FuFu.Q_MULTIPLIER[self.q_level - 1]
        damage = self.get_max_hp() * multiplier * (1 + self.get_q_bonus())
        return plan.add_damage(damage)

    def add_e_damage(self, plan: ActionPlan):
        multiplier = Character_FuFu.E_MULTIPLIER[self.e_level - 1]
        damage = self.get_max_hp() * multiplier * (1 + self.get_e_bonus())
        return plan.add_damage(damage)
    
    def add_hei_dao_damage(self, plan: ActionPlan):
        damage = self.get_max_hp() * Character_FuFu.HEI_DAO_MULTIPLIER * (1 + self.get_normal_a_bonus())
        return plan.add_damage(damage)
    
    def add_mang_huang_damage(self, plan: ActionPlan):
        return self.add_hei_dao_damage(plan)
    
    def add_bai_dao_damage(self, plan: ActionPlan):
        damage = self.get_max_hp() * Character_FuFu.BAI_DAO_MULTIPLIER * (1 + self.get_normal_a_bonus())
        return plan.add_damage(damage)

    def __add_salon_member_damage(self, plan: ActionPlan, multiplier, force_add_fufu_q_bonus):
        max_hp = self.get_max_hp()
        e_bonus = 1
        if plan.qi_fen_zhi_supervisor.effective_qi_fen_zhi == 0 and force_add_fufu_q_bonus:
            # print("force add q bonus")
            max_hp += round(self.MAX_QI_FEN_ZHI * self.QI_HP_MULTIPLIER * Character_FuFu.BASE_HP)
            e_bonus += self.MAX_QI_FEN_ZHI * Character_FuFu.QI_BONUS_MULTIPLIER[self.q_level - 1]

        e_bonus += self.get_e_bonus() + self.gu_you_tian_fu_2_bonus(max_hp)

        e_extra_bonus = 1
        for t in plan.characters:
            if t.get_hp().get_cur_hp_per() > 0.5:
                e_extra_bonus += 0.1
        
        damage = max_hp *  multiplier * e_bonus * e_extra_bonus
        return plan.add_damage(damage)

    def add_fu_ren_damage(self, plan: ActionPlan, force_add_fufu_q_bonus):
        multiplier = Character_FuFu.FU_REN_MULTIPLIER[self.e_level - 1]
        return self.__add_salon_member_damage(plan, multiplier, force_add_fufu_q_bonus)
    
    def add_xun_jue_damage(self, plan: ActionPlan, force_add_fufu_q_bonus):
        multiplier = Character_FuFu.XUN_JUE_MULTIPLIER[self.e_level - 1]
        return self.__add_salon_member_damage(plan, multiplier, force_add_fufu_q_bonus)
    
    def add_pang_xie_damage(self, plan: ActionPlan, force_add_fufu_q_bonus):
        multiplier = Character_FuFu.PANG_XIE_MULTIPLIER[self.e_level - 1]
        return self.__add_salon_member_damage(plan, multiplier, force_add_fufu_q_bonus)
    
    def get_salon_member_start_time(self, after_charged_a=False):
        """
        沙龙成员出现的时机有两个：释放e技能后，白芙重击切为黑芙后

        默认为释放 e 技能后，如果是白芙重击切为黑芙，则传参 after_charged_a 为 True 
        """
        return 0


class FuFuActionPlan(ActionPlan):
    def __init__(self, fufu_initial_state: Character_FuFu, teammates: list[Character]):
        self.__fufu: Character_FuFu = copy.deepcopy(fufu_initial_state)
        chs = copy.deepcopy(teammates)
        # 把芙芙放在 P1
        chs.insert(0, self.__fufu)
        super().__init__(characters=chs, monster=Monster())
        
        self.qi_fen_zhi_supervisor = Qi_Fen_Zhi_Supervisor(self.__fufu)

        if self.__fufu.ming_zuo_num >= 6:
            self.add_hei_fu_damage_callback(Hei_Fu_Cure_Supervisor(self.__fufu).on_hei_fu_damage)

        self.add_over_healed_callback(FuFu_GuYouTianFu_1_Supervisor(self.__fufu).on_over_healed)

        self.__fufu.get_weapon().apply_combat_attributes(self.__fufu)
        self.__fufu.get_weapon().apply_passive(self.__fufu, self)

        self.full_six_damage = 0

    ##################################################

    @staticmethod
    def get_hei_fu_first_cure_delay():
        return random.randint(1065, 1238) / 1000

    @staticmethod
    def get_hei_fu_cure_interval():
        return random.randint(913, 1074) / 1000

    @staticmethod
    def get_hei_fu_cure_extension():
        return random.randint(104, 272) / 1000

    @staticmethod
    def get_hei_fu_cure_fufu_delay():
        return random.randint(53, 173) / 1000

    def fufu_consume_hp_per(self, hp_per):
        self.modify_cur_hp(targets=self.characters, hp_per=(0 - hp_per))

    def add_hei_fu_damage_callback(self, callback):
        self.events.on_hei_fu_damage += callback

    def remove_hei_fu_damage_callback(self, callback):
        self.events.on_hei_fu_damage -= callback
    
    def call_hei_fu_damage_callback(self):
        if hasattr(self.events, "on_hei_fu_damage"):
            self.events.on_hei_fu_damage(self)


class Qi_Fen_Zhi_Supervisor(ActionPlanAttributeSupplier):
    def __init__(self, fufu: Character_FuFu):
        self.fufu = fufu
        self.__stopped = True

    def is_bonus_valid(self, plan: FuFuActionPlan):
        cur_time = plan.get_current_action_time()
        if cur_time < self.__start_time or cur_time > self.__bonus_end_time:
            plan.debug("超出芙芙增伤时间范围：{.3f} - {.3f}".format(self.__start_time, self.__bonus_end_time))
            return False
        
        return True

    def get_elem_bonus(self, plan: FuFuActionPlan, target_character):
        if self.is_bonus_valid(plan):
            return self.elem_bonus
        else:
            return 0
    
    def get_incoming_healing_bonus(self, plan, target_character):
        if self.is_bonus_valid(plan):
            return self.incoming_healing_bonus
        else:
            return 0
    
    def get_hp_percent(self, plan, target_character):
        if target_character is self.fufu and self.is_bonus_valid(plan):
            return self.hp_per_bonus
        else:
            return 0

    def start_supervise(self, plan: FuFuActionPlan, start_time):
        self.__start_time = start_time
        self.__pao_pao_end_time = start_time + 18
        self.__bonus_end_time = start_time + 18 + random.randint(0, 433) / 1000

        self.blocking = True

        self.__qi_fen_zhi = 0
        self.effective_qi_fen_zhi = 0

        self.elem_bonus = 0
        self.incoming_healing_bonus = 0
        self.hp_per_bonus = 0

        self.set_qi_fen_zhi(plan, self.fufu.BASE_QI_FEN_ZHI)
        plan.add_extra_attr(self)
        plan.add_consume_hp_callback(self.on_hp_changed)
        plan.add_regenerate_hp_callback(self.on_hp_changed)

        self.started = True

    def stop_supervise(self, plan: FuFuActionPlan):
        plan.debug("气氛值调整线程终止")
        plan.remove_consume_hp_callback(self.on_hp_changed)
        plan.remove_regenerate_hp_callback(self.on_hp_changed)

        self.started = False

    def on_hp_changed(self, plan: FuFuActionPlan, source: Character, targets_with_data: list[Character_HP_Change_Data]):
        cur_time = plan.get_current_action_time()
        if cur_time > self.__pao_pao_end_time:
            print("泡泡消失了，停止监控生命值变动")
            self.stop_supervise(plan)
            return
        
        qi_fen_zhi = 0

        for tdata in targets_with_data:
            qi_fen_zhi += abs(tdata.data.hp_per) * self.fufu.QI_INCREASE_MULTIPLIER * 100

        self.add_qi_fen_zhi(plan, qi_fen_zhi)

    def add_qi_fen_zhi(self, plan: FuFuActionPlan, qi):
        self.__qi_fen_zhi += qi
        if self.__qi_fen_zhi >= self.fufu.MING_2_QI_FEN_ZHI:
            self.__qi_fen_zhi = self.fufu.MING_2_QI_FEN_ZHI
            plan.debug("气氛值已达最大值，停止监控生命值变动")
            self.stop_supervise(plan)
        plan.debug("气氛值增加%s, 增加到:%s", round(qi, 3), round(self.__qi_fen_zhi, 3))

        if self.blocking:
            plan.debug("气氛值调程线程从阻塞唤醒")
            # 为了能处理三小只一开始的时候同时扣血的情形，因为三小只分属不同的Action，第一只扣血不能立即 apply qi fen zhi
            # insert_action_runtime会保证插入到最后一只扣血的后面
            action = Apply_Qi_Fen_Zhi_Action(self)
            action.set_timestamp(plan.get_current_action_time())
            plan.insert_action_runtime(action)
            self.blocking = False

    def set_qi_fen_zhi(self, plan: FuFuActionPlan, qi):
        if qi == self.__qi_fen_zhi:
            return

        self.__qi_fen_zhi = qi
        plan.debug("气氛值直接设置为%s", qi)
        self.apply_qi_fen_zhi(plan)

    def apply_qi_fen_zhi(self, plan: FuFuActionPlan):
        cur_time = plan.get_current_action_time()
        if cur_time > self.__pao_pao_end_time:
            return False
        
        cur_qi_fen_zhi = self.__qi_fen_zhi
        if cur_qi_fen_zhi == self.effective_qi_fen_zhi:
            self.blocking = True
            plan.debug("气氛值调整线程：气氛值没变化，转入阻塞")
            return False

        plan.debug("气氛值调整开始：生效层数%s", round(cur_qi_fen_zhi, 3))

        if cur_qi_fen_zhi > self.fufu.MAX_QI_FEN_ZHI:
            elem_bonus_qi_fen_zhi = self.fufu.MAX_QI_FEN_ZHI
            hp_bonus_qi_fen_zhi = cur_qi_fen_zhi - self.fufu.MAX_QI_FEN_ZHI
        else:
            elem_bonus_qi_fen_zhi = cur_qi_fen_zhi
            hp_bonus_qi_fen_zhi = 0

        self.elem_bonus = self.fufu.qi_fen_zhi_to_elem_bonus(elem_bonus_qi_fen_zhi)
        self.incoming_healing_bonus = self.fufu.qi_fen_zhi_to_healing_bonus(elem_bonus_qi_fen_zhi)
        self.hp_per_bonus = hp_bonus_qi_fen_zhi * self.fufu.QI_HP_MULTIPLIER

        self.effective_qi_fen_zhi = cur_qi_fen_zhi

        return True


class Apply_Qi_Fen_Zhi_Action(Action):
    def __init__(self, supervisor: Qi_Fen_Zhi_Supervisor):
        super().__init__("气氛值生效线程")
        self.supervisor = supervisor

    def do_impl(self, plan: FuFuActionPlan):
        changed = self.supervisor.apply_qi_fen_zhi(plan)
        if not changed:
            return

        action = Apply_Qi_Fen_Zhi_Action(self.supervisor)
        next_time = self.get_timestamp() + random.uniform(0.45, 0.55)
        action.set_timestamp(next_time)
        plan.insert_action_runtime(action)


# 固有天赋1： 非源自芙芙的治疗溢出时，会触发芙芙回血
class FuFu_GuYouTianFu_1_Supervisor:
    def __init__(self, fufu: Character_FuFu):
        self.fufu = fufu
        self.min_cure_num = 0
        self.end_time = None

    def on_over_healed(self, plan: FuFuActionPlan, source: Character, targets_with_data: list[Character_HP_Change_Data]):
        if source is None or source is self.fufu:
            return

        cur_time = plan.get_current_action_time()

        if self.end_time is None:
            self.start_cure(plan, cur_time)
        elif cur_time <= self.end_time:
            self.end_time = cur_time + 4
            plan.debug("芙芙固有天赋1效果延长到%s", self.end_time)
        else:
            plan.remove_over_healed_callback(self.on_over_healed)
            new_supervisor = FuFu_GuYouTianFu_1_Supervisor()
            plan.add_over_healed_callback(new_supervisor.on_over_healed)
            new_supervisor.start_cure(plan, cur_time)

    def insert_action(self, plan: FuFuActionPlan, t):
        action = FuFu_GuYouTianFu_1_Action(self)
        action.set_timestamp(t)
        plan.insert_action_runtime(action)

    @staticmethod
    def get_first_cure_interval():
        return randtime(int(2.078 * 1000), int(2.16 * 1000))

    def start_cure(self, plan: FuFuActionPlan, cur_time):
        self.end_time = cur_time + 4
        plan.debug("芙芙固有天赋1治疗启动, end_time=%s", self.end_time)
        # 至少保证治疗两次
        self.min_cure_num = 2
        self.insert_action(plan, cur_time + self.get_first_cure_interval())
        
    @staticmethod
    def get_cure_interval():
        return randtime(int(1.952 * 1000), int(2.047 * 1000))

    def do_cure(self, plan: FuFuActionPlan):
        cur_time = plan.get_current_action_time()
        can_cure = False
        if self.min_cure_num > 0:
            self.min_cure_num -= 1
            can_cure = True
        elif cur_time <= self.end_time:
            can_cure = True

        if not can_cure:
            return
        
        plan.debug("芙芙固有天赋1治疗")
        plan.regenerate_hp(plan.characters, hp_per=0.02)

        next_time = cur_time + self.get_cure_interval()
        self.insert_action(plan, next_time)    


class FuFu_GuYouTianFu_1_Action(Action):
    def __init__(self, supervisor: FuFu_GuYouTianFu_1_Supervisor):
        super().__init__("固有天赋1治疗")
        self.supervisor = supervisor

    def do_impl(self, plan: FuFuActionPlan):
        self.supervisor.do_cure(plan)


# FIXME: 在动画开始多久后添加这个 Action?
class FuFu_Q_Bonus_Action(Action):
    """
    注：plan.add_action 时，min_t 和 max_t 填写芙芙大招动画开始的时间，实际的增伤开始与结束时间会自动计算
    """
    def __init__(self, fufu: Character_FuFu):
        super().__init__("芙芙 Q 功能开始生效")
        self.fufu = fufu

    def set_timestamp(self, t):
        super().set_timestamp(t)
        self.bonus_start_time = t + random.uniform(1.649, 1.821)

    def do_impl(self, plan: FuFuActionPlan):
        plan.qi_fen_zhi_supervisor.start_supervise(plan, self.bonus_start_time)


class FuFu_Q_Damage_Action(FuFu_Q_Bonus_Action):
    def __init__(self, fufu: Character_FuFu):
        super().__init__("芙芙Q出伤")
        self.fufu = fufu

    def do_impl(self, plan: FuFuActionPlan):
        super().do_impl(plan)
        self.fufu.add_q_damage(plan)


class FuFu_E_Action(Action):
    def __init__(self, fufu: Character_FuFu):
        super().__init__("芙芙E出伤")
        self.fufu = fufu

    def do_impl(self, plan: FuFuActionPlan):
        self.fufu.add_e_damage(plan)


class Hei_Fu_Cure_Supervisor:
    def __init__(self, fufu: Character_FuFu):
        self.fufu = fufu
        self.end_time = None
        self.is_cure_fufu_sync = True
        self.last_cure_teammate_actual_time = 0
        self.last_cure_teammate_effective_time = 0

    def on_hei_fu_damage(self, plan: FuFuActionPlan):
        cur_action_time = plan.get_current_action_time()
        if self.end_time is None:
            self.start_cure_teammate(plan, cur_action_time)
            return
        
        if cur_action_time <= self.end_time:
            self.end_time += 2.9
            plan.debug("adjust end_time to %s", round(self.end_time, 3))
        else:
            plan.remove_hei_fu_damage_callback(self.on_hei_fu_damage)
            new_supervisor = Hei_Fu_Cure_Supervisor()
            plan.add_hei_fu_damage_callback(new_supervisor.on_hei_fu_damage)
            new_supervisor.start_cure_teammate(plan, cur_action_time)

    def start_cure_teammate(self, plan: FuFuActionPlan, cur_action_time):
        actual_cure_time = cur_action_time + plan.get_hei_fu_first_cure_delay()
        self.end_time = actual_cure_time + (2.9 - 1) + plan.get_hei_fu_cure_extension()
        plan.debug("黑芙治疗启动, end_time=%s", round(self.end_time, 3))

        action = Hei_Fu_Cure_Teammate_Action(self)
        action.actual_cure_time = actual_cure_time
        effective_time = actual_cure_time + plan.get_effective_delay()
        action.set_timestamp(effective_time)        
        plan.insert_action_runtime(action)

        self.is_cure_fufu_sync = True
        cure_fufu_delay = plan.get_hei_fu_cure_fufu_delay()
        self.start_cure_fu_fu(plan, 
                              actual_cure_time + cure_fufu_delay, 
                              effective_time + cure_fufu_delay)

    def start_cure_fu_fu(self, plan: FuFuActionPlan, actual_time, effective_time=None):
        # plan.debug("start_cure_fufu: actual_time:%s, effetive_time:%s", actual_time, str(effective_time))
        action = Hei_Fu_Cure_FuFu_Action(self)
        action.actual_cure_time = actual_time
        if not effective_time:
            effective_time = actual_time + plan.get_effective_delay()
        action.set_timestamp(effective_time)
        plan.insert_action_runtime(action)

    def on_consume_hp(self, plan: FuFuActionPlan, source: Character, targets_with_data: list[Character_HP_Change_Data]):
        cur_action_time = plan.get_current_action_time()
        if cur_action_time > self.end_time:
            plan.remove_consume_hp_callback(self.on_consume_hp)
            return
        
        fufu_hp_decreased = False
        for tdata in targets_with_data:
            if tdata.character is self.fufu:
                fufu_hp_decreased = tdata.has_changed()
                break

        if fufu_hp_decreased:
            plan.remove_consume_hp_callback(self.on_consume_hp)
            self.start_cure_fu_fu(plan, cur_action_time)

    
class Hei_Fu_Cure_Action(Action):
    def __init__(self, name, supervisor: Hei_Fu_Cure_Supervisor):
        super().__init__(name)
        self.actual_cure_time = 0
        self.supervisor: Hei_Fu_Cure_Supervisor = supervisor

    def get_cure_num(self):
        fufu = self.supervisor.fufu
        return round(fufu.get_max_hp() * 0.04)
    
    def do_impl(self, plan: FuFuActionPlan):
        if self.actual_cure_time > self.supervisor.end_time:
            self.debug("%s超时，不执行", self.name)
            return
        
        self.do_cure(plan)


class Hei_Fu_Cure_Teammate_Action(Hei_Fu_Cure_Action):
    def __init__(self, supervisor: Hei_Fu_Cure_Supervisor):
        super().__init__("治疗后台三人", supervisor)

    def do_cure(self, plan: FuFuActionPlan):
        cure_num = self.get_cure_num()
        self.debug("治疗后台三人, %s", cure_num)
        fufu = self.supervisor.fufu
        plan.regenerate_hp(targets=fufu.get_teammates(), hp=cure_num)

        self.re_schedule(plan)

    def re_schedule(self, plan: FuFuActionPlan):
        next_time = self.actual_cure_time + plan.get_hei_fu_cure_interval()
        effective_time = next_time + plan.get_effective_delay()
        self.supervisor.last_cure_teammate_actual_time = next_time
        self.supervisor.last_cure_teammate_effective_time = effective_time

        action = Hei_Fu_Cure_Teammate_Action(self.supervisor)
        action.actual_cure_time = next_time
        action.set_timestamp(effective_time)
        plan.insert_action_runtime(action)


class Hei_Fu_Cure_FuFu_Action(Hei_Fu_Cure_Action):
    def __init__(self, supervisor):
        super().__init__("治疗芙芙", supervisor)

    def do_cure(self, plan: FuFuActionPlan):
        fufu = self.supervisor.fufu

        if fufu.get_hp().is_full():
            self.debug("治疗芙芙时，芙芙满血，阻塞并转入独立模式")
            # 芙芙是满血的，不用治疗，转入阻塞独立模式
            self.supervisor.is_cure_fufu_sync = False
            plan.add_consume_hp_callback(self.supervisor.on_consume_hp)
        else:
            cure_num = self.get_cure_num()
            self.debug("治疗芙芙，%s", cure_num)
            plan.regenerate_hp(targets=[fufu], hp=cure_num)

            self.re_schedule(plan)

    def re_schedule(self, plan: FuFuActionPlan):
        if self.supervisor.is_cure_fufu_sync:
            cure_fufu_delay = plan.get_hei_fu_cure_fufu_delay()
            actual_time = self.supervisor.last_cure_teammate_actual_time + cure_fufu_delay
            effective_time = self.supervisor.last_cure_teammate_effective_time + cure_fufu_delay
            self.supervisor.start_cure_fu_fu(plan, actual_time, effective_time)
            
        else:
            next_time = self.actual_cure_time + plan.get_hei_fu_cure_interval()
            self.supervisor.start_cure_fu_fu(plan, next_time)

class Mang_Huang_Damage_Action(Action):
    def __init__(self, name, fufu: Character_FuFu):
        super().__init__(name)
        self.fufu = fufu

    def do_impl(self, plan: FuFuActionPlan):
        damage = self.fufu.add_mang_huang_damage(plan)
        plan.full_six_damage += damage


class Hei_Fu_Damage_Action(Action):
    def __init__(self, name, fufu: Character_FuFu):
        super().__init__(name)
        self.fufu = fufu

    def do_impl(self, plan: FuFuActionPlan):
        damage = self.fufu.add_hei_dao_damage(plan)
        plan.full_six_damage += damage

        plan.call_hei_fu_damage_callback()


class Bai_Dao_Kou_Xue_Action(Action):
    def do_impl(self, plan: FuFuActionPlan):
        # 白刀扣血 1%
        self.debug(self.name)
        plan.fufu_consume_hp_per(0.01)


class Bai_Fu_Damage_Action(Action):
    def __init__(self, name, fufu: Character_FuFu):
        super().__init__(name)
        self.fufu = fufu

    def do_impl(self, plan: FuFuActionPlan):
        damage = self.fufu.add_bai_dao_damage(plan)
        plan.full_six_damage += damage


class Salon_Member_Damage_Action(Action):
    def __init__(self, name, fufu: Character_FuFu):
        super().__init__(name)
        self.fufu = fufu
        self.force_add_fufu_q_bonus = False

    def enable_force_add_fufu_q_bonus(self):
        self.force_add_fufu_q_bonus = True


class Fu_Ren_Kou_Xue_Action(Action):
    NAME = "夫人扣血"
    INTERVAL = (1468, 1684)

    def __init__(self):
        super().__init__(Fu_Ren_Kou_Xue_Action.NAME)

    def do_impl(self, plan: FuFuActionPlan):
        self.debug(Fu_Ren_Kou_Xue_Action.NAME)
        plan.fufu_consume_hp_per(0.016)


class Fu_Ren_Damage_Action(Salon_Member_Damage_Action):
    NAME = "夫人出伤"
    INTERVAL = (1467, 1725)
    TIME_AFTER_KOU_XUE = (330, 721)

    def __init__(self, fufu: Character_FuFu):
        super().__init__(Fu_Ren_Damage_Action.NAME, fufu)

    def do_impl(self, plan: FuFuActionPlan):
        self.fufu.add_fu_ren_damage(plan, self.force_add_fufu_q_bonus)


class Xun_Jue_Kou_Xue_Action(Action):
    NAME = "勋爵扣血"
    INTERVAL = (3180, 3387)

    def __init__(self):
        super().__init__(Xun_Jue_Kou_Xue_Action.NAME)

    def do_impl(self, plan: FuFuActionPlan):
        self.debug(Xun_Jue_Kou_Xue_Action.NAME)
        plan.fufu_consume_hp_per(0.024)


class Xun_Jue_Damage_Action(Salon_Member_Damage_Action):
    NAME = "勋爵出伤"
    INTERVAL = (3127, 3443)
    TIME_AFTER_KOU_XU = (723, 951)

    def __init__(self, fufu: Character_FuFu):
        super().__init__(Xun_Jue_Damage_Action.NAME, fufu)

    def do_impl(self, plan: FuFuActionPlan):
        self.fufu.add_xun_jue_damage(plan, self.force_add_fufu_q_bonus)


class Pang_Xie_Kou_Xue_Action(Action):
    NAME = "螃蟹扣血"
    INTERVAL = (5056, 5293)

    def __init__(self):
        super().__init__(Pang_Xie_Kou_Xue_Action.NAME)

    def do_impl(self, plan: FuFuActionPlan):
        self.debug(Pang_Xie_Kou_Xue_Action.NAME)
        plan.fufu_consume_hp_per(0.036)


class Pang_Xie_Damage_Action(Salon_Member_Damage_Action):
    NAME = "螃蟹出伤"
    INTERVAL = (5063, 5325)
    TIME_AFTER_KOU_XU = (745, 1018)

    def __init__(self, fufu: Character_FuFu):
        super().__init__(Pang_Xie_Damage_Action.NAME, fufu)

    def do_impl(self, plan: FuFuActionPlan):
        self.fufu.add_pang_xie_damage(plan, self.force_add_fufu_q_bonus)


class Ge_Zhe_Cure_Action(Action):
    def __init__(self, fufu: Character_FuFu):
        super().__init__("歌者治疗")
        self.fufu = fufu

    def do_impl(self, plan: FuFuActionPlan):
        cure_num = self.fufu.get_ge_zhe_cure_num(plan)
        foreground_character = plan.get_foreground_character()
        self.debug("歌者治疗 %s, 治疗量: %s", foreground_character.name, cure_num)
        plan.regenerate_hp(targets=[foreground_character], hp=cure_num)


# for debug only
salon_member_min_k_num = {
    Fu_Ren_Kou_Xue_Action.NAME: 0,
    Xun_Jue_Kou_Xue_Action.NAME: 0,
    Pang_Xie_Kou_Xue_Action.NAME: 0,
}
salon_member_min_c_num = {
    Fu_Ren_Damage_Action.NAME: 0,
    Xun_Jue_Damage_Action.NAME: 0,
    Pang_Xie_Damage_Action.NAME: 0
}


def schedule_little_three(plan: FuFuActionPlan, 
                          fufu: Character_FuFu,
                          start_time, end_time,
                          kou_xue_cls, chu_shang_cls,
                          kou_xue_num=None, chu_shang_num=None):
    """
    关于 kou_xue_num 和 chu_shang_num:
    
    为了使每次运行的结果更稳定，这两个参数在最终版本是一定要指定具体数值，不能为 None 的，这个数值的确定方法如下:
    
    * 首先：将文件开头的enable_debug置为true，将MAX_RUN_NUM设置为一个比较大的值，例如 10000
    * 配置好 logging 模块的输出文件并启用
    * 执行程序，在Logging的输出里会有建议值
    """
    kou_xue_interval_min, kou_xue_interval_max = kou_xue_cls.INTERVAL
    chu_shang_interval_min, chu_shang_interval_max = chu_shang_cls.INTERVAL
    chu_kou_interval_min, chu_kou_interval_max = chu_shang_cls.TIME_AFTER_KOU_XU
 

    # 三小只第一次扣血并不一定是同时的，是在一个窗口内有先后顺序
    kou_xue_time = start_time + randtime(0, 133)
    last_chu_shang_time = 0

    k_num = 0
    c_num = 0

    k_action_lst = []
    c_action_lst = []

    while kou_xue_time < end_time:
        kou_xue_action = kou_xue_cls()
        kou_xue_action.set_timestamp(kou_xue_time + plan.get_effective_delay())
        plan.insert_action(kou_xue_action)
        k_action_lst.append(kou_xue_action)
        k_num += 1

        if not chu_shang_num or c_num < chu_shang_num:
            if last_chu_shang_time:
                # 我们可以从两种途径计算出本次出伤的时间：
                # 1. 上次出伤时间 + 出伤间隔
                # 2. 扣血时间 + 出伤-扣血间隔

                # 途径1 的 最小、最大值
                c_min = last_chu_shang_time + chu_shang_interval_min / 1000
                c_max = last_chu_shang_time + chu_shang_interval_max / 1000

                # 途径2 的 最小、最大值
                k_min = kou_xue_time + chu_kou_interval_min / 1000
                k_max = kou_xue_time + chu_kou_interval_max / 1000

                # 有交集：出伤时间点需要同时满足两者的要求
                #   [k_min, k_max]   [k_min, k_max]     [k_min, k_max]    [k_min,     k_max]
                # [c_min, c_max]      [c_min, c_max]  [c_min,     c_max]    [c_min, c_max]
                # 无交集: 以 途径1 计算出的为准
                #                 [k_min, k_max]
                # [c_min, c_max]                  [c_min, c_max]

                # 途径1：随机出一个时间点
                chu_shang_time = last_chu_shang_time + randtime(chu_shang_interval_min, chu_shang_interval_max)

                if k_min > c_max or k_max < c_min:
                    # 没有交集，以出伤间隔为准
                    # logging.debug("以出伤间隔为准 kou_xue_time: %s, last_chu_shang_time: %s, c_min: %s, c_max:%s, k_min:%s, k_max:%s",
                    #             kou_xue_time, last_chu_shang_time, c_min, c_max, k_min, k_max)
                    pass
                else:
                    # 有交集，需要同时满足两者的要求
                    overlap_min = max(c_min, k_min)
                    overlap_max = min(c_max, k_max)

                    if chu_shang_time < overlap_min or chu_shang_time > overlap_max:
                        chu_shang_time = randtime(
                            round(overlap_min * 1000), round(overlap_max * 1000))

            else:
                chu_shang_time = kou_xue_time + randtime(chu_kou_interval_min, chu_kou_interval_max)

            if chu_shang_time < end_time:
                chu_shang_action = chu_shang_cls(fufu)
                chu_shang_action.set_timestamp(chu_shang_time)
                plan.insert_action(chu_shang_action)
                c_action_lst.append(chu_shang_action)
                c_num += 1

            last_chu_shang_time = chu_shang_time

        if kou_xue_num and k_num >= kou_xue_num:
            break

        kou_xue_time += randtime(kou_xue_interval_min, kou_xue_interval_max)

    if kou_xue_num and k_num < kou_xue_num:
        print("Warning: kou_xue_num specified, but not fullfilled:" + str(k_num) + " < " + str(kou_xue_num))

    if chu_shang_num and c_num < chu_shang_num:
        print("Warning: chu_shang_num specified, but not fullfilled:" + str(c_num) + " < " + str(chu_shang_num))

    if enable_debug:
        # logging.debug(f"{name}: {start_time:.3f} to {end_time:.3f}: k_num = {k_num} c_num = {c_num}")
        cur_min_k_num = salon_member_min_k_num[kou_xue_cls.NAME]
        cur_min_c_num = salon_member_min_c_num[chu_shang_cls.NAME]
        if cur_min_k_num == 0 or k_num <  cur_min_k_num:
            salon_member_min_k_num[kou_xue_cls.NAME] = k_num

        if cur_min_c_num == 0 or c_num < cur_min_c_num:
            salon_member_min_c_num[chu_shang_cls.NAME] = c_num


    return (k_action_lst, c_action_lst)


def calc_score(fufu_initial_state: Character_FuFu, 
               create_plan_func: Callable[[Character_FuFu], FuFuActionPlan]):
    all_damage = 0
    full_six_zhan_bi = 0
    run_num = MAX_RUN_NUM

    for _ in range(0, run_num):
        plan = create_plan_func(fufu_initial_state)

        with plan:
            plan.run()

            all_damage += plan.total_damage
            full_six_zhan_bi += plan.full_six_damage / plan.total_damage

            if enable_record:
                expect_score = ys_expect_damage(plan.total_damage, fufu_initial_state.get_crit_rate(), fufu_initial_state.get_crit_damage())
                crit_score = round(plan.total_damage * (1 + fufu_initial_state.get_crit_damage()))
                logging.debug("damage: %d, expect_score:%s, crit_score:%s",
                            round(plan.total_damage), round(expect_score), round(crit_score))

    all_damage /= run_num
    full_six_zhan_bi /= run_num

    if enable_debug:
        logging.debug("min_k_num: %s", salon_member_min_k_num)
        logging.debug("min_c_num: %s", salon_member_min_c_num)
        

    return (all_damage, round(full_six_zhan_bi, 3))


def scan_syw_combine(syw_combine: list[ShengYiWu], 
                     fufu_creator_func: Callable[[], Character_FuFu],
                     check_fufu_func: Callable[[Character_FuFu], bool]) -> Character_FuFu:
    fufu = fufu_creator_func()
    fufu.set_syw_combine(syw_combine)

    name_count = fufu.get_syw_name_count()
    # print(name_count)
    for n in name_count:
        if name_count[n] < 2:  # 散件不计算套装效果
            continue

        # print(n)
        if n == ShengYiWu.HUA_HAI:
            fufu.get_hp().modify_max_hp_per(0.2)
        elif n == ShengYiWu.SHUI_XIAN:
            fufu.add_all_bonus(0.15)
        elif n == ShengYiWu.QIAN_YAN:
            fufu.get_hp().modify_max_hp_per(0.2)
        elif n == ShengYiWu.CHEN_LUN:
            fufu.add_all_bonus(0.15)
        elif n == ShengYiWu.JU_TUAN:
            fufu.add_e_bonus(0.2)
            if name_count[n] >= 4:
                # FIXME: 暂时不考虑芙芙在前台会吃不到 0.25 增伤的问题，需要后续软件框架继续完善
                # 满命芙芙：qeaa起手时，在aa时三小只有一次同时出伤，此时应该是吃不到的
                # 非满命芙芙：基本在后台，因此基本是能吃满增伤的
                fufu.add_e_bonus(0.25 + 0.25)

    if not check_fufu_func(fufu):
        return None

    return fufu

def qualify_syw(score_data: ShengYiWu_Score, 
                fufu_creator_func: Callable[[], Character_FuFu],
                check_fufu_func: Callable[[Character_FuFu], bool],
                qualify_func):
    fufu = scan_syw_combine(score_data.syw_combine, fufu_creator_func, check_fufu_func)
    if not fufu:
        return False

    # 关于qualify_func:
    #
    # ”录制“一次计算过程，作为快速筛选的依据
    # 录制方法：
    # 0. 在get_debug_raw_score_list设置好用于录制的圣遗物组合，选那种80分的，不要选最好的，也不要选太差的
    # 1. 找到本文件开头处的 enable_debug和enable_record，均置为 True
    # 然后执行，在logging的输出文件里能找到录制好的计算过程，稍作处理去掉一些冗余即可，也可不处理
    # 后面会打印出这个计算的结果(需要把后面的 logging.debug注释去掉)，记得运行一下确认伤害量是正常的
    # 可多录制几次(默认10次)，找接近于平均值的

    damage = qualify_func(fufu)

    score_data.damage_to_score(damage, fufu.get_crit_rate(), fufu.get_crit_damage())
    score_data.custom_data = fufu

    # logging.debug("damage:%s, expect_score:%s, crit_score:%s",
    #              damage, score_data.expect_score, score_data.crit_score)

    return True


def calculate_score_common(score_data: ShengYiWu_Score, 
                    fufu_creator_func: Callable[[], Character_FuFu], 
                    check_fufu_func: Callable[[Character_FuFu], bool],
                    create_plan_func: Callable[[Character_FuFu], FuFuActionPlan]):
    if score_data.custom_data:
        fufu = score_data.custom_data
    else:
        fufu = scan_syw_combine(score_data.syw_combine, fufu_creator_func, check_fufu_func)

    if not fufu:
        return False

    # logging.debug(str(fufu))
    damage, full_six_zhan_bi = calc_score(fufu, create_plan_func)
    if not damage:
        return False

    score_data.damage_to_score(damage, fufu.get_crit_rate(), fufu.get_crit_damage())

    if enable_record:
        logging.debug("finished: damage: %d, full_six_zhan_bi: %s, expect_score:%s, crit_score:%s, crit_rate: %s, crit_damage: %s",
                        round(damage), round(full_six_zhan_bi, 3),
                        round(score_data.expect_score), round(score_data.crit_score),
                        round(fufu.get_crit_rate(), 3), round(fufu.get_crit_damage(), 3))
    
    panel_hp = fufu.get_max_hp()
    score_data.custom_data = [full_six_zhan_bi, int(panel_hp),
                              round(fufu.get_e_bonus(), 3), round(fufu.get_normal_a_bonus(), 3),
                              round(fufu.get_crit_rate(), 3), round(fufu.get_crit_damage(), 3), 
                              round(fufu.get_energy_recharge(), 1)]

    return True


def get_debug_raw_score_list():
    # [(zhui_yi, h, cc:0.152, cd:0.132, re:0.097, defp:0.073),
    # (shui_xian, y, cc:0.117, cd:0.194, def:23, elem:23),
    # (shui_xian, s, cc:0.074, cd:0.218, hpp:0.466, re:0.091, atk:18),
    # (hua_hai, b, cc:0.093, cd:0.21, hpp:0.466, defp:0.131, def:23),
    # (hua_hai, t, cc:0.07, cd:0.622, hpp:0.111, hp:687, defp:0.058)]]
    # 只计算双水fixed_hp = (1 + 0.466 + 0.466 + 0.111 + 0.2 + 0.25) * 15307 + 4780 + 687 = 43627(实际为43625)
    # fixed_full_bonus = 1 + 万叶0.4 + 2水仙 = 1.55
    # fixed_e_bonus = 1 + 万叶0.4 + 固有天赋0.28 + 2水仙 = 1.83
    syw_combine = [
        ShengYiWu(ShengYiWu.ZHUI_YI, ShengYiWu.PART_HUA,
                  crit_rate=0.152, crit_damage=0.132, energy_recharge=0.097, def_per=0.073),
        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_YU,
                  crit_rate=0.117, crit_damage=0.194, def_v=23, elem_mastery=23),
        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_SHA,
                  crit_rate=0.074, crit_damage=0.218, energy_recharge=0.091, atk=18, hp_percent=0.466),
        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_BEI,
                  crit_rate=0.093, crit_damage=0.21, def_per=0.131, def_v=23, hp_percent=0.466),
        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_TOU, crit_damage=ShengYiWu.CRIT_DAMAGE_MAIN,
                  def_per=0.058, hp=687, hp_percent=0.111, crit_rate=0.07)
    ]
    return [ShengYiWu_Score(syw_combine)]


def match_sha_callback(syw: ShengYiWu):
    return syw.hp_percent == ShengYiWu.BONUS_MAX or syw.energy_recharge == ShengYiWu.ENERGY_RECHARGE_MAX


def match_bei_callback(syw: ShengYiWu):
    return syw.hp_percent == ShengYiWu.BONUS_MAX or syw.elem_type == Ys_Elem_Type.SHUI


def match_tou_callback(syw: ShengYiWu):
    return syw.crit_rate == ShengYiWu.CRIT_RATE_MAIN or syw.crit_damage == ShengYiWu.CRIT_DAMAGE_MAIN or syw.hp_percent == ShengYiWu.BONUS_MAX

def check_sys_args():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--fast", action="store_true", help="fast mode, qualifier threshold will set to 1.7")
    parser.add_argument("-n", "--no_qualifier", action="store_true", help="no qualifier, maybe extremely slow")
    args = parser.parse_args()

    enable_qualifier = True
    if args.no_qualifier:
        enable_qualifier = False
        print("no qualifier, maybe extremely slow")
    elif args.fast:
        print("fast mode, set threshold to 1.7")
        set_qualifier_threshold(1.7)

    return enable_qualifier

def find_syw_for_fu_ning_na(calculate_score_callback, 
                            result_txt_file,
                            calculate_score_qualifier=None):
    enable_qualifier = check_sys_args()

    if enable_debug:
        raw_score_list = get_debug_raw_score_list()
    else:
        combine_desc_lst = Syw_Combine_Desc.any_2p2([ShengYiWu.JU_TUAN,
                                                    ShengYiWu.HUA_HAI,
                                                    ShengYiWu.QIAN_YAN,
                                                    ShengYiWu.CHEN_LUN,
                                                    ShengYiWu.SHUI_XIAN])

        combine_desc_lst.append(Syw_Combine_Desc(
            set1_name=ShengYiWu.JU_TUAN, set1_num=4))

        raw_score_list = find_syw_combine(combine_desc_lst,
                                          match_sha_callback=match_sha_callback,
                                          match_bei_callback=match_bei_callback,
                                          match_tou_callback=match_tou_callback)
        print(len(raw_score_list))

    result_description = ", ".join(["满命六刀伤害占比", "面板最大生命值", 
                                    "战技元素伤害加成", "满命六刀元素伤害加成",
                                    "暴击率", "暴击伤害", "充能效率"])
    
    if enable_qualifier:
        qualifier = calculate_score_qualifier
    else:
        qualifier = None

    return calculate_score(raw_score_list,
                           calculate_score_callbak=calculate_score_callback,
                           result_txt_file=result_txt_file,
                           result_description=result_description,
                           calculate_score_qualifier=qualifier
                           )
