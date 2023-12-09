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
    return syw.atk_per == ShengYiWu.BONUS_MAX or syw.elem_mastery == ShengYiWu.ELEM_MASTERY_MAIN


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
    ju_tuan = find_syw(match_syw_callback=lambda s: match_syw(s, ShengYiWu.JU_TUAN))
    ru_lei = find_syw(match_syw_callback=lambda s: match_syw(s, ShengYiWu.RU_LEI))
    zhui_yi = find_syw(match_syw_callback=lambda s: match_syw(s, ShengYiWu.ZHUI_YI))
    jue_dou_shi = find_syw(match_syw_callback=lambda s: match_syw(s, ShengYiWu.JUE_DOU_SHI))
    shi_jin = find_syw(match_syw_callback=lambda s: match_syw(s, ShengYiWu.SHI_JIN))

    ju_tuan_2_combins = list(itertools.combinations(ju_tuan, 2))
    ju_tuan_4_combins = list(itertools.combinations(ju_tuan, 4))
    ru_lei_combins = list(itertools.combinations(ru_lei, 2))
    zhui_yi_combins = list(itertools.combinations(zhui_yi, 2))
    jue_dou_shi_combins = list(itertools.combinations(jue_dou_shi, 2))
    shi_jin_combins = list(itertools.combinations(shi_jin, 4))

    all_combins_2 = ju_tuan_2_combins + ru_lei_combins + zhui_yi_combins + jue_dou_shi_combins
    all_combins = [(l[0] + l[1])
                   for l in list(itertools.combinations(all_combins_2, 2))] + ju_tuan_4_combins + shi_jin_combins
    
    return all_combins


def calculate_score_callback(combine):
    max_atk = 852 #绝弦754， 最初的大魔术852
    base_atk = int(max_atk * (1 + 0.24)) + 311      # 突破加成0.24
    mo_shu_crit_damage = 0.662
    base_crit_damage = 1 + 0.5 + mo_shu_crit_damage
    base_elem_mastery = 0 #165 # 绝弦
    wan_ye_bonus = 0.4
    base_elem_bonus = 1 + wan_ye_bonus

    crit_rate = sum([p.crit_rate for p in combine]) + 0.05
    crit_rate = round(crit_rate, 3)
    if crit_rate < 0.65:
        return None

    atk = sum([p.atk for p in combine])
    atk_per = sum([p.atk_per for p in combine])
    extra_crit_damage = sum([p.crit_damage for p in combine])
    extra_elem_bonus = sum([p.elem_bonus for p in combine])
    elem_mastery = sum([p.elem_mastery for p in combine]) + base_elem_mastery

    elem_mastery = round(elem_mastery, 1)
    if elem_mastery < 100:
        return None
    
    syw_names = [p.name for p in combine]
    # print(syw_names)
    name_count = {i: syw_names.count(i) for i in syw_names}
    # print(name_count)
    for n in name_count:
        if name_count[n] < 2:  # 散件不计算套装效果
            continue

        # print(n)
        if n == ShengYiWu.RU_LEI:
            extra_elem_bonus += 0.15
        elif n == ShengYiWu.ZHUI_YI:
            atk_per += 0.18
        elif n == ShengYiWu.JUE_DOU_SHI:
            atk_per += 0.18
        elif n == ShengYiWu.JU_TUAN:
            extra_elem_bonus += 0.2
            if name_count[n] >= 4:
                extra_elem_bonus += 0.25 + 0.25
        elif n == ShengYiWu.SHI_JIN:
            elem_mastery += 80 + 100
            atk_per += 0.14

    all_atk = int(atk_per * max_atk) + atk + base_atk
    e_bonus = base_elem_bonus + extra_elem_bonus
    crit_damage = base_crit_damage + extra_crit_damage

    e_damage = all_atk * 178 / 100 * e_bonus
    e_damage_crit = e_damage * crit_damage
    e_damage_expect = calc_expect_score(e_damage, crit_rate, crit_damage)
    return [e_damage_expect, e_damage_crit, elem_mastery, int(all_atk), round(crit_rate, 3), round(crit_damage - 1, 3), combine]


result_description = ["总评分", "期望伤害评分", "暴击伤害评分", "精通", "实战攻击力", "暴击率", "暴击伤害", "圣遗物组合"]

def find_syw_for_fei_xie_er():
    return calculate_score(find_combine_callback=find_combins_callback,
                    match_sha_callback=match_sha_callback,
                    match_bei_callback=match_bei_callback,
                    calculate_score_callbak=calculate_score_callback,
                    result_txt_file="fei_xie_er_syw.txt",
                    result_description=result_description)

# Main body
if __name__ == '__main__':
    find_syw_for_fei_xie_er()