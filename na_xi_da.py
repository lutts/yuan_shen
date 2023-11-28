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

ming_zuo_num = 6
qian_tai_damage = True
shuang_cao = False  # 双草

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


def find_combins_callback_all():
    shen_lin = find_syw(
        match_syw_callback=lambda s: match_syw(s, ShengYiWu.SHEN_LIN))
    shi_jin = find_syw(
        match_syw_callback=lambda s: match_syw(s, ShengYiWu.SHI_JIN))
    ju_tuan = find_syw(
        match_syw_callback=lambda s: match_syw(s, ShengYiWu.JU_TUAN))
    yue_tuan = find_syw(
        match_syw_callback=lambda s: match_syw(s, ShengYiWu.YUE_TUAN))

    shen_lin_2 = list(itertools.combinations(shen_lin, 2))
    shi_jin_2 = list(itertools.combinations(shi_jin, 2))
    ju_tuan_2 = list(itertools.combinations(ju_tuan, 2))
    yue_tuan_2 = list(itertools.combinations(yue_tuan, 2))

    all_2 = shen_lin_2 + shi_jin_2 + ju_tuan_2 + yue_tuan_2
    all_4 = list(itertools.combinations(shen_lin, 4)) + \
        list(itertools.combinations(shi_jin, 4)) + \
            list(itertools.combinations(ju_tuan, 4))

    return [(l[0] + l[1])
            for l in list(itertools.combinations(all_2, 2))] + all_4


def find_combins_callback():
    shen_lin = find_syw(
        match_syw_callback=lambda s: match_syw(s, ShengYiWu.SHEN_LIN))
    return list(itertools.combinations(shen_lin, 4))


def calculate_score_callback(combine: list[ShengYiWu]):
    wu_qi_atk = 542
    base_atk = 299
    bai_zhi_atk = wu_qi_atk + base_atk

    extra_elem_mastery = {
        "武器": 265,
        "等级突破加成": 115,
        "大招转化自久岐忍": 243,  # 固有天赋，阿忍带圣显，四饰金加的150可以被纳西妲大招转化
        "圣显": 78,
        # "队友1000精通": 250,
    }

    if ming_zuo_num >= 4:
        extra_elem_mastery["四命最小加成"] = 100

    if shuang_cao:
        gong_ming_elem_mastery = 50 + 30 + 20  # 双草共鸣
        zhuan_wu_extra_elem_mastery = 32 # 和装备者元素类型相同
        extra_elem_mastery["双草"] = gong_ming_elem_mastery + zhuan_wu_extra_elem_mastery
    else:
        extra_elem_mastery["双草"] = 0

    extra_elem_bonus = {
        # "草套2件套效果": 0.15,
    }

    if shuang_cao:
        extra_elem_bonus["专武(草行久钟)"] = 2 * 0.1
    else:
        extra_elem_bonus["专武(草行久钟)"] = 3 * 0.1


    if ming_zuo_num >= 5:
        extra_elem_bonus["一命计算一个火系"] = 0.316
    elif ming_zuo_num >= 1:
        extra_elem_bonus["一命计算一个火系"] = 0.268

    panel_crit_rate = 0.05
    crit_damage = 1 + 0.5
    elem_mastery = sum(extra_elem_mastery.values())
    elem_bonus = 1 + sum(extra_elem_bonus.values())
    atk = 311
    atk_per = 0
    energy_recharge = 0

    for p in combine:
        panel_crit_rate += p.crit_rate
        crit_damage += p.crit_damage
        elem_mastery += p.elem_mastery
        elem_bonus += p.elem_bonus
        atk += p.atk
        atk_per += p.atk_per
        energy_recharge += p.energe_recharge

    syw_names = [p.name for p in combine]
    # print(syw_names)
    name_count = {i: syw_names.count(i) for i in syw_names}
    # print(name_count)
    for n in name_count:
        if name_count[n] < 2:  # 散件不计算套装效果
            continue

        if n == ShengYiWu.SHEN_LIN:
            elem_bonus += 0.15
        elif n == ShengYiWu.SHI_JIN:
            elem_mastery += 80
            if name_count[n] >= 4:
                elem_mastery += 150  # 草行久钟
        elif n == ShengYiWu.JU_TUAN:
            elem_bonus += 0.2
            if name_count[n] >= 4:
                elem_bonus += 0.25 + 0.25
        elif n == ShengYiWu.YUE_TUAN:
            elem_mastery += 80

    background_elem_mastery = elem_mastery - extra_elem_mastery["大招转化自久岐忍"]
    if qian_tai_damage:
        real_elem_mastery = elem_mastery
    else:
        real_elem_mastery = background_elem_mastery

    crit_rate = panel_crit_rate + min((real_elem_mastery - 200) * 0.0003, 0.24)
    crit_rate = round(crit_rate, 3)
    if crit_rate < 0.64:
        return None
    
    elem_bonus += min((real_elem_mastery - 200) * 0.001, 0.8)
    all_atk = int(bai_zhi_atk * (1 + atk_per)) + atk
    energy_recharge = (energy_recharge + 1) * 100

    if ming_zuo_num >= 3:
        atk_bei_lv = 2.193
        elem_mastery_bei_lv = 4.386
    else:
        atk_bei_lv = 1.858
        elem_mastery_bei_lv = 3.715

    non_crit_score = (all_atk * atk_bei_lv + real_elem_mastery * elem_mastery_bei_lv) * elem_bonus
    crit_score = non_crit_score * crit_damage
    expect_score = non_crit_score * (1 + crit_rate * (crit_damage - 1))
    return [expect_score, crit_score, elem_mastery, background_elem_mastery, int(all_atk), round(panel_crit_rate, 3), round(crit_rate, 3), round(crit_damage - 1, 3), round(energy_recharge, 3), combine]


result_description = ["总评分", "期望伤害评分", "暴击伤害评分", "实战前台精通", "实战后台精通", "实战攻击力", "面板暴击率", "实战暴击率", "暴伤", "充能效率", "圣遗物组合"]
def find_syw_for_na_xi_da_all():
    return calculate_score(find_combine_callback=find_combins_callback_all,
                           match_sha_callback=match_sha_callback,
                           match_bei_callback=match_bei_callback,
                           calculate_score_callbak=calculate_score_callback,
                           result_txt_file="na_xi_da_syw.txt",
                           result_description=result_description
                           )

def find_syw_for_na_xi_da():
    return calculate_score(find_combine_callback=find_combins_callback,
                           match_sha_callback=match_sha_callback,
                           match_bei_callback=match_bei_callback,
                           calculate_score_callbak=calculate_score_callback,
                           result_txt_file="na_xi_da_syw.txt",
                           result_description=result_description)

# Main body
if __name__ == '__main__':
    find_syw_for_na_xi_da()
