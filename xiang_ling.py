#!/user/bin/env python3 -tt
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

import sys
import os
import logging
import itertools
from base_syw import ShengYiWu, calculate_score, find_syw


def match_sha_callback(syw: ShengYiWu):
    return syw.energe_recharge == ShengYiWu.ENERGE_RECHARGE_MAX


def match_bei_callback(syw: ShengYiWu):
    return syw.elem_type == ShengYiWu.ELEM_TYPE_HUO # or syw.atk_per == ShengYiWu.BONUS_MAX


def match_syw(s: ShengYiWu, expect_name):
    if s.name != expect_name:
        return False

    if s.part == ShengYiWu.PART_SHA:
        return match_sha_callback(s)
    elif s.part == ShengYiWu.PART_BEI:
        return match_bei_callback(s)
    else:
        return True

def find_combins_callback():
    jue_yuan = find_syw(match_syw_callback=lambda s: match_syw(s, ShengYiWu.JUE_YUAN))
    return list(itertools.combinations(jue_yuan, 4))


def calculate_score_callback(combine):
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


def find_syw_for_xiang_ling():
    return calculate_score(find_combine_callback=find_combins_callback,
                    match_sha_callback=match_sha_callback,
                    match_bei_callback=match_bei_callback,
                    calculate_score_callbak=calculate_score_callback,
                    result_txt_file="xiang_ling_syw.txt")

# Main body
if __name__ == '__main__':
    find_syw_for_xiang_ling()