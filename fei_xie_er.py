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
    max_atk = 852 #绝弦754， 最初的大魔术852
    tu_po_atk_per = 0.24
    mo_shu_crit_damage = 0.662
    mo_shu_atk_per = 0.32  # 双雷 32%
    base_crit_damage = 1 + 0.5 + mo_shu_crit_damage
    base_elem_mastery = 0 #165 # 绝弦
    wan_ye_bonus = 0.4
    base_elem_bonus = 1 + wan_ye_bonus

    combine = score_data.syw_combine

    crit_rate = sum([p.crit_rate for p in combine]) + 0.05
    crit_rate = round(crit_rate, 3)
    if crit_rate < 0.65:
        return None

    atk = sum([p.atk for p in combine]) + 311
    atk_per = sum([p.atk_per for p in combine]) + tu_po_atk_per + mo_shu_atk_per
    extra_crit_damage = sum([p.crit_damage for p in combine])
    extra_elem_bonus = sum([p.elem_bonus for p in combine])
    elem_mastery = sum([p.elem_mastery for p in combine]) + base_elem_mastery

    elem_mastery = round(elem_mastery, 1)
    #if elem_mastery < 100:
    #    return None
    
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

    all_atk = int(max_atk * (1 + atk_per)) + atk
    e_bonus = base_elem_bonus + extra_elem_bonus
    crit_damage = base_crit_damage + extra_crit_damage

    # 刻晴eqe4az手法时，伤害来源
    # 召唤奥兹：原激化
    # 奥兹：8次伤害，其中3次超激化
    # 断罪雷影：9次超激化
    # 这里按12级e计算

    zhao_huan_damage = all_atk * 231 / 100 * e_bonus

    ao_zi_damage = all_atk * 178 / 100 * e_bonus * 5

    chao_ji_hua_bonus = 1446.85 * 1.15 * (1 + 5 * elem_mastery / (elem_mastery + 1200))
    ao_zi_damage += (all_atk * 178 / 100 + chao_ji_hua_bonus) * e_bonus * 3

    duan_zui_lei_ying_damage = (all_atk * 80 / 100 + chao_ji_hua_bonus) * e_bonus * 9

    all_damage = zhao_huan_damage + ao_zi_damage + duan_zui_lei_ying_damage
    
    score_data.damage_to_score(all_damage, crit_rate, crit_damage)
    score_data.custom_data = [elem_mastery, int(all_atk), round(crit_rate, 3), round(crit_damage - 1, 3)]

    return True


result_description = ["精通", "实战攻击力", "暴击率", "暴击伤害"]

def match_sha_callback(syw: ShengYiWu):
    return syw.atk_per == ShengYiWu.BONUS_MAX or syw.elem_mastery == ShengYiWu.ELEM_MASTERY_MAIN


def match_bei_callback(syw: ShengYiWu):
    return syw.elem_type == Ys_Elem_Type.LEI

def match_tou_callback(syw: ShengYiWu):
    return syw.crit_rate == ShengYiWu.CRIT_RATE_MAIN or syw.crit_damage == ShengYiWu.CRIT_DAMAGE_MAIN

def find_syw_for_fei_xie_er():
    combine_desc_lst = Syw_Combine_Desc.any_2p2([ShengYiWu.JU_TUAN,
                                                 ShengYiWu.RU_LEI,
                                                 ShengYiWu.ZHUI_YI,
                                                 ShengYiWu.JUE_DOU_SHI])

    combine_desc_lst.append(Syw_Combine_Desc(set1_name=ShengYiWu.JU_TUAN, set1_num=4))
    combine_desc_lst.append(Syw_Combine_Desc(set1_name=ShengYiWu.SHI_JIN, set1_num=4))

    raw_score_list = find_syw_combine(combine_desc_lst,
                                      match_sha_callback=match_sha_callback,
                                      match_bei_callback=match_bei_callback,
                                      match_tou_callback=match_tou_callback)
    print(len(raw_score_list))

    return calculate_score(raw_score_list,
                           calculate_score_callbak=calculate_score_callback,
                           result_txt_file="fei_xie_er_syw.txt",
                           result_description=result_description)

# Main body
if __name__ == '__main__':
    find_syw_for_fei_xie_er()