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
    return syw.atk_per == ShengYiWu.BONUS_MAX


def match_bei_callback(syw: ShengYiWu):
    return syw.atk_per == ShengYiWu.BONUS_MAX or syw.elem_type == ShengYiWu.ELEM_TYPE_BING


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
    bing_tao = find_syw(match_syw_callback=lambda s: match_syw(s, ShengYiWu.BING_TAO))
    return list(itertools.combinations(bing_tao, 4))


def calculate_score_callback(combine: list[ShengYiWu]):
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
    energe_recharge = 1
    elem_bonus = 1 + sum(extra_elem_bonus.values())
    base_elem_bonus = elem_bonus

    for p in combine:
        crit_rate += p.crit_rate
        crit_damage += p.crit_damage
        atk += p.atk
        atk_per += p.atk_per
        energe_recharge += p.energe_recharge
        elem_bonus += p.elem_bonus

    if crit_rate < 0.4:
        return None
    
    energe_recharge *= 100
    if energe_recharge <= 116.5:
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
    crit_score = non_crit_score * crit_damage / base_crit_damage
    expect_score = non_crit_score * (1 + real_crit_rate * (crit_damage - 1))
    return [expect_score, crit_score, int(panel_atk), round(elem_bonus, 3), round(crit_rate, 3), round(crit_damage - 1, 3), round(energe_recharge, 1), combine]


def find_syw_for_ling_hua():
    return calculate_score(find_combine_callback=find_combins_callback,
                    match_sha_callback=match_sha_callback,
                    match_bei_callback=match_bei_callback,
                    calculate_score_callbak=calculate_score_callback,
                    result_txt_file="ling_hua_syw.txt")

# Main body
if __name__ == '__main__':
    find_syw_for_ling_hua()