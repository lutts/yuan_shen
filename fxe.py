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
from ys_reaction import *
from character import Character
from monster import Monster
from base_syw import ShengYiWu, ShengYiWu_Score, calculate_score, Syw_Combine_Desc, find_syw_combine

def get_fei_xie_er_with_mo_shu() -> Character:
    ch = Character("菲谢尔", elem_type=Ys_Elem_Type.LEI, e_level=12, base_atk=852)
    ch.add_crit_damage(0.662)
    return ch
    
def get_fei_xie_er_with_jue_xian() -> Character:
    ch = Character("菲谢尔", elem_type=Ys_Elem_Type.LEI, e_level=12, base_atk=754)
    ch.add_elem_mastery(165)
    return ch

def calculate_score_callback(score_data: ShengYiWu_Score):
    fei_xie_er = get_fei_xie_er_with_mo_shu()
    fei_xie_er.add_atk_per(0.24) # 突破加成
    fei_xie_er.add_atk_per(0.32) # 双雷32%
    fei_xie_er.add_all_bonus(0.4)   # 万叶

    combine = score_data.syw_combine

    fei_xie_er.add_crit_rate(sum([p.crit_rate for p in combine]))
    crit_rate = round(fei_xie_er.get_crit_rate(), 3)
    if crit_rate < 0.65:
        return None

    fei_xie_er.add_atk(sum([p.atk for p in combine]))
    fei_xie_er.add_atk_per(sum([p.atk_per for p in combine]))
    fei_xie_er.add_crit_damage(sum([p.crit_damage for p in combine]))
    fei_xie_er.add_all_bonus(sum([p.elem_bonus for p in combine]))
    fei_xie_er.add_elem_mastery(sum([p.elem_mastery for p in combine]))

    # elem_mastery = round(fei_xie_er.get_elem_mastery, 1)
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
            fei_xie_er.add_all_bonus(0.15)
        elif n == ShengYiWu.ZHUI_YI:
            fei_xie_er.add_atk_per(0.18)
        elif n == ShengYiWu.JUE_DOU_SHI:
            fei_xie_er.add_atk_per(0.18)
        elif n == ShengYiWu.JU_TUAN:
            fei_xie_er.add_e_bonus(0.2)
            if name_count[n] >= 4:
                fei_xie_er.add_e_bonus(0.25 + 0.25)
        elif n == ShengYiWu.SHI_JIN:
            # 队伍有双雷
            fei_xie_er.add_elem_mastery(80 + 100)
            fei_xie_er.add_atk_per(0.14)

    # 刻晴eqe4az手法时，伤害来源
    # 召唤奥兹：原激化
    # 奥兹：8次伤害，其中3次超激化
    # 断罪雷影：9次超激化
    # 这里按12级e计算
            
    all_atk = fei_xie_er.get_atk()
    e_bonus = fei_xie_er.get_e_bonus()

    monster = Monster()

    no_reaction = Ys_No_Reaction(fei_xie_er, monster)
    chao_ji_hua = Ys_Reaction_JiHua(ch=fei_xie_er, monster=monster, ji_hua_type=JiHua_Type.Chao_JiHua)

    zhao_huan_damage = no_reaction.do_damage(all_atk * 231 / 100, e_bonus)

    ao_zi_damage = no_reaction.do_damage(all_atk * 178 / 100, e_bonus) * 5
    ao_zi_damage = chao_ji_hua.do_damage(all_atk * 178 / 100, e_bonus) * 3

    duan_zui_lei_ying_damage = chao_ji_hua.do_damage(all_atk * 80 / 100, e_bonus) * 9

    all_damage = zhao_huan_damage + ao_zi_damage + duan_zui_lei_ying_damage
    
    score_data.damage_to_score(all_damage, fei_xie_er.get_crit_rate(), fei_xie_er.get_crit_damage())
    score_data.custom_data = [fei_xie_er.get_elem_mastery(), int(all_atk), 
                              round(crit_rate, 3), round(fei_xie_er.get_crit_damage(), 3)]

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