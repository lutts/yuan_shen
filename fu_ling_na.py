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

ju_tuan = [
    ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_HUA, crit_rate=0.14, atk=14, crit_damage=0.078, energe_recharge=0.168),
    ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_HUA, crit_rate=0.07, crit_damage=0.194, atk=39, def_per=0.058),
    ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_HUA, hp_percent=0.117, elem_mastery=16, crit_damage=0.163, energe_recharge=0.11),
    ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_HUA, crit_damage=0.14, def_per=0.131, crit_rate=0.066, atk=33),
    ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_HUA, crit_damage=0.21, hp_percent=0.152, crit_rate=0.031, def_v=23),

    ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_YU, hp=568, crit_damage=0.21, hp_percent=0.053, def_v=56),
    ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_YU, def_v=37, elem_mastery=40, crit_damage=0.257, crit_rate=0.027),
    ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_YU, def_v=37, hp_percent=0.163, def_per=0.109, crit_damage=0.14),
    ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_YU, hp_percent=0.14, elem_mastery=19, crit_rate=0.097, energe_recharge=0.052),
    ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_YU, elem_mastery=37, energe_recharge=0.11, crit_damage=0.14, crit_rate=0.07),

    ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_SHA, energe_recharge=0.045, crit_damage=0.078, crit_rate=0.113, def_v=60),

    ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_BEI, crit_damage=0.132, energe_recharge=0.11, def_v=62, def_per=0.073, elem_bonus=0.466),
    
    ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_TOU, hp_percent=0.466, crit_damage=0.202, crit_rate=0.074, def_per=0.066, def_v=63),
    ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_TOU, crit_rate=0.311, def_v=37, hp=239, atk=33, hp_percent=0.157),
    ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_TOU, crit_rate=0.311, def_v=39, elem_mastery=44, hp=896, crit_damage=0.078),
    ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_TOU, crit_damage=0.622, hp=478, hp_percent=0.111, atk=0.087, crit_rate=0.066),
    ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_TOU, crit_damage=0.622, crit_rate=0.062, energe_recharge=0.097, def_v=32, def_per=0.131),
]

def find_combine(all_swy):
    ju_tuan_combins = list(itertools.combinations(ju_tuan, 4))

    hua_hai_combins = list(itertools.combinations(hua_hai, 2))
    qian_yan_combins = list(itertools.combinations(qian_yan, 2))
    chen_lun_combins = list(itertools.combinations(chen_lun, 2))
    shui_xian_combins = list(itertools.combinations(shui_xian, 2))

    all_combins_2p2 = hua_hai_combins + qian_yan_combins + \
        chen_lun_combins + shui_xian_combins
    return [(l[0] + l[1])
                    for l in list(itertools.combinations(all_combins_2p2, 2))] + ju_tuan_combins

def calculate_score(combine):
    YeLan_Max_Hp = 15307.0
    base_hp = int(YeLan_Max_Hp * (1 
                            + 0.28 # 专武
                            + 0.466 # 生命沙
                            + 0.7  # 二命
                            + 0.25  # 双水
                            + 0.2 # 夜兰四命保底两个e
                            )) + 4780
    base_crit_damage = 1 + 0.5 + 0.882
    wan_ye_bonus = 0.4
    shui_shen_bonus = 1.24
    base_water_plus = 1 + 0.75 + shui_shen_bonus + wan_ye_bonus + 0.25 # 夜兰自身平均增伤

    crit_rate = sum([p.crit_rate for p in combine]) + 0.242
    if crit_rate < 0.70:
        return None

    hp = sum([p.hp for p in combine])
    hp_per = sum([p.hp_percent for p in combine])
    extra_crit_damage = sum([p.crit_damage for p in combine])
    extra_water_plus = sum([p.elem_bonus for p in combine])
    total_energe_recharge = (sum([p.energe_recharge for p in combine]) + 1) * 100

    if total_energe_recharge < 107:
        return None

    # syw_names = [p.name for p in combine]
    # #print(syw_names)
    # name_count = {i:syw_names.count(i) for i in syw_names}
    # #print(name_count)
    # for n in name_count:
    #     if name_count[n] != 2:
    #         continue

    #     #print(n)
    #     if n == ShengYiWu.HUA_HAI:
    #         hp_per += 0.2
    #     elif n == ShengYiWu.SHUI_XIAN:
    #         extra_water_plus += 0.15
    #     elif n == ShengYiWu.QIAN_YAN:
    #         hp_per += 0.2
    #     elif n == ShengYiWu.CHEN_LUN:
    #         extra_water_plus += 0.15

    all_hp = hp_per * YeLan_Max_Hp + hp + base_hp

    # print('all_hp:' + str(all_hp))
    # print('base_hp:' + str(base_hp))
    #if extra_water_plus < 0.466:
    #    print("extra_plus:" + str(extra_water_plus))
    # print('base_plus:' + str(base_water_plus))
    # print('extra_cd:' + str(extra_crit_damage))
    # print('base_cd:' + str(base_crit_damage))
    # print('-----------------------------')

    # non_crit_score: 不暴击的情况下，相对于base的增幅
    non_crit_score= all_hp / base_hp * (base_water_plus + extra_water_plus) / base_water_plus
    # crit_score: 暴击了的情况下，暴击伤害相对于base的增幅
    crit_score = non_crit_score* (base_crit_damage + extra_crit_damage) / base_crit_damage
    expect_crit_damage_bonus = crit_rate * (extra_crit_damage + base_crit_damage - 1)
    # 当前圣遗物组合的伤害期望
    expect_score = non_crit_score* (1 + expect_crit_damage_bonus)

    return [expect_score, crit_score, int(all_hp), round(crit_rate, 3), round(base_crit_damage +
                                                                extra_crit_damage - 1, 3), round(total_energe_recharge, 1), combine]

# Main body
if __name__ == '__main__':
    find_syw(syw_s_b, find_combine, calculate_score, "fu_ling_na_syw.txt")
