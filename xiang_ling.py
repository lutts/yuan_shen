#!/user/bin/env python3 -tt
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

import sys
import os
import logging
import itertools

from ys_basic import Ys_Elem_Type
from base_syw import ShengYiWu, ShengYiWu_Score, calculate_score, Syw_Combine_Desc, find_syw_combine, calc_expect_damage


def calculate_score_callback(score_data: ShengYiWu_Score):
    base_atk = 225
    wu_qi_atk = 510
    bai_zhi_atk = base_atk + wu_qi_atk

    extra_atk = {
        "班尼特": int(755 * 1.19),
        "双火": int(bai_zhi_atk * 0.25),
    }

    extra_energy_recharge = {
        "渔获": 0.459,
        "绝缘2件套": 0.2,
    }

    extra_elem_bonus = {
        "万叶": 0, #0.4,
        "夜兰平均增伤": 0.29,
        "雷神e": 0.003 * 80
    }

    extra_crit_rate = {
        "渔获": 0.12,
    }

    crit_rate = 0.05 + sum(extra_crit_rate.values())
    crit_damage = 1 + 0.5
    base_crit_damage = crit_damage
    elem_mastery = 96
    elem_bonus = 1 + sum(extra_elem_bonus.values())
    base_elem_bonus = elem_bonus
    atk = 311 + sum(extra_atk.values())
    atk_per = 0
    energy_recharge = 1 + sum(extra_energy_recharge.values())

    combine = score_data.syw_combine

    for p in combine:
        crit_rate += p.crit_rate
        crit_damage += p.crit_damage
        elem_mastery += p.elem_mastery
        elem_bonus += p.elem_bonus
        atk += p.atk
        atk_per += p.atk_per
        energy_recharge += p.energy_recharge

    crit_rate = round(crit_rate, 3)
    if crit_rate < 0.6:
        return None
    
    elem_mastery = round(elem_mastery, 1)
    if elem_mastery < 180:
        return None
    
    energy_recharge *= 100
    energy_recharge = round(energy_recharge, 1)
    if energy_recharge < 230:
        return None
    
    elem_bonus += min(energy_recharge / 4 / 100, 0.75)

    all_atk = int(bai_zhi_atk * (1 + atk_per)) + atk
    panel_atk = all_atk - sum(extra_atk.values()) + extra_atk["双火"]

    base_atk = bai_zhi_atk + 311 + sum(extra_atk.values())
    non_crit_score = all_atk / base_atk * elem_bonus / base_elem_bonus

    score_data.crit_score = non_crit_score * crit_damage / base_crit_damage
    score_data.expect_score = calc_expect_damage(non_crit_score, crit_rate, crit_damage)

    panel_crit_rate = crit_rate - sum(extra_crit_rate.values())
    score_data.custom_data = [elem_mastery, int(all_atk), int(panel_atk), 
            round(panel_crit_rate, 3), round(crit_damage - 1, 3), round(energy_recharge, 1)]
    
    return True


result_description = ["元素精通", "实战攻击力", "双火面板攻击力", "面板暴击率", "暴击伤害", "充能效率"]


def match_sha_callback(syw: ShengYiWu):
    return syw.energy_recharge == ShengYiWu.ENERGY_RECHARGE_MAX


def match_bei_callback(syw: ShengYiWu):
    return syw.elem_type == Ys_Elem_Type.HUO # or syw.atk_per == ShengYiWu.BONUS_MAX


def match_tou_callback(syw: ShengYiWu):
    return syw.crit_rate == ShengYiWu.CRIT_RATE_MAIN or syw.crit_damage == ShengYiWu.CRIT_DAMAGE_MAIN


def find_syw_for_xiang_ling():
    raw_score_list = find_syw_combine([Syw_Combine_Desc(set1_name=ShengYiWu.JUE_YUAN, set1_num=4)],
                                      match_sha_callback=match_sha_callback,
                                      match_bei_callback=match_bei_callback,
                                      match_tou_callback=match_tou_callback)
    print(len(raw_score_list))

    return calculate_score(raw_score_list,
                           calculate_score_callbak=calculate_score_callback,
                           result_txt_file="xiang_ling_syw.txt",
                           result_description=result_description)

# Main body
if __name__ == '__main__':
    find_syw_for_xiang_ling()