#!/user/bin/env python3 -tt
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

import sys
import os
import logging
import itertools
from base_syw import ShengYiWu, calculate_score, find_syw, calc_expect_damage

ming_zuo_num = 1

def match_sha_callback(syw: ShengYiWu):
    return syw.hp_percent == 0.466 or syw.energy_recharge == ShengYiWu.energy_recharge_MAX


def match_bei_callback(syw: ShengYiWu):
    return syw.hp_percent == 0.466 or syw.elem_type == ShengYiWu.ELEM_TYPE_SHUI


def match_syw(s: ShengYiWu, expect_name):
    if s.name != expect_name:
        return False

    if s.part == ShengYiWu.PART_SHA:
        return match_sha_callback(s)
    elif s.part == ShengYiWu.PART_BEI:
        return match_bei_callback(s)
    else:
        return True


def find_combine_callback():
    yue_tuan = find_syw(
        match_syw_callback=lambda s: match_syw(s, ShengYiWu.YUE_TUAN))
    lie_ren = find_syw(
        match_syw_callback=lambda s: match_syw(s, ShengYiWu.LIE_REN))
    
    return list(itertools.combinations(yue_tuan, 4)) + list(itertools.combinations(lie_ren, 4))

def calculate_score_callback(combine: list[ShengYiWu]):
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
    crit_score = non_crit_score * crit_damage
    expect_score = calc_expect_damage(non_crit_score, crit_rate, crit_damage)

    return [expect_score, crit_score, all_hp, panel_crit_rate, crit_rate, round(crit_damage - 1, 3), energy_recharge, combine]


result_description = ["总评分", "期望伤害评分", "暴击伤害评分", "生命值", "面板暴击率", "实战暴击率", "暴击伤害", "充能效率", "圣遗物组合"]


def find_syw_for_na_wei_lai_te():
    return calculate_score(find_combine_callback=find_combine_callback,
                           match_sha_callback=match_sha_callback,
                           match_bei_callback=match_bei_callback,
                           calculate_score_callbak=calculate_score_callback,
                           result_txt_file="na_wei_lai_te_syw.txt",
                           result_description=result_description)


# Main body
if __name__ == '__main__':
    find_syw_for_na_wei_lai_te()
