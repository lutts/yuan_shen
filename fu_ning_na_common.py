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

from base_syw import ShengYiWu, ShengYiWu_Score, calculate_score, Syw_Combine_Desc, find_syw_combine, calc_expect_damage
from health_point import HealthPoint
from character import Character, Character_HP_Change_Data
from monster import Monster
from ye_lan import YeLanQBonus
from action import Action, ActionPlan


enable_debug = False
enable_record = False
MAX_RUN_NUM = 10

HEI_FU_BEI_LV = 18
BAI_FU_BEI_LV = 18 + 25

ZHUAN_WU_HP_BEI_LV = 0.14
ZHUAN_WU_E_BONUS_BEI_LV = 0.08

def randtime(t_min, t_max):
    return random.randint(t_min, t_max) / 1000


class Character_FuFu(Character):
    NAME = "furina"
    BASE_HP = 15307

    def __init__(self, ming_zuo_num=6, has_zhuan_wu=True, required_energy_recharge=120):
        """
        * ming_zuo_num: 命座数
        * has_zhuan_wu: 是否有专武
        * required_energy_recharge: 充能需求

        充能需求参考：
        四命以下: 双水170%, 单水220
        四命及以上: 双水120, 单水160
        有雷神、西福斯的月光等其他充能手段酌情调整
        """
        super().__init__(name=Character_FuFu.NAME, base_hp=Character_FuFu.BASE_HP)
        self.ming_zuo_num = ming_zuo_num
        self.has_zhuan_wu = has_zhuan_wu


        self.required_energy_recharge = required_energy_recharge

        if ming_zuo_num >= 1:
            self.BASE_QI_FEN_ZHI = 150
            self.MAX_QI_FEN_ZHI = 400
        else:
            self.BASE_QI_FEN_ZHI = 0
            self.MAX_QI_FEN_ZHI = 300

        self.MAX_TOTAL_QI_FEN_ZHI = self.MAX_QI_FEN_ZHI

        if ming_zuo_num >= 2:
            self.QI_INCREASE_BEI_LV = 3.5
            self.QI_HP_BEI_LV = 0.0035
            self.MING_2_HP_BONUS_MAX = 1.4
            self.MAX_TOTAL_QI_FEN_ZHI = 800
        else:
            self.QI_INCREASE_BEI_LV = 1
            self.QI_HP_BEI_LV = 0
            self.MING_2_HP_BONUS_MAX = 0

        if ming_zuo_num >= 3:
            self.Q_BEI_LV = 24.2
            self.QI_TO_BONUS_BEI_LV = 0.0031
            self.QI_TO_CURE_BEI_LV = 0.0013
        else:
            self.Q_BEI_LV = 20.5
            self.QI_TO_BONUS_BEI_LV = 0.0025
            self.QI_TO_CURE_BEI_LV = 0.001

        if ming_zuo_num >= 5:
            self.E_BEI_LV = 16.7
            self.GE_ZHE_CURE_BEI_LV = 10.2
            self.GE_ZHE_CURE_BASE = 1271

            self.FU_REN_BEI_LV = 6.87
            self.XUN_JUE_BEI_LV = 12.67
            self.PANG_XIE_BEI_LV = 17.61
        else:
            self.E_BEI_LV = 14.2
            self.GE_ZHE_CURE_BEI_LV = 8.64
            self.GE_ZHE_CURE_BASE = 1017

            self.FU_REN_BEI_LV = 5.82
            self.XUN_JUE_BEI_LV = 10.73
            self.PANG_XIE_BEI_LV = 14.92

        self.bei_lv_to_salon_member_name = {
            self.FU_REN_BEI_LV: "夫人",
            self.XUN_JUE_BEI_LV: "勋爵",
            self.PANG_XIE_BEI_LV: "螃蟹"
        }

        self.bei_lv_to_str = {
            self.FU_REN_BEI_LV: "fufu.FU_REN_BEI_LV / 100",
            self.XUN_JUE_BEI_LV: "fufu.XUN_JUE_BEI_LV / 100",
            self.PANG_XIE_BEI_LV: "fufu.PANG_XIE_BEI_LV / 100"
        }

    def gu_you_tian_fu_2_bonus(self, hp):
        return min(self.get_hp().get_max_hp() / 1000 * 0.007, 0.28)


R_CUR_HP_KEY = "cur_hp"
R_CUR_A_BONUS_KEY = "cur_a_bonus"
R_CUR_E_BONUS_KEY = "cur_e_bonus"
R_SALON_MEMBER_BONUS_KEY = "salon_member_bonus"
R_CUR_Q_BONUS_KEY = "cur_q_bonus"

R_CUR_HP_INIT = R_CUR_HP_KEY + " = hp"
R_CUR_A_BONUS_INIT = R_CUR_A_BONUS_KEY + " = 1 + a_bonus"
R_CUR_E_BONUS_INIT = R_CUR_E_BONUS_KEY + " = 1 + e_bonus"
R_SALON_MEMBER_BONUS_INIT = R_SALON_MEMBER_BONUS_KEY + " = 1 + e_bonus + 0.28"
R_CUR_Q_BONUS_INIT = R_CUR_Q_BONUS_KEY + " = 1 + q_bonus"


class FuFuActionPlan(ActionPlan):
    def __init__(self, fufu_initial_state: Character_FuFu, teammate_hps: dict[str, HealthPoint]):
        self.__fufu: Character_FuFu = copy.deepcopy(fufu_initial_state)
        self.__teammates: list[Character] = []
        for name, hp in teammate_hps.items():
            c = Character(name)
            c.set_hp(copy.deepcopy(hp))
            self.__teammates.append(c)

        super().__init__(characters=[self.__fufu] + self.__teammates,
                         monster=Monster())
        
        self.qi_fen_zhi_supervisor = Qi_Fen_Zhi_Supervisor()

        if self.__fufu.ming_zuo_num >= 6:
            self.add_hei_fu_damage_callback(Hei_Fu_Cure_Supervisor().on_hei_fu_damage)

        if self.__fufu.has_zhuan_wu:
            self.zhuan_wu_supervisor = Zhuan_Wu_Supervisor()
            self.add_consume_hp_callback(self.zhuan_wu_supervisor.on_hp_changed)
            self.add_regenerate_hp_callback(self.zhuan_wu_supervisor.on_hp_changed)
        else:
            self.zhuan_wu_supervisor = None

        self.ye_lan_q_bonus = YeLanQBonus()

        self.full_six_damage = 0

        # 以下变量用于预筛选代码录制
        self.ye_lan_e_num = 0
        self.extra_a_bonus = 0
        self.extra_e_bonus = 0
        self.extra_q_bonus = 0
        self.recorded_strs = {
            R_CUR_HP_KEY: R_CUR_HP_INIT,
            R_CUR_A_BONUS_KEY: R_CUR_A_BONUS_INIT,
            R_CUR_E_BONUS_KEY: R_CUR_E_BONUS_INIT,
            R_SALON_MEMBER_BONUS_KEY: R_SALON_MEMBER_BONUS_INIT,
            R_CUR_Q_BONUS_KEY: R_CUR_Q_BONUS_INIT
        }
        self.last_printed_strs = {}

    def get_fufu(self) -> Character_FuFu:
        return self.__fufu
    
    def get_teammates(self) -> list[Character]:
        return self.__teammates

    def get_teammate(self, name) -> Character:
        for t in self.__teammates:
            if t.name == name:
                return t

    def get_max_hp(self):
        return self.__fufu.get_hp().get_max_hp()

    def get_a_bonus(self):
        self.debug("芙芙普攻元素增伤: %s", round(self.__fufu.get_a_bonus(), 3))
        return self.__fufu.get_a_bonus() + self.get_ye_lan_q_bonus()

    def get_e_bonus(self):
        self.debug("芙芙e元素增伤: %s", round(self.__fufu.get_e_bonus(), 3))
        return self.__fufu.get_e_bonus() + self.get_ye_lan_q_bonus()

    def get_q_bonus(self):
        self.debug("芙芙q元素增伤: %s", round(self.__fufu.get_q_bonus(), 3))
        return self.__fufu.get_q_bonus() + self.get_ye_lan_q_bonus()

    def get_ye_lan_q_bonus(self):
        if self.__fufu.is_in_foreground():
            self.debug("芙芙在前台获得夜兰增伤: %s", round(
                self.ye_lan_q_bonus.bonus(self.get_current_action_time()), 3))
            return self.ye_lan_q_bonus.bonus(self.get_current_action_time())
        else:
            return 0

    ##################################################

    def __damage_record_hp(self):
        # for damage record
        s = "cur_hp = hp"
        p = []
        if self.zhuan_wu_supervisor and self.zhuan_wu_supervisor.hp_bonus_level:
            p.append("0.14 * " + str(self.zhuan_wu_supervisor.hp_bonus_level))

        if self.ye_lan_e_num:
            p.append("0.1 * " + str(self.ye_lan_e_num))

        if self.qi_fen_zhi_supervisor.effective_qi_fen_zhi > self.__fufu.MAX_QI_FEN_ZHI and self.__fufu.ming_zuo_num >= 2:
            p.append(
                "(" + str(min(800, round(self.qi_fen_zhi_supervisor.effective_qi_fen_zhi, 3))) + " - 400) * 0.0035")

        if p:
            s += " + ("
            s += " + ".join(p)
            s += ") * Character_FuFu.BASE_HP"

        if s != self.recorded_strs[R_CUR_HP_KEY]:
            self.recorded_strs[R_CUR_HP_KEY] = s

    def damage_record_hp(self):
        self.__damage_record_hp()
    
    def add_all_bonus(self, bonus):
        self.extra_a_bonus += bonus
        self.extra_e_bonus += bonus
        self.extra_q_bonus += bonus
        self.damage_record_bonus()

    def sub_all_bonus(self, bonus):
        self.extra_a_bonus -= bonus
        self.extra_e_bonus -= bonus
        self.extra_q_bonus -= bonus
        self.damage_record_bonus()

    def __damage_record_bonus(self):
        a_lst = []
        e_lst = []
        q_lst = []

        if self.extra_a_bonus:
            a_lst.append(str(round(self.extra_a_bonus, 3)))
        
        if self.extra_e_bonus:
            e_lst.append(str(round(self.extra_e_bonus, 3)))

        if self.extra_q_bonus:
            q_lst.append(str(round(self.extra_q_bonus, 3)))

        if self.__fufu.BASE_QI_FEN_ZHI:
            q_lst.append(str(self.__fufu.BASE_QI_FEN_ZHI) + " * " + str(self.__fufu.QI_TO_BONUS_BEI_LV))

        if self.zhuan_wu_supervisor and self.zhuan_wu_supervisor.e_bonus_level:
            e_lst.append("0.08 * " + str(self.zhuan_wu_supervisor.e_bonus_level))


        qi = min(self.__fufu.MAX_QI_FEN_ZHI, self.qi_fen_zhi_supervisor.effective_qi_fen_zhi)
        qi = round(qi, 3)
        if qi:
            qi_str = str(qi) + " * " + str(self.__fufu.QI_TO_BONUS_BEI_LV)
            a_lst.append(qi_str)
            e_lst.append(qi_str)

        a_str = R_CUR_A_BONUS_INIT
        if a_lst:
            a_str += " + " 
            a_str += " + ".join(a_lst)

        if a_str != self.recorded_strs[R_CUR_A_BONUS_KEY]:
            self.recorded_strs[R_CUR_A_BONUS_KEY] = a_str

        salon_member_str = R_SALON_MEMBER_BONUS_INIT
        e_str = R_CUR_E_BONUS_INIT
        if e_lst:
            e_lst_str = " + " + " + ".join(e_lst)
            e_str += e_lst_str
            salon_member_str += e_lst_str

        if e_str != self.recorded_strs[R_CUR_E_BONUS_KEY]:
            self.recorded_strs[R_CUR_E_BONUS_KEY] = e_str

        if salon_member_str != self.recorded_strs[R_SALON_MEMBER_BONUS_KEY]:
            self.recorded_strs[R_SALON_MEMBER_BONUS_KEY] = salon_member_str

        q_str = R_CUR_Q_BONUS_INIT
        if q_lst:
            q_str += " + "
            q_str += " + ".join(q_lst)

        if q_str != self.recorded_strs[R_CUR_Q_BONUS_KEY]:
            self.recorded_strs[R_CUR_Q_BONUS_KEY] = q_str

    def damage_record_bonus(self):
        self.__damage_record_bonus()

    def print_recored_str(self, key, print_empty_line=True):
        s = self.recorded_strs[key]
        last_printed = None
        if key in self.last_printed_strs:
            last_printed = self.last_printed_strs[key]

        if s != last_printed:
            if print_empty_line:
                logging.debug("")
            logging.debug(s)
            self.last_printed_strs[key] = s
            return True

    def print_damage(self, bei_lv_str, bonus_key, others=None):
        cur_hp_changed = self.print_recored_str(R_CUR_HP_KEY)
        self.print_recored_str(bonus_key, print_empty_line=not cur_hp_changed)
        s = ["damage += cur_hp", bei_lv_str]
        s.append(bonus_key)
        if others:
            s.append(str(others))
        s.append(str(round(self.monster.kang_xin_xi_su, 3)))
        s.append(str(round(self.monster.fang_yu_xi_shu, 3)))
        logging.debug(" * ".join(s))

    @staticmethod
    def get_effective_delay():
        return random.randint(66, 117) / 1000

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
    
    def fufu_q_start(self):
        self.qi_fen_zhi_supervisor.set_qi_fen_zhi(self, self.__fufu.BASE_QI_FEN_ZHI)
        self.qi_fen_zhi_supervisor.start_supervise(self)

    def fufu_q_stop(self):
        self.qi_fen_zhi_supervisor.stop_supervise(self)
        self.qi_fen_zhi_supervisor.set_qi_fen_zhi(self, 0)

    def fufu_consume_hp_per(self, hp_per):
        self.modify_cur_hp(targets=self.characters, hp_per=(0 - hp_per))

    def add_hei_fu_damage_callback(self, callback):
        self.events.on_hei_fu_damage += callback
    
    def call_hei_fu_damage_callback(self):
        if hasattr(self.events, "on_hei_fu_damage"):
            self.events.on_hei_fu_damage(self)


class Zhuan_Wu_Supervisor:
    def __init__(self):
        self.__e_bonus_level = 0
        self.__e_bonus_last_change_time = 0

        self.__hp_bonus_level = 0
        self.__hp_bonus_last_change_time = 0

    @property
    def e_bonus_level(self):
        return self.__e_bonus_level
    
    @property
    def hp_bonus_level(self):
        return self.__hp_bonus_level

    def on_hp_changed(self, plan: FuFuActionPlan, source: Character, targets_with_data: list[Character_HP_Change_Data]):
        fufu = plan.get_fufu()
        for tdata in targets_with_data:
            if tdata.character is fufu:
                self.increase_e_bonus_level(plan)
            else:
                self.increase_hp_bonus_level(plan)

        if self.__hp_bonus_level >= 2 and self.__e_bonus_level >= 3:
            plan.remove_consume_hp_callback(self.on_hp_changed)
            plan.remove_regenerate_hp_callback(self.on_hp_changed)
                      
    def increase_e_bonus_level(self, plan: FuFuActionPlan):
        if self.__e_bonus_level >= 3:
            return
        
        cur_time = plan.get_current_action_time()

        if self.__e_bonus_last_change_time and (cur_time - self.__e_bonus_last_change_time < 0.2):
            return

        self.__e_bonus_last_change_time = cur_time
        self.__e_bonus_level += 1

        action = Increase_ZhuanWu_E_Bonus_Level_Action(self)
        action.set_timestamp(cur_time + plan.get_effective_delay())
        plan.insert_action_runtime(action)

    def increase_hp_bonus_level(self, plan: FuFuActionPlan):
        if self.__hp_bonus_level >= 2:
            return
        
        cur_time = plan.get_current_action_time()

        if self.__hp_bonus_last_change_time and (cur_time - self.__hp_bonus_last_change_time < 0.2):
            # 有0.2秒的CD
            return

        self.__hp_bonus_last_change_time = cur_time
        self.__hp_bonus_level += 1

        action = Increase_ZhuanWu_Hp_Level_Action(self)
        action.set_timestamp(cur_time + plan.get_effective_delay())
        plan.insert_action_runtime(action)

        
class Increase_ZhuanWu_Hp_Level_Action(Action):
    def __init__(self, supervisor: Zhuan_Wu_Supervisor):
        super().__init__("专武生命值叠层")
        self.supervisor = supervisor

    def do_impl(self, plan: FuFuActionPlan):
        plan.get_fufu().get_hp().modify_max_hp_per(ZHUAN_WU_HP_BEI_LV)
        self.debug("专武生命叠一层，目前层数: %d",  self.supervisor.hp_bonus_level)
        if enable_record:
            plan.damage_record_hp()


class Increase_ZhuanWu_E_Bonus_Level_Action(Action):
    def __init__(self, supervisor: Zhuan_Wu_Supervisor):
        super().__init__("专武战技增伤叠层")
        self.supervisor = supervisor

    def do_impl(self, plan: FuFuActionPlan):
        plan.get_fufu().add_e_bonus(ZHUAN_WU_E_BONUS_BEI_LV)
        plan.debug("专武战技叠一层，目前层数: %d", self.supervisor.e_bonus_level)
        plan.damage_record_bonus()


class Qi_Fen_Zhi_Supervisor:
    def __init__(self):
        self.blocking = True

        self.__qi_fen_zhi = 0
        self.effective_qi_fen_zhi = 0
        self.prev_qi_elem_bonus = 0
        self.prev_qi_healing_bonus = 0
        self.prev_qi_hp_per_bonus = 0

    def start_supervise(self, plan: FuFuActionPlan):
        plan.add_consume_hp_callback(self.on_hp_changed)
        plan.add_regenerate_hp_callback(self.on_hp_changed)

    def stop_supervise(self, plan: FuFuActionPlan):
        plan.remove_consume_hp_callback(self.on_hp_changed)
        plan.remove_regenerate_hp_callback(self.on_hp_changed)

    def on_hp_changed(self, plan: FuFuActionPlan, source: Character, targets_with_data: list[Character_HP_Change_Data]):
        qi_fen_zhi = 0
        fufu = plan.get_fufu()

        for tdata in targets_with_data:
            qi_fen_zhi += abs(tdata.data.hp_per) * fufu.QI_INCREASE_BEI_LV * 100

        self.add_qi_fen_zhi(plan, qi_fen_zhi)

        if self.__qi_fen_zhi >= fufu.MAX_TOTAL_QI_FEN_ZHI:
            self.stop_supervise(plan)

    def add_qi_fen_zhi(self, plan: FuFuActionPlan, qi):
        fufu = plan.get_fufu()
        self.__qi_fen_zhi += qi
        if self.__qi_fen_zhi > fufu.MAX_TOTAL_QI_FEN_ZHI:
            self.__qi_fen_zhi = fufu.MAX_TOTAL_QI_FEN_ZHI
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
        if self.__qi_fen_zhi == self.effective_qi_fen_zhi:
            self.blocking = True
            plan.debug("气氛值调整线程：气氛值没变化，转入阻塞")
            return False

        plan.debug("气氛值调整开始：生效层数%s", round(self.__qi_fen_zhi, 3))

        t = self.__do_apply_qi_fen_zhi(plan)

        self.effective_qi_fen_zhi = self.__qi_fen_zhi
        self.prev_qi_elem_bonus = t[0]
        self.prev_qi_healing_bonus = t[1]
        self.prev_qi_hp_per_bonus = t[2]

        if enable_record:
            plan.damage_record_hp()
            plan.damage_record_bonus()

        return True

    def __do_apply_qi_fen_zhi(self, plan: FuFuActionPlan):
        fufu = plan.get_fufu()

        if self.__qi_fen_zhi > fufu.MAX_QI_FEN_ZHI:
            bonus_qi_fen_zhi = fufu.MAX_QI_FEN_ZHI
            hp_qi_fen_zhi = self.__qi_fen_zhi - fufu.MAX_QI_FEN_ZHI
        else:
            bonus_qi_fen_zhi = self.__qi_fen_zhi
            hp_qi_fen_zhi = 0

        elem_bonus = bonus_qi_fen_zhi * fufu.QI_TO_BONUS_BEI_LV
        healing_bonus = bonus_qi_fen_zhi * fufu.QI_TO_CURE_BEI_LV
        hp_per_bonus = hp_qi_fen_zhi * fufu.QI_HP_BEI_LV

        fufu.modify_all_elem_bonus(elem_bonus - self.prev_qi_elem_bonus)
        fufu.modify_incoming_healing_bonus(healing_bonus - self.prev_qi_healing_bonus)
        for t in plan.get_teammates():
            t.modify_incoming_healing_bonus(healing_bonus - self.prev_qi_healing_bonus)
        fufu.get_hp().modify_max_hp_per(hp_per_bonus - self.prev_qi_hp_per_bonus)
        plan.debug("气氛值调整完成，生命值上限：%d， a_bonus: %s, e_bonus: %s, q_bonus: %s, healing_bonus:%s",
                   round(fufu.get_hp().get_max_hp()),
                   round(fufu.get_a_bonus(), 3), round(fufu.get_e_bonus(), 3),
                   round(fufu.get_q_bonus(), 3), round(fufu.get_incoming_healing_bonus(), 3))

        return (elem_bonus, healing_bonus, hp_per_bonus)


class Apply_Qi_Fen_Zhi_Action(Action):
    def __init__(self, supervisor: Qi_Fen_Zhi_Supervisor):
        super().__init__("气氛值生效线程")
        self.supervisor = supervisor
        self.blocking = False

    def do_impl(self, plan: FuFuActionPlan):
        changed = self.supervisor.apply_qi_fen_zhi(plan)
        if not changed:
            return

        action = Apply_Qi_Fen_Zhi_Action(self.supervisor)
        next_time = self.get_timestamp() + random.randint(429, 587) / 1000
        action.set_timestamp(next_time)
        plan.insert_action_runtime(action)


class ZhongLiAction(Action):
    def __init__(self, name):
        super().__init__(name)

    def do_impl(self, plan: FuFuActionPlan):
        plan.monster.add_jian_kang(0.2)


class WanYe:
    def __init__(self, elem_mastery, xi_fu_si_jing_lian_num=0):
        """
        * elem_mastery: 万叶精通
        * xi_fu_si_jing_lian_num: 西福斯精炼数
        """
        self.started = False
        self.start_time = 0

        self.elem_bonus = elem_mastery * 0.04 / 100
        # self.ming_2_bonus = (elem_mastery + 200) * 0.04 / 100
        if xi_fu_si_jing_lian_num <= 0:
            self.energy_recharge = 0
        else:
            if xi_fu_si_jing_lian_num > 5:
                xi_fu_si_jing_lian_num = 5
            bei_lv = (0.036 + 0.09 * (xi_fu_si_jing_lian_num - 1)) / 100
            self.energy_recharge = elem_mastery * bei_lv * 0.3

        # logging.debug("wan ye: elem_bonus: %s, 2 ming bonus: %s, energy_recharge: %s",
        #              round(self.elem_bonus, 3), round(self.ming_2_bonus, 3), round(self.energy_recharge, 1))


class WanYeQAction(Action):
    def __init__(self, name, wan_ye: WanYe):
        super().__init__(name)
        self.wan_ye = wan_ye

    def do_impl(self, plan: FuFuActionPlan):
        self.debug("万叶q")
        fufu = plan.get_fufu()
        fufu.add_all_bonus(self.wan_ye.elem_bonus)
        plan.add_all_bonus(self.wan_ye.elem_bonus)
        fufu.add_energy_recharge(self.wan_ye.energy_recharge)

        plan.monster.add_jian_kang(0.4)


class WanYeBonusStopAction(Action):
    def __init__(self, name, wan_ye: WanYe):
        super().__init__(name)
        self.wan_ye = wan_ye

    def do_impl(self, plan: FuFuActionPlan):
        self.debug("万叶增伤消失")
        plan.get_fufu().sub_all_bonus(self.wan_ye.elem_bonus)
        plan.sub_all_bonus(self.wan_ye.elem_bonus)


class FengTaoInvalidAction(Action):
    def do_impl(self, plan: FuFuActionPlan):
        self.debug("风套减抗消失")
        plan.monster.sub_jian_kang(0.4)


class FuFu_Q_Action(Action):
    def do_impl(self, plan: FuFuActionPlan):
        plan.switch_to_forground(plan.get_fufu().name)
        plan.fufu_q_start()
        self.do_damage(plan)

    def do_damage(self, plan: FuFuActionPlan):
        hp = plan.get_max_hp()
        q_bonus = 1 + plan.get_q_bonus()

        q_damage = hp * plan.get_fufu().Q_BEI_LV / 100 * q_bonus
        q_damage = plan.add_damage(q_damage)
        self.debug("芙芙q出伤, %d, hp: %s, q_bonus:%s, monster:%s",
                   round(q_damage), hp, round(q_bonus, 3), plan.monster)
        if enable_record:
            plan.print_damage(bei_lv_str="fufu.Q_BEI_LV / 100",
                            bonus_key=R_CUR_Q_BONUS_KEY)


class FuFu_E_Action(Action):
    def do_impl(self, plan: FuFuActionPlan):
        plan.switch_to_forground(plan.get_fufu().name)
        hp = plan.get_max_hp()
        e_bonus = 1 + plan.get_e_bonus()

        e_damage = hp * plan.get_fufu().E_BEI_LV / 100 * e_bonus
        e_damage = plan.add_damage(e_damage)
        self.debug("芙芙e出伤, %d, hp: %s, bonus: %s, monster:%s",
                   round(e_damage), hp, round(e_bonus, 3), plan.monster)
        if enable_record:
            plan.print_damage(bei_lv_str="fufu.E_BEI_LV / 100",
                            bonus_key=R_CUR_E_BONUS_KEY)


class Hei_Fu_Cure_Supervisor:
    def __init__(self):
        self.end_time = 0
        self.is_cure_fufu_sync = True
        self.last_cure_teammate_actual_time = 0
        self.last_cure_teammate_effective_time = 0

    def on_hei_fu_damage(self, plan: FuFuActionPlan):
        cur_action_time = plan.get_current_action_time()
        if cur_action_time <= self.end_time:
            self.end_time += 2.9
            plan.debug("adjust end_time to %s", round(self.end_time, 3))
        else:
            self.start_cure_teammate(plan, cur_action_time)

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
            if tdata.character is plan.get_fufu():
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

    def get_cure_num(self, fufu: Character):
        return round(fufu.get_hp().get_max_hp() * 0.04)
    
    def do_impl(self, plan: FuFuActionPlan):
        if self.get_timestamp() > self.supervisor.end_time:
            self.debug("%s超时，不执行", self.name)
            return
        
        self.do_cure(plan)


class Hei_Fu_Cure_Teammate_Action(Hei_Fu_Cure_Action):
    def __init__(self, supervisor: Hei_Fu_Cure_Supervisor):
        super().__init__("治疗后台三人", supervisor)

    def do_cure(self, plan: FuFuActionPlan):
        cure_num = self.get_cure_num(plan.get_fufu())
        self.debug("治疗后台三人, %s", cure_num)
        plan.regenerate_hp(targets=plan.get_teammates(), hp=cure_num)

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
        fufu = plan.get_fufu()

        if fufu.get_hp().is_full():
            self.debug("治疗芙芙时，芙芙满血，阻塞并转入独立模式")
            # 芙芙是满血的，不用治疗，转入阻塞独立模式
            self.supervisor.is_cure_fufu_sync = False
            plan.add_consume_hp_callback(self.supervisor.on_consume_hp)
        else:
            cure_num = self.get_cure_num(fufu)
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


# 芒、荒的伤害刀似乎都是按黑芙计算的
# 注意：芒荒刀出伤的时候，芙芙不一定在前台


class Mang_Huang_Damage_Action(Action):
    def do_impl(self, plan: FuFuActionPlan):
        monster = plan.monster

        hp = plan.get_max_hp()
        a_bonus = 1 + plan.get_a_bonus()

        damage = hp * HEI_FU_BEI_LV / 100 * a_bonus
        damage = plan.add_damage(damage)
        plan.full_six_damage += damage
        self.debug("芒/荒刀出伤，%d, hp: %s, bonus: %s, monster:%s",
                   round(damage), hp, round(a_bonus, 3), monster)
        if enable_record:
            plan.print_damage(bei_lv_str="HEI_FU_BEI_LV / 100",
                            bonus_key=R_CUR_A_BONUS_KEY)


class Hei_Fu_Damage_Action(Action):
    def do_impl(self, plan: FuFuActionPlan):
        plan.switch_to_forground(plan.get_fufu().name)
        self.do_damage(plan)
        #self.do_cure(plan)
        plan.call_hei_fu_damage_callback()

    def do_damage(self, plan: FuFuActionPlan):
        hp = plan.get_max_hp()
        a_bonus = 1 + plan.get_a_bonus()
        damage = hp * HEI_FU_BEI_LV / 100 * a_bonus
        damage = plan.add_damage(damage)
        plan.full_six_damage += damage
        self.debug("%s出伤, %d, hp: %s, bonus:%s, monster:%s",
                   self.name, round(damage), hp, round(a_bonus, 3), plan.monster)
        if enable_record:
            plan.print_damage(bei_lv_str="HEI_FU_BEI_LV / 100",
                            bonus_key=R_CUR_A_BONUS_KEY)


class Bai_Dao_Kou_Xue_Action(Action):
    def do_impl(self, plan: FuFuActionPlan):
        # 白刀扣血 1%
        self.debug("%s", self.name)
        plan.fufu_consume_hp_per(0.01)


class Bai_Fu_Damage_Action(Action):
    def do_impl(self, plan: FuFuActionPlan):
        plan.switch_to_forground(plan.get_fufu().name)

        hp = plan.get_max_hp()
        bonus = 1 + plan.get_a_bonus()
        damage = hp * BAI_FU_BEI_LV / 100 * bonus
        damage = plan.add_damage(damage)
        plan.full_six_damage += damage
        self.debug("%s出伤，%d, hp: %s, bonus:%s, monster:%s",
                   self.name, round(damage), hp, round(bonus,  3), plan.monster)
        if enable_record:
            plan.print_damage(bei_lv_str="BAI_FU_BEI_LV / 100",
                            bonus_key=R_CUR_A_BONUS_KEY)


class Switch_To_Character_Action(Action):
    def __init__(self, name, character_name):
        super().__init__(name)
        self.character_name = character_name

    def do_impl(self, plan: FuFuActionPlan):
        self.debug("切换到%s", self.character_name)
        plan.switch_to_forground(self.character_name)

class Q_Animation_Action(Action):
    def __init__(self, name, character_name):
        super().__init__(name)
        self.character_name = character_name

    def do_impl(self, plan: FuFuActionPlan):
        self.set_anim_state(plan.get_character(self.character_name))

    def set_anim_state(self, ch: Character):
        pass

class Q_Animation_Start_Action(Q_Animation_Action):
    def set_anim_state(self, ch: Character):
        self.debug("%s大招动画开始", self.character_name)
        ch.get_hp().set_in_q_animation(True)


class Q_Animation_Stop_Action(Q_Animation_Action):
    def set_anim_state(self, ch: Character):
        self.debug("%s大招动画结束", self.character_name)
        ch.get_hp().set_in_q_animation(False)


class Ye_Lan_4_Ming_Action(Action):
    def do_impl(self, plan: FuFuActionPlan):
        plan.ye_lan_e_num += 1
        self.debug("夜兰四命生效一层")
        if enable_record:
            plan.damage_record_hp()
        plan.get_fufu().get_hp().modify_max_hp_per(0.1)
        for t in plan.get_teammates():
            t.get_hp().modify_max_hp_per(0.1)

        # hps_str = "fufu:" + str(plan.get_fufu().get_hp().get_max_hp()) + ", "
        # for t in plan.get_teammates():
        #     hps_str += t.name + ":" + str(t.get_hp().get_max_hp()) + ", "
        # self.debug("夜兰e后各角色生命值上限: %s", hps_str)


class Ye_Lan_Q_Bonus_Start(Action):
    def __init__(self, name, ye_lan_name):
        super().__init__(name)
        self.ye_lan_name = ye_lan_name

    def do_impl(self, plan: FuFuActionPlan):
        self.debug("夜兰大招出伤")
        ye_lan = plan.get_teammate(self.ye_lan_name)
        ye_lan.get_hp().set_in_q_animation(False)
        plan.ye_lan_q_bonus.start(self.get_timestamp())


class Fu_Fu_Q_Bonus_Stop_Action(Action):
    def do_impl(self, plan: FuFuActionPlan):
        self.debug("芙芙大招效果消失")
        plan.fufu_q_stop()


class Ye_Lan_Q_Bonus_Stop_Actioin(Action):
    def do_impl(self, plan: FuFuActionPlan):
        self.debug("夜兰大招效果消失")
        plan.ye_lan_q_bonus.stop()


class Salon_Member_Damage_Action(Action):
    def __init__(self, name, force_add_fufu_q_bonus=False):
        super().__init__(name)
        self.force_add_fufu_q_bonus = force_add_fufu_q_bonus

    def do_damage(self, plan: FuFuActionPlan, bei_lv):
        hp = plan.get_max_hp()
        fufu = plan.get_fufu()
        e_bonus = 1 + plan.get_e_bonus() + fufu.gu_you_tian_fu_2_bonus(hp)

        if plan.qi_fen_zhi_supervisor.effective_qi_fen_zhi == 0 and self.force_add_fufu_q_bonus:
            # print("force add q bonus")
            hp += round(fufu.MAX_QI_FEN_ZHI * fufu.QI_HP_BEI_LV * Character_FuFu.BASE_HP)
            e_bonus += fufu.MAX_QI_FEN_ZHI * fufu.QI_TO_BONUS_BEI_LV

        e_extra_bonus = 1
        if fufu.get_hp().get_cur_hp_per() > 0.5:
            e_extra_bonus += 0.1
        
        for t in plan.get_teammates():
            if t.get_hp().get_cur_hp_per() >  0.5:
                e_extra_bonus += 0.1
        
        damage = hp * bei_lv / 100 * e_bonus * e_extra_bonus
        damage = plan.add_damage(damage)

        self.debug("%s出伤, damage: %s, hp:%s bonus:%s, monster:%s",
                   fufu.bei_lv_to_salon_member_name[bei_lv], round(damage), 
                   hp, round(e_bonus, 3), plan.monster)
        if enable_record:
            plan.print_damage(bei_lv_str=fufu.bei_lv_to_str[bei_lv],
                            bonus_key=R_SALON_MEMBER_BONUS_KEY, 
                            others=round(e_extra_bonus, 1))


class Fu_Ren_Kou_Xue_Action(Action):
    def do_impl(self, plan: FuFuActionPlan):
        self.debug("夫人扣血")
        plan.fufu_consume_hp_per(0.016)


class Fu_Ren_Damage_Action(Salon_Member_Damage_Action):
    def do_impl(self, plan: FuFuActionPlan):
        self.do_damage(plan, plan.get_fufu().FU_REN_BEI_LV)


class Xun_Jue_Kou_Xue_Action(Action):
    def do_impl(self, plan: FuFuActionPlan):
        self.debug("勋爵扣血")
        plan.fufu_consume_hp_per(0.024)


class Xun_Jue_Damage_Action(Salon_Member_Damage_Action):
    def do_impl(self, plan: FuFuActionPlan):
        self.do_damage(plan, plan.get_fufu().XUN_JUE_BEI_LV)


class Pang_Xie_Kou_Xue_Action(Action):
    def do_impl(self, plan: FuFuActionPlan):
        self.debug("螃蟹扣血")
        plan.fufu_consume_hp_per(0.036)


class Pang_Xie_Damage_Action(Salon_Member_Damage_Action):
    def do_impl(self, plan: FuFuActionPlan):
        self.do_damage(plan, plan.get_fufu().PANG_XIE_BEI_LV)


class Ge_Zhe_Cure_Action(Action):
    def do_impl(self, plan: FuFuActionPlan):
        fufu = plan.get_fufu()
        cure_num = round(plan.get_max_hp() * fufu.GE_ZHE_CURE_BEI_LV / 100 + fufu.GE_ZHE_CURE_BASE)

        foreground_character = plan.get_foreground_character()
        self.debug("歌者治疗 %s, 治疗量: %s", foreground_character.name, cure_num)
        plan.regenerate_hp(targets=[foreground_character], hp=cure_num)


FU_REN_NAME = "夫人"
XUN_JUE_NAME = "勋爵"
PANG_XIE_NAME = "螃蟹"

kou_xue_interval_dict = {
    FU_REN_NAME: (1468, 1684),
    XUN_JUE_NAME: (3180, 3387),
    PANG_XIE_NAME: (5056, 5293)
}

chu_shang_interval_dict = {
    FU_REN_NAME: (1467, 1725),
    XUN_JUE_NAME: (3127, 3443),
    PANG_XIE_NAME: (5063, 5325)
}

chu_shang_kou_xue_interval_dict = {
    FU_REN_NAME: (330, 721),
    XUN_JUE_NAME: (723, 951),
    PANG_XIE_NAME: (745, 1018)
}


def schedule_little_three(plan: FuFuActionPlan, name,
                          start_time, end_time,
                          kou_xue_cls, chu_shang_cls,
                          kou_xue_num=None, chu_shang_num=None):
    kou_xue_interval_min, kou_xue_interval_max = kou_xue_interval_dict[name]
    chu_shang_interval_min, chu_shang_interval_max = chu_shang_interval_dict[name]
    chu_kou_interval_min, chu_kou_interval_max = chu_shang_kou_xue_interval_dict[name]

    # 三小只第一次扣血并不一定是同时的，是在一个窗口内有先后顺序
    kou_xue_time = start_time + randtime(0, 133)
    last_chu_shang_time = 0

    k_num = 0
    c_num = 0

    k_action_lst = []
    c_action_lst = []

    while kou_xue_time < end_time:
        kou_xue_action = kou_xue_cls(name + "扣血")
        kou_xue_action.set_timestamp(kou_xue_time + plan.get_effective_delay())
        plan.insert_action(kou_xue_action)
        k_action_lst.append(kou_xue_action)
        k_num += 1

        if chu_shang_num and c_num < chu_shang_num:
            if last_chu_shang_time:
                c_min = last_chu_shang_time + chu_shang_interval_min / 1000
                c_max = last_chu_shang_time + chu_shang_interval_max / 1000

                k_min = kou_xue_time + chu_kou_interval_min / 1000
                k_max = kou_xue_time + chu_kou_interval_max / 1000

                chu_shang_time = last_chu_shang_time + \
                    randtime(chu_shang_interval_min, chu_shang_interval_max)
                if k_min > c_max or k_max < c_min:
                    # 没有交集，以出伤间隔为准
                    logging.debug("以出伤间隔为准 kou_xue_time: %s, last_chu_shang_time: %s, c_min: %s, c_max:%s, k_min:%s, k_max:%s",
                                kou_xue_time, last_chu_shang_time, c_min, c_max, k_min, k_max)
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
                chu_shang_action = chu_shang_cls(name + "出伤")
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
        print(f"{start_time:.3f} to {end_time:.3f}: k_num = {k_num} c_num = {c_num}")

    return (k_action_lst, c_action_lst)


def calc_score(fufu_initial_state: Character_FuFu, 
               aciton_plan_creator_func: Callable[[Character_FuFu], ActionPlan]):
    all_damage = 0
    full_six_zhan_bi = 0
    run_num = MAX_RUN_NUM

    for _ in range(0, run_num):
        plan = aciton_plan_creator_func(fufu_initial_state)
        plan.run()
        if enable_record:
            expect_score = calc_expect_damage(plan.total_damage, fufu_initial_state.get_crit_rate(), 1 + fufu_initial_state.get_crit_damage())
            crit_score = round(plan.total_damage * (1 + fufu_initial_state.get_crit_damage()))
            logging.debug("damage: %d, expect_score:%s, crit_score:%s",
                          round(plan.total_damage), round(expect_score), round(crit_score))
        all_damage += plan.total_damage
        full_six_zhan_bi += plan.full_six_damage / plan.total_damage

    all_damage /= run_num
    full_six_zhan_bi /= run_num

    return (all_damage, round(full_six_zhan_bi, 3))


def scan_syw_combine(combine: list[ShengYiWu], 
                     fufu_creator_func: Callable[[], Character_FuFu]) -> Character_FuFu:
    fufu = fufu_creator_func()
    fufu.add_crit_rate(0.242 - 0.05)  # 突破加成
    fufu.get_hp().modify_max_hp(4780)  # 花

    for p in combine:
        fufu.add_crit_rate(p.crit_rate)
        fufu.add_crit_damage(p.crit_damage)
        fufu.get_hp().modify_max_hp(p.hp)
        fufu.get_hp().modify_max_hp_per(p.hp_percent)
        fufu.add_all_bonus(p.elem_bonus)
        fufu.add_energy_recharge(p.energy_recharge)

    crit_rate = round(fufu.get_crit_rate(), 3)
    if crit_rate < 0.70:
        return None

    energy_recharge = fufu.get_energy_recharge()
    if energy_recharge < fufu.required_energy_recharge:
        return None

    syw_names = [p.name for p in combine]
    # print(syw_names)
    name_count = {i: syw_names.count(i) for i in syw_names}
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
                # FIXME: 暂时不考虑芙芙在前台会吃不到 0.25 增伤的问题，后续需要补充
                fufu.add_e_bonus(0.25 + 0.25)

    return fufu

def qualify_syw(score_data: ShengYiWu_Score, fufu_creator_func, qualify_func):
    fufu = scan_syw_combine(score_data.syw_combine, fufu_creator_func)
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

    score_data.damage_to_score(
        damage, fufu.get_crit_rate(), 1 + fufu.get_crit_damage())
    score_data.custom_data = fufu

    # logging.debug("damage:%s, expect_score:%s, crit_score:%s",
    #              damage, score_data.expect_score, score_data.crit_score)

    return True


def calculate_score_common(score_data: ShengYiWu_Score, 
                    fufu_creator_func: Callable[[], Character_FuFu], 
                    aciton_plan_creator_func: Callable[[Character_FuFu], ActionPlan]):
    if score_data.custom_data:
        fufu = score_data.custom_data
    else:
        fufu = scan_syw_combine(score_data.syw_combine, fufu_creator_func)

    if not fufu:
        return False

    # logging.debug(str(fufu))
    damage, full_six_zhan_bi = calc_score(fufu, aciton_plan_creator_func)
    if not damage:
        return False

    score_data.damage_to_score(
        damage, fufu.get_crit_rate(), 1 + fufu.get_crit_damage())

    if enable_record:
        logging.debug("finished: damage: %d, full_six_zhan_bi: %s, expect_score:%s, crit_score:%s, crit_rate: %s, crit_damage: %s",
                        round(damage), round(full_six_zhan_bi, 3),
                        round(score_data.expect_score), round(score_data.crit_score),
                        round(fufu.get_crit_rate(), 3), round(fufu.get_crit_damage(), 3))
    
    panel_hp = fufu.get_hp().get_max_hp()
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
    return syw.hp_percent == ShengYiWu.BONUS_MAX or syw.elem_type == ShengYiWu.ELEM_TYPE_SHUI


def match_tou_callback(syw: ShengYiWu):
    return syw.crit_rate == ShengYiWu.CRIT_RATE_MAIN or syw.crit_damage == ShengYiWu.CRIT_DAMAGE_MAIN or syw.hp_percent == ShengYiWu.BONUS_MAX


def find_syw_for_fu_ning_na(calculate_score_callback, 
                            result_txt_file,
                            calculate_score_qualifier=None):
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
    
    return calculate_score(raw_score_list,
                           calculate_score_callbak=calculate_score_callback,
                           result_txt_file=result_txt_file,
                           result_description=result_description,
                           calculate_score_qualifier=calculate_score_qualifier
                           )


# Main body
if __name__ == '__main__':
    logging.basicConfig(filename='D:\\logs\\fufu.log', encoding='utf-8', filemode='w', level=logging.DEBUG)
    logging.basicConfig(level=logging.DEBUG)
    print("默认算法复杂，圣遗物多的话需要执行0.5~1小时多")
    find_syw_for_fu_ning_na()
