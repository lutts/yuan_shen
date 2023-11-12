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


def calculate_score_callback(combine):
    ling_hua_max_atk = 1016
    base_atk = int(ling_hua_max_atk * (1
                                   + 0.2  # 宗室
                                   + 0.2  # 千岩
                                   + 0.48  # 讨龙
                                   )) + 311  # 羽毛
    base_crit_damage = 1 + (0.441  # 雾切
                            + 0.884 # 突破加成
                            )
    wu_qie_bonus = 0.12 + 0.28
    wan_ye_bonus = 0.4
    shui_shen_bonus = 0 #1.24
    base_elem_bonus = 1 + wu_qie_bonus + wan_ye_bonus + shui_shen_bonus

    crit_rate = sum([p.crit_rate for p in combine]) + 0.05
    if crit_rate < 0.4:
        return None
    
    real_crit_rate = crit_rate + (0.15 # 双冰
                                  + 0.2 # 四件套效果之一
                                )

    atk = sum([p.atk for p in combine])
    atk_per = sum([p.atk_per for p in combine])
    extra_crit_damage = sum([p.crit_damage for p in combine])
    extra_elem_bonus = sum([p.elem_bonus for p in combine])
    total_energe_recharge = (
        sum([p.energe_recharge for p in combine]) + 1) * 100

    if total_energe_recharge < 116.5:
        return None

    # 出战时总攻击力
    all_atk = atk_per * ling_hua_max_atk + atk + base_atk
    # 非出战时面板攻击力
    panel_atk = (1 + atk_per) * ling_hua_max_atk + atk + 311

    non_crit_score = all_atk / base_atk * (base_elem_bonus + extra_elem_bonus) / base_elem_bonus
    crit_score = non_crit_score * (base_crit_damage + extra_crit_damage) / base_crit_damage
    expect_crit_damage_bonus = real_crit_rate * (extra_crit_damage + base_crit_damage - 1)
    expect_score = non_crit_score * (1 + expect_crit_damage_bonus)
    return [expect_score, crit_score, int(panel_atk), round(crit_rate, 3), round(base_crit_damage + extra_crit_damage - 1, 3), round(total_energe_recharge, 1), combine]


# Main body
if __name__ == '__main__':
    calculate_score(find_combine_callback=find_combins_callback,
                    match_sha_callback=match_sha_callback,
                    match_bei_callback=match_bei_callback,
                    calculate_score_callbak=calculate_score_callback,
                    result_txt_file="ling_hua_syw.txt")
