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

jue_yuan = [
    ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_HUA, hp_percent=0.181, energe_recharge=0.123, def_v=23, crit_rate=0.07),
    #ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_HUA, atk_per=0.041, crit_rate=0.062, elem_mastery=54, crit_damage=0.21),
    ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_HUA, crit_rate=0.144, crit_damage=0.078, hp_percent=0.105, elem_mastery=40),
    ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_HUA, elem_mastery=44, crit_damage=0.21, def_per=0.066, energe_recharge=0.194),
    ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_HUA, elem_mastery=21, crit_rate=0.066, energe_recharge=0.181, crit_damage=0.124),
    ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_HUA, atk=33, crit_rate=0.066, atk_per=0.111, crit_damage=0.117),

    ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_YU, def_per=0.073, atk_per=0.087, crit_rate=0.027, energe_recharge=0.285),
    ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_YU, crit_damage=0.148, def_per=0.117, def_v=19, crit_rate=0.148),
    ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_YU, crit_rate=0.039, crit_damage=0.35, hp_percent=0.041, def_v=39),
    ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_YU, hp=448, crit_damage=0.078, energe_recharge=0.311, hp_percent=0.053),
    ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_YU, hp=807, atk_per=0.047, energe_recharge=0.11, crit_damage=0.171),
    ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_YU, elem_mastery=16, atk_per=0.058, crit_damage=0.148, crit_rate=0.132),

    ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_TOU, crit_rate=0.311, atk_per=0.047, crit_damage=0.256, energe_recharge=0.104, hp=209),
    ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_TOU, crit_rate=0.311, atk=31, crit_damage=0.179, def_per=0.058, energe_recharge=0.104),
    ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_TOU, crit_rate=0.311, crit_damage=0.218, hp_percent=0.087, elem_mastery=16, atk_per=0.099),

    ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_SHA, hp_percent=0.093, crit_damage=0.14, crit_rate=0.07, atk=35, energe_recharge=0.518),
    ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_SHA, hp=448, crit_rate=0.07, atk_per=0.082, def_v=44, energe_recharge=0.518),
    ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_SHA, crit_damage=0.194, elem_mastery=19, hp=508, def_v=0.117, energe_recharge=0.518),
    ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_SHA, hp=0.117, crit_rate=0.027, def_per=0.19, crit_damage=0.14, energe_recharge=0.518),
]

syw_s_b = {
    ShengYiWu.PART_SHA : [
        ShengYiWu(ShengYiWu.LIE_REN, ShengYiWu.PART_SHA, atk=14, crit_rate=0.14, def_v=37,  crit_damage=0.148, energe_recharge=0.518),
        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_SHA, elem_mastery=23, crit_damage=0.218, def_v=44, crit_rate=0.07, energe_recharge=0.518),

        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_SHA, hp_percent=0.093, crit_damage=0.14, crit_rate=0.07, atk=35, energe_recharge=0.518),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_SHA, hp=448, crit_rate=0.07, atk_per=0.082, def_v=44, energe_recharge=0.518),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_SHA, crit_damage=0.194, elem_mastery=19, hp=508, def_v=0.117, energe_recharge=0.518),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_SHA, hp=0.117, crit_rate=0.027, def_per=0.19, crit_damage=0.14, energe_recharge=0.518),

        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_SHA, crit_rate=0.101, hp=508, atk_per=0.099, def_v=23, energe_recharge=0.518),
    ],
    ShengYiWu.PART_BEI : [
        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_BEI, crit_rate=0.035, def_v=44, atk_per=0.053, crit_damage=0.28),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_BEI, crit_rate=0.062, crit_damage=0.28, atk=14, def_v=16),
        ShengYiWu(ShengYiWu.YUE_TUAN, ShengYiWu.PART_BEI, hp_percent=0.041, crit_damage=0.14, crit_rate=0.105, hp=568),
        ShengYiWu(ShengYiWu.JUE_DOU_SHI, ShengYiWu.PART_BEI, atk_per=0.163, energe_recharge=0.065, atk=29, crit_damage=0.202),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_BEI, crit_rate=0.031, energe_recharge=0.097, elem_mastery=21, crit_damage=0.256),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_BEI, crit_damage=0.256, def_per=0.139, energe_recharge=0.091, atk_per=0.058),
    ]
}


def find_combins(all_syw):
    return list(itertools.combinations(jue_yuan, 4))


def calculate_score(combine):
    max_atk = 735
    ban_ni_te_atk = int(755 * 1.19)
    shuang_huo_atk = int(max_atk * 0.25)
    extra_atk = ban_ni_te_atk + shuang_huo_atk
    base_atk = max_atk + 311 + extra_atk
    base_crit_damage = 1 + 0.5
    base_elem_mastery = 96
    base_energy_recharge = 1 + (0.459 # 鱼叉
                                + 0.2 # 绝缘
                                )
    wan_ye_bonus = 0.4
    ye_lan_bonus = 0.29
    lei_shen_bonus = 0.24
    base_elem_bonus = 1 + lei_shen_bonus + wan_ye_bonus + ye_lan_bonus

    crit_rate = sum([p.crit_rate for p in combine]) + 0.05
    if crit_rate < 0.5:
        return None

    real_crit_rate = crit_rate + 0.12 # 鱼叉

    atk = sum([p.atk for p in combine])
    atk_per = sum([p.atk_per for p in combine])
    extra_crit_damage = sum([p.crit_damage for p in combine])
    total_energe_recharge = (
        sum([p.energe_recharge for p in combine]) + base_energy_recharge) * 100
    elem_mastery = sum([p.elem_mastery for p in combine]) + base_elem_mastery

    if total_energe_recharge < 220:
        return None
    
    if elem_mastery < 180:
        return None
    
    extra_elem_bonus = min(total_energe_recharge / 4 / 100, 0.75)

    all_atk = atk_per * max_atk + atk + base_atk

    non_crit_score = all_atk / base_atk * (extra_elem_bonus + base_elem_bonus) / base_elem_bonus
    crit_score = non_crit_score * (base_crit_damage + extra_crit_damage) / base_crit_damage
    expect_crit_damage_bonus = real_crit_rate * (extra_crit_damage + base_crit_damage - 1)
    expect_score = non_crit_score * (1 + expect_crit_damage_bonus)
    return [expect_score, crit_score, elem_mastery, int(all_atk), round(crit_rate, 3), round(base_crit_damage + extra_crit_damage - 1, 3), round(total_energe_recharge, 1), combine]


# Main body
if __name__ == '__main__':
    find_syw(syw_s_b, find_combins, calculate_score, "xiang_ling_syw.txt")
