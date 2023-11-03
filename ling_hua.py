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

bing_tao = [
    ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_HUA, atk_per=0.105,
              elem_mastery=19, crit_rate=0.132, energe_recharge=0.11),
    ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_HUA, crit_rate=0.086,
              crit_damage=0.202, elem_mastery=40, energe_recharge=0.052),
    ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_HUA, elem_mastery=16,
              atk_per=0.134, crit_damage=0.132, crit_rate=0.089),
    ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_HUA, def_v=21,
              atk_per=0.134, atk=27, crit_damage=0.218),
    ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_HUA, atk_per=0.099,
              hp_percent=0.099, crit_damage=0.21, energe_recharge=0.058),
    ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_HUA, elem_mastery=16,
              crit_rate=0.039, crit_damage=0.264, def_v=46),
    ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_YU, crit_damage=0.194,
              energe_recharge=0.052, elem_mastery=19, hp_percent=0.233),
    ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_YU, crit_damage=0.14,
              elem_mastery=40, crit_rate=0.101, atk_per=0.105),
    ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_YU, def_v=23,
              crit_rate=0.128, crit_damage=0.07, atk_per=0.099),
    ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_YU, crit_damage=0.256,
              energe_recharge=0.097, def_per=0.058, atk_per=0.041),
    ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_YU, crit_rate=0.066,
              crit_damage=0.21, hp=299, atk_per=0.099),
    ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_SHA,
              crit_rate=0.097, hp=209, crit_damage=0.202, def_v=42),
    ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_BEI,
              atk_per=0.192, hp=299, energe_recharge=0.11, atk=16),
    ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_TOU, crit_rate=0.311,
              atk_per=0.152, elem_mastery=44, crit_damage=0.148),
    ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_TOU, crit_damage=0.622,
              hp=239, elem_mastery=16, crit_rate=0.086, def_v=60),
]

syw_s_b = {
    "s": [
        ShengYiWu('huahai', ShengYiWu.PART_SHA, crit_damage=0.21,
                  hp=568, crit_rate=0.078, hp_percent=0.093),
        ShengYiWu('shenlin', ShengYiWu.PART_SHA, crit_rate=0.109,
                  def_v=32, crit_damage=0.233, hp=209),
        ShengYiWu('shenlin', ShengYiWu.PART_SHA, hp=269,
                  def_v=37, crit_damage=0.124, crit_rate=0.132),
        ShengYiWu('jueyuan', ShengYiWu.PART_SHA, elem_mastery=19,
                  hp_percent=0.105, crit_rate=0.086, crit_damage=0.202),
        ShengYiWu('yuetuan', ShengYiWu.PART_SHA, def_per=0.124,
                  crit_rate=0.101, crit_damage=0.132, atk=19),
        ShengYiWu('bingtao', ShengYiWu.PART_SHA, crit_rate=0.097,
                  hp=209, crit_damage=0.202, def_v=42),
    ],
    "b": [
        ShengYiWu('shenlin', ShengYiWu.PART_BEI, hp=239,
                  crit_rate=0.066, atk_per=0.21, atk=37),
        ShengYiWu('chenlun', ShengYiWu.PART_BEI, def_per=0.058,
                  crit_rate=0.07, crit_damage=0.218, atk=33),
        ShengYiWu('bingtao', ShengYiWu.PART_BEI, atk_per=0.192,
                  hp=299, energe_recharge=0.11, atk=16),
        ShengYiWu('huahai', ShengYiWu.PART_BEI, atk=35,
                  atk_per=0.111, elem_mastery=19, crit_rate=0.128),
    ],
}


def find_combins(all_syw):
    return list(itertools.combinations(bing_tao, 4))


def calculate_score(combine):
    ling_hua_max_atk = 1016
    base_atk = int(ling_hua_max_atk * (1
                                   + 0.2  # 宗室
                                   + 0.48  # 讨龙
                                   + 0.466  # 攻击沙
                                   )) + 311  # 羽毛
    base_crit_damage = 1 + (0.441  # 雾切
                            + 0.884 # 突破加成
                            )

    crit_rate = sum([p.crit_rate for p in combine]) + 0.05
    if crit_rate < 0.4:
        return None
    
    real_crit_rate = crit_rate + (0.15 # 双冰
                                  + 0.2 # 四件套效果之一
                                )

    atk = sum([p.atk for p in combine])
    atk_per = sum([p.atk_per for p in combine])
    extra_crit_damage = sum([p.crit_damage for p in combine])
    total_energe_recharge = (
        sum([p.energe_recharge for p in combine]) + 1) * 100

    if total_energe_recharge < 116.5:
        return None

    # 出战时总攻击力
    all_atk = atk_per * ling_hua_max_atk + atk + base_atk
    # 非出战时面板攻击力
    panel_atk = (1 + atk_per + 0.466) * ling_hua_max_atk + atk + 311

    non_crit_score = all_atk / base_atk
    crit_score = non_crit_score * (base_crit_damage + extra_crit_damage) / base_crit_damage
    expect_crit_damage_bonus = real_crit_rate * (extra_crit_damage + base_crit_damage - 1)
    expect_score = non_crit_score * (1 + expect_crit_damage_bonus)
    return [expect_score, crit_score, int(panel_atk), round(crit_rate, 3), round(base_crit_damage + extra_crit_damage - 1, 3), round(total_energe_recharge, 1), combine]


# Main body
if __name__ == '__main__':
    find_syw(syw_s_b, find_combins, calculate_score, "ling_hua_syw.txt")
