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

ming_zuo_num = 1

def calculate_score_callback(score_data: ShengYiWu_Score):
    base_hp = 14695

    extra_elem_bonus = {
        "水神q增伤": 300 * 0.0025,
        "万叶": 0.4,
        "专武": 0.14 * 3, 
        "固有天赋": 0.15 # 至高仲裁是纪律，不过基本吃不满
    }

    extra_crit_damage = {
        "专武": 0.882,
    }

    if  ming_zuo_num >= 2:
        extra_crit_damage["二命"] = 0.42

    extra_hp_bonus = {
        "专武": 0.16,
    }

    crit_rate = 0.05
    crit_damage = 1 + 0.5 + sum(extra_crit_damage.values())
    hp = 0
    hp_per = sum(extra_hp_bonus.values())
    elem_bonus = 1 + sum(extra_elem_bonus.values())
    energy_recharge = 1

    combine = score_data.syw_combine

    for p in combine:
        crit_rate += p.crit_rate
        crit_damage += p.crit_damage
        hp += p.hp
        hp_per += p.hp_percent
        elem_bonus += p.elem_bonus
        energy_recharge += p.energy_recharge

    energy_recharge *= 100
    energy_recharge = round(energy_recharge, 1)
    if energy_recharge < 110:
        return None
    
    panel_crit_rate = round(crit_rate, 3)

    syw_names = [p.name for p in combine]
    # print(syw_names)
    name_count = {i: syw_names.count(i) for i in syw_names}
    # print(name_count)
    for n in name_count:
        if name_count[n] < 2:  # 散件不计算套装效果
            continue

        if n == ShengYiWu.LIE_REN:
            crit_rate += 0.36
        elif n == ShengYiWu.YUE_TUAN:
            elem_bonus += 0.35

    crit_rate = round(crit_rate, 3)
    if crit_rate < 0.7:
        return None
    
    all_hp = int(base_hp * (1 + hp_per)) + hp + 4780

    non_crit_score = all_hp * 14.47 / 100 * elem_bonus

    score_data.damage_to_score(non_crit_score, crit_rate, crit_damage)

    score_data.custom_data = [all_hp, panel_crit_rate, crit_rate, round(crit_damage - 1, 3), energy_recharge]

    return True


result_description = ["生命值", "面板暴击率", "实战暴击率", "暴击伤害", "充能效率"]

def match_sha_callback(syw: ShengYiWu):
    return syw.hp_percent == 0.466 or syw.energy_recharge == ShengYiWu.ENERGY_RECHARGE_MAX


def match_bei_callback(syw: ShengYiWu):
    return syw.hp_percent == 0.466 or syw.elem_type == Ys_Elem_Type.SHUI


def match_tou_callback(syw: ShengYiWu):
    return syw.crit_rate == ShengYiWu.CRIT_RATE_MAIN or syw.crit_damage == ShengYiWu.CRIT_DAMAGE_MAIN or syw.hp_percent == ShengYiWu.BONUS_MAX


def find_syw_for_na_wei_lai_te():
    combine_desc_lst = [
        Syw_Combine_Desc(set1_name=ShengYiWu.YUE_TUAN, set1_num=4),
        Syw_Combine_Desc(set1_name=ShengYiWu.LIE_REN, set1_num=4),
    ]

    raw_score_list = find_syw_combine(combine_desc_lst,
                                      match_sha_callback=match_sha_callback,
                                      match_bei_callback=match_bei_callback,
                                      match_tou_callback=match_tou_callback)
    print(len(raw_score_list))

    return calculate_score(raw_score_list,
                           calculate_score_callbak=calculate_score_callback,
                           result_txt_file="na_wei_lai_te_syw.txt",
                           result_description=result_description)


# Main body
if __name__ == '__main__':
    find_syw_for_na_wei_lai_te()
