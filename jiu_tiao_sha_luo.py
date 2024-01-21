#!/user/bin/env python3 -tt
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

import sys
import os
import logging
import itertools
from base_syw import ShengYiWu, ShengYiWu_Score, calculate_score, set_score_threshold, Syw_Combine_Desc, find_syw_combine


def calculate_score_callback(score_data: ShengYiWu_Score):
    base_atk = 184  # 81级
    wu_qi_atk = 674
    bai_zhi_atk = base_atk + wu_qi_atk

    extra_crit_rate = {
        "天空之翼": 0.221
    }

    extra_crit_damage = {
        "天空之翼": 0.2,
        "吃自已六命加成": 0.6,
    }

    extra_atk = {
        "自已攻击力加成": int(bai_zhi_atk * 0.86)
    }

    extra_atk_per = {
        "突破加成": 0.24
    }

    extra_energy_recharge = {
        "绝缘2件套": 0.2,
    }

    crit_rate = 0.05 + sum(extra_crit_rate.values())
    crit_damage = 1 + 0.5 + sum(extra_crit_damage.values())
    atk = 311 + sum(extra_atk.values())
    atk_per = sum(extra_atk_per.values())
    elem_bonus = 0
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
    if crit_rate < 0.6:
        return None
    
    energy_recharge *= 100
    energy_recharge = round(energy_recharge, 1)
    if energy_recharge < 220:
        return None
    
    all_atk = int(bai_zhi_atk * (1 + atk_per)) + atk
    elem_bonus += min(energy_recharge / 4 / 100, 0.75)

    e_damage = all_atk * 251.5 / 100 * elem_bonus * 1.3  # EZ
    q_damage = all_atk * (778.2 + 64.8 * 6) / 100 * elem_bonus

    all_damage = e_damage + q_damage
    score_data.damage_to_score(all_damage, crit_rate, crit_damage)

    panel_atk = all_atk - sum(extra_atk.values())
    panel_crit_damage = crit_damage - 1 - sum(extra_crit_damage.values()) + extra_crit_damage["天空之翼"]
    score_data.custom_data = [int(panel_atk), crit_rate, round(panel_crit_damage, 3), energy_recharge]

    return True
    

result_description = ["总评分", "期望伤害评分", "暴击伤害评分", "攻击力", "暴击率", "暴击伤害", "充能效率"]


def match_sha_callback(syw: ShengYiWu):
    return syw.energy_recharge == ShengYiWu.ENERGY_RECHARGE_MAX 


def match_bei_callback(syw: ShengYiWu):
    return syw.elem_type == ShengYiWu.ELEM_TYPE_LEI


def match_tou_callback(syw: ShengYiWu):
    return syw.crit_rate == ShengYiWu.CRIT_RATE_MAIN or syw.crit_damage == ShengYiWu.CRIT_DAMAGE_MAIN


def find_syw_for_jiu_tiao_sha_luo():
    raw_score_list = find_syw_combine([Syw_Combine_Desc(set1_name=ShengYiWu.JUE_YUAN, set1_num=4)],
                                      match_sha_callback=match_sha_callback,
                                      match_bei_callback=match_bei_callback,
                                      match_tou_callback=match_tou_callback)
    print(len(raw_score_list))

    return calculate_score(raw_score_list,
                           calculate_score_callbak=calculate_score_callback,
                           result_txt_file="jiu_tiao_sha_luo_syw.txt",
                           result_description=result_description)

# Main body
if __name__ == '__main__':
    set_score_threshold(1.7)
    find_syw_for_jiu_tiao_sha_luo()
    