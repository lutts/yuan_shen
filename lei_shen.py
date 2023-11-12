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
    ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_HUA, atk_per=0.041, crit_rate=0.062, elem_mastery=54, crit_damage=0.21),
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

    ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_BEI, crit_damage=0.179, elem_mastery=91, atk=19, def_per=0.073, elem_bonus=0.466),
    ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_BEI, crit_damage=0.218, crit_rate=0.066, def_v=39, energe_recharge=0.058, atk_per=0.466),
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
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_BEI, crit_damage=0.218, crit_rate=0.066, def_v=39, energe_recharge=0.058, atk_per=0.466),

        ShengYiWu(ShengYiWu.SHA_SHANG, ShengYiWu.PART_BEI, elem_bonus=0.466, crit_rate=0.07, atk_per=0.053, atk=54, crit_damage=0.132),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_BEI, elem_bonus=0.466, crit_damage=0.179, elem_mastery=91, atk=19, def_per=0.073),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_BEI, elem_bonus=0.466, energe_recharge=0.123, crit_damage=0.148, atk_per=0.105, crit_rate=0.066),
    ]
}

def find_combins(all_syw):
    return list(itertools.combinations(jue_yuan, 4))

def calculate_score(combine):
    max_atk = 945
    ban_ni_te_atk = int(755 * 1.19)
    shuang_huo_atk = 0 # int(945 * 0.25)
    jiu_tiao_atk = 0 # int(858 * 0.86)
    extra_atk = ban_ni_te_atk + shuang_huo_atk + jiu_tiao_atk
    base_atk = max_atk + 311 + extra_atk
    base_crit_damage = 1.5
    wan_ye_bonus = 0.4
    ye_lan_bonus = 0.29
    base_elem_bonus = 1 + 0.27 + wan_ye_bonus + ye_lan_bonus

    crit_rate = 0
    atk = 0
    atk_per = 0
    extra_crit_damage = 0
    total_energe_recharge = 0
    extra_elem_bonus = 0

    for p in combine:
        crit_rate += p.crit_rate
        atk += p.atk
        atk_per += p.atk_per
        extra_crit_damage += p.crit_damage
        total_energe_recharge += p.energe_recharge
        extra_elem_bonus += p.elem_bonus

    crit_rate = sum([p.crit_rate for p in combine]) + 0.05
    if crit_rate < 0.6:
        return None

    if extra_crit_damage < 0.9:
        return None

    total_energe_recharge = (total_energe_recharge + 1.32 + 0.551 + 0.2) * 100
    extra_elem_bonus += (total_energe_recharge - 100) * 0.004 + min(total_energe_recharge / 4 / 100, 0.75)
    atk_per += min((total_energe_recharge -100) * 0.0028, 0.8)

    if total_energe_recharge < 260 or total_energe_recharge > 280:
        return None
   
    all_atk = atk_per * max_atk + atk + base_atk
    all_bonus = extra_elem_bonus + base_elem_bonus
    crit_damage = base_crit_damage + extra_crit_damage

    # 一轮伤害：两套普攻 + 4下
    # 愿力层数：夜兰70 + 万叶60 + 班尼特60 = 190 * 0.2 = 38 * 1.2 = 45层，所有队友产球5颗就有60层
    # 雷九万班：60层肯定没问题
    # 梦想一刀：(721% + 420%=1141%)攻击力
    # 一段：79.8% + 78.6% = 158.4%
    # 二段：78.4% + 78.6% = 157%
    # 三段：96.0% + 78.6% = 174.6%
    # 四段：(55.1% + 78.6% = 133.7%) + (55.3% + 78.6% = 133.9%)
    # 五段：131.9% + 78.6% = 210.5%

    q_damage = all_atk * 1141 / 100 * all_bonus
    q_damage_crit = q_damage * crit_damage
    q_damage_expect = q_damage * (1 + crit_rate * (crit_damage - 1))

    qa1_damage = all_atk * 158.4 / 100 * all_bonus * 3
    qa1_damage_crit = qa1_damage * crit_damage
    qa1_damage_expect = qa1_damage * (1 + crit_rate * (crit_damage - 1))

    qa2_damage = all_atk * 157 / 100 * all_bonus * 3
    qa2_damage_crit = qa2_damage * crit_damage
    qa2_damage_expect = qa2_damage * (1 + crit_rate * (crit_damage - 1))

    qa3_damage = all_atk * 174.6 / 100 * all_bonus * 3
    qa3_damage_crit = qa3_damage * crit_damage
    qa3_damage_expect = qa3_damage * (1 + crit_rate * (crit_damage - 1))

    qa4_damage = all_atk * 133.7 / 100 * all_bonus * 3 + all_atk * 133.9 / 100 * all_bonus * 3
    qa4_damage_crit = qa4_damage * crit_damage
    qa4_damage_expect = qa4_damage * (1 + crit_rate * (crit_damage - 1))

    qa5_damage = all_atk * 210.5 / 100 * all_bonus * 2
    qa5_damage_crit = qa5_damage * crit_damage
    qa5_damage_expect = qa5_damage * (1 + crit_rate * (crit_damage - 1))

    crit_score = q_damage_crit + qa1_damage_crit + qa2_damage_crit + qa3_damage_crit + qa4_damage_crit + qa5_damage_crit
    expect_score = q_damage_expect + qa1_damage_expect + qa2_damage_expect + qa3_damage_expect + qa4_damage_expect + qa5_damage_expect

    # expect_crit_damage_bonus = crit_rate * (extra_crit_damage + base_crit_damage - 1)

    # base_score = all_atk / base_atk * (extra_elem_bonus + base_elem_bonus) / base_elem_bonus
    # crit_score = base_score * (base_crit_damage + extra_crit_damage) / base_crit_damage
    # expect_score = base_score * (1 + expect_crit_damage_bonus)
    return [expect_score, crit_score, int(all_atk - extra_atk), round(crit_rate, 3), round(crit_damage - 1, 3), round(total_energe_recharge, 1), combine]


# Main body
if __name__ == '__main__':
    find_syw(syw_s_b, find_combins, calculate_score, "lei_shen_syw.txt")