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
    base_atk = 314
    wu_qi_atk = 608  # 波波刀/苍古
    #wu_qi_atk = 542  # 专武
    bai_zhi_atk = base_atk + wu_qi_atk

    na_xi_da_zhuan_wu_elem_mastery = 40
    shuang_cao_elem_mastery = 50 + 50   # 双草共鸣
    sheng_xian_mastery = 78  # 久岐忍圣显

    base_elem_bonus = 1 + 0.288  # 等级突破

    bo_bo_dao_bonus = 0.12
    bo_bo_dao_a_bonus = 2 * 0.2     # 波波刀2层
    bo_bo_dao_crit_rate = 0.331

    cang_gu_mastery = 0 #198
    cang_gu_elem_bonus = 0 #0.1    # 苍古
    cang_gu_a_bonus = 0 #0.16
    cang_gu_atk_per = 0 #0.2

    has_zhuan_wu = False

    if has_zhuan_wu:
        zhuan_wu_crit_rate = 0.04
        zhuan_wu_crit_damage = 0.882
    else:
        zhuan_wu_crit_rate = 0
        zhuan_wu_crit_damage = 0

    crit_rate = 0.05 + bo_bo_dao_crit_rate + zhuan_wu_crit_rate
    crit_damage = 1 + 0.5 + zhuan_wu_crit_damage
    elem_mastery = na_xi_da_zhuan_wu_elem_mastery + \
        shuang_cao_elem_mastery + sheng_xian_mastery + cang_gu_mastery
    panel_elem_mastery = 0
    atk = 311
    atk_per = cang_gu_atk_per
    elem_bonus = base_elem_bonus + bo_bo_dao_bonus + cang_gu_elem_bonus

    combine = score_data.syw_combine

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
        return False

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

    a_elem_bonus = elem_bonus + bo_bo_dao_a_bonus + cang_gu_a_bonus
    all_atk = int(bai_zhi_atk * (1 + atk_per)) + atk
    panel_atk = int(bai_zhi_atk * (1 + panel_atk_per)) + atk

    if has_zhuan_wu:
        a_e_extra_damage = elem_mastery * 1.2
    else:
        a_e_extra_damage = 0

    # 以下计算基于以下手法
    # Q 切久岐忍e 再切回海哥 aaa闪 aaa e aaa闪 aaa z aaa aaa，共计六发满层光幕攻击
    # 波波刀的普攻增伤需要海哥e之后才有，能覆盖开e后续所有的平A
    q_damage = (all_atk * 218.9 / 100 +
                elem_mastery * 175.1 / 100) * elem_bonus

    aaa_damage = all_atk * (91 + 93.2 + 62.8 + 62.8) / 100 + 4 * a_e_extra_damage
    z_damage = all_atk * (101.5 + 101.5) / 100

    
    e_damage = (all_atk * 3.485 / 100 +
                elem_mastery * 2.788 / 100 + a_e_extra_damage) * elem_bonus
    guang_mu_damage = (all_atk * 121 / 100 + elem_mastery * 241.9 / 100 + a_e_extra_damage) * 3 * elem_bonus * 6  # 六剑雨

    if cang_gu_a_bonus != 0:
        a_without_extra_bonus_num = 0
        a_with_extra_bonus_num = 6
    else:
        a_without_extra_bonus_num = 2
        a_with_extra_bonus_num = 4

    non_crit_score = q_damage + a_without_extra_bonus_num * aaa_damage * elem_bonus + \
        e_damage + z_damage + a_with_extra_bonus_num * \
        aaa_damage * a_elem_bonus + guang_mu_damage
    
    score_data.damage_to_score(non_crit_score, crit_rate, crit_damage)
    score_data.custom_data = [elem_mastery, panel_elem_mastery, int(panel_atk), round(crit_rate, 3), round(crit_damage - 1, 3)]

    return True


result_description = ["实战精通", "面板精通", "面板攻击力", "暴击率", "暴伤"]

def match_sha_callback(syw: ShengYiWu):
    return syw.elem_mastery == ShengYiWu.ELEM_MASTERY_MAIN


def match_bei_callback(syw: ShengYiWu):
    # or syw.atk_per == ShengYiWu.BONUS_MAX or syw.elem_mastery == ShengYiWu.ELEM_MASTERY_MAIN
    return syw.elem_type == Ys_Elem_Type.CAO

def match_tou_callback(syw: ShengYiWu):
    return syw.crit_rate == ShengYiWu.CRIT_RATE_MAIN or syw.crit_damage == ShengYiWu.CRIT_DAMAGE_MAIN

def find_syw_for_ai_er_hai_seng():
    combine_desc_lst = Syw_Combine_Desc.any_2p2([ShengYiWu.SHI_JIN,
                                                 ShengYiWu.YUE_TUAN,
                                                 ShengYiWu.SHEN_LIN])

    combine_desc_lst.append(Syw_Combine_Desc(set1_name=ShengYiWu.SHI_JIN, set1_num=4))

    raw_score_list = find_syw_combine(combine_desc_lst,
                                      match_sha_callback=match_sha_callback,
                                      match_bei_callback=match_bei_callback,
                                      match_tou_callback=match_tou_callback)
    print(len(raw_score_list))

    return calculate_score(raw_score_list,
                           calculate_score_callbak=calculate_score_callback,
                           result_txt_file="ai_er_hai_seng_syw.txt",
                           result_description=result_description)


# Main body
if __name__ == '__main__':
    find_syw_for_ai_er_hai_seng()
