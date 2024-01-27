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

from base_syw import ShengYiWu, ShengYiWu_Score, calculate_score, Syw_Combine_Desc, find_syw_combine
from health_point import HealthPoint
from character import Character
from monster import Monster
from ye_lan import YeLanQBonus
from action import Action, ActionPlan


# 命座
ming_zuo_num = 6
# 是否有专武
has_zhuan_wu = True

include_extra = False    # 某些配队，在芙芙大招结束后还继续输出，不切芙芙出来续大，此时将include_extra置为True

enable_debug = False
MAX_RUN_NUM = 10

# 队友生命值上限设置，影响到叠层速度


class Teammate:
    def __init__(self, base_hp, max_hp, elem_type=None):
        self.hp = HealthPoint(base_hp, max_hp)
        self.elem_type = elem_type


FU_FU_NAME = "furina"
YE_LAN_NAME = "ye lan"
ZHONG_LI_NAME = "zhong li"
WAN_YE_NAME = "wan ye"

# 夜芙万钟：目前的满命芙宁娜算法采用的是这个配队，
# 使用这个配队计算的伤害，也可以作为以下满命手法模式的通解：
# 
#   芙芙qeaa，其他角色放技能等叠满层，切芙芙重击转白芙, 白芙a两刀再重击转黑芙，切其他角色输出
#
# 钟离和万叶是这个手法模式下最好的辅助，钟离能避免芙芙砍的时候被击飞，万叶就不用说了
# 夜兰是这个手法模式下最好的副C
#
# 不修改算法的情况下，只允许改变各个角色的生命值上限
ye_fu_wan_zhong_team = {
    # 夜兰
    YE_LAN_NAME: Teammate(14450, 46461, elem_type=ShengYiWu.ELEM_TYPE_SHUI),
    # 钟离
    ZHONG_LI_NAME: Teammate(14695, 50567),
    # 万叶
    WAN_YE_NAME: Teammate(13348, 23505),
}

# 非满命算法针对以下手法模式：
#
#   芙芙eq，副 C 放技能，切奶妈奶全队，切主C站场输出直到芙芙大招结束，开启下一轮循环
#
# 下面是芙芙和沙龙成员的行动序列，奶妈不同介入时间的气氛值叠层情况
#
#  芙芙eq:  q期间三小只扣血，但芙芙大招期间不扣血，因此扣血情况是： 其他人扣7.6%
#  夫人扣血：基本是紧接在芙芙q动画结束的，二命以上：1.6 * 4 * 3.5 + 150 = 172.4, 一命：1.6 * 4 + 150 = 156.4
#  夫人扣血：二命：172.4 + 1.6 * 4 * 3.5 = 194.8，一命: 1.6 * 4 + 156.4 = 162.8
#  勋爵扣血：二命：194.8 + 2.4 * 4 * 3.5 = 228.4,一命：2.4 * 4 + 162.8 = 172.4
#          二命的话，此时就可以奶全队，228.4 + 7.6 * 3 * 3.5 + (1.6 + 1.6 + 2.4) * 4 * 3.5 = 386.6
#          虽然没满层，但也不差多少了，但如果芙芙的练度高，建议把全队奶再推后一些，多叠一些芙芙二命的生命值加成
#  夫人扣血：我们假设此前副C在放q，则之前夫人和勋爵扣不了放q的角色的血，则一命: 172.4 - (1.6 + 2.4) + 1.6 * 4 = 174.8
#  螃蟹扣血: 一命: 174.8 + 3.6 * 4 = 189.2
#  夫人扣血：一命：189.2 + 1.6 * 4 = 195.6
#          如果此时奶全队，则 195.6 + 7.6 * 3 + 1.6 * 4 + (1.6 + 2.4) * 3 + (1.6 + 3.6 + 1.6) * 4 = 264层
#
# 根据以上分析，对于二命芙芙，几个配队的第一轮打法如下：
#   注：奶妈e后都a了一下，是为了拖时间，确保放q的时候勋爵会扣血
#
#    影夜芙琴: 雷神e，芙芙eq，夜兰eq(e), 琴eaq，雷神qazazazazaz
#         或：雷神e，芙芙eq, 琴eaq, 夜兰eqe，琴e，雷神qazazazazaz，
#             缺点：雷神没砍完，芙芙大招就可能消失了，不切琴补减抗，风套效果会提前消失，适用于夜兰输出比雷神高的旅行者
#                  芙芙练度高也不推荐，奶妈越往后就越能多叠一些芙芙二命的生命值加成
#       注：也可以芙芙e，雷神e，琴e, 芙芙q，这样更有利于叠满层，但频繁切人有点繁琐
#
#    非风系奶妈+二命芙芙+风系辅助的配队：芙芙e，风系减抗，芙芙q, 奶妈eaq，风系减抗，主C输出
#
# 对于二命以下的芙芙，打法是一样的，只不过第一轮输出会低些，但第一轮扣了很多血后，进第二轮瞬间奶满就和二命体验差不多了

MAIN_CARRY = "主C"
SECONDARY_CARRY = "副C"
HEALER = "奶妈"

non_full_ming_zuo_team = {
    # 影宝
    MAIN_CARRY: Teammate(12907, 21650),
    # 夜兰
    SECONDARY_CARRY: Teammate(14450, 46461, elem_type=ShengYiWu.ELEM_TYPE_SHUI),
    # 琴
    HEALER: Teammate(12965, 24224)
}

# 将这个值设置你想要使用的配队
if ming_zuo_num >= 6:
    g_teammates = ye_fu_wan_zhong_team
else:
    g_teammates = non_full_ming_zuo_team

# 是否有四命夜兰，仅用于最终生命值上限的展示，不影响最终伤害的计算
if ming_zuo_num >= 6:
    has_4_ming_ye_lan = True
else:
    has_4_ming_ye_lan = False

# 算法自动根据配队检索，不需要手动改
has_shuang_shui = False
for t in g_teammates.values():
    if t.elem_type == ShengYiWu.ELEM_TYPE_SHUI:
        has_shuang_shui = True
        break

# 充能要求设置，如果队友有西福斯的月光或西风系列武器，或者队友有雷神等充能的话，可以适当下调
if ming_zuo_num >= 4:
    if has_shuang_shui:
        required_energy_recharge = 110
    else:
        required_energy_recharge = 160
else:
    if has_shuang_shui:
        required_energy_recharge = 170
    else:
        required_energy_recharge = 220

# 以下是队友或武器带来的一些额外属性（专武不需要手动填）
# 四命夜兰的生命值加成是在具体的流程中动态计算的，不能写死

# 武器或队友增加的暴伤
extra_crit_damage = {
}

# 武器或队友增加的生命值加成，双水不需要手动填，会自动根据上面的teammate进行计算
extra_hp_bonus = {
}

# 武器或队友带来的通用元素伤害加成
extra_common_elem_bonus = {
    # "万叶": "0.4"
}

# 武器或队友带来的战技增伤
extra_e_bonus = {
}

# 武器或队友带来的元素爆发增伤
extra_q_bonus = {
}

# 以下为自动计算区，无须手动更改

if has_shuang_shui:
    extra_hp_bonus["双水"] = 0.25

if ming_zuo_num >= 1:
    BASE_QI_FEN_ZHI = 150
    MAX_QI_FEN_ZHI = 400
else:
    BASE_QI_FEN_ZHI = 0
    MAX_QI_FEN_ZHI = 300

MAX_TOTAL_QI_FEN_ZHI = MAX_QI_FEN_ZHI

if ming_zuo_num >= 2:
    QI_INCREASE_BEI_LV = 3.5
    QI_HP_BEI_LV = 0.0035
    MING_2_HP_BONUS_MAX = 1.4
    MAX_TOTAL_QI_FEN_ZHI = 800
else:
    QI_INCREASE_BEI_LV = 1
    QI_HP_BEI_LV = 0
    MING_2_HP_BONUS_MAX = 0

if ming_zuo_num >= 3:
    Q_BEI_LV = 24.2
    QI_TO_BONUS_BEI_LV = 0.0031
    QI_TO_CURE_BEI_LV = 0.0013
else:
    Q_BEI_LV = 20.5
    QI_TO_BONUS_BEI_LV = 0.0025
    QI_TO_CURE_BEI_LV = 0.001

if ming_zuo_num >= 5:
    E_BEI_LV = 16.7
    GE_ZHE_CURE_BEI_LV = 10.2
    GE_ZHE_CURE_BASE = 1271

    FU_REN_BEI_LV = 6.87
    XUN_JUE_BEI_LV = 12.67
    PANG_XIE_BEI_LV = 17.61
else:
    E_BEI_LV = 14.2
    GE_ZHE_CURE_BEI_LV = 8.64
    GE_ZHE_CURE_BASE = 1017

    FU_REN_BEI_LV = 5.82
    XUN_JUE_BEI_LV = 10.73
    PANG_XIE_BEI_LV = 14.92

E_EXTRA_DAMAGE_BONUS = 1.4  # 队友大于50%血量，e技能伤害为原来的1.4倍
HEI_FU_BEI_LV = 18
BAI_FU_BEI_LV = 18 + 25

FU_NING_NA_BASE_HP = 15307

ZHUAN_WU_HP_BEI_LV = 0.14
ZHUAN_WU_E_BONUS_BEI_LV = 0.08

if has_zhuan_wu:
    extra_crit_damage["专武"] = 0.882


def gu_you_tian_fu_2_bonus(hp):
    return min(hp / 1000 * 0.007, 0.28)


def randtime(t_min, t_max):
    return random.randint(t_min, t_max) / 1000


class FuFuActionPlan(ActionPlan):
    def __init__(self, fufu_initial_state: Character):
        super().__init__()

        self.__fufu: Character = copy.deepcopy(fufu_initial_state)
        self.__teammates: list[Character] = []
        for name, t in g_teammates.items():
            c = Character(name)
            c.set_hp(copy.deepcopy(t.hp))
            self.__teammates.append(c)

        self.__forground_character: Character = None

        self.monster = Monster()

        self.__zhuan_wu_hp_last_change_time = None
        self.__zhuan_wu_hp_level = 0
        self.__zhuan_wu_e_bonus_last_change_time = None
        self.__zhuan_wu_e_bonus_level = 0

        self.__qi_fen_zhi = 0
        self.effective_qi_fen_zhi = 0
        self.__fufu_q_stopped = True

        self.prev_qi_elem_bonus = 0
        self.prev_qi_healing_bonus = 0
        self.prev_qi_hp_per_bonus = 0

        self.hei_fu_end_cure_teammate_time = 0
        self.hei_fu_end_cure_fufu_time = 0

        self.hei_fu_cure_teammate_action: Action = None
        self.hei_fu_cure_fufu_action: Action = None

        self.apply_qi_fen_zhi_action: Action = None

        self.ye_lan_q_bonus = YeLanQBonus()

        self.total_damage = 0
        self.full_six_damage = 0

        # 用于预筛选代码录制
        self.ye_lan_e_num = 0
        self.prev_hp_str = None

    def get_fufu(self) -> Character:
        return self.__fufu

    def get_foreground_character(self) -> Character:
        return self.__forground_character

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

    def get_teammates(self) -> list[Character]:
        return self.__teammates

    def get_teammate(self, name) -> Character:
        for t in self.__teammates:
            if t.name == name:
                return t

    ##################################################

    def __damage_record_hp(self):
        # for damage record
        s = "cur_hp = hp"
        p = []
        if self.__zhuan_wu_hp_level:
            p.append("0.14 * " + str(self.__zhuan_wu_hp_level))

        if self.ye_lan_e_num:
            p.append("0.1 * " + str(self.ye_lan_e_num))

        if self.effective_qi_fen_zhi > MAX_QI_FEN_ZHI and ming_zuo_num >= 2:
            p.append(
                "(" + str(min(800, round(self.__qi_fen_zhi, 3))) + " - 400) * 0.0035")

        if p:
            s += " + ("
            s += " + ".join(p)
            s += ") * FU_NING_NA_BASE_HP"

        if s != self.prev_hp_str:
            logging.debug(s)
            self.prev_hp_str = s

    def damage_record_hp(self):
        pass
        # self.__damage_record_hp()

    def switch_to_forground(self, character_name):
        if self.__forground_character:
            if self.__forground_character.name == character_name:
                return

        prev_fore = self.__forground_character
        if character_name == self.__fufu.name:
            self.__fufu.switch_to_foreground()
            self.__forground_character = self.__fufu
        else:
            for t in self.__teammates:
                if t.name == character_name:
                    t.switch_to_foreground()
                    self.__forground_character = t
                    break

        if prev_fore:
            prev_fore.switch_to_background()

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
        self.__fufu_q_stopped = False
        self.set_qi_fen_zhi(BASE_QI_FEN_ZHI)

    def fufu_q_stop(self):
        self.set_qi_fen_zhi(0)
        self.__fufu_q_stopped = True

    def add_qi_fen_zhi(self, qi):
        if self.__fufu_q_stopped or qi == 0:
            return

        if self.__qi_fen_zhi >= MAX_TOTAL_QI_FEN_ZHI:
            return

        self.__qi_fen_zhi += qi
        if self.__qi_fen_zhi > MAX_TOTAL_QI_FEN_ZHI:
            self.__qi_fen_zhi = MAX_TOTAL_QI_FEN_ZHI
        self.debug("气氛值增加%s, 增加到:%s", round(
            qi, 3), round(self.__qi_fen_zhi, 3))

        if self.apply_qi_fen_zhi_action and self.apply_qi_fen_zhi_action.blocking:
            self.apply_qi_fen_zhi_action.do(self)

    def set_qi_fen_zhi(self, qi):
        if self.__fufu_q_stopped or qi == self.__qi_fen_zhi:
            return

        self.__qi_fen_zhi = qi
        self.debug("气氛值直接设置为%s", qi)
        self.apply_qi_fen_zhi()

    def apply_qi_fen_zhi(self):
        if self.__qi_fen_zhi == self.effective_qi_fen_zhi:
            return False

        self.debug("气氛值调整开始：生效层数%s", round(self.__qi_fen_zhi, 3))

        t = self.__do_apply_qi_fen_zhi()

        self.effective_qi_fen_zhi = self.__qi_fen_zhi
        self.prev_qi_elem_bonus = t[0]
        self.prev_qi_healing_bonus = t[1]
        self.prev_qi_hp_per_bonus = t[2]

        self.damage_record_hp()

        return True

    def __do_apply_qi_fen_zhi(self):
        fufu = self.get_fufu()

        if self.__qi_fen_zhi > MAX_QI_FEN_ZHI:
            bonus_qi_fen_zhi = MAX_QI_FEN_ZHI
            hp_qi_fen_zhi = self.__qi_fen_zhi - MAX_QI_FEN_ZHI
        else:
            bonus_qi_fen_zhi = self.__qi_fen_zhi
            hp_qi_fen_zhi = 0

        elem_bonus = bonus_qi_fen_zhi * QI_TO_BONUS_BEI_LV
        healing_bonus = bonus_qi_fen_zhi * QI_TO_CURE_BEI_LV
        hp_per_bonus = hp_qi_fen_zhi * QI_HP_BEI_LV

        fufu.modify_all_elem_bonus(elem_bonus - self.prev_qi_elem_bonus)
        fufu.modify_incoming_healing_bonus(healing_bonus - self.prev_qi_healing_bonus)
        for t in self.__teammates:
            t.modify_incoming_healing_bonus(healing_bonus - self.prev_qi_healing_bonus)
        fufu.get_hp().modify_max_hp_per(hp_per_bonus - self.prev_qi_hp_per_bonus)
        self.debug("气氛值调整完成，生命值上限：%d， a_bonus: %s, e_bonus: %s, q_bonus: %s, healing_bonus:%s",
                   round(self.get_max_hp()),
                   round(fufu.get_a_bonus(), 3), round(fufu.get_e_bonus(), 3),
                   round(fufu.get_q_bonus(), 3), round(fufu.get_incoming_healing_bonus(), 3))

        return (elem_bonus, healing_bonus, hp_per_bonus)

    def increase_zhuan_wu_hp_level(self, cur_time):
        if not has_zhuan_wu:
            return

        if self.__zhuan_wu_hp_level >= 2:
            return

        if self.__zhuan_wu_hp_last_change_time and (cur_time - self.__zhuan_wu_hp_last_change_time < 0.2):
            # 有0.2秒的CD
            return

        self.__zhuan_wu_hp_last_change_time = cur_time
        self.__fufu.get_hp().modify_max_hp_per(ZHUAN_WU_HP_BEI_LV)
        self.__zhuan_wu_hp_level += 1
        self.debug("专武生命叠一层，目前层数: %d",  self.__zhuan_wu_hp_level)
        self.damage_record_hp()

    def increase_zhuan_wu_e_bonus_level(self, cur_time):
        if not has_zhuan_wu:
            return

        if self.__zhuan_wu_e_bonus_level >= 3:
            return

        if self.__zhuan_wu_e_bonus_last_change_time and (cur_time - self.__zhuan_wu_e_bonus_last_change_time < 0.2):
            return

        self.__zhuan_wu_e_bonus_last_change_time = cur_time
        self.__fufu.add_e_bonus(ZHUAN_WU_E_BONUS_BEI_LV)
        self.__zhuan_wu_e_bonus_level += 1
        self.debug("专武战技叠一层，目前层数: %d", self.__zhuan_wu_e_bonus_level)

    def do_trigger_gu_you_tian_fu_1(self):
        self.debug("触发芙芙固有天赋1")

    def change_cur_hp(self, cur_time, characters: list[Character] = [], hp=0, hp_per=0, healing_bonus=0, heal_by_fufu=True):
        changed_characters = []
        qi_fen_zhi = 0
        prev_qi_fen_zhi = 0
        fufu_hp_changed = False
        teammate_hp_changed = False

        over_heal_num = 0

        for c in characters:
            if hp > 0:
                _, hp_per_changed, over_heal_num = c.regenerate_hp(hp, healing_bonus)
                qi_fen_zhi += abs(hp_per_changed) * QI_INCREASE_BEI_LV * 100
            elif hp < 0:
                _, hp_per_changed, _ = c.get_hp().modify_cur_hp(hp)
                qi_fen_zhi += abs(hp_per_changed) * QI_INCREASE_BEI_LV * 100

            if hp_per > 0:
                _, hp_per_changed, over_heal_num = c.regenerate_hp_per(hp_per, healing_bonus)
                qi_fen_zhi += abs(hp_per_changed) * QI_INCREASE_BEI_LV * 100
            elif hp_per < 0:
                _, hp_per_changed, _ = c.get_hp().modify_cur_hp_per(hp_per)
                qi_fen_zhi += abs(hp_per_changed) * QI_INCREASE_BEI_LV * 100

            if qi_fen_zhi != prev_qi_fen_zhi:
                # hp changed
                if c is self.__fufu:
                    fufu_hp_changed = True
                else:
                    teammate_hp_changed = True

                changed_characters.append(c)

            prev_qi_fen_zhi = qi_fen_zhi

        if over_heal_num > 0 and not heal_by_fufu:
            self.do_trigger_gu_you_tian_fu_1()

        if qi_fen_zhi:
            self.debug("当前生命值变化，影响的角色: %s", ",".join(
                [c.name for c in changed_characters]))

            if cur_time < self.get_current_action_time():
                cur_time = self.get_current_action_time()

            action_time = cur_time + self.get_effective_delay()

            if fufu_hp_changed:
                # self.increase_zhuan_wu_e_bonus_level(cur_time)
                action = Increase_ZhuanWu_E_Bonus_Level_Action()
                action.set_timestamp(action_time)
                self.insert_action_runtime(action)

            if teammate_hp_changed:
                action = Increase_ZhuanWu_Hp_Level_Action()
                action.set_timestamp(action_time)
                self.insert_action_runtime(action)

                # self.increase_zhuan_wu_hp_level(cur_time)

        self.add_qi_fen_zhi(qi_fen_zhi)

        return changed_characters

    def consume_hp(self, hp_per):
        characters = [self.__fufu] + self.__teammates
        changed_characters = self.change_cur_hp(
            self.get_current_action_time(), characters=characters, hp_per=(0 - hp_per))

        # changed_characters_str = ""
        for c in changed_characters:
            # changed_characters_str += c.name + ", "
            if c is self.__fufu and self.hei_fu_cure_fufu_action and self.hei_fu_cure_fufu_action.blocking:
                self.hei_fu_cure_fufu_action.do(self)
        # self.debug("被扣血的角色 %s", changed_characters_str)


class Increase_ZhuanWu_Hp_Level_Action(Action):
    def __init__(self):
        super().__init__("专武生命值叠层")

    def do_impl(self, plan: FuFuActionPlan):
        plan.increase_zhuan_wu_hp_level(self.get_timestamp())


class Increase_ZhuanWu_E_Bonus_Level_Action(Action):
    def __init__(self):
        super().__init__("专武战技增伤叠层")

    def do_impl(self, plan: FuFuActionPlan):
        plan.increase_zhuan_wu_e_bonus_level(self.get_timestamp())


class Apply_Qi_Fen_Zhi_Action(Action):
    def __init__(self):
        super().__init__("气氛值生效线程")
        self.blocking = False

    def do_impl(self, plan: FuFuActionPlan):
        if not self.blocking:
            changed = plan.apply_qi_fen_zhi()
            if not changed:
                self.blocking = True
                self.debug("气氛值调整线程：气氛值没变化，转入阻塞")
                return

        action = Apply_Qi_Fen_Zhi_Action()
        # 为了能处理三小只一开始的时候同时扣血的情形，我们需要在blocking唤醒后，
        # 用同样的时间在后面插入一个action，因为 list.sort() 的稳定性，这个action会在三小只的后面
        if self.blocking:
            self.debug("气氛值调程线程从阻塞唤醒")
            action.set_timestamp(plan.get_current_action_time())
        else:
            next_time = self.get_timestamp() + random.randint(429, 587) / 1000
            action.set_timestamp(next_time)
        plan.insert_action_runtime(action)

        plan.apply_qi_fen_zhi_action = action


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
        fufu.add_energy_recharge(self.wan_ye.energy_recharge)

        plan.monster.add_jian_kang(0.4)


class WanYeBonusStopAction(Action):
    def __init__(self, name, wan_ye: WanYe):
        super().__init__(name)
        self.wan_ye = wan_ye

    def do_impl(self, plan: FuFuActionPlan):
        self.debug("万叶增伤消失")
        plan.get_fufu().sub_all_bonus(self.wan_ye.elem_bonus)


class FengTaoInvalidAction(Action):
    def do_impl(self, plan: FuFuActionPlan):
        self.debug("风套减抗消失")
        plan.monster.sub_jian_kang(0.4)


class FuFu_Q_Animation_Start(Action):
    def do_impl(self, plan: FuFuActionPlan):
        self.debug("芙芙大招动画开始")
        plan.get_fufu().get_hp().set_in_q_animation(True)

class FuFu_Q_Animation_Stop(Action):
    def do_impl(self, plan: FuFuActionPlan):
        self.debug("芙芙大招动画结束")
        plan.get_fufu().get_hp().set_in_q_animation(False)

class FuFu_Q_Action(Action):
    def do_impl(self, plan: FuFuActionPlan):
        plan.switch_to_forground(plan.get_fufu().name)
        self.start_qi_fen_zhi_thread(plan)
        self.do_damage(plan)

    def start_qi_fen_zhi_thread(self, plan: FuFuActionPlan):
        plan.fufu_q_start()
        plan.apply_qi_fen_zhi_action = Apply_Qi_Fen_Zhi_Action()
        plan.apply_qi_fen_zhi_action.blocking = True

    def do_damage(self, plan: FuFuActionPlan):
        monster = plan.monster

        hp = plan.get_max_hp()
        q_bonus = 1 + plan.get_q_bonus()

        q_damage = hp * Q_BEI_LV / 100 * q_bonus
        q_damage = monster.attacked(q_damage)

        plan.total_damage += q_damage
        self.debug("芙芙q出伤, %d, hp: %s, q_bonus:%s, monster:%s",
                   round(q_damage), hp, round(q_bonus, 3), monster)
        self.damage_record_hp(bei_lv_str="Q_BEI_LV / 100",
                              bonus=q_bonus, monster=monster)


class FuFu_E_Action(Action):
    def do_impl(self, plan: FuFuActionPlan):
        plan.switch_to_forground(plan.get_fufu().name)
        monster = plan.monster

        hp = plan.get_max_hp()
        e_bonus = 1 + plan.get_e_bonus()

        e_damage = hp * E_BEI_LV / 100 * e_bonus
        damage = monster.attacked(e_damage)

        plan.total_damage += damage
        self.debug("芙芙e出伤, %d, hp: %s, bonus: %s, monster:%s",
                   round(damage), hp, round(e_bonus, 3), monster)
        self.damage_record_hp(bei_lv_str="E_BEI_LV / 100",
                              bonus=e_bonus, monster=monster)


class Hei_Fu_Cure_Action(Action):
    def __init__(self, name):
        super().__init__(name)
        self.actual_cure_time = 0
        self.end_cure_time = 0

    def get_cure_num(self, fufu: Character):
        return round(fufu.get_hp().get_max_hp() * 0.04)


class Hei_Fu_Cure_Teammate_Action(Hei_Fu_Cure_Action):
    def __init__(self):
        super().__init__("治疗后台三人")

    def do_impl(self, plan: FuFuActionPlan):
        cure_num = self.get_cure_num(plan.get_fufu())
        self.debug("治疗后台三人, %s", cure_num)
        plan.change_cur_hp(cur_time=self.get_timestamp(),
                           characters=plan.get_teammates(), hp=cure_num)

        self.re_schedule(plan)

    def re_schedule(self, plan: FuFuActionPlan):
        next_time = self.actual_cure_time + plan.get_hei_fu_cure_interval()
        if next_time <= self.end_cure_time:
            action = Hei_Fu_Cure_Teammate_Action()
            action.actual_cure_time = next_time
            action.end_cure_time = self.end_cure_time
            action.set_timestamp(next_time + plan.get_effective_delay())
            plan.insert_action_runtime(action)

            plan.hei_fu_cure_teammate_action = action
        else:
            self.debug("治疗后台三人到时间，终止")
            plan.hei_fu_cure_teammate_action = None


class Hei_Fu_Cure_FuFu_Action(Hei_Fu_Cure_Action):
    def __init__(self, sync_with_cure_teammate=False):
        super().__init__("治疗芙芙")
        self.sync_with_cure_teammate = sync_with_cure_teammate
        self.blocking = False

    def do_impl(self, plan: FuFuActionPlan):
        # 有可能是从 blocking状态唤醒，需要检查时间
        if plan.get_current_action_time() <= self.end_cure_time:
            fufu = plan.get_fufu()

            if fufu.get_hp().is_full():
                self.debug("治疗芙芙时，芙芙满血，阻塞并转入独立模式")
                # 芙芙是满血的，不用治疗，转入阻塞独立模式
                self.blocking = True
                # 自此之后，不再和治疗队友保持同步
                self.sync_with_cure_teammate = False
            else:
                cure_num = self.get_cure_num(fufu)
                self.debug("治疗芙芙，%s", cure_num)
                plan.change_cur_hp(self.get_timestamp(),
                                   characters=[fufu], hp=cure_num)

                self.re_schedule(plan)
        else:
            self.debug("治疗芙芙，从blocking唤醒后发现超时，终止")
            plan.hei_fu_cure_fufu_action = None

    def re_schedule(self, plan: FuFuActionPlan):
        if self.sync_with_cure_teammate:
            if not plan.hei_fu_cure_teammate_action:
                self.debug("治疗芙芙重新调度时，同步模式下治疗队友已终止")
                plan.hei_fu_cure_fufu_action = None
                return
            else:
                next_time = plan.hei_fu_cure_teammate_action.actual_cure_time + \
                    plan.get_hei_fu_cure_fufu_delay()
        else:
            if self.blocking:
                next_time = plan.get_current_action_time() + plan.get_hei_fu_cure_interval()
            else:
                next_time = self.actual_cure_time + plan.get_hei_fu_cure_interval()

        if next_time <= self.end_cure_time:
            # self.debug("治疗重新调度，模式%s", self.sync_with_cure_teammate)
            action = Hei_Fu_Cure_FuFu_Action(
                sync_with_cure_teammate=self.sync_with_cure_teammate)
            action.actual_cure_time = next_time
            action.end_cure_time = self.end_cure_time
            action.set_timestamp(next_time + plan.get_effective_delay())
            plan.insert_action_runtime(action)
            plan.hei_fu_cure_fufu_action = action
        else:
            self.debug("治疗芙芙到时间，终止")
            plan.hei_fu_cure_fufu_action = None

# 芒、荒的伤害刀似乎都是按黑芙计算的
# 注意：芒荒刀出伤的时候，芙芙不一定在前台


class Mang_Huang_Damage_Action(Action):
    def do_impl(self, plan: FuFuActionPlan):
        monster = plan.monster

        hp = plan.get_max_hp()
        a_bonus = 1 + plan.get_a_bonus()

        damage = hp * HEI_FU_BEI_LV / 100 * a_bonus
        damage = monster.attacked(damage)

        plan.total_damage += damage
        plan.full_six_damage += damage
        self.debug("芒/荒刀出伤，%d, hp: %s, bonus: %s, monster:%s",
                   round(damage), hp, round(a_bonus, 3), monster)
        self.damage_record_hp(bei_lv_str="HEI_FU_BEI_LV / 100",
                              bonus=a_bonus, monster=monster)


class Hei_Fu_Damage_Action(Action):
    def do_impl(self, plan: FuFuActionPlan):
        plan.switch_to_forground(plan.get_fufu().name)
        self.do_damage(plan)
        self.do_cure(plan)

    def do_damage(self, plan: FuFuActionPlan):
        monster = plan.monster

        hp = plan.get_max_hp()
        a_bonus = 1 + plan.get_a_bonus()
        damage = hp * HEI_FU_BEI_LV / 100 * a_bonus
        damage = monster.attacked(damage)

        plan.total_damage += damage
        plan.full_six_damage += damage
        self.debug("%s出伤, %d, hp: %s, bonus:%s, monster:%s",
                   self.name, round(damage), hp, round(a_bonus, 3), monster)
        self.damage_record_hp(bei_lv_str="HEI_FU_BEI_LV / 100",
                              bonus=a_bonus, monster=monster)

    def do_cure(self, plan: FuFuActionPlan):
        # 治疗队友
        cure_teammate_restarted = False
        if plan.hei_fu_cure_teammate_action:
            # 有一个cure action在队列后面，延长治疗时间即可
            self.debug("延长奶刀治疗队友时间")
            plan.hei_fu_cure_teammate_action.end_cure_time += 2.9
        else:
            self.debug("启动奶刀治疗队友")
            cure_teammate_restarted = True
            plan.hei_fu_cure_teammate_action = self.start_new_cure(
                plan, Hei_Fu_Cure_Teammate_Action)

        # 治疗芙芙自身：因为治疗会blocking，逻辑更复杂
        if plan.hei_fu_cure_fufu_action:
            # 已经有一个action在队列上，要检查其状态
            if plan.hei_fu_cure_fufu_action.blocking:
                if self.get_timestamp() < plan.hei_fu_cure_fufu_action.end_cure_time:
                    # 阻塞着，在有效时间之内又砍了一刀奶刀，则延长结束时间
                    self.debug("奶刀治疗芙芙阻塞中，延长持续时间")
                    plan.hei_fu_cure_fufu_action.end_cure_time += 2.9
                else:
                    # 阻塞着，但已经超时了，重新启动
                    self.debug("上次奶刀治疗芙芙阻塞超时，重启")
                    plan.hei_fu_cure_fufu_action = None
            else:
                # 不在blocking，那么肯定在队列后面了
                plan.hei_fu_cure_fufu_action.end_cure_time += 2.9

        if not plan.hei_fu_cure_fufu_action:
            # 没有action，或者因为超时被重置了，需要重启
            if cure_teammate_restarted:
                self.debug("启动奶刀治疗芙芙，同步模式")
                action = Hei_Fu_Cure_FuFu_Action(sync_with_cure_teammate=True)
                action.end_cure_time = plan.hei_fu_cure_teammate_action.end_cure_time
                action.actual_cure_time = plan.hei_fu_cure_teammate_action.actual_cure_time + \
                    plan.get_hei_fu_cure_fufu_delay()
                action.set_timestamp(
                    action.actual_cure_time + plan.get_effective_delay())
                plan.insert_action_runtime(action)
            else:
                self.debug("启动奶刀治疗芙芙，独立模式")
                action = self.start_new_cure(plan, Hei_Fu_Cure_FuFu_Action)

            plan.hei_fu_cure_fufu_action = action

    def start_new_cure(self, plan: FuFuActionPlan, cls):
        actual_cure_time = self.get_timestamp() + plan.get_hei_fu_first_cure_delay()
        end_cure_time = actual_cure_time + \
            (2.9 - 1) + plan.get_hei_fu_cure_extension()
        action = cls()
        action.actual_cure_time = actual_cure_time
        action.end_cure_time = end_cure_time
        action.set_timestamp(actual_cure_time + plan.get_effective_delay())

        plan.insert_action_runtime(action)

        return action


class Bai_Dao_Kou_Xue_Action(Action):
    def do_impl(self, plan: FuFuActionPlan):
        # 白刀扣血 1%
        self.debug("%s", self.name)
        plan.consume_hp(0.01)


class Bai_Fu_Damage_Action(Action):
    def do_impl(self, plan: FuFuActionPlan):
        plan.switch_to_forground(plan.get_fufu().name)
        monster = plan.monster

        hp = plan.get_max_hp()
        bonus = 1 + plan.get_a_bonus()
        damage = hp * BAI_FU_BEI_LV / 100 * bonus
        damage = monster.attacked(damage)

        plan.total_damage += damage
        plan.full_six_damage += damage
        self.debug("%s出伤，%d, hp: %s, bonus:%s, monster:%s",
                   self.name, round(damage), hp, round(bonus,  3), monster)
        self.damage_record_hp(
            bei_lv_str="BAI_FU_BEI_LV / 100", bonus=bonus, monster=monster)


class Switch_to_Fu_Fu_Action(Action):
    def do_impl(self, plan: FuFuActionPlan):
        self.debug("切换到芙芙")
        plan.switch_to_forground(plan.get_fufu().name)


class Switch_To_Ye_Lan_Action(Action):
    def do_impl(self, plan: FuFuActionPlan):
        self.debug("切换到夜兰")
        plan.switch_to_forground(YE_LAN_NAME)


class Switch_To_ZhongLi_Action(Action):
    def do_impl(self, plan: FuFuActionPlan):
        plan.switch_to_forground(ZHONG_LI_NAME)
        self.debug("切换到钟离")


class Switch_To_Wan_Ye_Action(Action):
    def do_impl(self, plan: FuFuActionPlan):
        self.debug("切换到万叶")
        plan.switch_to_forground(WAN_YE_NAME)


class Ye_Lan_4_Ming_Action(Action):
    def do_impl(self, plan: FuFuActionPlan):
        plan.ye_lan_e_num += 1
        self.debug("夜兰四命生效一层")
        plan.damage_record_hp()
        plan.get_fufu().get_hp().modify_max_hp_per(0.1)
        for t in plan.get_teammates():
            t.get_hp().modify_max_hp_per(0.1)

        # hps_str = "fufu:" + str(plan.get_fufu().get_hp().get_max_hp()) + ", "
        # for t in plan.get_teammates():
        #     hps_str += t.name + ":" + str(t.get_hp().get_max_hp()) + ", "
        # self.debug("夜兰e后各角色生命值上限: %s", hps_str)


class Ye_Lan_Q_Animation_Start(Action):
    def do_impl(self, plan: FuFuActionPlan):
        self.debug("夜兰大招动画开始")
        ye_lan = plan.get_teammate(YE_LAN_NAME)
        ye_lan.get_hp().set_in_q_animation(True)


class Ye_Lan_Q_Bonus_Start(Action):
    def do_impl(self, plan: FuFuActionPlan):
        self.debug("夜兰大招出伤")
        ye_lan = plan.get_teammate(YE_LAN_NAME)
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


bei_lv_to_salon_member_name = {
    FU_REN_BEI_LV: "夫人",
    XUN_JUE_BEI_LV: "勋爵",
    PANG_XIE_BEI_LV: "螃蟹"
}

bei_lv_to_str = {
    FU_REN_BEI_LV: "FU_REN_BEI_LV / 100",
    XUN_JUE_BEI_LV: "XUN_JUE_BEI_LV / 100",
    PANG_XIE_BEI_LV: "PANG_XIE_BEI_LV / 100"
}


class Salon_Member_Damage_Action(Action):
    def __init__(self, name, force_add_fufu_q_bonus=False):
        super().__init__(name)
        self.force_add_fufu_q_bonus = force_add_fufu_q_bonus

    def do_damage(self, plan: FuFuActionPlan, bei_lv):
        hp = plan.get_max_hp()
        e_bonus = 1 + plan.get_e_bonus() + gu_you_tian_fu_2_bonus(hp)

        if plan.effective_qi_fen_zhi == 0 and self.force_add_fufu_q_bonus:
            # print("force add q bonus")
            hp += round(MAX_QI_FEN_ZHI * QI_HP_BEI_LV * FU_NING_NA_BASE_HP)
            e_bonus += MAX_QI_FEN_ZHI * QI_TO_BONUS_BEI_LV

        damage = hp * bei_lv / 100 * e_bonus * E_EXTRA_DAMAGE_BONUS
        damage = plan.monster.attacked(damage)

        plan.total_damage += damage

        self.debug("%s出伤, damage: %s, hp:%s bonus:%s, monster:%s",
                   bei_lv_to_salon_member_name[bei_lv], round(
                       damage), hp, round(e_bonus, 3),
                   plan.monster)
        self.damage_record_hp(bei_lv_str=bei_lv_to_str[bei_lv],
                              bonus=e_bonus, monster=plan.monster, other_bonus=E_EXTRA_DAMAGE_BONUS)


class Fu_Ren_Kou_Xue_Action(Action):
    def do_impl(self, plan: FuFuActionPlan):
        self.debug("夫人扣血")
        plan.consume_hp(0.016)


class Fu_Ren_Damage_Action(Salon_Member_Damage_Action):
    def do_impl(self, plan: FuFuActionPlan):
        self.do_damage(plan, FU_REN_BEI_LV)


class Xun_Jue_Kou_Xue_Action(Action):
    def do_impl(self, plan: FuFuActionPlan):
        self.debug("勋爵扣血")
        plan.consume_hp(0.024)


class Xun_Jue_Damage_Action(Salon_Member_Damage_Action):
    def do_impl(self, plan: FuFuActionPlan):
        self.do_damage(plan, XUN_JUE_BEI_LV)


class Pang_Xie_Kou_Xue_Action(Action):
    def do_impl(self, plan: FuFuActionPlan):
        self.debug("螃蟹扣血")
        plan.consume_hp(0.036)


class Pang_Xie_Damage_Action(Salon_Member_Damage_Action):
    def do_impl(self, plan: FuFuActionPlan):
        self.do_damage(plan, PANG_XIE_BEI_LV)


class Ge_Zhe_Cure_Action(Action):
    def do_impl(self, plan: FuFuActionPlan):
        cure_num = round(plan.get_max_hp() * GE_ZHE_CURE_BEI_LV / 100 + GE_ZHE_CURE_BASE)

        foreground_character = plan.get_foreground_character()
        self.debug("歌者治疗 %s, 治疗量: %s", foreground_character.name, cure_num)
        plan.change_cur_hp(self.get_timestamp(), characters=[foreground_character], hp=cure_num)

fu_ren_kou_xue_interval = (1468, 1684)
fu_ren_kou_xue_chu_shang_interval = (330, 721)
fu_ren_chu_shang_interval = (1467, 1725)

xun_jue_kou_xue_interval = (3180, 3387)
xun_jue_kou_xue_chu_shang_interval = (723, 951)
xun_jue_chu_shang_interval = (3127, 3443)

pang_xie_kou_xue_interval = (5056, 5293)
pang_xie_kou_xue_chu_shang_interval = (745, 1018)
pang_xie_chu_shang_interval = (5063, 5325)

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
            chu_shang_time = kou_xue_time + \
                randtime(chu_kou_interval_min, chu_kou_interval_max)

        if chu_shang_time < end_time:
            chu_shang_action = chu_shang_cls(name + "出伤")
            chu_shang_action.set_timestamp(chu_shang_time)
            plan.insert_action(chu_shang_action)
            c_action_lst.append(chu_shang_action)

            c_num += 1
            if c_num >= chu_shang_num:
                break

        last_chu_shang_time = chu_shang_time

        k_num += 1
        if k_num >= kou_xue_num:
            break

        kou_xue_time += randtime(kou_xue_interval_min, kou_xue_interval_max)

    return (k_action_lst, c_action_lst)


def calc_score_full_ming_zuo(fufu_initial_state: Character):
    plan = FuFuActionPlan(fufu_initial_state)

    # 这个 plan 有几个比较大的变数：
    # 1. 第三刀重击切白芙前，夫人有小概率的会扣血，使得气氛值叠层加快，后续伤害变高，实际操作4次出了一次，自动计算的概率好像更大些
    #    解决办法：人为控制扣血次数
    # 2. plan 结束时，有概率会有夫人两次出伤，实际大多数时候只有一次
    #    解决办法：人为去掉这次出伤
    # 3. 芙芙大招效果结整时，恰好有螃蟹的一次出伤，螃蟹的倍率是最大的， 能否吃到芙芙的增伤伤害会差很多，有小概率会吃不到
    #    解决办法：实测时大部分时候都吃到了，因此这里也手动强制，参见：force_add_fufu_q_bonus

    wan_ye = WanYe(elem_mastery=994, xi_fu_si_jing_lian_num=2)

    plan.add_action("钟离点按e", ZhongLiAction, 6.285, 6.453, negative=True)
    plan.add_action("芙芙q出伤", FuFu_Q_Action, 2.783, 2.884, negative=True)
    plan.add_action("万叶q", WanYeQAction, 0.616,
                    0.7, negative=True, wan_ye=wan_ye)

    plan.add_action("芙芙点按e", FuFu_E_Action,  0, 0)
    plan.add_action("第一刀", Hei_Fu_Damage_Action, 1.15, 1.284)
    three_little_first_action = "三小只开始扣血"
    plan.add_action(three_little_first_action, Action, 1.282, 1.455)
    plan.add_action("第二刀", Hei_Fu_Damage_Action,
                    0.366, 0.401, base_action="第一刀")
    plan.add_action("荒刀", Mang_Huang_Damage_Action,
                    0.55, 0.617, base_action="第一刀")

    plan.add_action("切夜兰出来", Switch_To_Ye_Lan_Action,
                    0.333, 0.549, base_action="第二刀")
    ye_lan_first_e = "夜兰第一个e引爆"
    plan.add_action(ye_lan_first_e, Action, 0.667, 0.7, base_action="切夜兰出来")
    plan.add_action("夜兰四命生效1", Ye_Lan_4_Ming_Action,
                    0.016, 0.083, base_action=ye_lan_first_e)
    plan.add_action("夜兰q动画开始", Ye_Lan_Q_Animation_Start,
                    0.133, 0.333, base_action=ye_lan_first_e)
    plan.add_action("夜兰q增伤开始", Ye_Lan_Q_Bonus_Start,
                    1.3, 1.352, base_action="夜兰q动画开始")
    plan.add_action("夜兰四命生效2", Ye_Lan_4_Ming_Action,
                    0.868, 0.952, base_action="夜兰q增伤开始")

    plan.add_action("切芙芙出来", Switch_to_Fu_Fu_Action,
                    0.25, 0.316, base_action="夜兰四命生效2")
    three_little_disappear = "三小只开始消失，众水的歌者出来"
    plan.add_action(three_little_disappear, Action,
                    0.751, 0.783, base_action="切芙芙出来")
    plan.add_action("第三刀重击出伤", Hei_Fu_Damage_Action,
                    0.8, 0.883, base_action="切芙芙出来")
    plan.add_action("第四刀", Bai_Fu_Damage_Action, 0.75,
                    0.767, base_action="第三刀重击出伤")
    plan.add_action("第四刀扣血", Bai_Dao_Kou_Xue_Action, 0.165, 0.230,
                    base_action="第四刀", effective_delay=plan.get_effective_delay())
    plan.add_action("第五刀", Bai_Fu_Damage_Action,
                    0.383, 0.417, base_action="第四刀")
    plan.add_action("第五刀扣血", Bai_Dao_Kou_Xue_Action, 0.165, 0.230,
                    base_action="第五刀", effective_delay=plan.get_effective_delay())
    plan.add_action("芒刀", Mang_Huang_Damage_Action,
                    0.6, 0.734, base_action="第四刀")
    plan.add_action("第六刀重击", Bai_Fu_Damage_Action,
                    0.683, 0.734, base_action="第五刀")
    plan.add_action("第六刀扣血", Bai_Dao_Kou_Xue_Action, 0.05, 0.117,
                    base_action="第六刀重击", effective_delay=plan.get_effective_delay())

    # TODO: 这里的切人时间沿用了切夜兰出来的时间，是否需要重新测试
    plan.add_action("切万叶出来", Switch_To_Wan_Ye_Action,
                    0.333, 0.549, base_action="第六刀重击")
    plan.add_action("万叶e扩散", Action, 1.568, 1.568, base_action="切万叶出来")

    three_little_2nd_action = "三小只再次切出来后第一次扣血"
    plan.add_action(three_little_2nd_action, Action,
                    0.916, 1.067, base_action="第六刀重击")

    plan.add_action("夜兰第三个e", Ye_Lan_4_Ming_Action,
                    10.5, 11, base_action=ye_lan_first_e)

    plan.add_action("芙芙大招效果消失", Fu_Fu_Q_Bonus_Stop_Action,
                    18.253, 18.737, "芙芙q出伤")

    # TODO: 这里的切人时间沿用了切夜兰出来的时间，实际切人时间需要进行测试统计
    second_run_turn_start = "切钟离出来"
    plan.add_action(second_run_turn_start, Switch_To_ZhongLi_Action,
                    0.033, 0.549, base_action="芙芙大招效果消失")

    plan.add_action("夜兰大招效果消失", Ye_Lan_Q_Bonus_Stop_Actioin,
                    14.97, 14.97, "夜兰q增伤开始")
    plan.add_action("万叶增伤消失", WanYeBonusStopAction, 8, 8,
                    base_action="万叶e扩散", wan_ye=wan_ye)
    plan.add_action("风套减抗消失", FengTaoInvalidAction,
                    10, 10, base_action="万叶e扩散")

    if enable_debug:
        action_names = [a.name for a in plan.action_list]
        action_name_set = set(action_names)
        if len(action_names) != len(action_name_set):
            raise Exception("action name duplicated!")

    three_little_first_action_time = plan.find_action(
        three_little_first_action).get_timestamp()
    three_little_disappear_time = plan.find_action(
        three_little_disappear).get_timestamp()
    # print(three_little_first_action_time)
    # print(three_little_disappear_time)

    schedule_little_three(plan, FU_REN_NAME,
                          three_little_first_action_time, three_little_disappear_time,
                          Fu_Ren_Kou_Xue_Action, Fu_Ren_Damage_Action,
                          kou_xue_num=3, chu_shang_num=3)

    schedule_little_three(plan, XUN_JUE_NAME,
                          three_little_first_action_time, three_little_disappear_time,
                          Xun_Jue_Kou_Xue_Action, Xun_Jue_Damage_Action,
                          kou_xue_num=2, chu_shang_num=2)

    schedule_little_three(plan, PANG_XIE_NAME,
                          three_little_first_action_time, three_little_disappear_time,
                          Pang_Xie_Kou_Xue_Action, Pang_Xie_Damage_Action,
                          kou_xue_num=1, chu_shang_num=1)

    second_start_time = plan.find_action(
        three_little_2nd_action).get_timestamp()
    second_end_time = plan.find_action(
        second_run_turn_start).get_timestamp() + random.randint(6285, 6453) / 1000
    # print(second_start_time)
    # print(second_end_time)

    schedule_little_three(plan, FU_REN_NAME,
                          second_start_time, second_end_time,
                          Fu_Ren_Kou_Xue_Action, Fu_Ren_Damage_Action,
                          kou_xue_num=8, chu_shang_num=8)

    schedule_little_three(plan, XUN_JUE_NAME,
                          second_start_time, second_end_time,
                          Xun_Jue_Kou_Xue_Action, Xun_Jue_Damage_Action,
                          kou_xue_num=4, chu_shang_num=4)

    _, c_action_lst = schedule_little_three(plan, PANG_XIE_NAME,
                                            second_start_time, second_end_time,
                                            Pang_Xie_Kou_Xue_Action, Pang_Xie_Damage_Action,
                                            kou_xue_num=3, chu_shang_num=3)
    # 为了避免波动太大，强制让这次的螃蟹吃到芙芙q增伤
    c_action_lst[1].force_add_fufu_q_bonus = True

    ge_zhe_start_time = three_little_disappear_time
    ge_zhe_stop_time = plan.find_action("第六刀重击").get_timestamp()

    ge_zhe_cure_time = ge_zhe_start_time + random.randint(1019, 1199) / 1000
    while ge_zhe_cure_time < ge_zhe_stop_time:
        ge_zhe = Ge_Zhe_Cure_Action("众水的歌者治疗")
        ge_zhe.set_timestamp(ge_zhe_cure_time + plan.get_effective_delay())
        plan.insert_action(ge_zhe)

        # FIXME: 这里没有考虑固有天赋2，如果当前生命值上限低于4w，则治疗间隔是更长的
        # 歌者的治疗间隔目前是在这里写死的，实际应该是根据生命值上限实时决定的
        # 不过话说回来，按满命的流程，切白芙的时候，最终排名靠前的圣遗物组合应该生命值上限都在4w附近吧？
        ge_zhe_cure_time += random.randint(1612, 1783) / 1000

    # plan.sort_action()
    # print(len(plan.action_list))
    # for a in plan.action_list:
    #    self.debug(str(round(a.get_timestamp(), 3)) + ":" + a.name)

    plan.run()
    return (plan.total_damage, plan.full_six_damage)


def calc_score_ying_ye_fu_qin(fufu_initial_state: Character):
    plan = FuFuActionPlan(fufu_initial_state)

    YING_BAO = MAIN_CARRY
    YE_LAN_NAME = SECONDARY_CARRY
    QIN = HEALER

    plan.add_action("芙芙点按e", FuFu_E_Action,  0, 0)
    plan.add_action("芙芙大招动画开始", FuFu_Q_Animation_Start, 0.9, 0.9)
    three_little_first_action = "三小只开始扣血"
    plan.add_action(three_little_first_action, Action, 1.317, 1.45)
    plan.add_action("芙芙大招动画结束", FuFu_Q_Animation_Stop, 1.7, 1.7, base_action="芙芙大招动画开始")


if ming_zuo_num >= 6:
    calc_score_worker = calc_score_full_ming_zuo
else:
    calc_score_worker = calc_score_ying_ye_fu_qin

def calc_score(fufu_initial_state: Character):
    all_damage = 0
    full_six_zhan_bi = 0
    run_num = MAX_RUN_NUM

    if enable_debug:
        run_num = 1

    for _ in range(0, run_num):
        total_damage,  full_six_damage = calc_score_worker(fufu_initial_state)
        all_damage += total_damage
        full_six_zhan_bi += full_six_damage / total_damage

    all_damage /= run_num
    full_six_zhan_bi /= run_num

    return (all_damage, round(full_six_zhan_bi, 3))


def scan_syw_combine(combine: list[ShengYiWu]) -> Character:
    fufu = Character(name="fufu", base_hp=FU_NING_NA_BASE_HP)
    fufu.set_crit_rate(0.242)  # 突破加成
    fufu.set_crit_damage(0.5 + sum(extra_crit_damage.values()))
    fufu.get_hp().modify_max_hp(4780)  # 花
    fufu.get_hp().modify_max_hp_per(sum(extra_hp_bonus.values()))
    fufu.set_e_bonus(sum(extra_e_bonus.values()))
    fufu.set_q_bonus(sum(extra_q_bonus.values()))
    fufu.add_all_bonus(sum(extra_common_elem_bonus.values()))

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
    if energy_recharge < required_energy_recharge:
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


def ye_fu_wan_zhong_team_qualifier(hp):
    damage = 0
    cur_hp = hp
    damage += cur_hp * Q_BEI_LV / 100 * 1.615 * 1.05 * 0.487
    damage += cur_hp * E_BEI_LV / 100 * 2.013 * 1.25 * 0.487
    damage += cur_hp * HEI_FU_BEI_LV / 100 * 2.013 * 1.25 * 0.487

    cur_hp = hp + (0.14 * 1) * FU_NING_NA_BASE_HP
    damage += cur_hp * HEI_FU_BEI_LV / 100 * 2.082 * 1.25 * 0.487
    damage += cur_hp * FU_REN_BEI_LV / 100 * 2.442 * 1.25 * 0.487 * 1.4
    damage += cur_hp * HEI_FU_BEI_LV / 100 * 2.082 * 1.25 * 0.487
    damage += cur_hp * PANG_XIE_BEI_LV / 100 * 2.702 * 1.25 * 0.487 * 1.4
    damage += cur_hp * XUN_JUE_BEI_LV / 100 * 2.702 * 1.25 * 0.487 * 1.4

    cur_hp = hp + (0.14 * 2 + 0.1 * 1) * FU_NING_NA_BASE_HP
    damage += cur_hp * FU_REN_BEI_LV / 100 * 3.185 * 1.25 * 0.487 * 1.4

    cur_hp = hp + (0.14 * 2 + 0.1 * 1 + (435.583 - 400) * 0.0035) * FU_NING_NA_BASE_HP
    damage += cur_hp * FU_REN_BEI_LV / 100 * 3.308 * 1.25 * 0.487 * 1.4

    cur_hp = hp + (0.14 * 2 + 0.1 * 2 + (469.181 - 400) * 0.0035) * FU_NING_NA_BASE_HP
    damage += cur_hp * XUN_JUE_BEI_LV / 100 * 3.308 * 1.25 * 0.487 * 1.4

    cur_hp = hp + (0.14 * 2 + 0.1 * 2 + (519.571 - 400) * 0.0035) * FU_NING_NA_BASE_HP
    damage += cur_hp * HEI_FU_BEI_LV / 100 * 2.868 * 1.25 * 0.487
    damage += cur_hp * BAI_FU_BEI_LV / 100 * 2.868 * 1.25 * 0.487

    cur_hp = hp + (0.14 * 2 + 0.1 * 2 + (537.08 - 400) * 0.0035) * FU_NING_NA_BASE_HP
    damage += cur_hp * BAI_FU_BEI_LV / 100 * 2.903 * 1.25 * 0.487
    damage += cur_hp * HEI_FU_BEI_LV / 100 * 2.903 * 1.25 * 0.487

    cur_hp = hp + (0.14 * 2 + 0.1 * 2 + (551.085 - 400) * 0.0035) * FU_NING_NA_BASE_HP
    damage += cur_hp * BAI_FU_BEI_LV / 100 * 2.903 * 1.25 * 0.487

    cur_hp = hp + (0.14 * 2 + 0.1 * 2 + (768.799 - 400) * 0.0035) * FU_NING_NA_BASE_HP
    damage += cur_hp * FU_REN_BEI_LV / 100 * 3.308 * 1.25 * 0.487 * 1.4
    damage += cur_hp * XUN_JUE_BEI_LV / 100 * 3.308 * 1.25 * 0.487 * 1.4
    damage += cur_hp * PANG_XIE_BEI_LV / 100 * 3.308 * 1.25 * 0.487 * 1.4

    cur_hp = hp + (0.14 * 2 + 0.1 * 2 + (791.207 - 400) * 0.0035) * FU_NING_NA_BASE_HP
    damage += cur_hp * FU_REN_BEI_LV / 100 * 3.308 * 1.25 * 0.487 * 1.4

    cur_hp = hp + (0.14 * 2 + 0.1 * 2 + (800 - 400) * 0.0035) * FU_NING_NA_BASE_HP
    damage += cur_hp * FU_REN_BEI_LV / 100 * 3.308 * 1.25 * 0.487 * 1.4
    damage += cur_hp * XUN_JUE_BEI_LV / 100 * 3.308 * 1.25 * 0.487 * 1.4

    cur_hp = hp + (0.14 * 2 + 0.1 * 3 + (800 - 400) * 0.0035) * FU_NING_NA_BASE_HP
    damage += cur_hp * FU_REN_BEI_LV / 100 * 3.308 * 1.25 * 0.487 * 1.4
    damage += cur_hp * PANG_XIE_BEI_LV / 100 * 3.308 * 1.25 * 0.487 * 1.4

    cur_hp = hp + (0.14 * 2 + 0.1 * 3) * FU_NING_NA_BASE_HP
    damage += cur_hp * FU_REN_BEI_LV / 100 * 2.068 * 1.25 * 0.487 * 1.4
    damage += cur_hp * XUN_JUE_BEI_LV / 100 * 2.068 * 1.25 * 0.487 * 1.4
    damage += cur_hp * FU_REN_BEI_LV / 100 * 2.068 * 1.25 * 0.487 * 1.4
    damage += cur_hp * FU_REN_BEI_LV / 100 * 1.67 * 1.25 * 0.487 * 1.4
    damage += cur_hp * XUN_JUE_BEI_LV / 100 * 1.67 * 1.25 * 0.487 * 1.4
    damage += cur_hp * PANG_XIE_BEI_LV / 100 * 1.67 * 1.05 * 0.487 * 1.4
    damage += cur_hp * FU_REN_BEI_LV / 100 * 1.67 * 1.05 * 0.487 * 1.4

    return damage


def ying_ye_fu_qin_qualifier(hp):
    return 0


def calculate_score_qualifier(score_data: ShengYiWu_Score):
    fufu = scan_syw_combine(score_data.syw_combine)
    if not fufu:
        return False

    # ”录制“一次计算过程，作为快速筛选的依据
    # 录制方法：
    # 0. 在get_debug_raw_score_list设置好用于录制的圣遗物组合，选那种80分的，不要选最好的，也不要选太差的
    # 1. 找到本文件开头处的 enable_debug，置为 True
    # 2. 找到本文件以入action.py中的 damage_record_hp，恢复被注释的代码
    # 3. 在calculate_score_callback，去掉四行Logging相关的注释，你可能需要修改logging的输出文件路径
    # 然后执行，在logging的输出文件里能找到录制好的计算过程，稍作处理去掉一些冗余即可，也可不处理
    # 后面会打印出这个计算的结果(需要把后面的 logging.debug注释去掉)，记得运行一下确认伤害量是正常的
    # 可多录制几次，找接近于平均值的

    hp = fufu.get_hp().get_max_hp()

    if ming_zuo_num >= 6:
        damage = ye_fu_wan_zhong_team_qualifier(hp)
    else:
        damage = ying_ye_fu_qin_qualifier(hp)

    score_data.damage_to_score(
        damage, fufu.get_crit_rate(), 1 + fufu.get_crit_damage())
    score_data.custom_data = fufu

    # logging.debug("damage:%s, expect_score:%s, crit_score:%s",
    #              damage, score_data.expect_score, score_data.crit_score)

    return True


def calculate_score_callback(score_data: ShengYiWu_Score):
    if score_data.custom_data:
        fufu = score_data.custom_data
    else:
        fufu = scan_syw_combine(score_data.syw_combine)

    if not fufu:
        return False

    # logging.debug(str(fufu))
    damage, full_six_zhan_bi = calc_score(fufu)
    if not damage:
        return False

    score_data.damage_to_score(
        damage, fufu.get_crit_rate(), 1 + fufu.get_crit_damage())

    # logging.debug("finished: damage: %d, full_six_zhan_bi: %s, expect_score:%s, crit_score:%s, crit_rate: %s, crit_damage: %s",
    #                 round(damage), round(full_six_zhan_bi, 3),
    #                 round(score_data.expect_score), round(score_data.crit_score),
    #                 round(fufu.get_crit_rate(), 3), round(fufu.get_crit_damage(), 3))

    panel_hp = fufu.get_hp().get_max_hp()
    fufu.get_hp().modify_max_hp_per(MING_2_HP_BONUS_MAX)
    if has_zhuan_wu:
        fufu.get_hp().modify_max_hp_per(ZHUAN_WU_HP_BEI_LV * 2)
    if has_4_ming_ye_lan:
        # 至少在单个怪上两次e
        fufu.get_hp().modify_max_hp_per(0.2)

    max_hp = fufu.get_hp().get_max_hp()

    max_e_bonus = fufu.get_e_bonus()
    if has_zhuan_wu:
        max_e_bonus += ZHUAN_WU_E_BONUS_BEI_LV * 3
    max_e_bonus += 0.28  # 按固有天赋2吃满计算
    # 大招满气氛值增伤
    qi_max_elem_bonus = QI_TO_BONUS_BEI_LV * MAX_QI_FEN_ZHI
    max_e_bonus += qi_max_elem_bonus

    max_a_bonus = fufu.get_normal_a_bonus() + qi_max_elem_bonus

    score_data.custom_data = [full_six_zhan_bi, int(max_hp), int(panel_hp), round(max_e_bonus, 3), round(max_a_bonus, 3),
                              round(fufu.get_crit_rate(), 3), round(fufu.get_crit_damage(), 3), round(fufu.get_energy_recharge(), 1)]

    return True


result_description = ", ".join(["满命六刀伤害占比", "实战最大生命值上限",
                                "面板最大生命值", "战技最高元素伤害加成(不包含夜兰的)", "满命六刀最高元素伤害加成（不包含夜兰的）",
                                "暴击率", "暴击伤害", "充能效率"])


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


def find_syw_for_fu_ning_na():
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

    return calculate_score(raw_score_list,
                           calculate_score_callbak=calculate_score_callback,
                           result_txt_file="fu_ning_na_syw.txt",
                           result_description=result_description,
                           calculate_score_qualifier=calculate_score_qualifier
                           )


# Main body
if __name__ == '__main__':
    # logging.basicConfig(filename='D:\\logs\\fufu.log', encoding='utf-8', filemode='w', level=logging.DEBUG)
    # logging.basicConfig(level=logging.DEBUG)
    print("默认算法复杂，圣遗物多的话需要执行0.5~1小时多")
    find_syw_for_fu_ning_na()
