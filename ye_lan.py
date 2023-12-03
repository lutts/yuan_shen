#!/user/bin/env python3 -tt
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

import sys
import os
import logging
import itertools
from base_syw import ShengYiWu, find_syw, calculate_score

ming_zuo_num = 6

ye_lan_base_hp = 14450.0

def match_sha_callback(syw:ShengYiWu):
    return syw.hp_percent == 0.466 or syw.energe_recharge == ShengYiWu.ENERGE_RECHARGE_MAX


def match_bei_callback(syw:ShengYiWu):
    return syw.hp_percent == 0.466 or syw.elem_type == ShengYiWu.ELEM_TYPE_SHUI


def match_syw(s : ShengYiWu, expect_name):
    if s.name != expect_name:
        return False
    
    if s.part == ShengYiWu.PART_SHA:
        return match_sha_callback(s)
    elif s.part == ShengYiWu.PART_BEI:
        return match_bei_callback(s)
    else:
        return True

def find_combine_callback():
    hua_hai = find_syw(match_syw_callback=lambda s: match_syw(s, ShengYiWu.HUA_HAI))
    qian_yan = find_syw(match_syw_callback=lambda s: match_syw(s, ShengYiWu.QIAN_YAN))
    chen_lun = find_syw(match_syw_callback=lambda s: match_syw(s, ShengYiWu.CHEN_LUN))
    shui_xian = find_syw(match_syw_callback=lambda s: match_syw(s, ShengYiWu.SHUI_XIAN))
    jue_yuan = find_syw(match_syw_callback=lambda s: match_syw(s, ShengYiWu.JUE_YUAN))

    hua_hai_combins = list(itertools.combinations(hua_hai, 2))
    qian_yan_combins = list(itertools.combinations(qian_yan, 2))
    chen_lun_combins = list(itertools.combinations(chen_lun, 2))
    shui_xian_combins = list(itertools.combinations(shui_xian, 2))

    jue_yuan_4 = list(itertools.combinations(jue_yuan, 4))

    all_combins = hua_hai_combins + qian_yan_combins + \
        chen_lun_combins + shui_xian_combins
    return [(l[0] + l[1])
                    for l in list(itertools.combinations(all_combins, 2))] + jue_yuan_4


class YeLanQBonus:
    def __init__(self):
        self.__invalid = False
        self.__stopped = True

    def invalidate(self):
        self.__invalid = True

    def start(self, start_time):
        self.__stopped = False
        self.__start_time = start_time
    
    def bonus(self, checkpoint_time):
        if self.__stopped or self.__invalid:
            return 0
        
        dur = checkpoint_time - self.__start_time
        if dur <= 0:
            return 0
        
        if dur >= 15:
            return 0
        
        return (1 + int(dur) * 3.5) / 100
    
    def stop(self):
        self.__stopped = True

def calculate_score_callback(combine : list[ShengYiWu], has_fu_fu = True, has_lei_shen = False):
    extra_hp_bonus = {
        "专武": 0.16,
    }

    if ming_zuo_num >= 4:
        extra_hp_bonus["四命保底两个e"] = 0.2

    common_elem_bonus = {
        "专武": 0.2,
        "万叶": 0.4,
        "夜兰大招平均增伤": 0.27,
    }

    extra_crit_damage = {
        "专武": 0.882,
    }

    extra_q_bonus = {
    }

    if has_fu_fu:
        extra_hp_bonus["双水"] = 0.18 + 0.25
        common_elem_bonus["芙芙q"] = 1.24
    
    if has_lei_shen:
        extra_q_bonus["雷神e"] = 70 * 0.003
        if not has_fu_fu:
            extra_hp_bonus["四色"] = 0.3

    po_ju_shi_avg_bonus = 0.36  # 大招开启后第10秒左右切出来放打满命5下
    
    crit_rate = 0.242
    crit_damage = 1 + 0.5 + sum(extra_crit_damage.values())
    hp = 0
    hp_per = 0
    elem_bonus = 1 + sum(common_elem_bonus.values())
    energe_recharge = 1

    for p in combine:
        crit_rate += p.crit_rate
        crit_damage += p.crit_damage
        hp += p.hp
        hp_per += p.hp_percent
        elem_bonus += p.elem_bonus
        energe_recharge += p.energe_recharge

    crit_rate = round(crit_rate, 3)
    if crit_rate < 0.70:
        return None

    syw_names = [p.name for p in combine]
    # print(syw_names)
    name_count = {i: syw_names.count(i) for i in syw_names}
    # print(name_count)
    for n in name_count:
        if name_count[n] < 2: # 散件不计算套装效果
            continue

        # print(n)
        if n == ShengYiWu.HUA_HAI:
            hp_per += 0.2
        elif n == ShengYiWu.SHUI_XIAN:
            elem_bonus += 0.15
        elif n == ShengYiWu.QIAN_YAN:
            hp_per += 0.2
        elif n == ShengYiWu.CHEN_LUN:
            elem_bonus += 0.15
        elif n == ShengYiWu.JUE_YUAN:
            if name_count[n] >= 4:
                energe_recharge += 0.2 # 绝缘2件套

    energe_recharge *= 100
    energe_recharge = round(energe_recharge, 1)
    if energe_recharge < 120:
        return None
    
    if ShengYiWu.JUE_YUAN in name_count and name_count[ShengYiWu.JUE_YUAN] >= 4:
        extra_q_bonus["绝缘4件套"] = min(energe_recharge / 4 / 100, 0.75)
    
    all_hp = int(ye_lan_base_hp * (1 + hp_per + sum(extra_hp_bonus.values()))) + hp + 4780

    # 扣除切人时间，按一轮循环中11次协同攻击算
    # 技能伤害：15.53%生命值上限
    # 协同伤害：10.35%生命值上限 * 3 * 11
    # 二命额外协同伤害：一般能打出5次，14%生命值上限 * 5
    # 强化破局矢伤害：20.84%生命上限 * 1.56 * 5
    # 两个e: 45.2生命值上限 * 2
    if ming_zuo_num >= 3:
        q_bei_lv = 15.53
        qx_bei_lv = 10.35
    else:
        q_bei_lv = 13.89
        qx_bei_lv = 9.26

    q_elem_bonus = elem_bonus + sum(extra_q_bonus.values())
    q_damage = all_hp * q_bei_lv / 100 * (q_elem_bonus - common_elem_bonus["夜兰大招平均增伤"])
    q_damage_crit = q_damage * crit_damage
    q_damage_expect = q_damage * (1 + crit_rate * (crit_damage - 1))

    qx_damage = all_hp * qx_bei_lv / 100 * q_elem_bonus * 3 * 11
    qx_damage_crit = qx_damage * crit_damage
    qx_damage_expect = qx_damage * (1 + crit_rate * (crit_damage - 1))

    if ming_zuo_num >= 2:
        extra_qx_damage = all_hp * 14 / 100 * q_elem_bonus * 5
        extra_qx_damage_crit = extra_qx_damage * crit_damage
        extra_qx_damage_expect = extra_qx_damage * \
            (1 + crit_rate * (crit_damage - 1))
    else:
        extra_qx_damage_crit = 0
        extra_qx_damage_expect = 0

    if ming_zuo_num == 6:
        po_ju_shi_elem_bonus = (elem_bonus - common_elem_bonus["夜兰大招平均增伤"] + po_ju_shi_avg_bonus)
        po_ju_shi_damage = all_hp * 20.84 / 100 * po_ju_shi_elem_bonus * 1.56 * 5
        po_ju_shi_damage_crit = po_ju_shi_damage * crit_damage
        po_ju_shi_damage_expect = po_ju_shi_damage * \
            (1 + crit_rate * (crit_damage - 1))
    else:
        po_ju_shi_damage_crit = 0
        po_ju_shi_damage_expect = 0

    # e技能只有一个能吃到夜兰自身大招增伤，开局两个都吃不到，但不考虑
    if ming_zuo_num >= 1:
        if ming_zuo_num == 6:
            e_bei_lv = 48.1
        else: # 非满命一般只会升到9
            if ming_zuo_num == 5:
                e_bei_lv = 45.2
            else:
                e_bei_lv = 38.4

        e_damage = all_hp * e_bei_lv / 100 * (elem_bonus * 2 - common_elem_bonus["夜兰大招平均增伤"])
    else:
        # 0命一般只会升到9级
        e_damage = all_hp * 38.4 / 100 * elem_bonus

    e_damage_crit = e_damage * crit_damage
    e_damage_expect = e_damage * (1 + crit_rate * (crit_damage - 1))

    crit_score = q_damage_crit + qx_damage_crit + \
        extra_qx_damage_crit + po_ju_shi_damage_crit + e_damage_crit
    expect_score = q_damage_expect + qx_damage_expect + \
        extra_qx_damage_expect + po_ju_shi_damage_expect + e_damage_expect

    return [expect_score, crit_score, int(all_hp), round(elem_bonus, 3), round(crit_rate, 3), round(crit_damage - 1, 3), round(energe_recharge, 1), combine]


result_description = ["总评分", "期望伤害评分", "暴击伤害评分", "实战生命值上限", "实战元素伤害加成", "暴击率", "暴击伤害", "充能效率", "圣遗物组合"]


def calculate_score_callback_only_fufu(combine):
    return calculate_score_callback(combine)

def calculate_score_callback_only_lei_shen(combine):
    return calculate_score_callback(combine, False, True)

def find_syw_for_ye_lan_with_fu_fu():
    return calculate_score(find_combine_callback=find_combine_callback,
                    match_sha_callback=match_sha_callback,
                    match_bei_callback=match_bei_callback,
                    calculate_score_callbak=calculate_score_callback_only_fufu,
                    result_txt_file="ye_lan_syw_with_fu_fu.txt",
                    result_description=result_description)

def find_syw_for_ye_lan_with_lei_shen():
    return calculate_score(find_combine_callback=find_combine_callback,
                    match_sha_callback=match_sha_callback,
                    match_bei_callback=match_bei_callback,
                    calculate_score_callbak=calculate_score_callback_only_lei_shen,
                    result_txt_file="ye_lan_syw_with_lei_shen.txt",
                    result_description=result_description)


# Main body
if __name__ == '__main__':
    find_syw_for_ye_lan_with_fu_fu()