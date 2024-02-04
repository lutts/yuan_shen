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
from base_syw import ShengYiWu, ShengYiWu_Score, calculate_score, Syw_Combine_Desc, find_syw_combine

use_lie_ren = False

def calculate_score_callback(score_data: ShengYiWu_Score):
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
    }

    if use_lie_ren:
        extra_elem_bonus["水神增伤"] = 1.24

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

    combine = score_data.syw_combine

    for p in combine:
        crit_rate += p.crit_rate
        crit_damage += p.crit_damage
        atk += p.atk
        atk_per += p.atk_per
        hp += p.hp
        hp_per += p.hp_percent
        elem_bonus += p.elem_bonus
        elem_mastery += p.elem_mastery

    elem_mastery = round(elem_mastery, 1)
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

    crit_rate = round(crit_rate, 3)
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
    score_data.damage_to_score(az_damage, crit_rate, crit_damage)
    score_data.custom_data = [panel_hp, elem_mastery, int(all_atk), round(crit_rate, 3), round(crit_damage - 1, 3)]

    return True


result_description = ["面板生命值上限", "元素精通", "实战攻击力", "暴击率(猎人叠满)", "暴击伤害"]


def match_sha_callback(syw: ShengYiWu):
    return syw.hp_percent ==  ShengYiWu.BONUS_MAX or syw.elem_mastery == ShengYiWu.ELEM_MASTERY_MAIN


def match_bei_callback(syw: ShengYiWu):
    return syw.elem_type == Ys_Elem_Type.HUO or syw.hp_percent == ShengYiWu.BONUS_MAX

def match_tou_callback(syw: ShengYiWu):
    return syw.crit_rate == ShengYiWu.CRIT_RATE_MAIN or syw.crit_damage == ShengYiWu.CRIT_DAMAGE_MAIN


def get_raw_score_list():
    set2_names = [ShengYiWu.ZHUI_YI, ShengYiWu.JUE_DOU_SHI]
    if use_lie_ren:
        set2_names.append(ShengYiWu.LIE_REN)
    combine_desc_lst = Syw_Combine_Desc.any_2p2(set2_names)

    combine_desc_lst.append(Syw_Combine_Desc(set1_name=ShengYiWu.ZHUI_YI, set1_num=4))
    if use_lie_ren:
        combine_desc_lst.append(Syw_Combine_Desc(set1_name=ShengYiWu.LIE_REN, set1_num=4))

    raw_score_list = find_syw_combine(combine_desc_lst,
                                      match_sha_callback=match_sha_callback,
                                      match_bei_callback=match_bei_callback,
                                      match_tou_callback=match_tou_callback)
    print(len(raw_score_list))
    return raw_score_list
    

def find_syw_for_hu_tao():
    global use_lie_ren
    use_lie_ren = False

    return calculate_score(get_raw_score_list(),
                    calculate_score_callbak=calculate_score_callback,
                    result_txt_file="hu_tao_syw_no_lie_ren.txt",
                    result_description=result_description)

def find_syw_for_hu_tao_lie_ren():
    global use_lie_ren
    use_lie_ren = True

    return calculate_score(get_raw_score_list(),
                    calculate_score_callbak=calculate_score_callback,
                    result_txt_file="hu_tao_syw_lie_ren.txt",
                    result_description=result_description)

# Main body
if __name__ == '__main__':
    find_syw_for_hu_tao()