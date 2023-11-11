#!/user/bin/env python3 -tt
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

import sys
import os
import logging
import itertools
from base_syw import ShengYiWu, all_syw_exclude_s_b, find_syw
from ye_lan_shui_shen_syw import hua_hai, qian_yan, chen_lun, shui_xian, syw_s_b

ju_tuan = [
    ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_HUA, crit_rate=0.14, atk=14, crit_damage=0.078, energe_recharge=0.168),
    ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_HUA, crit_rate=0.07, crit_damage=0.194, atk=39, def_per=0.058),
    ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_HUA, hp_percent=0.117, elem_mastery=16, crit_damage=0.163, energe_recharge=0.11),
    ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_HUA, crit_damage=0.14, def_per=0.131, crit_rate=0.066, atk=33),
    ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_HUA, crit_damage=0.21, hp_percent=0.152, crit_rate=0.031, def_v=23),

    ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_YU, hp=568, crit_damage=0.21, hp_percent=0.053, def_v=56),
    ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_YU, def_v=37, elem_mastery=40, crit_damage=0.256, crit_rate=0.027),
    ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_YU, def_v=37, hp_percent=0.163, def_per=0.109, crit_damage=0.14),
    ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_YU, hp_percent=0.14, elem_mastery=19, crit_rate=0.097, energe_recharge=0.052),
    ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_YU, elem_mastery=37, energe_recharge=0.11, crit_damage=0.14, crit_rate=0.07),

    ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_SHA, energe_recharge=0.045, crit_damage=0.078, crit_rate=0.113, def_v=60),

    ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_BEI, crit_damage=0.132, energe_recharge=0.11, def_v=62, def_per=0.073, elem_bonus=0.466),
    
    ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_TOU, hp_percent=0.466, crit_damage=0.202, crit_rate=0.074, def_per=0.066, def_v=63),
    ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_TOU, crit_rate=0.311, def_v=37, hp=239, atk=33, hp_percent=0.157),
    ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_TOU, crit_rate=0.311, def_v=39, elem_mastery=44, hp=896, crit_damage=0.078),
    ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_TOU, crit_damage=0.622, hp=478, hp_percent=0.111, atk_per=0.087, crit_rate=0.066),
    ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_TOU, crit_damage=0.622, crit_rate=0.062, energe_recharge=0.097, def_v=32, def_per=0.131),
]

def find_combine(all_swy):
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
    
    #print(len(all_combins))
    #print(len(set(all_combins)))
    return all_combins


def calc_score(hp, e_bonus, q_bonus, crit_rate, crit_damage):
    """
    计算分数时，按一轮循环中以下攻击次数计算
    夫人：13次，倍率6.87， 13*6.87=89.31
    勋爵：7次，倍率12.67，7*12.67=88.69
    螃蟹：4.5次，倍率17.61, 4.5*17.61=79.245
    满命6下，一半算黑芙，一半算白芙，3 * 18% + 3 * 33% = 153%，这6下时增伤很可能还没满
    """

    e_extra_damage = 1.4 # 队友大于50%血量，e技能伤害为原来的1.4倍 （注：实测为1.542倍)

    fu_ren_damage_non_crit = hp * 6.87 / 100 * e_bonus * 13 * e_extra_damage
    fu_ren_damage_crit = fu_ren_damage_non_crit * crit_damage
    fu_ren_damage_expect = fu_ren_damage_non_crit * (1 + crit_rate * (crit_damage - 1))

    xun_jue_damage_non_crit = hp * 12.67 / 100 * e_bonus * 7 * e_extra_damage
    xun_jue_damage_crit = xun_jue_damage_non_crit * crit_damage
    xun_jue_damage_expect = xun_jue_damage_non_crit * (1 + crit_rate * (crit_damage - 1))

    pang_xie_damage_non_crit = hp * 17.61 / 100 * e_bonus * 4.5 * e_extra_damage
    pang_xie_damage_crit = pang_xie_damage_non_crit * crit_damage
    pang_xie_damage_expect = pang_xie_damage_non_crit * (1 + crit_rate * (crit_damage - 1))

    # 以下按 芙芙qea 切万叶 切芙芙azaaa计算，前三个aaz为黑芙，后三个aaa为白芙
    bai_fu_full_six_damage_non_crit = hp * (18 + 25) / 100 * q_bonus * 3
    hei_fu_full_six_damage_non_crit = hp * 18 / 100 * q_bonus * 3
    full_six_damage_non_crit = bai_fu_full_six_damage_non_crit + hei_fu_full_six_damage_non_crit
    full_six_damage_crit = full_six_damage_non_crit * crit_damage
    full_six_damage_expect = full_six_damage_non_crit * (1 + crit_rate * (crit_damage - 1))
    
    all_crit = fu_ren_damage_crit + xun_jue_damage_crit + pang_xie_damage_crit + full_six_damage_crit
    all_expect = fu_ren_damage_expect + xun_jue_damage_expect + pang_xie_damage_expect + full_six_damage_expect

    return (all_crit, all_expect)

def calculate_score(combine):
    YeLan_Max_Hp = 15307.0
    base_hp = int(YeLan_Max_Hp * (1 
                            + 0.28 # 专武叠满两层
                            + 0.466 # 生命沙
                            + 1.0  # 二命
                            + 0.25  # 双水
                            + 0.2 # 夜兰四命保底两个e
                            )) + 4780
    base_crit_damage = 1 + 0.5 + 0.882
    wan_ye_bonus = 0.4
    shui_shen_bonus = 1.24
    zhuan_wu_e_bonus = 0.08 * 3
    ye_lan_bonus = 0.25 # 夜兰平均增伤
    base_e_bonus = 1 + wan_ye_bonus + shui_shen_bonus + zhuan_wu_e_bonus + ye_lan_bonus
    base_q_bonus = 1 + wan_ye_bonus + shui_shen_bonus + ye_lan_bonus

    crit_rate = sum([p.crit_rate for p in combine]) + 0.242
    if crit_rate < 0.70:
        return None

    hp = sum([p.hp for p in combine])
    hp_per = sum([p.hp_percent for p in combine])
    extra_crit_damage = sum([p.crit_damage for p in combine])
    extra_water_bonus = sum([p.elem_bonus for p in combine])
    total_energe_recharge = (sum([p.energe_recharge for p in combine]) + 1) * 100

    if total_energe_recharge < 107:
        return None
    
    extra_e_bonus = 0

    syw_names = [p.name for p in combine]
    #print(syw_names)
    name_count = {i:syw_names.count(i) for i in syw_names}
    #print(name_count)
    for n in name_count:
        if name_count[n] < 2:  # 散件不计算套装效果
            continue

        #print(n)
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
            else:
                extra_e_bonus += 0.2 + 0.25 + 0.25

    all_hp = hp_per * YeLan_Max_Hp + hp + base_hp
    all_crit_damage = base_crit_damage + extra_crit_damage
    e_bonus = base_e_bonus + extra_e_bonus + extra_water_bonus
    q_bonus = base_q_bonus + extra_water_bonus

    crit_score, expect_score = calc_score(all_hp, e_bonus, q_bonus, crit_rate, all_crit_damage)
    panel_hp = YeLan_Max_Hp * (1 + 0.466 + hp_per) + 4780 + hp

    # print('all_hp:' + str(all_hp))
    # print("e_bonus:" + str(e_bonus))
    # print("q_bonus:" + str(q_bonus))
    # print('crit_rate:' + str(crit_rate))
    # print('crit_damage:' + str(all_crit_damage))
    # print("crit_score:" + str(crit_score))
    # print("expect_score:" + str(expect_score))
    # print('-----------------------------')

    return [expect_score, crit_score, int(all_hp), int(panel_hp), round(crit_rate, 3), round(all_crit_damage - 1, 3), round(total_energe_recharge, 1), combine]

# Main body
if __name__ == '__main__':
    find_syw(syw_s_b, find_combine, calculate_score, "fu_ling_na_syw.txt")
