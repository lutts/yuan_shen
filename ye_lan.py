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

def match_sha_callback(syw:ShengYiWu):
    return syw.hp_percent == 0.466


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

    hua_hai_combins = list(itertools.combinations(hua_hai, 2))
    qian_yan_combins = list(itertools.combinations(qian_yan, 2))
    chen_lun_combins = list(itertools.combinations(chen_lun, 2))
    shui_xian_combins = list(itertools.combinations(shui_xian, 2))

    all_combins = hua_hai_combins + qian_yan_combins + \
        chen_lun_combins + shui_xian_combins
    return [(l[0] + l[1])
                    for l in list(itertools.combinations(all_combins, 2))]


def calculate_score_callback(combine):
    YeLan_Max_Hp = 14450.0
    base_hp = int(YeLan_Max_Hp * (1
                                  #+ 0.3  # 四色
                                  + 0.18 + 0.25 # 双水
                                  + 0.16  # 专武
                                  + 0.2  # 四命保底两个e
                                  )) + 4780
    base_crit_damage = 1 + 0.5 + 0.882
    zhuan_wu_bonus = 0.2
    wan_ye_bonus = 0.4
    lei_shen_bonus = 0 #0.27
    shui_shen_bonus = 1.24
    base_water_bonus = 1 + zhuan_wu_bonus + shui_shen_bonus + \
        wan_ye_bonus + lei_shen_bonus + 0.25  # 夜兰自身平均增伤

    crit_rate = sum([p.crit_rate for p in combine]) + 0.242
    if crit_rate < 0.75:
        return None

    hp = sum([p.hp for p in combine])
    hp_per = sum([p.hp_percent for p in combine])
    extra_crit_damage = sum([p.crit_damage for p in combine])
    extra_water_bonus = sum([p.elem_bonus for p in combine])
    total_energe_recharge = (
        sum([p.energe_recharge for p in combine]) + 1) * 100

    if total_energe_recharge < 120:
        return None

    syw_names = [p.name for p in combine]
    # print(syw_names)
    name_count = {i: syw_names.count(i) for i in syw_names}
    # print(name_count)
    for n in name_count:
        if name_count[n] != 2:
            continue

        # print(n)
        if n == ShengYiWu.HUA_HAI:
            hp_per += 0.2
        elif n == ShengYiWu.SHUI_XIAN:
            extra_water_bonus += 0.15
        elif n == ShengYiWu.QIAN_YAN:
            hp_per += 0.2
        elif n == ShengYiWu.CHEN_LUN:
            extra_water_bonus += 0.15

    all_hp = int(hp_per * YeLan_Max_Hp) + hp + base_hp
    elem_bonus = base_water_bonus + extra_water_bonus
    crit_damage = base_crit_damage + extra_crit_damage

    # print('all_hp:' + str(all_hp))
    # print('base_hp:' + str(base_hp))
    # if extra_water_bonus < 0.466:
    #    print("extra_bonus:" + str(extra_water_bonus))
    # print('base_bonus:' + str(base_water_bonus))
    # print('extra_cd:' + str(extra_crit_damage))
    # print('base_cd:' + str(base_crit_damage))
    # print('-----------------------------')

    # 扣除切人时间，按一轮循环中11次协同攻击算
    # 技能伤害：15.53%生命值上限
    # 协同伤害：10.35%生命值上限 * 3 * 11
    # 二命额外协同伤害：一般能打出5次，14%生命值上限 * 5
    # 强化破局矢伤害：20.84%生命上限 * 1.56 * 5
    # 两个e: 45.2生命值上限 * 2
    q_damage = all_hp * 15.53 / 100 * elem_bonus
    q_damage_crit = q_damage * crit_damage
    q_damage_expect = q_damage * (1 + crit_rate * (crit_damage - 1))

    qx_damage = all_hp * 10.35 / 100 * elem_bonus * 3 * 11
    qx_damage_crit = qx_damage * crit_damage
    qx_damage_expect = qx_damage * (1 + crit_rate * (crit_damage - 1))

    extra_qx_damage = all_hp * 14 / 100 * elem_bonus * 5
    extra_qx_damage_crit = extra_qx_damage * crit_damage
    extra_qx_damage_expect = extra_qx_damage * \
        (1 + crit_rate * (crit_damage - 1))

    po_ju_shi_damage = all_hp * 20.84 / 100 * elem_bonus * 1.56 * 5
    po_ju_shi_damage_crit = po_ju_shi_damage * crit_damage
    po_ju_shi_damage_expect = po_ju_shi_damage * \
        (1 + crit_rate * (crit_damage - 1))

    e_damage = all_hp * 45.2 / 100 * elem_bonus * 2
    e_damage_crit = e_damage * crit_damage
    e_damage_expect = e_damage * (1 + crit_rate * (crit_damage - 1))

    crit_score = q_damage_crit + qx_damage_crit + \
        extra_qx_damage_crit + po_ju_shi_damage_crit + e_damage_crit
    expect_score = q_damage_expect + qx_damage_expect + \
        extra_qx_damage_expect + po_ju_shi_damage_expect + e_damage_expect

    # # non_crit_score: 不暴击的情况下，相对于base的增幅
    # non_crit_score= all_hp / base_hp * (base_water_bonus + extra_water_bonus) / base_water_bonus
    # # crit_score: 暴击了的情况下，暴击伤害相对于base的增幅
    # crit_score = non_crit_score* (base_crit_damage + extra_crit_damage) / base_crit_damage
    # expect_crit_damage_bonus = crit_rate * (extra_crit_damage + base_crit_damage - 1)
    # # 当前圣遗物组合的伤害期望
    # expect_score = non_crit_score* (1 + expect_crit_damage_bonus)

    return [expect_score, crit_score, int(all_hp), round(crit_rate, 3), round(crit_damage - 1, 3), round(total_energe_recharge, 1), combine]


def find_syw_for_ye_lan():
    return calculate_score(find_combine_callback=find_combine_callback,
                    match_sha_callback=match_sha_callback,
                    match_bei_callback=match_bei_callback,
                    calculate_score_callbak=calculate_score_callback,
                    result_txt_file="ye_lan_syw.txt")

# Main body
if __name__ == '__main__':
    find_syw_for_ye_lan()