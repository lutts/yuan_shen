#!/user/bin/env python3 -tt
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

import sys
import os
import logging
import itertools

from ys_basic import Ys_Elem_Type, ys_expect_damage
from monster import Monster
from base_syw import ShengYiWu, ShengYiWu_Score, calculate_score, Syw_Combine_Desc, find_syw_combine

ming_zuo_num = 6

if ming_zuo_num >= 3:
    q_bei_lv = 15.53
    qx_bei_lv = 10.35
else:
    q_bei_lv = 13.89
    qx_bei_lv = 9.26

if ming_zuo_num >= 1:
    if ming_zuo_num == 6:
        e_bei_lv = 48.1
    else:  # 非满命一般只会升到9
        if ming_zuo_num == 5:
            e_bei_lv = 45.2
        else:
            e_bei_lv = 38.4
else:
    e_bei_lv = 38.4  # 9级

fu_fu_q_bonus = 1.24
wan_ye_bonus = 0.4

ye_lan_base_hp = 14450.0

class YeLanQBonus:
    def __init__(self):
        self.__invalid = False
        self.__stopped = True
        self.__start_time = 0

    def invalidate(self):
        self.__invalid = True

    def start(self, start_time):
        self.__stopped = False
        self.__start_time = start_time

    def bonus(self, checkpoint_time):
        #logging.debug("YeLanQBonus.bonus, checkpoint_time: %s, stopped:%s, invalid:%s, start_time:%s",
        #              round(checkpoint_time, 3), self.__stopped, self.__invalid, round(self.__start_time, 3))
        if self.__stopped or self.__invalid:
            return 0

        dur = checkpoint_time - self.__start_time
        if dur <= 0:
            return 0

        if dur >= 15:
            return 0

        return (1 + int(dur) * 3.5) / 100

    def stop(self):
        self.__stopped = True


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


def scan_syw_combine(combine: list[ShengYiWu], has_fu_fu=True, has_lei_shen=False):
    extra_hp_bonus = {
        "专武": 0.16,
    }

    common_elem_bonus = {
        "专武": 0.2,
        "万叶": wan_ye_bonus,
        "芙芙q": 0,
    }

    extra_crit_damage = {
        "专武": 0.882,
    }

    extra_q_bonus = {
    }

    if has_fu_fu:
        extra_hp_bonus["双水"] = 0.18 + 0.25   # 天赋0.18, 双水0.25
        common_elem_bonus["芙芙q"] = fu_fu_q_bonus  # 除了起手第一个e，所有伤害都能吃到芙芙的增伤

    if has_lei_shen:
        extra_q_bonus["雷神e"] = 70 * 0.003
        if not has_fu_fu:
            extra_hp_bonus["四色"] = 0.3

    crit_rate = 0.242
    crit_damage = 1 + 0.5 + sum(extra_crit_damage.values())
    hp = 4780
    hp_per = sum(extra_hp_bonus.values())
    elem_bonus = 1 + sum(common_elem_bonus.values())
    energy_recharge = 1

    for p in combine:
        crit_rate += p.crit_rate
        crit_damage += p.crit_damage
        hp += p.hp
        hp_per += p.hp_percent
        elem_bonus += p.elem_bonus
        energy_recharge += p.energy_recharge

    crit_rate = round(crit_rate, 3)
    if crit_rate < 0.70:
        return None

    syw_names = [p.name for p in combine]
    # print(syw_names)
    name_count = {i: syw_names.count(i) for i in syw_names}
    # print(name_count)
    for n in name_count:
        if name_count[n] < 2:  # 散件不计算套装效果
            continue

        # print(n)
        if n == ShengYiWu.HUA_HAI:
            hp_per += 0.2
        elif n == ShengYiWu.SHUI_XIAN:
            elem_bonus += 0.15
        elif n == ShengYiWu.QIAN_YAN:
            hp_per += 0.2
        elif n == ShengYiWu.CHEN_LUN:
            elem_bonus += 0.15
        elif n == ShengYiWu.JUE_YUAN:
            if name_count[n] >= 4:
                energy_recharge += 0.2  # 绝缘2件套

    energy_recharge *= 100
    energy_recharge = round(energy_recharge, 1)
    if energy_recharge < 120:
        return None

    if ShengYiWu.JUE_YUAN in name_count and name_count[ShengYiWu.JUE_YUAN] >= 4:
        extra_q_bonus["绝缘4件套"] = min(energy_recharge / 4 / 100, 0.75)

    all_hp = int(ye_lan_base_hp * (1 + hp_per)) + hp
    q_elem_bonus = elem_bonus + sum(extra_q_bonus.values())
    e_po_ju_shi_elem_bonus = elem_bonus

    return (all_hp, q_elem_bonus, e_po_ju_shi_elem_bonus, crit_rate, crit_damage, energy_recharge)

def calculate_score_qualifier(score_data: ShengYiWu_Score, has_fu_fu=True, has_lei_shen=False):
    scan_result = scan_syw_combine(score_data.syw_combine, has_fu_fu, has_lei_shen)
    if not scan_result:
        return False
    
    all_hp, q_elem_bonus, e_po_ju_shi_elem_bonus, crit_rate, crit_damage, energy_recharge = scan_result
    # 以第8秒的破局矢伤害为初步判断依据
    po_ju_shi_bonus = e_po_ju_shi_elem_bonus + (1 + 3.5 * 8)
    # 两次在单怪上e
    hp = all_hp + 0.1 * 2 * ye_lan_base_hp
    damage = hp * 20.84 / 100 * 1.56 * po_ju_shi_bonus

    score_data.damage_to_score(damage, crit_rate, crit_damage - 1)
    score_data.custom_data = scan_result

    return True


def calculate_score_callback(score_data: ShengYiWu_Score, has_fu_fu=True, has_lei_shen=False):
    if score_data.custom_data:
        scan_result = score_data.custom_data
    else:
        scan_result = scan_syw_combine(score_data.syw_combine, has_fu_fu, has_lei_shen)

    if not scan_result:
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


def calculate_score_qualifier_only_fu_fu(score_data: ShengYiWu_Score):
    return calculate_score_qualifier(score_data)

def calculate_score_callback_only_fufu(score_data: ShengYiWu_Score):
    return calculate_score_callback(score_data)

def calculate_score_qualifier_only_lei_shen(score_data: ShengYiWu_Score):
    return calculate_score_qualifier(score_data, False, True)

def calculate_score_callback_only_lei_shen(score_data: ShengYiWu_Score):
    return calculate_score_callback(score_data, False, True)


def match_sha_callback(syw: ShengYiWu):
    return syw.hp_percent == ShengYiWu.BONUS_MAX or syw.energy_recharge == ShengYiWu.ENERGY_RECHARGE_MAX


def match_bei_callback(syw: ShengYiWu):
    return syw.hp_percent == ShengYiWu.BONUS_MAX or syw.elem_type == Ys_Elem_Type.SHUI


def match_tou_callback(syw: ShengYiWu):
    return syw.crit_rate == ShengYiWu.CRIT_RATE_MAIN or syw.crit_damage == ShengYiWu.CRIT_DAMAGE_MAIN or syw.hp_percent == ShengYiWu.BONUS_MAX


def get_raw_score_list():
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
                           #calculate_score_qualifier=calculate_score_qualifier_only_fu_fu
                           )


def find_syw_for_ye_lan_with_lei_shen():
    return calculate_score(get_raw_score_list(),
                           calculate_score_callbak=calculate_score_callback_only_lei_shen,
                           result_txt_file="ye_lan_syw_with_lei_shen.txt",
                           result_description=result_description,
                           #calculate_score_qualifier=calculate_score_qualifier_only_lei_shen
                           )


# Main body
if __name__ == '__main__':
    find_syw_for_ye_lan_with_lei_shen()
