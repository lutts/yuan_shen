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
from ye_lan import YeLanQBonus

def calculate_score_callback(score_data: ShengYiWu_Score):
    base_atk = 337
    wu_qi_atk = 608
    bai_zhi_atk = base_atk + wu_qi_atk

    has_ye_lan = True
    ye_lan_ming_zuo_num = 6
    has_fu_fu = False

    extra_energy_recharge = {
        "绝缘2件套": 0.2,
        "薙草之稻光": 0.551,
        "薙草之稻光开大加成": 0.3,
    }

    extra_atk = {
        "班尼特": int(755 * 1.19),
        "双火": 0, # int(945 * 0.25),
        "九条": 0, #int(858 * 0.86),
    }

    extra_crit_damage = {
        "九条": 0, #0.6,
    }

    extra_elem_bonus = {
        "万叶": 0.4,
    }

    if has_fu_fu:
        extra_elem_bonus["芙芙"] = 1.24

    crit_rate = 0.05
    crit_damage = 1 + 0.5 + sum(extra_crit_damage.values())
    atk = sum(extra_atk.values()) + 311
    atk_per = 0
    energy_recharge = 1.32 + sum(extra_energy_recharge.values())
    elem_bonus = 1 + sum(extra_elem_bonus.values())

    combine = score_data.syw_combine

    for p in combine:
        crit_rate += p.crit_rate
        crit_damage += p.crit_damage
        atk += p.atk
        atk_per += p.atk_per
        energy_recharge += p.energy_recharge
        elem_bonus += p.elem_bonus

    crit_rate = round(crit_rate, 3)
    if crit_rate < 0.65:
        return None

    energy_recharge *= 100
    panel_energy_recharge = energy_recharge - extra_energy_recharge["薙草之稻光开大加成"] * 100

    panel_energy_recharge = round(panel_energy_recharge, 1)
    if panel_energy_recharge < 260:
        return None
    
    elem_bonus += (energy_recharge - 100) * 0.004  # 固有天赋2
    #panel_elem_bonus = elem_bonus - sum(extra_elem_bonus.values())
    elem_bonus += min(energy_recharge / 4 / 100, 0.75)

    panel_atk = int(bai_zhi_atk * (1 + atk_per)) + atk - sum(extra_atk.values()) + extra_atk["双火"]
    atk_per += min((energy_recharge - 100) * 0.0028, 0.8)
   
    all_atk = int(bai_zhi_atk * (1 + atk_per)) + atk

    if has_ye_lan and ye_lan_ming_zuo_num == 6:
        ye_lan_bonus = YeLanQBonus()
        ye_lan_bonus.start(3.567)

        # 和满命夜兰配队不能采用az打法，因为时间只够打2次az，虽然2次az比5a伤害还高些，但只能触发两次回能，5a能触发3次
        # 和满命夜兰配队本来就因为影宝砍不满导致充能压力大，所以5a是最理想的

        q_damage = all_atk * 1141 / 100 * (elem_bonus + ye_lan_bonus.bonus(11.319))
        qa1_damage = all_atk * 158.4 / 100 * (elem_bonus + ye_lan_bonus.bonus(11.752))
        qa2_damage = all_atk * 157 / 100 * (elem_bonus + ye_lan_bonus.bonus(12.053))
        qa3_damage = all_atk * 174.6 / 100 * (elem_bonus + ye_lan_bonus.bonus(12.053))
        qa4_bonus = elem_bonus + ye_lan_bonus.bonus(13.137)
        qa4_damage = all_atk * 133.7 / 100 * qa4_bonus + all_atk * 133.9 / 100 * qa4_bonus
        qa5_damage = all_atk * 210.5 / 100 * (elem_bonus + ye_lan_bonus.bonus(13.871))

        all_damage = q_damage + qa1_damage + qa2_damage + qa3_damage + qa4_damage + qa5_damage
    else:
        # 一轮伤害：两套普攻 + 4下 或者 5az
        # 愿力层数：夜兰70 + 万叶60 + 班尼特60 = 190 * 0.2 = 38 * 1.2 = 45层，所有队友产球5颗就有60层
        # 雷九万班：60层肯定没问题
        # 梦想一刀：(721% + 420%=1141%)攻击力
        # 一段：79.8% + 78.6% = 158.4%
        # 二段：78.4% + 78.6% = 157%
        # 三段：96.0% + 78.6% = 174.6%
        # 四段：(55.1% + 78.6% = 133.7%) + (55.3% + 78.6% = 133.9%)
        # 五段：131.9% + 78.6% = 210.5%
        # 重击：(109.9% + 78.6% = 188.5%) + (132.7% + 78.6% = 211.3%)

        qa1_bei_lv = 158.4
        qa2_bei_lv = 157
        qa3_bei_lv = 174.6
        qa4_1_bei_lv = 133.7
        qa4_2_bei_lv = 133.9
        qa5_bei_lv = 210.5
        qaz_1_bei_lv = 188.5
        qaz_2_bei_lv = 211.3

        use_5az = False

        if use_5az: 
            a_timestamps = [
                12.937, 14.404, 15.887, 17.321, 18.771
            ]

            z1_timestamps = [
                13.554, 15.038, 16.554, 17.953, 19.354
            ]

            z2_timestamps = [
                13.704, 15.221, 16.637, 18.071, 19.554
            ]

            ye_lan_bonus = YeLanQBonus()
            ye_lan_bonus.start(4.369)

            if not has_ye_lan:
                ye_lan_bonus.invalidate()

            q_damage = all_atk * 1141 / 100 * (elem_bonus + ye_lan_bonus.bonus(12.104))

            all_damage = q_damage

            for t in a_timestamps:
                qa1_elem_bonus = elem_bonus + ye_lan_bonus.bonus(t)
                all_damage += all_atk * qa1_bei_lv / 100 * qa1_elem_bonus

            for t in z1_timestamps:
                z1_elem_bonus = elem_bonus + ye_lan_bonus.bonus(t)
                all_damage += all_atk * qaz_1_bei_lv / 100 * z1_elem_bonus

            for t in z2_timestamps:
                z2_elem_bonus = elem_bonus + ye_lan_bonus.bonus(t)
                all_damage += all_atk * qaz_2_bei_lv / 100 * z2_elem_bonus
        else: # 全程普攻
            ye_lan_bonus = YeLanQBonus()
            ye_lan_bonus.start(3.884)

            if not has_ye_lan:
                ye_lan_bonus.invalidate()

            q_damage = all_atk * 1141 / 100 * (elem_bonus + ye_lan_bonus.bonus(11.686))

            all_damage = q_damage

            timestamps_and_bei_lv = [
                (12.271, qa1_bei_lv),
                (12.704, qa2_bei_lv),
                (12.954, qa3_bei_lv),
                (13.487, qa4_1_bei_lv),
                (13.741, qa4_2_bei_lv),
                (14.454, qa5_bei_lv),

                (15.187, qa1_bei_lv),
                (15.671, qa2_bei_lv),
                (16.02, qa3_bei_lv),
                (16.437, qa4_1_bei_lv),
                (16.737, qa4_2_bei_lv),
                (17.471, qa5_bei_lv),

                (18.171, qa1_bei_lv),
                (18.537, qa2_bei_lv),
                (18.904, qa3_bei_lv),
                (19.403, qa4_1_bei_lv),
                (19.604, qa4_2_bei_lv)
            ]

            for tb in timestamps_and_bei_lv:
                t, bei_lv = tb
                bonus_with_ye_lan = elem_bonus + ye_lan_bonus.bonus(t)
                all_damage += all_atk * bei_lv / 100 * bonus_with_ye_lan
    
    score_data.damage_to_score(all_damage, crit_rate, crit_damage)

    panel_crit_damage = crit_damage - sum(extra_crit_damage.values())
    panel_crit_damage = round(panel_crit_damage - 1, 3)
    score_data.custom_data = [int(all_atk), int(panel_atk), round(elem_bonus, 3), 
                              round(crit_rate, 3), panel_crit_damage, round(panel_energy_recharge, 1)]
    
    return True


result_description = ["实战攻击力", "面板攻击力", "实战最大伤害加成", "暴击率", "暴击伤害", "面板充能效率"]

def match_sha_callback(syw: ShengYiWu):
    return syw.energy_recharge == ShengYiWu.ENERGY_RECHARGE_MAX


def match_bei_callback(syw: ShengYiWu):
    return syw.atk_per == ShengYiWu.BONUS_MAX or syw.elem_type == Ys_Elem_Type.LEI

def match_tou_callback(syw: ShengYiWu):
    return syw.crit_rate == ShengYiWu.CRIT_RATE_MAIN or syw.crit_damage == ShengYiWu.CRIT_DAMAGE_MAIN


def find_syw_for_lei_shen():
    raw_score_list = find_syw_combine([Syw_Combine_Desc(set1_name=ShengYiWu.JUE_YUAN, set1_num=4)],
                                      match_sha_callback=match_sha_callback,
                                      match_bei_callback=match_bei_callback,
                                      match_tou_callback=match_tou_callback)
    print(len(raw_score_list))

    return calculate_score(raw_score_list,
                           calculate_score_callbak=calculate_score_callback,
                           result_txt_file="lei_shen_syw.txt",
                           result_description=result_description)

# Main body
if __name__ == '__main__':
    find_syw_for_lei_shen()