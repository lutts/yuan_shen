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
    # or syw.atk_per == ShengYiWu.BONUS_MAX or syw.elem_mastery == ShengYiWu.ELEM_MASTERY_MAIN
    return syw.elem_type == ShengYiWu.ELEM_TYPE_CAO


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
    shi_jin = find_syw(
        match_syw_callback=lambda s: match_syw(s, ShengYiWu.SHI_JIN))
    yue_tuan = find_syw(
        match_syw_callback=lambda s: match_syw(s, ShengYiWu.YUE_TUAN))
    shen_lin = find_syw(
        match_syw_callback=lambda s: match_syw(s, ShengYiWu.SHEN_LIN))

    shi_jin_2 = list(itertools.combinations(shi_jin, 2))
    shi_jin_4 = list(itertools.combinations(shi_jin, 4))
    yue_tuan_2 = list(itertools.combinations(yue_tuan, 2))
    shen_lin_2 = list(itertools.combinations(shen_lin, 2))

    all_combines_2 = shi_jin_2 + yue_tuan_2 + shen_lin_2

    return [(l[0] + l[1])
            for l in list(itertools.combinations(all_combines_2, 2))] + shi_jin_4


def calculate_score_callback(combine):
    max_atk = 841
    na_xi_da_zhuan_wu_elem_mastery = 40
    base_elem_mastery = na_xi_da_zhuan_wu_elem_mastery + (50 + 50  # 双草共鸣
                                                          + 76  # 圣显
                                                          )
    base_atk = max_atk + 311
    base_crit_damage = 1 + 0.5
    base_elem_bonus = 1 + (0.288  # 等级突破
                           + 0.12  # 波波刀
                           )

    elem_mastery = sum([p.elem_mastery for p in combine]) + base_elem_mastery
    crit_rate = sum([p.crit_rate for p in combine]) + 0.05 + 0.331  # 波波刀

    if crit_rate < 0.65:
        return None
    
    syw_names = [p.name for p in combine]
    # print(syw_names)
    name_count = {i: syw_names.count(i) for i in syw_names}
    # print(name_count)
    for n in name_count:
        if name_count[n] < 2:  # 散件不计算套装效果
            continue

        # print(n)
        if n == ShengYiWu.SHI_JIN:
            if name_count[n] == 2:
                elem_mastery += 80
            else:
                
            hp_per += 0.2
        elif n == ShengYiWu.SHUI_XIAN:
            extra_water_bonus += 0.15
        elif n == ShengYiWu.QIAN_YAN:
            hp_per += 0.2
        elif n == ShengYiWu.CHEN_LUN:
            extra_water_bonus += 0.15

    atk = sum([p.atk for p in combine])
    atk_per = sum([p.atk_per for p in combine])
    extra_crit_damage = sum([p.crit_damage for p in combine])

    elem_bonus = base_elem_bonus + min((elem_mastery - 200) * 0.001, 0.8)

    all_atk = atk_per * max_atk + atk + base_atk
    crit_damage = base_crit_damage + extra_crit_damage

    atk_bei_lv = 2.193
    elem_bei_lv = 4.386

    non_crit_score = atk_bei_lv * all_atk + elem_bei_lv * elem_mastery * elem_bonus
    crit_score = non_crit_score * crit_damage
    expect_score = non_crit_score * (1 + crit_rate * (crit_damage - 1))
    return [expect_score, crit_score, elem_mastery, int(all_atk), round(panel_crit_rate, 3), round(crit_rate, 3), round(crit_damage - 1, 3), combine]


def find_syw_for_ai_er_hai_seng():
    return calculate_score(find_combine_callback=find_combins_callback,
                           match_sha_callback=match_sha_callback,
                           match_bei_callback=match_bei_callback,
                           calculate_score_callbak=calculate_score_callback,
                           result_txt_file="ai_er_hai_seng_syw.txt")


# Main body
if __name__ == '__main__':
    find_syw_for_ai_er_hai_seng()
