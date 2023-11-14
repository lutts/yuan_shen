#!/user/bin/env python3 -tt
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

import sys
import os
import logging
import itertools
from base_syw import ShengYiWu, calculate_score, find_syw


def match_sha_callback(syw: ShengYiWu):
    return syw.hp_percent == 0.466


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
    ju_tuan = find_syw(
        match_syw_callback=lambda s: match_syw(s, ShengYiWu.JU_TUAN))
    hua_hai = find_syw(
        match_syw_callback=lambda s: match_syw(s, ShengYiWu.HUA_HAI))
    qian_yan = find_syw(
        match_syw_callback=lambda s: match_syw(s, ShengYiWu.QIAN_YAN))
    chen_lun = find_syw(
        match_syw_callback=lambda s: match_syw(s, ShengYiWu.CHEN_LUN))
    shui_xian = find_syw(
        match_syw_callback=lambda s: match_syw(s, ShengYiWu.SHUI_XIAN))

    ju_tuan_4_combins = list(itertools.combinations(ju_tuan, 4))

    ju_tuan_2_combins = list(itertools.combinations(ju_tuan, 2))
    hua_hai_combins = list(itertools.combinations(hua_hai, 2))
    qian_yan_combins = list(itertools.combinations(qian_yan, 2))
    chen_lun_combins = list(itertools.combinations(chen_lun, 2))
    shui_xian_combins = list(itertools.combinations(shui_xian, 2))

    all_combins_2 = hua_hai_combins + qian_yan_combins + \
        chen_lun_combins + shui_xian_combins + ju_tuan_2_combins
    all_combins = [(l[0] + l[1])
                   for l in list(itertools.combinations(all_combins_2, 2))] + ju_tuan_4_combins

    # print(len(all_combins))
    # print(len(set(all_combins)))
    return all_combins

shui_shen_q_bonus = 1.24
fu_ning_na_Max_Hp = 15307.0
ming_2_average_bonus = 1.2  # 二命，按平均1.2算，有可能更高

def calc_score(hp, e_bonus, full_bonus, crit_rate, crit_damage, shui_shen_q_bonus):
    """
    计算分数时，按17秒内攻击次数计算
    夫人：10次，倍率6.87，另外计算7次不吃芙芙大招增伤的伤害
    勋爵：5次，倍率12.67，另外计算3次不吃芙芙大招增伤的伤害
    螃蟹：4次，倍率17.61，另外计算1次不吃芙芙大招增伤的伤害
    满命6下，一半算黑芙，一半算白芙，3 * 18% + 3 * 33% = 153%，这6下时增伤很可能还没满

    第一轮前6秒吃不满增伤
    第二轮及以后，有全队奶的时候，能瞬间叠满
    """

    FU_REN_NUM = 17
    XUN_JUE_NUM = 8
    PANG_XIE_NUM = 5

    FU_REN_NUM_Q = 10
    XUN_JUE_NUM_Q = 5
    PANG_XIE_NUM_Q = 4

    seamless_q = True
    only_e = False

    if seamless_q:
        FU_REN_NUM = FU_REN_NUM_Q
        XUN_JUE_NUM = XUN_JUE_NUM_Q
        PANG_XIE_NUM = PANG_XIE_NUM_Q

    e_extra_damage = 1.4  # 队友大于50%血量，e技能伤害为原来的1.4倍 （注：实测为1.542倍)

    fu_ren_damage_non_crit = hp * 6.87 / 100  * e_extra_damage * (e_bonus * FU_REN_NUM_Q + (e_bonus - shui_shen_q_bonus) * (FU_REN_NUM - FU_REN_NUM_Q))
    fu_ren_damage_crit = fu_ren_damage_non_crit * crit_damage
    fu_ren_damage_expect = fu_ren_damage_non_crit * \
        (1 + crit_rate * (crit_damage - 1))

    xun_jue_damage_non_crit = hp * 12.67 / 100 * e_extra_damage * (e_bonus * XUN_JUE_NUM_Q + (e_bonus - shui_shen_q_bonus) * (XUN_JUE_NUM - XUN_JUE_NUM_Q))
    xun_jue_damage_crit = xun_jue_damage_non_crit * crit_damage
    xun_jue_damage_expect = xun_jue_damage_non_crit * \
        (1 + crit_rate * (crit_damage - 1))

    pang_xie_damage_non_crit = hp * 17.61 / 100 * e_extra_damage * (e_bonus * PANG_XIE_NUM_Q + (e_bonus - shui_shen_q_bonus) * (PANG_XIE_NUM - PANG_XIE_NUM_Q))
    pang_xie_damage_crit = pang_xie_damage_non_crit * crit_damage
    pang_xie_damage_expect = pang_xie_damage_non_crit * \
        (1 + crit_rate * (crit_damage - 1))

    if not only_e:
        # 以下按 芙芙qe 切万叶 切芙芙aazaaz计算，前三个aaz为黑芙，第一轮这三下吃不满q增伤，第二轮要看什么时候切奶妈
        # 后三个aaz为白芙，此时增伤已满，hp是变动的，第一轮平均为0.251，第二轮有全队奶时，能很快吃满
        actual_hei_fu_bonus = full_bonus  # - shui_shen_q_bonus + shui_shen_q_bonus * 0.85
        actual_hei_fu_hp = hp #- int(fu_ning_na_Max_Hp * ming_2_average_bonus)
        actual_bai_fu_hp = hp #- actual_hei_fu_hp + int(fu_ning_na_Max_Hp * 0.251)
        bai_fu_full_six_damage_non_crit = actual_bai_fu_hp * (18 + 25) / 100 * full_bonus * 3
        hei_fu_full_six_damage_non_crit = actual_hei_fu_hp * 18 / 100 * actual_hei_fu_bonus * 3
        full_six_damage_non_crit = bai_fu_full_six_damage_non_crit + \
            hei_fu_full_six_damage_non_crit
        full_six_damage_crit = full_six_damage_non_crit * crit_damage
        full_six_damage_expect = full_six_damage_non_crit * \
            (1 + crit_rate * (crit_damage - 1))
    else:
        full_six_damage_crit = 0
        full_six_damage_expect = 0

    all_crit = fu_ren_damage_crit + xun_jue_damage_crit + \
        pang_xie_damage_crit + full_six_damage_crit
    all_expect = fu_ren_damage_expect + xun_jue_damage_expect + \
        pang_xie_damage_expect + full_six_damage_expect

    return (all_crit, all_expect)


def calculate_score_callback(combine):
    fu_ning_na_Max_Hp = 15307.0
    base_hp = int(fu_ning_na_Max_Hp * (1
                                  + 0.28  # 专武叠满两层
                                  + ming_2_average_bonus
                                  + 0.25  # 双水
                                  + 0.2  # 夜兰四命保底两个e
                                  )) + 4780
    base_crit_damage = 1 + 0.5 + 0.882
    gu_you_tian_fu_2_bonus = 0.28 # 基本是能吃满的
    wan_ye_bonus = 0.4
    zhuan_wu_e_bonus = 0.08 * 3
    fu_ning_na_bonus = 0.25  # 夜兰平均增伤
    base_e_bonus = 1 + wan_ye_bonus + shui_shen_q_bonus + zhuan_wu_e_bonus + fu_ning_na_bonus + gu_you_tian_fu_2_bonus
    base_full_bonus = 1 + wan_ye_bonus + shui_shen_q_bonus + fu_ning_na_bonus

    crit_rate = sum([p.crit_rate for p in combine]) + 0.242
    if crit_rate < 0.70:
        return None

    hp = sum([p.hp for p in combine])
    hp_per = sum([p.hp_percent for p in combine])
    extra_crit_damage = sum([p.crit_damage for p in combine])
    extra_water_bonus = sum([p.elem_bonus for p in combine])
    total_energe_recharge = (
        sum([p.energe_recharge for p in combine]) + 1) * 100

    if total_energe_recharge < 110:
        return None

    extra_e_bonus = 0

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
            extra_water_bonus += 0.15
        elif n == ShengYiWu.QIAN_YAN:
            hp_per += 0.2
        elif n == ShengYiWu.CHEN_LUN:
            extra_water_bonus += 0.15
        elif n == ShengYiWu.JU_TUAN:
            if name_count[n] == 2:
                extra_e_bonus += 0.2
            elif name_count[n] >= 4:
                extra_e_bonus += 0.2 + 0.25 + 0.25

    all_hp = int(hp_per * fu_ning_na_Max_Hp) + hp + base_hp
    all_crit_damage = base_crit_damage + extra_crit_damage
    e_bonus = base_e_bonus + extra_e_bonus + extra_water_bonus
    full_bonus = base_full_bonus + extra_water_bonus

    crit_score, expect_score = calc_score(
        all_hp, e_bonus, full_bonus, crit_rate, all_crit_damage, shui_shen_q_bonus)
    panel_hp = fu_ning_na_Max_Hp * (1 + hp_per) + 4780 + hp

    # print('all_hp:' + str(all_hp))
    # print("e_bonus:" + str(e_bonus))
    # print("full_bonus:" + str(full_bonus))
    # print('crit_rate:' + str(crit_rate))
    # print('crit_damage:' + str(all_crit_damage))
    # print("crit_score:" + str(crit_score))
    # print("expect_score:" + str(expect_score))
    # print('-----------------------------')

    return [expect_score, crit_score, int(all_hp), int(panel_hp), round(e_bonus, 3), round(full_bonus, 3), round(crit_rate, 3), round(all_crit_damage - 1, 3), round(total_energe_recharge, 1), combine]

def find_syw_for_fu_ling_na():
    return calculate_score(find_combine_callback=find_combine_callback,
                    match_sha_callback=match_sha_callback,
                    match_bei_callback=match_bei_callback,
                    calculate_score_callbak=calculate_score_callback,
                    result_txt_file="fu_ling_na_syw.txt")
    

# Main body
if __name__ == '__main__':
    find_syw_for_fu_ling_na()