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
    return syw.elem_mastery == ShengYiWu.ELEM_MASTERY_MAIN


def match_bei_callback(syw: ShengYiWu):
    return syw.elem_type == ShengYiWu.ELEM_TYPE_CAO # or syw.atk_per == ShengYiWu.BONUS_MAX or syw.elem_mastery == ShengYiWu.ELEM_MASTERY_MAIN


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
    shen_lin = find_syw(match_syw_callback=lambda s: match_syw(s, ShengYiWu.SHEN_LIN))
    return list(itertools.combinations(shen_lin, 4))


def calculate_score_callback(combine):
    max_atk = 841
    base_elem_mastery = 265 + 115 + (100  # 专武，突破精通提升，四命
                               + 243  # 固有天赋，阿忍带圣显，四饰金加的150可以被纳西妲大招转化
                               + 76 # 圣显
                               )
    base_atk = max_atk + 311
    base_crit_damage = 1 + 0.5
    fixed_elem_bonus = 1 + (0.466  # 草伤杯
                            + 0.15  # 草套2件套效果
                            + 0.316  # 1命
                            + 0.3 # 专武
                            )
    base_elem_bonus = fixed_elem_bonus + \
        min((base_elem_mastery - 200) * 0.001, 0.8)

    elem_mastery = sum([p.elem_mastery for p in combine]) + base_elem_mastery
    panel_elem_mastery = sum([p.elem_mastery for p in combine]) + 265 + 115
    panel_crit_rate = sum([p.crit_rate for p in combine]) + 0.05
    crit_rate = panel_crit_rate + min((elem_mastery - 200) * 0.0003, 0.24)
    if crit_rate < 0.64:
        return None

    atk = sum([p.atk for p in combine])
    atk_per = sum([p.atk_per for p in combine])
    extra_crit_damage = sum([p.crit_damage for p in combine])

    elem_bonus = fixed_elem_bonus + min((elem_mastery - 200) * 0.001, 0.8)

    total_energe_recharge = (
        sum([p.energe_recharge for p in combine]) + 1) * 100

    all_atk = atk_per * max_atk + atk + base_atk
    crit_damage = base_crit_damage + extra_crit_damage

    atk_bei_lv = 2.193
    elem_bei_lv = 4.386

    non_crit_score = (atk_bei_lv * all_atk + elem_bei_lv * elem_mastery) * elem_bonus
    crit_score = non_crit_score * crit_damage
    expect_score = non_crit_score * (1 + crit_rate * (crit_damage - 1))
    return [expect_score, crit_score, elem_mastery, panel_elem_mastery, int(all_atk), round(panel_crit_rate, 3), round(crit_rate, 3), round(crit_damage - 1, 3), round(total_energe_recharge, 3), combine]

def find_syw_for_na_xi_da():
    return calculate_score(find_combine_callback=find_combins_callback,
                    match_sha_callback=match_sha_callback,
                    match_bei_callback=match_bei_callback,
                    calculate_score_callbak=calculate_score_callback,
                    result_txt_file="na_xi_da_syw.txt")


# Main body
if __name__ == '__main__':
    find_syw_for_na_xi_da()