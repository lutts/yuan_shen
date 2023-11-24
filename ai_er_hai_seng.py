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


def calculate_score_callback(combine : list[ShengYiWu]):
    base_atk = 314
    wu_qi_atk = 608 # 波波刀
    bai_zhi_atk = base_atk + wu_qi_atk
    na_xi_da_zhuan_wu_elem_mastery = 40
    shuang_cao_elem_mastery = 50 + 50   # 双草共鸣
    sheng_xian_mastery = 76 # 久岐忍圣显
    base_elem_bonus = 1 + 0.288  # 等级突破
    bo_bo_dao_bonus = 0.12
    bo_bo_dao_a_bonus = 2 * 0.2     # 波波刀2层
    bo_bo_dao_crit_rate = 0.331

    crit_rate = 0.05 + bo_bo_dao_crit_rate
    crit_damage = 1 + 0.5
    elem_mastery = na_xi_da_zhuan_wu_elem_mastery + shuang_cao_elem_mastery + sheng_xian_mastery
    panel_elem_mastery = 0
    atk = 311
    atk_per = 0
    elem_bonus = base_elem_bonus + bo_bo_dao_bonus

    for p in combine:
        crit_rate += p.crit_rate
        crit_damage += p.crit_damage
        elem_mastery += p.elem_mastery
        panel_elem_mastery += p.elem_mastery
        atk += p.atk
        atk_per += p.atk_per
        elem_bonus += p.elem_bonus

    crit_rate = round(crit_rate, 3)
    if crit_rate < 0.65:
        return None
    
    panel_atk_per = atk_per
    
    syw_names = [p.name for p in combine]
    # print(syw_names)
    name_count = {i: syw_names.count(i) for i in syw_names}
    # print(name_count)
    for n in name_count:
        if name_count[n] < 2:  # 散件不计算套装效果
            continue

        # print(n)
        if n == ShengYiWu.SHI_JIN:
            elem_mastery += 80
            panel_elem_mastery += 80
            if name_count[n] >= 4:
                atk_per += 0.14
                elem_mastery += 50 + 50
        elif n == ShengYiWu.YUE_TUAN:
            elem_mastery += 80
            panel_elem_mastery += 80
        elif n == ShengYiWu.SHEN_LIN:
            elem_bonus += 0.15
    
    # 固有天赋2
    elem_bonus += min(elem_mastery * 0.001, 1)
    
    a_elem_bonus = elem_bonus + bo_bo_dao_a_bonus
    all_atk = int(bai_zhi_atk * (1 + atk_per)) + atk
    panel_atk = int(bai_zhi_atk * (1 + panel_atk_per)) + atk

    # 以下计算基于以下手法
    # Q 切久岐忍e 再切回海哥 aaa闪 aaa e aaa闪 aaa z aaa aaa，共计六发满层光幕攻击
    # 波波刀的普攻增伤需要海哥e之后才有，能覆盖开e后续所有的平A
    q_damage = (all_atk * 218.9 / 100 + elem_mastery * 175.1 / 100) * elem_bonus

    aaa_damage = all_atk * (91 + 93.2 + 62.8 + 62.8) / 100
    z_damage = all_atk * (101.5 + 101.5) / 100

    e_damage = (all_atk * 3.485 / 100 + elem_mastery * 2.788 / 100) * elem_bonus
    guang_mu_damage = (all_atk * 121 / 100 + elem_mastery * 241.9 / 100) * 3 * elem_bonus * 6  # 六剑雨

    non_crit_score = q_damage + 2 * aaa_damage * elem_bonus + e_damage + z_damage + 4 * aaa_damage * a_elem_bonus + guang_mu_damage
    crit_score = non_crit_score * crit_damage
    expect_score = non_crit_score * (1 + crit_rate * (crit_damage - 1))

    return [expect_score, crit_score, elem_mastery, panel_elem_mastery, int(panel_atk), round(crit_rate, 3), round(crit_damage - 1, 3), combine]


def find_syw_for_ai_er_hai_seng():
    return calculate_score(find_combine_callback=find_combins_callback,
                           match_sha_callback=match_sha_callback,
                           match_bei_callback=match_bei_callback,
                           calculate_score_callbak=calculate_score_callback,
                           result_txt_file="ai_er_hai_seng_syw.txt")


# Main body
if __name__ == '__main__':
    find_syw_for_ai_er_hai_seng()
