#!/user/bin/env python3 -tt
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

import sys
import os
import logging
import itertools
from base_syw import ShengYiWu, all_syw_exclude_s_b, find_syw
from ye_lan_shui_shen_syw import hua_hai, qian_yan, chen_lun, shui_xian, syw_s_b


def find_combine(all_swy):
    hua_hai_combins = list(itertools.combinations(hua_hai, 2))
    qian_yan_combins = list(itertools.combinations(qian_yan, 2))
    chen_lun_combins = list(itertools.combinations(chen_lun, 2))
    shui_xian_combins = list(itertools.combinations(shui_xian, 2))

    all_combins = hua_hai_combins + qian_yan_combins + \
        chen_lun_combins + shui_xian_combins
    return [(l[0] + l[1])
                    for l in list(itertools.combinations(all_combins, 2))]


def calculate_score(combine):
    YeLan_Max_Hp = 14450.0
    base_hp = int(YeLan_Max_Hp * (1 
                            + 0.466 # 生命沙
                            #+ 0.3 #四色
                             + 0.18 + 0.25 # 双水
                            + 0.16 # 专武
                            + 0.2 # 四命保底两个e
                            )) + 4780
    base_crit_damage = 1 + 0.5 + 0.882
    wan_ye_bonus = 0.4
    lei_shen_bonus = 0#0.27
    shui_shen_bonus = 1.24
    base_water_bonus = 1 + shui_shen_bonus + wan_ye_bonus + lei_shen_bonus + 0.25 # 夜兰自身平均增伤

    crit_rate = sum([p.crit_rate for p in combine]) + 0.242
    if crit_rate < 0.75:
        return None

    hp = sum([p.hp for p in combine])
    hp_per = sum([p.hp_percent for p in combine])
    extra_crit_damage = sum([p.crit_damage for p in combine])
    extra_water_bonus = sum([p.elem_bonus for p in combine])
    total_energe_recharge = (sum([p.energe_recharge for p in combine]) + 1) * 100

    #if total_energe_recharge < 140:
    #    return None

    syw_names = [p.name for p in combine]
    #print(syw_names)
    name_count = {i:syw_names.count(i) for i in syw_names}
    #print(name_count)
    for n in name_count:
        if name_count[n] != 2:
            continue

        #print(n)
        if n == ShengYiWu.HUA_HAI:
            hp_per += 0.2
        elif n == ShengYiWu.SHUI_XIAN:
            extra_water_bonus += 0.15
        elif n == ShengYiWu.QIAN_YAN:
            hp_per += 0.2
        elif n == ShengYiWu.CHEN_LUN:
            extra_water_bonus += 0.15

    all_hp = hp_per * YeLan_Max_Hp + hp + base_hp

    # print('all_hp:' + str(all_hp))
    # print('base_hp:' + str(base_hp))
    #if extra_water_bonus < 0.466:
    #    print("extra_bonus:" + str(extra_water_bonus))
    # print('base_bonus:' + str(base_water_bonus))
    # print('extra_cd:' + str(extra_crit_damage))
    # print('base_cd:' + str(base_crit_damage))
    # print('-----------------------------')

    # non_crit_score: 不暴击的情况下，相对于base的增幅
    non_crit_score= all_hp / base_hp * (base_water_bonus + extra_water_bonus) / base_water_bonus
    # crit_score: 暴击了的情况下，暴击伤害相对于base的增幅
    crit_score = non_crit_score* (base_crit_damage + extra_crit_damage) / base_crit_damage
    expect_crit_damage_bonus = crit_rate * (extra_crit_damage + base_crit_damage - 1)
    # 当前圣遗物组合的伤害期望
    expect_score = non_crit_score* (1 + expect_crit_damage_bonus)

    return [expect_score, crit_score, int(all_hp), round(crit_rate, 3), round(base_crit_damage +
                                                                extra_crit_damage - 1, 3), round(total_energe_recharge, 1), combine]

# Main body
if __name__ == '__main__':
    find_syw(syw_s_b, find_combine, calculate_score, "ye_lan_syw.txt")
