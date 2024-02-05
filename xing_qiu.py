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


def calculate_score_callback(score_data: ShengYiWu_Score):
    base_atk = 191  # 82级
    wu_qi_atk = 454
    bai_zhi_atk = base_atk + wu_qi_atk

    extra_energy_recharge = {
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
    energy_recharge = 1 + sum(extra_energy_recharge.values())

    combine = score_data.syw_combine

    for p in combine:
        crit_rate += p.crit_rate
        crit_damage += p.crit_damage
        atk += p.atk
        atk_per += p.atk_per
        elem_bonus += p.elem_bonus
        energy_recharge += p.energy_recharge

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
            energy_recharge += 0.2
            if name_count[n] >= 4:
                is_4_jue_yuan = True

    energy_recharge *= 100
    energy_recharge = round(energy_recharge, 1)
    if energy_recharge < 200:
        return None

    all_atk = int(bai_zhi_atk * (1 + atk_per)) + atk
    if is_4_jue_yuan:
        extra_q_bonus += min(energy_recharge / 4 / 100, 0.75)

    # 手法: eqe，第二个e有四命加成
    e_damage_1 = all_atk * (336 + 382) / 100 * elem_bonus
    e_damage_2 = all_atk * (336 + 382) / 100 * elem_bonus * 1.5  # 四命
    e_damage = e_damage_1 + e_damage_2

    q_num = 2 + 3 + 5 + 2 + 3 + 5 + 2 + 3 + 5 + 2 + 3 + 5
    q_damage = all_atk * 115 / 100 * (elem_bonus + extra_q_bonus) * q_num

    all_damage = e_damage + q_damage

    score_data.damage_to_score(all_damage, crit_rate, crit_damage - 1)

    q_bonus = elem_bonus + extra_q_bonus
    score_data.custom_data = [int(all_atk), round(elem_bonus, 3), round(q_bonus, 3), int(e_damage), int(q_damage),
                              crit_rate, round(crit_damage - 1, 3), energy_recharge]

    return True


result_description = ["攻击力", "e增伤", "q增伤", "e伤害", "q伤害", "暴击率", "暴击伤害", "充能效率"]


def match_sha_callback(syw: ShengYiWu):
    return syw.atk_per == ShengYiWu.BONUS_MAX


def match_bei_callback(syw: ShengYiWu):
    return syw.elem_type == Ys_Elem_Type.SHUI


def match_tou_callback(syw: ShengYiWu):
    return syw.crit_rate == ShengYiWu.CRIT_RATE_MAIN or syw.crit_damage == ShengYiWu.CRIT_DAMAGE_MAIN


def find_syw_for_xing_qiu():
    combine_desc_lst = Syw_Combine_Desc.any_2p2([ShengYiWu.JUE_YUAN,
                                                 ShengYiWu.ZONG_SHI,
                                                 ShengYiWu.CHEN_LUN,
                                                 ShengYiWu.SHUI_XIAN,
                                                 ShengYiWu.ZHUI_YI,
                                                 ShengYiWu.JUE_DOU_SHI])

    combine_desc_lst.append(Syw_Combine_Desc(
        set1_name=ShengYiWu.JUE_YUAN, set1_num=4))

    raw_score_list = find_syw_combine(combine_desc_lst,
                                      match_sha_callback=match_sha_callback,
                                      match_bei_callback=match_bei_callback,
                                      match_tou_callback=match_tou_callback)
    print(len(raw_score_list))

    return calculate_score(raw_score_list,
                           calculate_score_callbak=calculate_score_callback,
                           result_txt_file="xing_qiu_syw.txt",
                           result_description=result_description)


# Main body
if __name__ == '__main__':
    find_syw_for_xing_qiu()
