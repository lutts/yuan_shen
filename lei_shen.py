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
    return syw.atk_per == ShengYiWu.BONUS_MAX or syw.elem_type == ShengYiWu.ELEM_TYPE_LEI


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
    base_atk = 337
    wu_qi_atk = 608
    bai_zhi_atk = base_atk + wu_qi_atk

    extra_energe_recharge = {
        "绝缘2件套": 0.2,
        "薙草之稻光": 0.551,
        "薙草之稻光开大加成": 0.3,
    }

    extra_atk = {
        "班尼特": int(755 * 1.19),
        "双火": 0, # int(945 * 0.25),
        "九条": 0, # int(858 * 0.86),
    }

    extra_crit_damage = {
        "九条": 0, #0.6,
    }

    extra_elem_bonus = {
        "万叶": 0.4,
        "夜兰": 0.25,
        "水神": 0, # 1.24,
    }

    crit_rate = 0.05
    crit_damage = 1 + 0.5 + sum(extra_crit_damage.values())
    atk = sum(extra_atk.values()) + 311
    atk_per = 0
    energe_recharge = 1.32 + sum(extra_energe_recharge.values())
    elem_bonus = 1 + sum(extra_elem_bonus.values())

    for p in combine:
        crit_rate += p.crit_rate
        crit_damage += p.crit_damage
        atk += p.atk
        atk_per += p.atk_per
        energe_recharge += p.energe_recharge
        elem_bonus += p.elem_bonus

    if crit_rate < 0.6:
        return None

    energe_recharge *= 100
    panel_energe_recharge = energe_recharge - extra_energe_recharge["薙草之稻光开大加成"] * 100

    if panel_energe_recharge < 260:
        return None
    
    elem_bonus += (energe_recharge - 100) * 0.004  # 固有天赋2
    #panel_elem_bonus = elem_bonus - sum(extra_elem_bonus.values())
    elem_bonus += min(energe_recharge / 4 / 100, 0.75)

    panel_atk = int(bai_zhi_atk * (1 + atk_per)) + atk - sum(extra_atk.values()) + extra_atk["双火"]
    atk_per += min((energe_recharge - 100) * 0.0028, 0.8)
   
    all_atk = int(bai_zhi_atk * (1 + atk_per)) + atk

    # 一轮伤害：两套普攻 + 4下
    # 愿力层数：夜兰70 + 万叶60 + 班尼特60 = 190 * 0.2 = 38 * 1.2 = 45层，所有队友产球5颗就有60层
    # 雷九万班：60层肯定没问题
    # 梦想一刀：(721% + 420%=1141%)攻击力
    # 一段：79.8% + 78.6% = 158.4%
    # 二段：78.4% + 78.6% = 157%
    # 三段：96.0% + 78.6% = 174.6%
    # 四段：(55.1% + 78.6% = 133.7%) + (55.3% + 78.6% = 133.9%)
    # 五段：131.9% + 78.6% = 210.5%

    q_damage = all_atk * 1141 / 100 * elem_bonus
    q_damage_crit = q_damage * crit_damage
    q_damage_expect = q_damage * (1 + crit_rate * (crit_damage - 1))

    qa1_damage = all_atk * 158.4 / 100 * elem_bonus * 3
    qa1_damage_crit = qa1_damage * crit_damage
    qa1_damage_expect = qa1_damage * (1 + crit_rate * (crit_damage - 1))

    qa2_damage = all_atk * 157 / 100 * elem_bonus * 3
    qa2_damage_crit = qa2_damage * crit_damage
    qa2_damage_expect = qa2_damage * (1 + crit_rate * (crit_damage - 1))

    qa3_damage = all_atk * 174.6 / 100 * elem_bonus * 3
    qa3_damage_crit = qa3_damage * crit_damage
    qa3_damage_expect = qa3_damage * (1 + crit_rate * (crit_damage - 1))

    qa4_damage = all_atk * 133.7 / 100 * elem_bonus * 3 + all_atk * 133.9 / 100 * elem_bonus * 3
    qa4_damage_crit = qa4_damage * crit_damage
    qa4_damage_expect = qa4_damage * (1 + crit_rate * (crit_damage - 1))

    qa5_damage = all_atk * 210.5 / 100 * elem_bonus * 2
    qa5_damage_crit = qa5_damage * crit_damage
    qa5_damage_expect = qa5_damage * (1 + crit_rate * (crit_damage - 1))

    crit_score = q_damage_crit + qa1_damage_crit + qa2_damage_crit + qa3_damage_crit + qa4_damage_crit + qa5_damage_crit
    expect_score = q_damage_expect + qa1_damage_expect + qa2_damage_expect + qa3_damage_expect + qa4_damage_expect + qa5_damage_expect

    # expect_crit_damage_bonus = crit_rate * (extra_crit_damage + base_crit_damage - 1)

    # base_score = all_atk / base_atk * (extra_elem_bonus + base_elem_bonus) / base_elem_bonus
    # crit_score = base_score * (base_crit_damage + extra_crit_damage) / base_crit_damage
    # expect_score = base_score * (1 + expect_crit_damage_bonus)
    return [expect_score, crit_score, int(all_atk), int(panel_atk), round(crit_rate, 3), round(crit_damage - 1, 3), round(panel_energe_recharge, 1), combine]


def find_syw_for_lei_shen():
    return calculate_score(find_combine_callback=find_combins_callback,
                    match_sha_callback=match_sha_callback,
                    match_bei_callback=match_bei_callback,
                    calculate_score_callbak=calculate_score_callback,
                    result_txt_file="lei_shen_syw.txt")

# Main body
if __name__ == '__main__':
    find_syw_for_lei_shen()