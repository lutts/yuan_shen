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
    return syw.hp_percent ==  ShengYiWu.BONUS_MAX or syw.elem_mastery == ShengYiWu.ELEM_MASTERY_MAIN


def match_bei_callback(syw: ShengYiWu):
    return syw.elem_type == ShengYiWu.ELEM_TYPE_HUO or syw.hp_percent == ShengYiWu.BONUS_MAX


def match_syw(s: ShengYiWu, expect_name):
    if s.name != expect_name:
        return False

    if s.part == ShengYiWu.PART_SHA:
        return match_sha_callback(s)
    elif s.part == ShengYiWu.PART_BEI:
        return match_bei_callback(s)
    else:
        return True
    
def find_combins_callback_lie_ren():
    zhui_yi = find_syw(match_syw_callback=lambda s: match_syw(s, ShengYiWu.ZHUI_YI))
    lie_ren = find_syw(match_syw_callback=lambda s: match_syw(s, ShengYiWu.LIE_REN))
    jue_dou_shi = find_syw(match_syw_callback=lambda s: match_syw(s, ShengYiWu.JUE_DOU_SHI))

    zhui_yi_2_combins = list(itertools.combinations(zhui_yi, 2))
    zhui_yi_4_combins = list(itertools.combinations(zhui_yi, 4))

    lie_ren_2_combins = list(itertools.combinations(lie_ren, 2))
    lie_ren_4_combins = list(itertools.combinations(lie_ren, 4))

    jue_dou_shi_2_combins = list(itertools.combinations(jue_dou_shi, 2))

    all_2_combins = zhui_yi_2_combins + jue_dou_shi_2_combins + lie_ren_2_combins

    all_combins = [(l[0] + l[1])
                   for l in list(itertools.combinations(all_2_combins, 2))] + zhui_yi_4_combins + lie_ren_4_combins

    return all_combins

def find_combins_callback():
    zhui_yi = find_syw(match_syw_callback=lambda s: match_syw(s, ShengYiWu.ZHUI_YI))
    lie_ren = find_syw(match_syw_callback=lambda s: match_syw(s, ShengYiWu.LIE_REN))
    jue_dou_shi = find_syw(match_syw_callback=lambda s: match_syw(s, ShengYiWu.JUE_DOU_SHI))

    zhui_yi_2_combins = list(itertools.combinations(zhui_yi, 2))
    zhui_yi_4_combins = list(itertools.combinations(zhui_yi, 4))

    lie_ren_2_combins = [] #list(itertools.combinations(lie_ren, 2))
    lie_ren_4_combins = [] #list(itertools.combinations(lie_ren, 4))

    jue_dou_shi_2_combins = list(itertools.combinations(jue_dou_shi, 2))

    all_2_combins = zhui_yi_2_combins + jue_dou_shi_2_combins + lie_ren_2_combins

    all_combins = [(l[0] + l[1])
                   for l in list(itertools.combinations(all_2_combins, 2))] + zhui_yi_4_combins + lie_ren_4_combins

    return all_combins

def calculate_score_callback(combine: list[ShengYiWu]):
    base_hp = 15552

    base_atk = 107
    wu_qi_atk = 608 # 护摩
    bai_zhi_atk = base_atk + wu_qi_atk

    extra_crit_damage = {
        "等级突破": 0.884,
        "护摩": 0.662
    }

    extra_elem_bonus = {
        "生命低于50%时的固有天赋": 0.33,
        "夜兰平均增伤": 0.29,
        "水神增伤": 1.24,
    }

    extra_hp_bonus = {
        "护摩": 0.2,
        "双水": 0.25,
    }

    crit_rate = 0.05
    crit_damage = 1 + sum(extra_crit_damage.values())
    atk = 311
    atk_per = 0
    hp = 0
    hp_per = sum(extra_hp_bonus.values())
    elem_bonus = 1 + sum(extra_elem_bonus.values())
    elem_mastery = 0

    for p in combine:
        crit_rate += p.crit_rate
        crit_damage += p.crit_damage
        atk += p.atk
        atk_per += p.atk_per
        hp += p.hp
        hp_per += p.hp_percent
        elem_bonus += p.elem_bonus
        elem_mastery += p.elem_mastery

    if elem_mastery < 200:
        return None
    
    syw_names = [p.name for p in combine]
    # print(syw_names)
    name_count = {i: syw_names.count(i) for i in syw_names}
    # print(name_count)
    for n in name_count:
        if name_count[n] < 2:  # 散件不计算套装效果
            continue

        elif n == ShengYiWu.ZHUI_YI:
            atk_per += 0.18
            if name_count[n] >= 4:
                elem_bonus += 0.5
        elif n == ShengYiWu.JUE_DOU_SHI:
            atk_per += 0.18
        elif n == ShengYiWu.LIE_REN:
            elem_bonus += 0.15
            if name_count[n] >= 4:
                crit_rate += 0.36

    if crit_rate <= 0.65:
        return None
    
    # 按生命低于50%血时11次az的伤害计算
    panel_hp = int(base_hp * (1 + hp_per - extra_hp_bonus["双水"])) + hp + 4780
    all_hp = int(base_hp * (1 + hp_per)) + hp + 4780

    hu_mo_atk_bonus = int(all_hp * 0.018)  # 1.8%
    e_atk_bonus = int(all_hp * 0.0626)   # 6.26/5
    if e_atk_bonus >= bai_zhi_atk * 4: # 不超过基础攻击力的400%
        e_atk_bonus = bai_zhi_atk * 4
    all_atk = int(bai_zhi_atk * (1 + atk_per)) + atk + hu_mo_atk_bonus + e_atk_bonus

    # 11次az
    az_damage = all_atk * (69.3 + 200.9) / 100 * elem_bonus * 11
    az_damage_crit = az_damage * crit_damage
    az_damage_expect = az_damage * (1 + crit_rate * (crit_damage - 1))
    return [az_damage_expect, az_damage_crit, panel_hp, elem_mastery, int(all_atk), round(crit_rate, 3), round(crit_damage - 1, 3), combine]


def find_syw_for_hu_tao():
    return calculate_score(find_combine_callback=find_combins_callback,
                    match_sha_callback=match_sha_callback,
                    match_bei_callback=match_bei_callback,
                    calculate_score_callbak=calculate_score_callback,
                    result_txt_file="hu_tao_syw.txt")

def find_syw_for_hu_tao_lie_ren():
    return calculate_score(find_combine_callback=find_combins_callback_lie_ren,
                    match_sha_callback=match_sha_callback,
                    match_bei_callback=match_bei_callback,
                    calculate_score_callbak=calculate_score_callback,
                    result_txt_file="hu_tao_syw.txt")

# Main body
if __name__ == '__main__':
    find_syw_for_hu_tao()