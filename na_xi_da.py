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

def calculate_score_callback(combine : list[ShengYiWu]):
    wu_qi_atk = 542
    base_atk = 299
    bai_zhi_atk = wu_qi_atk + base_atk

    wu_qi_elem_mastery = 265
    tu_po_elem_mastery = 115
    ming_4_min_elem_mastery = 100
    q_extra_elem_mastery = 243  # 固有天赋，阿忍带圣显，四饰金加的150可以被纳西妲大招转化
    sheng_xian_elem_mastery = 76    # 久岐圣显

    shen_lin_elem_bonus = 0.15      # 草套2件套效果
    ming_1_elem_bonus = 0.316       # 1命
    wu_qi_elem_bonus = 0.3          # 专武

    panel_crit_rate = 0.05
    crit_damage = 1 + 0.5
    elem_mastery = wu_qi_elem_mastery + tu_po_elem_mastery + ming_4_min_elem_mastery + q_extra_elem_mastery + sheng_xian_elem_mastery
    panel_elem_mastery = wu_qi_elem_mastery + tu_po_elem_mastery
    elem_bonus = shen_lin_elem_bonus + ming_1_elem_bonus + wu_qi_elem_bonus
    atk = 311
    atk_per = 0
    energy_recharge = 0

    for p in combine:
        panel_crit_rate += p.crit_rate
        crit_damage += p.crit_damage
        elem_mastery += p.elem_mastery
        panel_elem_mastery += p.elem_mastery
        elem_bonus += p.elem_bonus
        atk += p.atk
        atk_per += p.atk_per
        energy_recharge += p.energe_recharge

    crit_rate = panel_crit_rate + + min((elem_mastery - 200) * 0.0003, 0.24)
    if crit_rate < 0.64:
        return None
    
    elem_bonus += min((elem_mastery - 200) * 0.001, 0.8)
    all_atk = int(bai_zhi_atk * (1 + atk_per)) + atk
    energy_recharge = (energy_recharge + 1) * 100

    non_crit_score = (all_atk * 2.193 + elem_mastery * 4.386) * elem_bonus
    crit_score = non_crit_score * crit_damage
    expect_score = non_crit_score * (1 + crit_rate * (crit_damage - 1))
    return [expect_score, crit_score, elem_mastery, panel_elem_mastery, int(all_atk), round(panel_crit_rate, 3), round(crit_rate, 3), round(crit_damage - 1, 3), round(energy_recharge, 3), combine]

def find_syw_for_na_xi_da():
    return calculate_score(find_combine_callback=find_combins_callback,
                    match_sha_callback=match_sha_callback,
                    match_bei_callback=match_bei_callback,
                    calculate_score_callbak=calculate_score_callback,
                    result_txt_file="na_xi_da_syw.txt")


# Main body
if __name__ == '__main__':
    find_syw_for_na_xi_da()