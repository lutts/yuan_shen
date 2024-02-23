#!/user/bin/env python3 -tt
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

import sys
import os
import logging
import itertools
from character import Character

from ys_basic import Ys_Elem_Type, ys_expect_damage
from ys_weapon import Ruo_Shui_Arrow
from monster import Monster
from characters import Ye_Lan_Ch, Ying_Bao_Ch, YeLan_Q_Bonus_Action, YeLanQBonus
from wan_ye import get_wan_ye_e_bonus, get_wan_ye_q_bonus
from ys_syw import ShengYiWu, ShengYiWu_Score, calculate_score, Syw_Combine_Desc, find_syw_combine

enable_debug = True

def calc_qx_and_po_ju_shi_damage(all_hp, q_elem_bonus, e_po_ju_shi_elem_bonus, qx_damage_timestamps,
                                 extra_qx_damage_timestamps, po_ju_shi_timestamps, ye_lan_q_bonus, e3_timestamp):
    all_damage = 0
    for tf in qx_damage_timestamps:
        t, in_front = tf
        if in_front:
            qx_bonus = q_elem_bonus + ye_lan_q_bonus.bonus(t)
        else:
            qx_bonus = q_elem_bonus
        hp = all_hp
        if e3_timestamp != 0 and t > e3_timestamp and ming_zuo_num >= 4:
            hp += int(0.1 * ye_lan_base_hp)
        all_damage += hp * qx_bei_lv / 100 * qx_bonus

    if ming_zuo_num >= 2:
        for tf in extra_qx_damage_timestamps:
            t, in_front = tf
            if in_front:
                qx_bonus = q_elem_bonus + ye_lan_q_bonus.bonus(t)
            else:
                qx_bonus = q_elem_bonus
            hp = all_hp
            if e3_timestamp != 0 and t > e3_timestamp and ming_zuo_num >= 4:
                hp += int(0.1 * ye_lan_base_hp)
            all_damage += hp * 14 / 100 * qx_bonus

    if ming_zuo_num == 6:
        for t in po_ju_shi_timestamps:
            po_ju_shi_bonus = e_po_ju_shi_elem_bonus + ye_lan_q_bonus.bonus(t)
            hp = all_hp
            if e3_timestamp != 0 and t > e3_timestamp and ming_zuo_num >= 4:
                hp += int(0.1 * ye_lan_base_hp)
            all_damage += hp * 20.84 / 100 * 1.56 * po_ju_shi_bonus

    return all_damage

def calc_score_with_fu_fu_2(all_hp, q_elem_bonus, e_po_ju_shi_elem_bonus, crit_rate, crit_damage):
    all_damage = 0

    # 第一个e 3/4芙芙增伤
    e1_damage = all_hp * e_bei_lv / 100 * (e_po_ju_shi_elem_bonus - fu_fu_q_bonus / 4)

    # 一个e最后增加10%
    if ming_zuo_num >= 4:
        all_hp += int(0.1 * ye_lan_base_hp)

    # 按350层算
    q_damage = all_hp * q_bei_lv / 100 * (q_elem_bonus - 50 * fu_fu_q_bonus / 400)

    ye_lan_q_bonus = YeLanQBonus()
    ye_lan_q_bonus.start(14.896)

    # 第二个e满层
    if ming_zuo_num >= 1:
        e2_damage = e2_damage = all_hp * e_bei_lv / 100 * (e_po_ju_shi_elem_bonus + ye_lan_q_bonus.bonus(15.879))
        # 再增加10%
        if ming_zuo_num >= 4:
            all_hp += int(0.1 * ye_lan_base_hp)
    else:
        e2_damage = 0

    e3_timestamp = 24.614
    e3_damage = all_hp * e_bei_lv / 100 * \
        (e_po_ju_shi_elem_bonus + ye_lan_q_bonus.bonus(e3_timestamp))

    qx_damage_timestamps = [
        (16.162, True), (16.362, True), (16.479, True),
        # 芙芙站场，吃不到Q增伤
        (17.596, False), (17.729, False), (17.812, False),
        (18.45, False), (18.596, False), (18.679, False),
        # 夜兰再次站场
        (21.847, True), (22.065, True), (22.164, True),
        (22.947, True), (23.065, True), (23.164, True),
        (23.914, True), (24.065, True), (24.164, True),
        (24.881, True), (24.931, True), (25.147, True),
        (25.164, True), (25.264, True), (25.264, True),
        # 芙芙大招消失
        # 25.98, 26.164, 26.264
    ]

    extra_qx_damage_timestamps = [
        (16.196, True), 
        (18.596, False), 
        (21.847, True), 
        (23.914, False), 
        # 芙芙大招消失
        # 25.98
    ]

    po_ju_shi_timestamps = [
        21.847, 22.164, 22.581, 23.164, 23.414
    ]

    all_damage = e1_damage + e2_damage + q_damage + e3_damage

    all_damage += calc_qx_and_po_ju_shi_damage(all_hp, q_elem_bonus, e_po_ju_shi_elem_bonus,
                                               qx_damage_timestamps, extra_qx_damage_timestamps, 
                                               po_ju_shi_timestamps, ye_lan_q_bonus, e3_timestamp)

    crit_score = all_damage * crit_damage
    expect_score = ys_expect_damage(all_damage, crit_rate, crit_damage - 1)

    return (expect_score, crit_score)
    


def calc_score_with_fu_fu(all_hp, q_elem_bonus, e_po_ju_shi_elem_bonus, crit_rate, crit_damage):
    all_damage = 0

    # 起手第一个e没有任何增伤
    e1_damage = all_hp * e_bei_lv / 100 * \
        (e_po_ju_shi_elem_bonus - fu_fu_q_bonus - wan_ye_bonus)
    
    if ming_zuo_num >= 4:
        all_hp += int(0.1 * ye_lan_base_hp)

    if ming_zuo_num >= 1:
        # 第二个e能吃到芙芙的满层增伤
        e2_damage = all_hp * e_bei_lv / 100 * e_po_ju_shi_elem_bonus
        if ming_zuo_num >= 4:
            all_hp += int(0.1 * ye_lan_base_hp)
    else:
        e2_damage = 0

    q_damage = all_hp * q_bei_lv / 100 * q_elem_bonus

    ye_lan_q_bonus = YeLanQBonus()
    ye_lan_q_bonus.start(13.71)

    e3_timestamp = 20.422

    e3_damage = all_hp * e_bei_lv / 100 * \
        (e_po_ju_shi_elem_bonus + ye_lan_q_bonus.bonus(e3_timestamp))

    qx_damage_timestamps = [
        # 芙芙站场
        (16.054, False), (16.287, False), (16.371, False),
        (16.954, False), (17.036, False), (17.187, False),
        # 夜兰站场
        (20.822, True), (20.956, True), (20.956, True),
        (20.989, True), (21.289, True), (21.406, True),
        (22.056, True), (22.139, True), (22.239, True),
        (23.222, True), (23.272, True), (23.372, True),
        (24.271, True), (24.372, True), (24.472, True),

        (25.372, True), (25.471, True), (25.589, True),
    ]

    extra_qx_damage_timestamps = [
        (16.054, False), 
        (20.706, True), 
        (23.158, True), 

        (25.172, True)
    ]

    po_ju_shi_timestamps = [
        21.022, 21.289, 21.689, 22.272, 22.472
    ]

    all_damage = e1_damage + e2_damage + q_damage + e3_damage

    all_damage += calc_qx_and_po_ju_shi_damage(all_hp, q_elem_bonus, e_po_ju_shi_elem_bonus,
                                               qx_damage_timestamps, extra_qx_damage_timestamps, 
                                               po_ju_shi_timestamps, ye_lan_q_bonus, e3_timestamp)

    return all_damage


def calc_score_with_lei_shen(all_hp, q_elem_bonus, e_po_ju_shi_elem_bonus, crit_rate, crit_damage):
    e1_damage = all_hp * e_bei_lv / 100 * e_po_ju_shi_elem_bonus
    q_damage = all_hp * q_bei_lv / 100 * q_elem_bonus

    ye_lan_q_bonus = YeLanQBonus()
    ye_lan_q_bonus.start(3.567)

    if ming_zuo_num >= 1:
        e_bonus = e_po_ju_shi_elem_bonus + ye_lan_q_bonus.bonus(4.636)
        e2_damage = all_hp * e_bei_lv / 100 * e_bonus
    else:
        e2_damage = 0

    qx_damage_timestamps = [
        (4.968, True), (5.186, True), (5.286, True),
        # 雷神站场
        (11.869, False), (12.053, False), (12.171, False),
        (12.704, False), (12.821, False), (12.904, False),
        (13.771, False), (13.854, False), (13.921, False),
        # 万叶站场
        (15.437, False), (15.571, False), (15.671, False),
        # 夜兰站场
        (17.471, True), (17.637, True), (17.754, True),
        (18.504, True), (18.504, True), (18.504, True)
    ]

    extra_qx_damage_timestamps = [
        (4.968, True), 
        (11.786, False), 
        (13.771, False), 
        (17.471, True)
    ]

    po_ju_shi_timestamps = [
        17.471, 17.754, 18.171, 18.754, 18.970
    ]

    all_damage = e1_damage + q_damage + e2_damage

    all_damage += calc_qx_and_po_ju_shi_damage(all_hp, q_elem_bonus, e_po_ju_shi_elem_bonus,
                                               qx_damage_timestamps, extra_qx_damage_timestamps, 
                                               po_ju_shi_timestamps, ye_lan_q_bonus, 0)

    return all_damage

def create_ye_lan(syw_combine: list[ShengYiWu], teammate_elem_types: list[Ys_Elem_Type]):
    weapon = Ruo_Shui_Arrow(base_atk=542, crit_damage=0.882)
    ye_lan = Ye_Lan_Ch(weapon, teammate_elem_types)
    ye_lan.set_syw_combine(syw_combine)

    crit_rate = round(crit_rate, 3)
    if crit_rate < 0.70:
        return None

    name_count = ye_lan.get_syw_name_count()
    # print(name_count)
    for n in name_count:
        if name_count[n] < 2:  # 散件不计算套装效果
            continue

        # print(n)
        if n == ShengYiWu.HUA_HAI:
            ye_lan.get_hp().modify_max_hp_per(0.2)
        elif n == ShengYiWu.SHUI_XIAN:
            ye_lan.add_all_bonus(0.15)
        elif n == ShengYiWu.QIAN_YAN:
            ye_lan.get_hp().modify_max_hp_per(0.2)
        elif n == ShengYiWu.CHEN_LUN:
            ye_lan.add_all_bonus(0.15)
        elif n == ShengYiWu.JUE_YUAN:
            ye_lan.add_energy_recharge(0.2)
            if name_count[n] >= 4:
                energy_recharge = ye_lan.get_energy_recharge()
                jue_yuan_bonus = min(energy_recharge / 4 / 100, 0.75)
                ye_lan.add_q_bonus(jue_yuan_bonus)

    energy_recharge = ye_lan.get_energy_recharge()
    if energy_recharge < 120:
        return None

    return ye_lan

def create_ye_lan_for_lei_ye_wan_ban(syw_combine: list[ShengYiWu]):
    ye_lan = create_ye_lan(syw_combine, [Ys_Elem_Type.LEI, Ys_Elem_Type.FENG, Ys_Elem_Type.HUO])
    if ye_lan:
        ye_lan.add_q_bonus(Ying_Bao_Ch.get_bonus_to_q(ye_lan.q_energy))
    return ye_lan

def create_ye_lan_for_lei_ye_xiang_ban(syw_combine: list[ShengYiWu]):
    ye_lan = create_ye_lan(syw_combine, [Ys_Elem_Type.LEI, Ys_Elem_Type.HUO, Ys_Elem_Type.HUO])
    if ye_lan:
        ye_lan.add_q_bonus(Ying_Bao_Ch.get_bonus_to_q(ye_lan.q_energy))
    return ye_lan

def create_ye_lan_for_ying_ye_fu_qin(syw_combine: list[ShengYiWu]):
    ye_lan = create_ye_lan(syw_combine, [Ys_Elem_Type.LEI, Ys_Elem_Type.SHUI, Ys_Elem_Type.FENG])
    if ye_lan:
        ye_lan.add_q_bonus(Ying_Bao_Ch.get_bonus_to_q(ye_lan.q_energy))
    return ye_lan

def create_ye_lan_for_ye_fu_wan_zhong(syw_combine: list[ShengYiWu]):
    return create_ye_lan(syw_combine, [Ys_Elem_Type.SHUI, Ys_Elem_Type.FENG, Ys_Elem_Type.YAN])

def calc_score_for_ye_fu_wan_zhong(score_data: ShengYiWu_Score):
    ye_lan = create_ye_lan_for_ye_fu_wan_zhong(score_data.syw_combine)
    if not ye_lan:
        return False
    
    monster = Monster(level=93)

    total_damage = 0

    # 钟离 e
    monster.add_jian_kang(0.2)

    # 芙芙 qeaa
    # 万叶 q
    monster.add_jian_kang(0.4)
    ye_lan.add_all_bonus(get_wan_ye_e_bonus())

    # 夜兰 eqe
    first_e_fufu_qi_bonus = 300 * 0.0031
    q_fufu_qi_bonus = 350 * 0.0031
    second_e_fufu_qi_bonus = 400 * 0.0031

    ye_lan.add_all_bonus(first_e_fufu_qi_bonus)
    total_damage += ye_lan.get_e_damage(monster)
    if ye_lan.ming_zuo_num >= 4:
        ye_lan.get_hp().modify_max_hp_per(0.1)

    ye_lan.add_all_bonus(q_fufu_qi_bonus - first_e_fufu_qi_bonus)
    total_damage += ye_lan.get_q_damage(monster)

    ye_lan_q_bonus = YeLanQBonus()
    ye_lan_q_bonus.start(14.896)

    ye_lan.add_all_bonus(second_e_fufu_qi_bonus - q_fufu_qi_bonus)

    if ye_lan.ming_zuo_num >= 1:
        total_damage += ye_lan.get_e_damage(monster)
        if ye_lan.ming_zuo_num >= 4:
            ye_lan.get_hp().modify_max_hp_per(0.1)




    
    

    return True

def calculate_score_callback(score_data: ShengYiWu_Score, has_fu_fu=True, has_lei_shen=False):
    ye_lan = create_ye_lan_for_ye_fu_wan_zhong(score_data.syw_combine)
    if not ye_lan:
        return False
    
    all_hp, q_elem_bonus, e_po_ju_shi_elem_bonus, crit_rate, crit_damage, energy_recharge = scan_result

    monster = Monster()

    if has_fu_fu:
        monster.add_jian_kang(0.2) # 钟离
        damage = calc_score_with_fu_fu(
            all_hp, q_elem_bonus, e_po_ju_shi_elem_bonus, crit_rate, crit_damage)
    else:
        damage = calc_score_with_lei_shen(
            all_hp, q_elem_bonus, e_po_ju_shi_elem_bonus, crit_rate, crit_damage)

    damage = monster.attacked(damage)
    score_data.damage_to_score(damage, crit_rate, crit_damage - 1)
    score_data.custom_data = [int(all_hp), round(e_po_ju_shi_elem_bonus, 3), 
                              round(crit_rate, 3), round(crit_damage - 1, 3), 
                              round(energy_recharge, 1)]
    return True


result_description = ", ".join(["出战生命值上限", "实战元素伤害加成", "暴击率", "暴击伤害", "充能效率"])


def calculate_score_callback_only_fufu(score_data: ShengYiWu_Score):
    return calculate_score_callback(score_data)


def calculate_score_callback_only_lei_shen(score_data: ShengYiWu_Score):
    return calculate_score_callback(score_data, False, True)


def match_sha_callback(syw: ShengYiWu):
    return syw.hp_percent == ShengYiWu.BONUS_MAX or syw.energy_recharge == ShengYiWu.ENERGY_RECHARGE_MAX


def match_bei_callback(syw: ShengYiWu):
    return syw.hp_percent == ShengYiWu.BONUS_MAX or syw.elem_type == Ys_Elem_Type.SHUI


def match_tou_callback(syw: ShengYiWu):
    return syw.crit_rate == ShengYiWu.CRIT_RATE_MAIN or syw.crit_damage == ShengYiWu.CRIT_DAMAGE_MAIN or syw.hp_percent == ShengYiWu.BONUS_MAX


def get_debug_raw_score_list():
    syw_combine_str_lst = ["(hua_hai, h, cc:0.035, cd:0.218, hpp:0.157, atk:31)",
                           "(hua_hai, y, cc:0.027, cd:0.28, re:0.123, def:23)",
                           "(shui_xian, s, cc:0.074, cd:0.218, hpp:0.466, re:0.091, atk:18)",
                           "(shui_xian, b, cc:0.074, hpp:0.204, hp:209, atk:16, bonus:0.466)",
                           "(jue_dou_shi, t, cc:0.311, cd:0.303, hpp:0.053, hp:209, atk:39)"
                           ]
    return [ShengYiWu_Score(ShengYiWu.string_to_syw_combine(syw_combine_str_lst))]


def get_raw_score_list():
    if enable_debug:
        return get_debug_raw_score_list
    
    combine_desc_lst = Syw_Combine_Desc.any_2p2([ShengYiWu.HUA_HAI,
                                                 ShengYiWu.QIAN_YAN,
                                                 ShengYiWu.CHEN_LUN,
                                                 ShengYiWu.SHUI_XIAN])

    combine_desc_lst.append(Syw_Combine_Desc(set1_name=ShengYiWu.JUE_YUAN, set1_num=4))

    raw_score_list = find_syw_combine(combine_desc_lst,
                                      match_sha_callback=match_sha_callback,
                                      match_bei_callback=match_bei_callback,
                                      match_tou_callback=match_tou_callback)
    print(len(raw_score_list))
    return  raw_score_list


def find_syw_for_ye_lan_with_fu_fu():
    return calculate_score(get_raw_score_list(),
                           calculate_score_callbak=calculate_score_callback_only_fufu,
                           result_txt_file="ye_lan_syw_with_fu_fu.txt",
                           result_description=result_description,
                           )


def find_syw_for_ye_lan_with_lei_shen():
    return calculate_score(get_raw_score_list(),
                           calculate_score_callbak=calculate_score_callback_only_lei_shen,
                           result_txt_file="ye_lan_syw_with_lei_shen.txt",
                           result_description=result_description,
                           )


# Main body
if __name__ == '__main__':
    find_syw_for_ye_lan_with_fu_fu()
