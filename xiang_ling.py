#!/user/bin/env python3 -tt
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

import sys
import os
import logging
import itertools
from base_syw import ShengYiWu, calculate_score, find_syw, calc_expect_score


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


def calculate_score_callback(combine: list[ShengYiWu]):
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

    for p in combine:
        crit_rate += p.crit_rate
        crit_damage += p.crit_damage
        elem_mastery += p.elem_mastery
        elem_bonus += p.elem_bonus
        atk += p.atk
        atk_per += p.atk_per
        energy_recharge += p.energe_recharge

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
    crit_score = non_crit_score * crit_damage / base_crit_damage
    expect_score = calc_expect_score(non_crit_score, crit_rate, crit_damage)

    panel_crit_rate = crit_rate - sum(extra_crit_rate.values())
    return [expect_score, crit_score, elem_mastery, int(all_atk), int(panel_atk), 
            round(panel_crit_rate, 3), round(crit_damage - 1, 3), round(energy_recharge, 1), combine]


result_description = ["总评分", "期望伤害评分", "暴击伤害评分", "元素精通", "实战攻击力", "双火面板攻击力", "面板暴击率", "暴击伤害", "充能效率", "圣遗物组合"]


def find_syw_for_xiang_ling():
    return calculate_score(find_combine_callback=find_combins_callback,
                    match_sha_callback=match_sha_callback,
                    match_bei_callback=match_bei_callback,
                    calculate_score_callbak=calculate_score_callback,
                    result_txt_file="xiang_ling_syw.txt",
                    result_description=result_description)

# Main body
if __name__ == '__main__':
    find_syw_for_xiang_ling()