#!/user/bin/env python3 -tt
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

import sys
import os
import logging
import typing
import copy
import itertools
from base_syw import ShengYiWu, calculate_score, find_syw, calc_expect_score
from health_point import HealthPoint
from character import Character
from ye_lan import YeLanQBonus


# 命座
ming_zuo_num = 6
# 是否有专武
has_zhuan_wu = True

include_extra = False    # 某些配队，在芙芙大招结束后还继续输出，不切芙芙出来续大，此时将include_extra置为True

# 队友生命值上限


class Teammate:
    def __init__(self, base_hp, max_hp, elem_type=None):
        self.hp = HealthPoint(base_hp, max_hp)
        self.elem_type = elem_type

teammates = {
    # 夜兰
    "ye lan": Teammate(14450, 46461, elem_type=ShengYiWu.ELEM_TYPE_SHUI),
    # 钟离
    "zhong li": Teammate(14695, 58661),
    # 万叶
    "wan ye": Teammate(13348, 23505),
}

# 是否有四命夜兰，仅用于最终生命值上限的展示，不影响最终伤害的计算
has_4_ming_ye_lan = True

has_shuang_shui = False
for t in teammates.values():
    if t.elem_type == ShengYiWu.ELEM_TYPE_SHUI:
        has_shuang_shui = True
        break

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
    base_qi_fen_zhi = 150
    max_qi_fen_zhi = 400
else:
    base_qi_fen_zhi = 0
    max_qi_fen_zhi = 300

if ming_zuo_num >= 2:
    qi_bei_lv = 3.5
    ming_2_hp_bonus_max = 1.4
else:
    qi_bei_lv = 1
    ming_2_hp_bonus_max = 0

if ming_zuo_num >= 3:
    q_bei_lv = 24.2
    qi_bonus_bei_lv = 0.0031
    qi_cure_bonus = 0.0013
else:
    q_bei_lv = 20.5
    qi_bonus_bei_lv = 0.0025
    qi_cure_bonus = 0.001

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

if ming_zuo_num >= 5:
    e_damage_bei_lv = 16.7
    e_cure_bei_lv = 10.2
    e_cure_base = 1271

    FU_REN_BEI_LV = 6.87
    XUN_JUE_BEI_LV = 12.67
    PANG_XIE_BEI_LV = 17.61
else:
    e_bei_lv = 14.2
    e_cure_bei_lv = 8.64
    e_cure_base = 1017

    FU_REN_BEI_LV = 5.82
    XUN_JUE_BEI_LV = 10.73
    PANG_XIE_BEI_LV = 14.92

if ming_zuo_num >= 6:
    only_e = False
else:
    only_e = True

e_extra_damage_bonus = 1.4  # 队友大于50%血量，e技能伤害为原来的1.4倍
HEI_FU_BEI_LV = 18
BAI_FU_BEI_LV = 18 + 25

fu_ning_na_base_hp = 15307.0

zhuan_wu_hp_bei_lv = 0.14
zhuan_wu_e_bonus_bei_lv = 0.08

if has_zhuan_wu:
    extra_crit_damage["专武"] = 0.882


def gu_you_tian_fu_2_bonus(hp):
    return min(hp / 1000 * 0.007, 0.28)


def match_sha_callback(syw: ShengYiWu):
    return syw.hp_percent == 0.466 or syw.energy_recharge == ShengYiWu.energy_recharge_MAX


def match_bei_callback(syw: ShengYiWu):
    return syw.hp_percent == 0.466 or syw.elem_type == ShengYiWu.ELEM_TYPE_SHUI


def match_syw(s: ShengYiWu, expect_name):
    if s.name != expect_name:
        return False

    if s.part == ShengYiWu.PART_SHA:
        return match_sha_callback(s)
    elif s.part == ShengYiWu.PART_BEI:
        return match_bei_callback(s)
    else:
        return True


def find_combine_callback():
    # [(zhui_yi, h, cc:0.152, cd:0.132, re:0.097, defp:0.073),
    # (shui_xian, y, cc:0.117, cd:0.194, def:23, elem:23),
    # (shui_xian, s, cc:0.074, cd:0.218, hpp:0.466, re:0.091, atk:18),
    # (hua_hai, b, cc:0.093, cd:0.21, hpp:0.466, defp:0.131, def:23),
    # (hua_hai, t, cc:0.07, cd:0.622, hpp:0.111, hp:687, defp:0.058)]]
    # 只计算双水fixed_hp = (1 + 0.466 + 0.466 + 0.111 + 0.2 + 0.25) * 15307 + 4780 + 687 = 43627(实际为43625)
    # fixed_full_bonus = 1 + 万叶0.4 + 2水仙 = 1.55
    # fixed_e_bonus = 1 + 万叶0.4 + 固有天赋0.28 + 2水仙 = 1.83
    return [
        (ShengYiWu(ShengYiWu.ZHUI_YI, ShengYiWu.PART_HUA,
                   crit_rate=0.152, crit_damage=0.132, energe_recharge=0.097, def_per=0.073),
         ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_YU,
                   crit_rate=0.117, crit_damage=0.194, def_v=23, elem_mastery=23),
         ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_SHA,
                   crit_rate=0.074, crit_damage=0.218, energe_recharge=0.091, atk=18, hp_percent=0.466),
         ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_BEI,
                   crit_rate=0.093, crit_damage=0.21, def_per=0.131, def_v=23, hp_percent=0.466)
         )
    ]

    ju_tuan = find_syw(
        match_syw_callback=lambda s: match_syw(s, ShengYiWu.JU_TUAN))
    hua_hai = find_syw(
        match_syw_callback=lambda s: match_syw(s, ShengYiWu.HUA_HAI))
    qian_yan = find_syw(
        match_syw_callback=lambda s: match_syw(s, ShengYiWu.QIAN_YAN))
    chen_lun = find_syw(
        match_syw_callback=lambda s: match_syw(s, ShengYiWu.CHEN_LUN))
    shui_xian = find_syw(
        match_syw_callback=lambda s: match_syw(s, ShengYiWu.SHUI_XIAN))

    ju_tuan_4_combins = list(itertools.combinations(ju_tuan, 4))

    ju_tuan_2_combins = list(itertools.combinations(ju_tuan, 2))
    hua_hai_combins = list(itertools.combinations(hua_hai, 2))
    qian_yan_combins = list(itertools.combinations(qian_yan, 2))
    chen_lun_combins = list(itertools.combinations(chen_lun, 2))
    shui_xian_combins = list(itertools.combinations(shui_xian, 2))

    all_combins_2 = hua_hai_combins + qian_yan_combins + \
        chen_lun_combins + shui_xian_combins + ju_tuan_2_combins
    all_combins = [(l[0] + l[1])
                   for l in list(itertools.combinations(all_combins_2, 2))] + ju_tuan_4_combins

    # print(len(all_combins))
    # print(len(set(all_combins)))
    return all_combins


FuFu = typing.NewType("FuFu", None)


class ActionTimestampException(Exception):
    """ Action time already setted """

class Action:
    def __init__(self, source, targets: list):
        self.done = False
        # timestamp是动态计算出来的，这里只是放一个占位符
        self.__timestamp = 0

        # action的发起者，action执行的时候，会从source获取一些属性，以决定如何作用于target
        # 发起者可以是系统，也可以是某个角色，不考虑怪物给角色上负面效果的情形
        self.__source = source
        # action的目标对像，可以有多个，可以是怪物，也可以是队友
        # 如果目标是怪物，目前我们关心的有：减抗、减防、造成伤害
        # 如果目标是队友，目前我们关心的有：双爆加成、治疗、扣血、改变各种属性（例如：攻击力，生命值上限、元素伤害加成，等等）
        self.__targets = targets

    def set_timestamp(self, t):
        if self.__timestamp:
            raise ActionTimestampException(
                "Action timestamp already setted, can not change")

        self.__timestamp = t

    def get_timestamp(self):
        return self.__timestamp

    def do(self, fufu, index=-1):
        if self.done:
            return None

        return self.do_impl(fufu, index)

    def do_impl(self, fufu: FuFu, index):
        """
        * fufu: 此Action所在的FuFu的实例
        * index: 在FuFu.action_list中的位置，某些action可能需要知道自已所有位置以方便”往前看“或”往后看“
                 index小于0表示不在action_list中
        """
        pass


class FuFuState2:
    def __init__(self, hp, e_bonus, q_bonus, common_bonus, crit_rate, crit_damage, energy_recharge):
        self.__hp = HealthPoint(fu_ning_na_base_hp, hp)
        self.__teammates_hps = {}
        for k, v in teammates.items():
            self.__teammates_hps[k] = v.hp

        self.__e_bonus = e_bonus
        self.__q_bonus = q_bonus
        self.__common_bonus = common_bonus
        self.__qi_fen_zhi = 0
        self.__feng_tao_in_effect = False

        self.__crit_rate = crit_rate
        self.__crit_damage = crit_damage

        self.__energy_recharge = energy_recharge

        self.__in_foreground = True

        self.__timestamp = None

    def get_max_hp(self):
        return self.__hp.get_max_hp()

    def get_cur_hp(self):
        return self.__hp.get_cur_hp()

    def get_qi_bonus(self):
        qi_fen_zhi = self.__qi_fen_zhi
        if qi_fen_zhi > max_qi_fen_zhi:
            qi_fen_zhi = max_qi_fen_zhi

        return qi_fen_zhi * qi_bonus_bei_lv

    def get_e_bonus(self):
        return self.__e_bonus + self.get_qi_bonus() + gu_you_tian_fu_2_bonus(self.get_max_hp())

    def get_q_bonus(self):
        return self.__q_bonus + self.get_qi_bonus()

    def get_common_bonus(self):
        return self.__common_bonus + self.get_qi_bonus()

    def is_feng_tao_in_effect(self):
        return self.__feng_tao_in_effect

    def get_crit_rate(self):
        return self.__crit_rate

    def get_crit_damage(self):
        return self.__crit_damage

    def get_energy_recharge(self):
        return self.__energy_recharge

    def is_in_foreground(self):
        return self.__in_foreground

    def get_timestamp(self):
        return self.__timestamp

    #########################################
    def add_e_bonus(self, bonus):
        self.__e_bonus += bonus

    def sub_e_bonus(self, bonus):
        self.__e_bonus -= bonus

    def add_q_bonus(self, bonus):
        self.__q_bonus += bonus

    def sub_q_bonus(self, bonus):
        self.__q_bonus -= bonus

    def add_common_bonus(self, bonus):
        self.__common_bonus += bonus
        self.add_e_bonus(bonus)
        self.add_q_bonus(bonus)

    def sub_common_bonus(self, bonus):
        self.__common_bonus -= bonus
        self.sub_e_bonus(bonus)
        self.sub_q_bonus(bonus)

    def set_feng_tao_in_effect(self, in_effect):
        self.__feng_tao_in_effect = in_effect

    def add_energy_recharge(self, er):
        self.__energy_recharge += er

    def set_in_foreground(self, in_foreground):
        self.__in_foreground = in_foreground

    def set_timestamp(self, t):
        self.__timestamp = t

    def add_max_hp_per(self, hp_per, to_fufu = True, to_teammates = False):
        if to_fufu:
            self.__hp.add_max_hp_per(hp_per)
        
        if to_teammates:
            for hp in self.__teammates_hps:
                hp.add_max_hp_per(hp_per)

    def sub_max_hp_per(self, hp_per, to_fufu = True, to_teammates = False):
        if to_fufu:
            self.__hp.sub_max_hp_per(hp_per)

        if to_teammates:
            for hp in self.__teammates_hps:
                hp.sub_max_hp_per(hp_per)

    def regenerate_hp(self, hp, to_fufu = True, to_tp1 = False):
        pass

class TeamStates:
    def __init__(self, fufu: Character):
        self.effective_time = 0

        self.states: dict[str, Character] = {
            "fufu": fufu
        }

        for key, hp in teammates.items():
            c = Character()
            c.set_hp(hp)
            self.states[key] = c

    def get_fufu_state(self):
        return self.states["fufu"]


class ActionPlan:
    # 专武叠层事件
    TEAMMATE_HP_CHANGE = "teammate hp change"
    FU_FU_HP_CHANGE = "fu fu hp change"

    def __init__(self, fufu: Character):
        self.cur_states = TeamStates(fufu)
        self.effective_states = self.cur_states
        self.snapshot_list: list[TeamStates] = []

        self.total_damage = 0

        self.action_list: list[Action] = []
        self.callback_dict: dict[str, Action] = {}

    ##################################################

    def take_snapshot(self, effective_time=0):
        snapshot = copy.deepcopy(self.state)
        snapshot.timestamp = effective_time

        self.snapshot_list.append(snapshot)

    def update_effective_state(self, cur_time):
        while self.snapshot_list:
            snapshot = self.snapshot_list[0]
            if cur_time > snapshot.timestamp:
                self.effective_state = snapshot
                self.snapshot_list.pop(0)
            else:
                break

    def add_callback(self, event: str, action: Action):
        if event in self.callback_dict:
            self.callback_dict[event].append(action)
        else:
            self.callback_dict[event] = [action]

    def do_callback(self, event: str):
        if event in self.callback_dict:
            for action in self.callback_dict[event]:
                action.do(self)

    def add_action(self, action):
        self.action_list.append(action)

    def sort_action(self):
        self.action_list.sort(key=lambda a: a.timestamp)

    def do_action(self):
        self.sort_action()

        index = 0
        while index <= len(self.action_list):
            action = self.action_list[index]
            self.update_effective_state(action.get_timestamp())
            action.do(self, index)

            index += 1


class TeammateHpChangeAction(Action):
    """
    不考虑掉层的问题，每层有6秒的时效，只要操作得当，则：

    * 三小只在场是不可能掉层的，因为三小只会同时扣芙芙和队友的血，所以是能维持满层的
    * 三小只不在场，那就只可能是切成白芙了，白芙满命刀是会扣1%血的，所以是能维持满层的

    唯一的掉层条件：在白芙状态维持太长时间，并且 队友和/或芙芙 是满血的，芙芙自身满血太长时间会掉战技叠层，队友满血太长时间会掉生命叠层
    """

    def __init__(self):
        super().__init__()

        self.cur_level = 0

    def do_impl(self, fufu: FuFu, index):
        if self.cur_level >= 2:
            return

        fufu.add_hp_per(zhuan_wu_hp_bei_lv)
        self.cur_level += 1


class FuFuHpChangeAction(Action):
    def __init__(self):
        super().__init__()

        self.cur_level = 0

    def do_impl(self, fufu: FuFu, index):
        if self.cur_level >= 3:
            return

        self.add_e_bonus(zhuan_wu_e_bonus_bei_lv)
        self.cur_level += 1


class WanYe:
    def __init__(self, elem_mastery, xi_fu_si_jing_lian_num=0):
        """
        * elem_mastery: 万叶精通
        * xi_fu_si_jing_lian_num: 西福斯精炼数
        """
        self.started = False
        self.start_time = 0

        self.elem_bonus = elem_mastery * 0.0004
        if xi_fu_si_jing_lian_num <= 0:
            self.energy_recharge = 0
        else:
            if xi_fu_si_jing_lian_num > 5:
                xi_fu_si_jing_lian_num = 5
            self.energy_recharge = elem_mastery * \
                (0.036 + 0.09 * (xi_fu_si_jing_lian_num - 1)) * 0.3
            self.energy_recharge = round(self.energy_recharge, 1)


class WanYeStartAction(Action):
    def __init__(self, wan_ye: WanYe):
        super().__init__()
        self.wan_ye = wan_ye

    def do_impl(self, fufu: FuFu, index=-1):
        fufu.add_common_bonus(self.wan_ye.elem_bonus)
        fufu.add_energy_recharge(self.wan_ye.energy_recharge)
        fufu.set_feng_tao_in_effect(True)

        fufu.take_snapshot()


class WanYeBonusStopAction(Action):
    def __init__(self, wan_ye: WanYe):
        super().__init__()
        self.wan_ye = wan_ye

    def do_impl(self, fufu: FuFu, index=-1):
        fufu.sub_common_bonus(self.wan_ye.elem_bonus)

        fufu.take_snapshot()


class FengTaoInvalidAction(Action):
    def do_impl(self, fufu: FuFu, index=-1):
        fufu.state.feng_tao_in_effect = False

        fufu.take_snapshot()


class Q_Action(Action):
    def do_impl(self, fufu: FuFu, index):
        hp = fufu.get_hp()
        q_bonus = fufu.get_q_bonus()

        q_damage = hp * q_bei_lv / 100 * q_bonus

        fufu.total_damage += q_damage


class E_Action(Action):
    def do_impl(self, fufu: FuFu, index):
        hp = fufu.get_hp()
        e_bonus = fufu.get_e_bonus()

        e_damage = hp * e_bei_lv / 100 * e_bonus

        fufu.total_damage += e_damage


class Hei_Fu_Cure_Action(Action):
    def do_impl(self, fufu: FuFu, index):
        return super().do_impl(fufu, index)


class Hei_Fu_Damage_Action(Action):
    def do_impl(self, fufu: FuFu, index):
        hp = fufu.get_hp()
        common_bonus = fufu.get_common_bonus()

        damage = hp * HEI_FU_BEI_LV / 100 * common_bonus

        fufu.total_damage += damage

        # TODO: triggle cure action


# 8个线程同时计算
def calc_score_worker():
    pass

def calc_score(fufu_initial_state: Character):
    pass


def calculate_score_callback(combine: list[ShengYiWu]):
    fufu = Character(base_hp=fu_ning_na_base_hp)
    fufu.set_crit_rate(0.242) # 突破加成
    fufu.set_crit_damage(0.5 + sum(extra_crit_damage.values()))
    fufu.add_max_hp(4780) # 花
    fufu.add_max_hp_per(sum(extra_hp_bonus.values()))
    fufu.set_e_bonus(sum(extra_e_bonus.values()))
    fufu.set_q_bonus(sum(extra_q_bonus.values()))
    fufu.add_all_bonus(sum(extra_common_elem_bonus.values()))

    for p in combine:
        fufu.add_crit_rate(p.crit_rate)
        fufu.add_crit_damage(p.crit_damage)
        fufu.add_max_hp(p.hp)
        fufu.add_max_hp_per(p.hp_percent)
        fufu.add_all_bonus(p.elem_bonus)
        fufu.add_energy_recharge(p.energe_recharge)

    crit_rate = round(fufu.get_crit_rate(), 3)
    if crit_rate < 0.70:
        return None
    
    energy_recharge = round(fufu.get_energy_recharge(), 1)
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
            fufu.add_max_hp_per(0.2)
        elif n == ShengYiWu.SHUI_XIAN:
            fufu.add_all_bonus(0.15)
        elif n == ShengYiWu.QIAN_YAN:
            fufu.add_max_hp_per(0.2)
        elif n == ShengYiWu.CHEN_LUN:
            fufu.add_all_bonus(0.15)
        elif n == ShengYiWu.JU_TUAN:
            fufu.add_e_bonus(0.2)
            if name_count[n] >= 4:
                # FIXME: 暂时不考虑芙芙在前台会吃不到 0.25 增伤的问题，后续需要补充 
                fufu.add_e_bonus(0.25 + 0.25)

    print(str(fufu))
    crit_score, expect_score, full_six_zhan_bi = calc_score(fufu)
    if not crit_score:
       return None

    panel_hp = fufu.get_max_hp()
    fufu.add_max_hp_per(ming_2_hp_bonus_max)
    if has_zhuan_wu:
        fufu.add_max_hp_per(zhuan_wu_hp_bei_lv * 2)
    if has_4_ming_ye_lan:
        # 至少在单个怪上两次e
        fufu.add_max_hp_per(0.2)

    max_hp = fufu.get_max_hp()

    max_e_bonus = fufu.get_e_bonus()
    if has_zhuan_wu:
        max_e_bonus += zhuan_wu_e_bonus_bei_lv * 3
    max_e_bonus += 0.28  # 按固有天赋2吃满计算
    # 大招满气氛值增伤
    qi_max_elem_bonus = qi_bonus_bei_lv * max_qi_fen_zhi
    max_e_bonus += qi_max_elem_bonus

    max_a_bonus = fufu.get_normal_a_bonus() + qi_max_elem_bonus

    return [expect_score, crit_score, full_six_zhan_bi, int(max_hp), int(panel_hp), round(max_e_bonus, 3), round(max_a_bonus, 3),
            round(crit_rate, 3), round(fufu.get_crit_damage(), 3), round(energy_recharge, 1), combine]


result_description = ["总评分", "期望伤害评分", "暴击伤害评分", "满命六刀伤害占比", "实战最大生命值上限",
                      "面板最大生命值", "战技最高元素伤害加成(不包含夜兰的)", "满命六刀最高元素伤害加成（不包含夜兰的）",
                      "暴击率", "暴击伤害", "充能效率", "圣遗物组合"]


def find_syw_for_fu_ning_na():
    return calculate_score(find_combine_callback=find_combine_callback,
                           match_sha_callback=match_sha_callback,
                           match_bei_callback=match_bei_callback,
                           calculate_score_callbak=calculate_score_callback,
                           result_txt_file="fu_ning_na_syw.txt",
                           result_description=result_description)


# Main body
if __name__ == '__main__':
    find_syw_for_fu_ning_na()
