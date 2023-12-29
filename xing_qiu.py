#!/user/bin/env python3 -tt
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

import sys
import os
import logging
import itertools
from base_syw import ShengYiWu, calculate_score, find_syw, calc_expect_score, set_score_threshold


def match_sha_callback(syw: ShengYiWu):
    return syw.atk_per == ShengYiWu.BONUS_MAX


def match_bei_callback(syw: ShengYiWu):
    return syw.elem_type == ShengYiWu.ELEM_TYPE_SHUI


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
    jue_yuan = find_syw(match_syw_callback=lambda s: match_syw(s, ShengYiWu.JUE_YUAN))
    zong_shi = find_syw(match_syw_callback=lambda s: match_syw(s, ShengYiWu.ZONG_SHI))
    chen_lun = find_syw(match_syw_callback=lambda s: match_syw(s, ShengYiWu.CHEN_LUN))
    shui_xian = find_syw(match_syw_callback=lambda s: match_syw(s, ShengYiWu.SHUI_XIAN))
    zhui_yi = find_syw(match_syw_callback=lambda s: match_syw(s, ShengYiWu.ZHUI_YI))
    jue_dou_shi = find_syw(match_syw_callback=lambda s: match_syw(s, ShengYiWu.JUE_DOU_SHI))

    zong_shi_2 = list(itertools.combinations(zong_shi, 2))
    chen_lun_2 = list(itertools.combinations(chen_lun, 2))
    shui_xian_2 = list(itertools.combinations(shui_xian, 2))
    zhui_yi_2 = list(itertools.combinations(zhui_yi, 2))
    jue_dou_shi_2 = list(itertools.combinations(jue_dou_shi, 2))
    jue_yuan_2 = list(itertools.combinations(jue_yuan, 2))

    all_2 = zong_shi_2 + chen_lun_2 + shui_xian_2 + zhui_yi_2 + jue_dou_shi_2 + jue_yuan_2

    return [(l[0] + l[1])
            for l in list(itertools.combinations(all_2, 2))] + list(itertools.combinations(jue_yuan, 4))

def calculate_score_callback(combine: list[ShengYiWu]):
    base_atk = 191  # 82级
    wu_qi_atk = 454
    bai_zhi_atk = base_atk + wu_qi_atk

    extra_energe_recharge = {
        "祭礼剑": 0.613,
    }

    extra_atk_per = {
        "突破加成": 0.24
    }

    extra_elem_bonus = {
        "固有天赋2": 0.2
    }

    crit_rate = 0.05
    crit_damage = 1 + 0.5
    atk = 311
    atk_per = sum(extra_atk_per.values())
    elem_bonus = sum(extra_elem_bonus.values())
    energe_recharge = 1 + sum(extra_energe_recharge.values())

    for p in combine:
        crit_rate += p.crit_rate
        crit_damage += p.crit_damage
        atk += p.atk
        atk_per += p.atk_per
        elem_bonus += p.elem_bonus
        energe_recharge += p.energe_recharge

    crit_rate = round(crit_rate, 3)
    if crit_rate < 0.55:
        return None
    
    extra_q_bonus = 0
    is_4_jue_yuan = False
    syw_names = [p.name for p in combine]
    # print(syw_names)
    name_count = {i: syw_names.count(i) for i in syw_names}
    # print(name_count)
    for n in name_count:
        if name_count[n] < 2:  # 散件不计算套装效果
            continue

        if n == ShengYiWu.CHEN_LUN:
            elem_bonus += 0.2
        elif n == ShengYiWu.SHUI_XIAN:
            elem_bonus += 0.2
        elif n == ShengYiWu.ZONG_SHI:
            extra_q_bonus += 0.2
        elif n == ShengYiWu.ZHUI_YI:
            atk_per += 0.18
        elif n == ShengYiWu.JUE_DOU_SHI:
            atk_per += 0.18
        elif n == ShengYiWu.JUE_YUAN:
            energe_recharge += 0.2
            if name_count[n] >= 4:
                is_4_jue_yuan = True
    
    energe_recharge *= 100
    energe_recharge = round(energe_recharge, 1)
    if energe_recharge < 200:
        return None
    
    all_atk = int(bai_zhi_atk * (1 + atk_per)) + atk
    if is_4_jue_yuan:
        extra_q_bonus += min(energe_recharge / 4 / 100, 0.75)

    e_damage_1 = all_atk * (336 + 382) / 100 * elem_bonus
    e_damage_2 = all_atk * (336 + 382) / 100 * (elem_bonus + 0.5)  # 四命
    e_damage = e_damage_1 + e_damage_2
    
    q_num = 2 + 3 + 5 + 2 + 3 + 5 + 2 + 3 + 5 + 2 + 3 + 5
    q_damage = all_atk * 115 / 100 * (elem_bonus + extra_q_bonus) * q_num

    all_damage = e_damage + q_damage
    crit_score = all_damage * crit_damage
    expect_score = calc_expect_score(all_damage, crit_rate, crit_damage)

    q_bonus = elem_bonus + extra_q_bonus
    return [expect_score, crit_score, int(all_atk), round(elem_bonus, 3), round(q_bonus, 3), int(e_damage), int(q_damage), crit_rate, round(crit_damage - 1, 3), energe_recharge, combine]
    

result_description = ["总评分", "期望伤害评分", "暴击伤害评分", "攻击力", "e增伤", "q增伤", "e伤害", "q伤害", "暴击率", "暴击伤害", "充能效率", "圣遗物组合"]


def find_syw_for_xing_qiu():
    return calculate_score(find_combine_callback=find_combins_callback,
                    match_sha_callback=match_sha_callback,
                    match_bei_callback=match_bei_callback,
                    calculate_score_callbak=calculate_score_callback,
                    result_txt_file="xing_qiu_syw.txt",
                    result_description=result_description)

# Main body
if __name__ == '__main__':
    find_syw_for_xing_qiu()
    