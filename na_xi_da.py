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

shen_lin = [
    ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_HUA, elem_mastery=40, def_v=21, crit_rate=0.027, crit_damage=0.241),

    ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_YU, crit_damage=0.078, atk_per=0.041, crit_rate=0.035, elem_mastery=96),
    ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_YU, energe_recharge=0.149, hp_percent=0.117, crit_rate=0.035, crit_damage=0.132),
    ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_YU, def_v=37, crit_damage=0.07, crit_rate=0.144, def_per=0.066),
    ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_YU, crit_damage=0.272, hp=239, crit_rate=0.07, def_v=23),
    ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_YU, crit_damage=0.132, crit_rate=0.066, hp_percent=0.041, elem_mastery=56),

    ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_SHA, crit_damage=0.124, hp_percent=0.198, energe_recharge=0.11, def_v=11),
    ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_SHA, energe_recharge=0.045, crit_rate=0.093, hp=508, def_per=0.124),

    ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_BEI, hp_percent=0.163, energe_recharge=0.045, elem_mastery=40, crit_rate=0.074),

    ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_TOU, crit_damage=0.622, atk=19, def_v=35, crit_rate=0.132, energe_recharge=0.052),
    ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_TOU, crit_damage=0.622, elem_mastery=47, def_v=32, atk_per=0.152, crit_rate=0.066),
]

syw_s_b = {
    ShengYiWu.PART_SHA : [
        ShengYiWu(ShengYiWu.LIE_REN, ShengYiWu.PART_SHA, def_per=0.073, crit_rate=0.128, crit_damage=0.148, hp_percent=0.041),
        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_SHA, atk_per=0.058, def_v=19, crit_damage=0.062, crit_rate=0.152),
        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_SHA, atk_per=0.14, def_v=35, crit_rate=0.062, atk=19),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_SHA, crit_damage=0.124, hp_percent=0.198, energe_recharge=0.11, def_v=11),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_SHA, energe_recharge=0.045, crit_rate=0.093, hp=508, def_per=0.124),
        ShengYiWu(ShengYiWu.ZHUI_YI, ShengYiWu.PART_SHA, atk=27, crit_damage=0.218, energe_recharge=0.104, atk_per=0.041),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_SHA, hp=538, crit_rate=0.062, crit_damage=0.202, hp_percent=0.058),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_SHA, energe_recharge=0.052, crit_damage=0.202, crit_rate=0.101, def_v=19),
    ],
    ShengYiWu.PART_BEI : [
        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_BEI, crit_rate=0.101, elem_mastery=19, crit_damage=0.179, hp=209),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_BEI, hp_percent=0.163, energe_recharge=0.045, elem_mastery=40, crit_rate=0.074),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_BEI, elem_mastery=54, atk_per=0.053, atk=33, crit_damage=0.155),
        ShengYiWu(ShengYiWu.CHEN_LUN, ShengYiWu.PART_BEI, crit_damage=0.21, elem_mastery=116, def_v=32, hp_percent=0.099),
        ShengYiWu('qi_shi', ShengYiWu.PART_BEI, elem_mastery=40, energe_recharge=0.058, crit_damage=0.241, hp_percent=0.047),
    ]
}


def find_combins(all_syw):
    return list(itertools.combinations(shen_lin, 4))


def calculate_score(combine):
    max_atk = 841
    base_elem_mastery = 380 + (100 # 四命
                               + 243 # 固有天赋，阿忍带圣显，四饰金加的150可以被纳西妲大招转化
                               + 187 # 精通沙
                               )
    base_atk = max_atk + 311
    base_crit_damage = 1 + 0.5
    base_elem_bonus = 1 + (0.466 # 草伤杯 
                           + 0.15 # 草套2件套效果 
                           + min((base_elem_mastery - 200) * 0.001, 0.8)
                           )

    elem_mastery = sum([p.elem_mastery for p in combine]) + base_elem_mastery
    panel_crit_rate = sum([p.crit_rate for p in combine]) + 0.05
    crit_rate = panel_crit_rate + min( (elem_mastery - 200) * 0.0003, 0.24)
    if crit_rate < 0.64:
        return None

    atk = sum([p.atk for p in combine])
    atk_per = sum([p.atk_per for p in combine])
    extra_crit_damage = sum([p.crit_damage for p in combine])
    
    elem_bonus = 1 + (0.466 # 草伤杯 
                           + 0.15 # 草套2件套效果 
                           + min((base_elem_mastery - 200) * 0.001, 0.8)
                           )

    all_atk = atk_per * max_atk + atk + base_atk

    atk_bei_lv = 2.193
    elem_bei_lv = 4.386

    non_crit_score = (atk_bei_lv * all_atk + elem_bei_lv * elem_mastery) / (atk_bei_lv * base_atk + elem_bei_lv * base_elem_mastery) * elem_bonus / base_elem_bonus
    crit_score = non_crit_score * (base_crit_damage + extra_crit_damage) / base_crit_damage
    expect_crit_damage_bonus = crit_rate * (extra_crit_damage + base_crit_damage - 1)
    expect_score = non_crit_score * (1 + expect_crit_damage_bonus)
    return [expect_score, crit_score, elem_mastery, int(all_atk), round(panel_crit_rate, 3), round(crit_rate, 3), round(base_crit_damage + extra_crit_damage - 1, 3), combine]


# Main body
if __name__ == '__main__':
    find_syw(syw_s_b, find_combins, calculate_score, "na_xi_da_syw.txt")
