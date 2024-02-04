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
    base_atk = 342
    wu_qi_atk = 674
    bai_zhi_atk = base_atk + wu_qi_atk

    extra_atk_per = {
        "宗室": 0.2,
        "千岩":  0.2,
        "讨龙": 0.48,
    }

    extra_crit_damage = {
        "雾切": 0.441,
    }

    extra_elem_bonus = {
        "雾切": 0.12 + 0.28,
        "万叶": 0.4,
        "水神": 0, #1.24,
    }

    crit_rate = 0.05
    crit_damage = 1 + 0.884 + sum(extra_crit_damage.values())
    base_crit_damage = crit_damage
    atk = 311
    atk_per = sum(extra_atk_per.values())
    energy_recharge = 1
    elem_bonus = 1 + sum(extra_elem_bonus.values())
    base_elem_bonus = elem_bonus

    combine = score_data.syw_combine

    for p in combine:
        crit_rate += p.crit_rate
        crit_damage += p.crit_damage
        atk += p.atk
        atk_per += p.atk_per
        energy_recharge += p.energy_recharge
        elem_bonus += p.elem_bonus

    crit_rate = round(crit_rate, 3)
    if crit_rate < 0.4 or crit_rate > 0.5:
        return None
    
    energy_recharge *= 100
    energy_recharge = round(energy_recharge, 1)
    if energy_recharge <= 116.5:
        return None
    
    real_crit_rate = crit_rate + (0.15 # 双冰
                                  + 0.2 # 四件套效果之一，这是假设怪是冻不住的，因为盵不到另外0.2
                                )

    # 出战时总攻击力
    all_atk = int(bai_zhi_atk * (1 + atk_per)) + atk
    # 非出战时面板攻击力
    panel_atk = int(bai_zhi_atk * (1 + atk_per - sum(extra_atk_per.values()))) + atk

    base_atk = int(bai_zhi_atk * (1 + sum(extra_atk_per.values()))) + 311
    non_crit_score = all_atk / base_atk * elem_bonus / base_elem_bonus

    score_data.crit_score = non_crit_score * crit_damage / base_crit_damage
    score_data.expect_score = calc_expect_damage(non_crit_score, real_crit_rate, crit_damage)
    score_data.custom_data = [int(panel_atk), round(crit_rate, 3), round(crit_damage - 1, 3), round(energy_recharge, 1)]

    return True


result_description = ["面板攻击力", "暴击率", "暴击伤害", "充能效率"]

def match_sha_callback(syw: ShengYiWu):
    return syw.atk_per == ShengYiWu.BONUS_MAX


def match_bei_callback(syw: ShengYiWu):
    return syw.atk_per == ShengYiWu.BONUS_MAX or syw.elem_type == Ys_Elem_Type.BING

def match_tou_callback(syw: ShengYiWu):
    return syw.crit_rate == ShengYiWu.CRIT_RATE_MAIN or syw.crit_damage == ShengYiWu.CRIT_DAMAGE_MAIN

def find_syw_for_ling_hua():
    raw_score_list = find_syw_combine([Syw_Combine_Desc(set1_name=ShengYiWu.BING_TAO, set1_num=4)],
                                      match_sha_callback=match_sha_callback,
                                      match_bei_callback=match_bei_callback,
                                      match_tou_callback=match_tou_callback)
    print(len(raw_score_list))

    return calculate_score(raw_score_list,
                           calculate_score_callbak=calculate_score_callback,
                           result_txt_file="ling_hua_syw.txt",
                           result_description=result_description)

# Main body
if __name__ == '__main__':
    find_syw_for_ling_hua()