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
from monster import Monster
from ys_syw import ShengYiWu, ShengYiWu_Score, calculate_score, Syw_Combine_Desc, find_syw_combine
from ye_lan import YeLanQBonus

enable_debug = False

def calculate_score_callback(score_data: ShengYiWu_Score):
    base_atk = 337
    wu_qi_atk = 608
    bai_zhi_atk = base_atk + wu_qi_atk

    has_ye_lan = True
    ye_lan_ming_zuo_num = 1
    has_fu_fu = False

    extra_energy_recharge = {
        "绝缘2件套": 0.2,
        "薙草之稻光": 0.551,
        "薙草之稻光开大加成": 0.3,
    }

    extra_atk = {
        "班尼特": int(756 * 1.39) + bai_zhi_atk * 0.2,  # 宗室四件套
        "双火": 0, # int(945 * 0.25),
        "九条": 0 # round(858 * 0.86),
    }

    extra_crit_damage = {
        "九条": 0 # 0.6,
    }

    extra_elem_bonus = {
        "万叶": (994 + 200) * 0.0004,
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
    elem_bonus += 0.27 # e技能加成

    panel_atk = int(bai_zhi_atk * (1 + atk_per)) + atk - sum(extra_atk.values()) + extra_atk["双火"]
    atk_per += min((energy_recharge - 100) * 0.0028, 0.8)
   
    all_atk = int(bai_zhi_atk * (1 + atk_per)) + atk

    # 一轮伤害：两套普攻 + 4下 或者 5az
    # 愿力层数：夜兰70 + 万叶60 + 班尼特60 = 190 * 0.2 = 38 * 1.2 = 45层，所有队友产球5颗就有60层
    # 雷九万班：60层肯定没问题
    meng_xiang_yi_dao_bei_lv = 852 + 8.26 * 60
        
    yuan_li_bei_lv = 1.54 * 60
    
    qa1_bei_lv = 93.5 + yuan_li_bei_lv
    qa2_bei_lv = 91.9 + yuan_li_bei_lv
    qa3_bei_lv = 112.5 + yuan_li_bei_lv
    qa4_1_bei_lv = 64.6 + yuan_li_bei_lv
    qa4_2_bei_lv = 64.8 + yuan_li_bei_lv
    qa5_bei_lv = 154.6 + yuan_li_bei_lv
    qaz_1_bei_lv = 128.8 + yuan_li_bei_lv
    qaz_2_bei_lv = 155.5 +  yuan_li_bei_lv

    if has_ye_lan and ye_lan_ming_zuo_num == 6:
        ye_lan_bonus = YeLanQBonus()
        ye_lan_bonus.start(3.567)

        # 和满命夜兰配队不能采用az打法，因为时间只够打2次az，虽然2次az比5a伤害还高些，但只能触发两次回能，5a能触发3次
        # 和满命夜兰配队本来就因为影宝砍不满导致充能压力大，所以5a是最理想的

        q_damage = all_atk * meng_xiang_yi_dao_bei_lv / 100 * (elem_bonus + ye_lan_bonus.bonus(11.319))
        qa1_damage = all_atk * qa1_bei_lv / 100 * (elem_bonus + ye_lan_bonus.bonus(11.752))
        qa2_damage = all_atk * qa2_bei_lv / 100 * (elem_bonus + ye_lan_bonus.bonus(12.053))
        qa3_damage = all_atk * qa3_bei_lv / 100 * (elem_bonus + ye_lan_bonus.bonus(12.053))
        qa4_bonus = elem_bonus + ye_lan_bonus.bonus(13.137)
        qa4_damage = all_atk * qa4_1_bei_lv / 100 * qa4_bonus + all_atk * qa4_2_bei_lv / 100 * qa4_bonus
        qa5_damage = all_atk * qa5_bei_lv / 100 * (elem_bonus + ye_lan_bonus.bonus(13.871))

        all_damage = q_damage + qa1_damage + qa2_damage + qa3_damage + qa4_damage + qa5_damage
    else:
        

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

            q_damage = all_atk * meng_xiang_yi_dao_bei_lv / 100 * (elem_bonus + ye_lan_bonus.bonus(12.104))

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

            q_damage = all_atk * meng_xiang_yi_dao_bei_lv / 100 * (elem_bonus + ye_lan_bonus.bonus(11.686))
            
            # monster = Monster(level=93)
            # monster.set_kang_xin(3.7)
            # monster.add_jian_kang(0.4)
            # monster.set_ignore_defence(0.6)
            # print("monster:", monster)
            # meng_xiang_yi_dao_damage = monster.attacked(q_damage)
            # meng_xiang_yi_dao_damage *= crit_damage
            # print(f"all_atk:{all_atk}, elem_bonus: {elem_bonus}, crit_damage: {crit_damage}")
            # print("梦想一刀暴击伤害：", round(meng_xiang_yi_dao_damage))

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
    
    monster = Monster()
    monster.add_jian_kang(0.4) # 万叶
    monster.set_ignore_defence(0.6)
    all_damage = monster.attacked(all_damage)
    
    score_data.damage_to_score(all_damage, crit_rate, crit_damage - 1)

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

def get_debug_raw_score_list():
    # [(jue_yuan, h, cc:0.062, cd:0.21, atkp:0.041, elem:54), 
    # (jue_yuan, y, cc:0.039, cd:0.35, hpp:0.041, def:39), 
    # (lie_ren, s, cc:0.14, cd:0.148, re:0.518, atk:14, def:37),
    # (jue_yuan, b, cc:0.066, cd:0.218, re:0.058, atkp:0.466, def:39), 
    # (jue_yuan, t, cc:0.311, cd:0.256, hp:209, re:0.104, atkp:0.047)]
    syw_combine = [
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_HUA,
                  crit_rate=0.062, crit_damage=0.21, atk_per=0.041, elem_mastery=54),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_YU,
                  crit_rate=0.039, crit_damage=0.35, hp_percent=0.041, def_v=39),
        ShengYiWu(ShengYiWu.LIE_REN, ShengYiWu.PART_SHA, energy_recharge=ShengYiWu.ENERGY_RECHARGE_MAX,
                  crit_rate=0.14, crit_damage=0.148, atk=14, def_v=37),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_BEI, atk_per=ShengYiWu.BONUS_MAX,
                  crit_rate=0.066, crit_damage=0.218, energy_recharge=0.058, def_v=39),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_TOU, crit_rate=ShengYiWu.CRIT_RATE_MAIN,
                  crit_damage=0.256, hp=209, energy_recharge=0.104, atk_per=0.047)
    ]
    return [ShengYiWu_Score(syw_combine)]


def find_syw_for_lei_shen():
    if enable_debug:
        raw_score_list = get_debug_raw_score_list()
    else:
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