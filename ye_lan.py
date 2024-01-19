#!/user/bin/env python3 -tt
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

import sys
import os
import logging
import itertools
from base_syw import ShengYiWu, find_syw, calculate_score, calc_expect_score

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


def match_sha_callback(syw: ShengYiWu):
    return syw.hp_percent == 0.466 or syw.energy_recharge == ShengYiWu.energy_recharge_MAX


def match_bei_callback(syw: ShengYiWu):
    return syw.hp_percent == 0.466 or syw.elem_type == ShengYiWu.ELEM_TYPE_SHUI


def match_syw(s: ShengYiWu, expect_name):
    if s.name != expect_name:
        return False

    if s.part == ShengYiWu.PART_SHA:
        return match_sha_callback(s)
    elif s.part == ShengYiWu.PART_BEI:
        return match_bei_callback(s)
    else:
        return True


def find_combine_callback():
    # [(hua_hai, h, cc:0.035, cd:0.218, hpp:0.157, atk:31),
    # (qian_yan, y, cc:0.101, cd:0.132, hpp:0.041, re:0.175),
    # (qian_yan, s, cc:0.066, cd:0.21, hpp:0.466, atk:33, elem:40),
    # (hua_hai, b, cd:0.14, hpp:0.163, re:0.052, atk:27, bonus:0.466),
    # jue_dou_shi, t, cc:0.311, cd:0.303, hpp:0.053, hp:209, atk:39)]]
    # return [
    #     (
    #         ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_HUA,
    #                   crit_rate=0.035, crit_damage=0.218, hp_percent=0.157, atk=31),
    #         ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_YU,
    #                   crit_rate=0.101, crit_damage=0.132, hp_percent=0.041, energy_recharge=0.175),
    #         ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_SHA,
    #                   crit_rate=0.066, crit_damage=0.21, hp_percent=0.466, atk=33, elem_mastery=40),
    #         ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_BEI, elem_bonus=0.466, elem_type=ShengYiWu.ELEM_TYPE_SHUI,
    #                   crit_damage=0.14, hp_percent=0.163, energy_recharge=0.052, atk=27)
    #     )
    # ]
    hua_hai = find_syw(
        match_syw_callback=lambda s: match_syw(s, ShengYiWu.HUA_HAI))
    qian_yan = find_syw(
        match_syw_callback=lambda s: match_syw(s, ShengYiWu.QIAN_YAN))
    chen_lun = find_syw(
        match_syw_callback=lambda s: match_syw(s, ShengYiWu.CHEN_LUN))
    shui_xian = find_syw(
        match_syw_callback=lambda s: match_syw(s, ShengYiWu.SHUI_XIAN))
    jue_yuan = find_syw(
        match_syw_callback=lambda s: match_syw(s, ShengYiWu.JUE_YUAN))

    hua_hai_combins = list(itertools.combinations(hua_hai, 2))
    qian_yan_combins = list(itertools.combinations(qian_yan, 2))
    chen_lun_combins = list(itertools.combinations(chen_lun, 2))
    shui_xian_combins = list(itertools.combinations(shui_xian, 2))

    jue_yuan_4 = list(itertools.combinations(jue_yuan, 4))

    all_combins = hua_hai_combins + qian_yan_combins + \
        chen_lun_combins + shui_xian_combins
    return [(l[0] + l[1])
            for l in list(itertools.combinations(all_combins, 2))] + jue_yuan_4


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
    expect_score = calc_expect_score(all_damage, crit_rate, crit_damage)

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

    crit_score = all_damage * crit_damage
    expect_score = calc_expect_score(all_damage, crit_rate, crit_damage)

    return (expect_score, crit_score)


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

    crit_score = all_damage * crit_damage
    expect_score = calc_expect_score(all_damage, crit_rate, crit_damage)

    return (expect_score, crit_score)


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

def calculate_score_qualifier(combine: list[ShengYiWu], has_fu_fu=True, has_lei_shen=False):
    scan_result = scan_syw_combine(combine, has_fu_fu, has_lei_shen)
    if not scan_result:
        return None
    
    all_hp, q_elem_bonus, e_po_ju_shi_elem_bonus, crit_rate, crit_damage, energy_recharge = scan_result
    # 以第8秒的破局矢伤害为初步判断依据
    po_ju_shi_bonus = e_po_ju_shi_elem_bonus + (1 + 3.5 * 8)
    # 两次在单怪上e
    hp = all_hp + 0.1 * 2 * ye_lan_base_hp
    damage = hp * 20.84 / 100 * 1.56 * po_ju_shi_bonus

    expect_score = calc_expect_score(damage, crit_rate, crit_damage)
    crit_score = damage * crit_damage

    return [expect_score, crit_score, scan_result, combine]


def calculate_score_callback(combine, has_fu_fu=True, has_lei_shen=False):
    if isinstance(combine[-1], list):
        scan_result = combine[3]
        combine = combine[-1]
    else:
        scan_result = scan_syw_combine(combine, has_fu_fu, has_lei_shen)

    if not scan_result:
        return None
    
    all_hp, q_elem_bonus, e_po_ju_shi_elem_bonus, crit_rate, crit_damage, energy_recharge = scan_result

    if has_fu_fu:
        expect_score, crit_score = calc_score_with_fu_fu(
            all_hp, q_elem_bonus, e_po_ju_shi_elem_bonus, crit_rate, crit_damage)
    else:
        expect_score, crit_score = calc_score_with_lei_shen(
            all_hp, q_elem_bonus, e_po_ju_shi_elem_bonus, crit_rate, crit_damage)

    #panel_hp = int(ye_lan_base_hp * (1 + hp_per)) + hp
    return [expect_score, crit_score, int(all_hp), round(e_po_ju_shi_elem_bonus, 3), round(crit_rate, 3), round(crit_damage - 1, 3), 
            round(energy_recharge, 1), combine]


result_description = ["总评分", "期望伤害评分", "暴击伤害评分",
                      "出战生命值上限", "实战元素伤害加成", "暴击率", "暴击伤害", "充能效率", "圣遗物组合"]

def calculate_score_qualifier_only_fu_fu(combine):
    return calculate_score_qualifier(combine)

def calculate_score_callback_only_fufu(combine):
    return calculate_score_callback(combine)

def calculate_score_qualifier_only_lei_shen(combine):
    return calculate_score_qualifier(combine, False, True)

def calculate_score_callback_only_lei_shen(combine):
    return calculate_score_callback(combine, False, True)


def find_syw_for_ye_lan_with_fu_fu():
    return calculate_score(find_combine_callback=find_combine_callback,
                           match_sha_callback=match_sha_callback,
                           match_bei_callback=match_bei_callback,
                           calculate_score_callbak=calculate_score_callback_only_fufu,
                           result_txt_file="ye_lan_syw_with_fu_fu.txt",
                           result_description=result_description,
                           #calculate_score_qualifier=calculate_score_qualifier_only_fu_fu
                           )


def find_syw_for_ye_lan_with_lei_shen():
    return calculate_score(find_combine_callback=find_combine_callback,
                           match_sha_callback=match_sha_callback,
                           match_bei_callback=match_bei_callback,
                           calculate_score_callbak=calculate_score_callback_only_lei_shen,
                           result_txt_file="ye_lan_syw_with_lei_shen.txt",
                           result_description=result_description,
                           #calculate_score_qualifier=calculate_score_qualifier_only_lei_shen
                           )


# Main body
if __name__ == '__main__':
    find_syw_for_ye_lan_with_fu_fu()
