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

syw_s_b = {
    ShengYiWu.PART_SHA: [
        ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_SHA, energe_recharge=0.045, crit_damage=0.078, crit_rate=0.113, def_v=60),
        ShengYiWu(ShengYiWu.LIE_REN, ShengYiWu.PART_SHA, crit_rate=0.027, def_v=23, crit_damage=0.264, hp=478),
        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_SHA, energe_recharge=0.052, crit_damage=0.202, elem_mastery=44, crit_rate=0.062),
        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_SHA, def_v=21, crit_damage=0.187, crit_rate=0.087, atk_per=0.041),
        ShengYiWu(ShengYiWu.ZHUI_YI, ShengYiWu.PART_SHA, atk=19, crit_damage=0.14, elem_mastery=33, crit_rate=0.105),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_SHA, crit_rate=0.066, atk=33, elem_mastery=40, crit_damage=0.21),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_SHA, elem_mastery=44, atk=16, energe_recharge=0.058, crit_damage=0.272),
        ShengYiWu(ShengYiWu.CHEN_LUN, ShengYiWu.PART_SHA, hp=448, crit_damage=0.311, def_per=0.073, elem_mastery=40),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_SHA, energe_recharge=0.091, crit_rate=0.163, crit_damage=0.078, hp=239),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_SHA, crit_rate=0.031, def_v=23, crit_damage=0.295, energe_recharge=0.104),

        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_SHA, hp=837, elem_mastery=16, crit_damage=0.257, atk=19),
        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_SHA, atk=18, energe_recharge=0.091, crit_damage=0.218, crit_rate=0.074),
    ],
    ShengYiWu.PART_BEI: [
        ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_BEI, crit_damage=0.132, energe_recharge=0.11, def_v=62, def_per=0.73, elem_bonus=0.466),
        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_BEI, hp_percent=0.163, crit_damage=0.14, energe_recharge=0.052, atk=27, elem_bonus=0.466),
        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_BEI, crit_rate=0.109, def_v=32, hp=478, hp_percent=0.058, elem_bonus=0.466),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_BEI, hp_percent=0.152, crit_damage=0.194, def_v=19, hp=239, elem_bonus=0.466),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_BEI, hp=717, hp_percent=0.146, def_per=0.073, crit_damage=0.07, elem_bonus=0.466),
        ShengYiWu(ShengYiWu.YUE_TUAN, ShengYiWu.PART_BEI, atk=29, crit_damage=0.241, hp=239, hp_percent=0.099, elem_bonus=0.466),
        ShengYiWu(ShengYiWu.YUE_TUAN,   ShengYiWu.PART_BEI, hp=538, crit_damage=0.078, atk_per=0.152, crit_rate=0.074, elem_bonus=0.466),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_BEI, atk=14, hp_percent=0.14, crit_damage=0.202, hp=269, elem_bonus=0.466),

        ShengYiWu(ShengYiWu.LIE_REN, ShengYiWu.PART_BEI, crit_rate=0.031, crit_damage=0.218, elem_mastery=31, def_v=37, hp_percent=0.466),
        ShengYiWu(ShengYiWu.LIE_REN, ShengYiWu.PART_BEI, energe_recharge=0.045, crit_rate=0.101, atk=18, hp=657, hp_percent=0.466),

    ],
}

def find_combine(all_swy):
    return list(itertools.combinations(ju_tuan, 4))

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
