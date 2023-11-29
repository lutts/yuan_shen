#!/user/bin/env python3 -tt
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

import sys
import os
import logging
import itertools
from base_syw import ShengYiWu, calculate_score, find_syw, set_score_threshold


def match_sha_callback(syw: ShengYiWu):
    return syw.energe_recharge == ShengYiWu.ENERGE_RECHARGE_MAX 


def match_bei_callback(syw: ShengYiWu):
    return syw.elem_type == ShengYiWu.ELEM_TYPE_LEI


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
    base_atk = 184  # 81级
    wu_qi_atk = 674
    bai_zhi_atk = base_atk + wu_qi_atk

    extra_crit_rate = {
        "天空之翼": 0.221
    }

    extra_crit_damage = {
        "天空之翼": 0.2,
        "吃自已六命加成": 0.6,
    }

    extra_atk = {
        "自已攻击力加成": int(bai_zhi_atk * 0.86)
    }

    extra_atk_per = {
        "突破加成": 0.24
    }

    extra_energe_recharge = {
        "绝缘2件套": 0.2,
    }

    crit_rate = 0.05 + sum(extra_crit_rate.values())
    crit_damage = 1 + 0.5 + sum(extra_crit_damage.values())
    atk = 311 + sum(extra_atk.values())
    atk_per = sum(extra_atk_per.values())
    elem_bonus = 0
    energe_recharge = 1 + sum(extra_energe_recharge.values())

    for p in combine:
        crit_rate += p.crit_rate
        crit_damage += p.crit_damage
        atk += p.atk
        atk_per += p.atk_per
        elem_bonus += p.elem_bonus
        energe_recharge += p.energe_recharge

    crit_rate = round(crit_rate, 3)
    if crit_rate < 0.6:
        return None
    
    energe_recharge *= 100
    energe_recharge = round(energe_recharge, 1)
    if energe_recharge < 220:
        return None
    
    all_atk = int(bai_zhi_atk * (1 + atk_per)) + atk
    elem_bonus += min(energe_recharge / 4 / 100, 0.75)

    e_damage = all_atk * 251.5 / 100 * elem_bonus * 1.3  # EZ
    q_damage = all_atk * (778.2 + 64.8 * 6) / 100 * elem_bonus

    all_damage = e_damage + q_damage
    crit_score = all_damage * crit_damage
    expect_score = all_damage * (1 + crit_rate * (crit_damage - 1))

    panel_atk = all_atk - sum(extra_atk.values())
    panel_crit_damage = crit_damage - 1 - sum(extra_crit_damage.values()) + extra_crit_damage["天空之翼"]
    return [expect_score, crit_score, int(panel_atk), crit_rate, round(panel_crit_damage, 3), energe_recharge, combine]
    

result_description = ["总评分", "期望伤害评分", "暴击伤害评分", "攻击力", "暴击率", "暴击伤害", "充能效率", "圣遗物组合"]


def find_syw_for_jiu_tiao_sha_luo():
    return calculate_score(find_combine_callback=find_combins_callback,
                    match_sha_callback=match_sha_callback,
                    match_bei_callback=match_bei_callback,
                    calculate_score_callbak=calculate_score_callback,
                    result_txt_file="jiu_tiao_sha_luo_syw.txt",
                    result_description=result_description)

# Main body
if __name__ == '__main__':
    set_score_threshold(1.7)
    find_syw_for_jiu_tiao_sha_luo()
    