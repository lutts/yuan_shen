#!/user/bin/env python3 -tt
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

from base_syw import ShengYiWu

hua_hai = [
    ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_HUA, elem_mastery=82, atk=19, hp_percent=0.122, def_v=19),
    ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_HUA, crit_rate=0.035, crit_damage=0.218, hp_percent=0.157, atk=31),
    ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_HUA, crit_rate=0.14, atk_per=0.117, crit_damage=0.07, energe_recharge=0.045),
    ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_HUA, crit_damage=0.078, crit_rate=0.148, elem_mastery=16, atk_per=0.099),
    ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_HUA, crit_damage=0.218, def_per=0.073, hp_percent=0.105, energe_recharge=0.104),
    ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_YU, def_v=23, crit_rate=0.027, crit_damage=0.028, energe_recharge=0.123),
    ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_SHA, energe_recharge=0.052, crit_damage=0.202, elem_mastery=44, crit_rate=0.062),
    ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_BEI, hp_percent=0.163, crit_damage=0.14, energe_recharge=0.052, atk=27, elem_bonus=0.466),
    ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_TOU, crit_damage=0.622, atk=18, def_v=56, atk_per=0.105, crit_rate=0.093),
    ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_TOU, crit_damage=0.622, def_per=0.058, hp=687, hp_percent=0.111, crit_rate=0.07),
]

qian_yan = [
    ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_HUA, crit_damage=0.132, crit_rate=0.101, atk=16, energe_recharge=0.175),
    ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_HUA, def_v=39, atk=16, crit_damage=0.241, crit_rate=0.066),
    ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_HUA, energe_recharge=0.117, atk=14, atk_per=0.117, crit_damage=0.264),
    ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_YU, crit_damage=0.132, energe_recharge=0.175, crit_rate=0.101, hp_percent=0.041),
    ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_YU, atk_per=0.111, energe_recharge=0.117, hp_percent=0.21, def_per=0.073),
    ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_YU, def_v=23, crit_rate=0.031, hp=478, hp_percent=0.216),
    ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_SHA, crit_rate=0.066, atk=33, elem_mastery=40, crit_damage=0.21),
    ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_SHA, elem_mastery=44, atk=16, energe_recharge=0.058, crit_damage=0.272),
    ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_BEI, hp=717, hp_percent=0.146, def_per=0.073, crit_damage=0.07, elem_bonus=0.466),
    ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_TOU, hp_percent=0.466, hp=209, crit_rate=0.074, atk=18, crit_damage=0.241),
]

chen_lun = [
    ShengYiWu(ShengYiWu.CHEN_LUN, ShengYiWu.PART_HUA, crit_rate=0.066, crit_damage=0.148, hp_percent=0.146, def_per=0.109),
    ShengYiWu(ShengYiWu.CHEN_LUN, ShengYiWu.PART_HUA, crit_damage=0.054, energe_recharge=0.065, crit_rate=0.132, def_v=39),
    ShengYiWu(ShengYiWu.CHEN_LUN, ShengYiWu.PART_YU, crit_rate=0.14, atk_per=0.053, hp=478, crit_damage=0.109),
    ShengYiWu(ShengYiWu.CHEN_LUN, ShengYiWu.PART_YU, crit_damage=0.14, def_per=0.16, crit_rate=0.101, hp=239),
    ShengYiWu(ShengYiWu.CHEN_LUN, ShengYiWu.PART_YU, def_v=16, crit_damage=0.117, crit_rate=0.124, atk_per=0.041),
    ShengYiWu(ShengYiWu.CHEN_LUN, ShengYiWu.PART_YU, hp_percent=0.047, def_per=0.066, energe_recharge=0.065, crit_rate=0.167),
    ShengYiWu(ShengYiWu.CHEN_LUN, ShengYiWu.PART_SHA, hp=448, crit_damage=0.311, def_per=0.073, elem_mastery=40),
    ShengYiWu(ShengYiWu.CHEN_LUN, ShengYiWu.PART_TOU, crit_rate=0.311, energe_recharge=0.058, def_v=37, crit_damage=0.155, hp_percent=0.134),
    ShengYiWu(ShengYiWu.CHEN_LUN, ShengYiWu.PART_TOU, crit_rate=0.311, def_v=44, crit_damage=0.225, energe_recharge=0.097, elem_mastery=23),
]

shui_xian = [
    ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_HUA, energe_recharge=0.123, atk=37, crit_rate=0.039, crit_damage=0.233),
    ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_HUA, elem_mastery=42, crit_rate=0.105, atk=14, hp_percent=0.134),
    ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_YU, crit_damage=0.07, atk_per=0.058, energe_recharge=0.104, crit_rate=0.136),
    ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_YU, crit_damage=0.21, atk_per=0.169, hp=209, hp_percent=0.087),
    ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_YU, def_v=23, crit_rate=0.117, crit_damage=0.194, elem_mastery=23),

    ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_SHA, hp=837, elem_mastery=16, crit_damage=0.257, atk=19),
    ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_SHA, atk=18, energe_recharge=0.091, crit_damage=0.218, crit_rate=0.074),
    ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_SHA, crit_damage=0.078, atk_per=0.087, crit_rate=0.132, def_v=16),

    ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_BEI, crit_rate=0.109, def_v=32, hp=478, hp_percent=0.058, elem_bonus=0.466),
]

syw_s_b = {
    ShengYiWu.PART_SHA: [
        ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_SHA, energe_recharge=0.045, crit_damage=0.078, crit_rate=0.113, def_v=60),
        ShengYiWu(ShengYiWu.LIE_REN, ShengYiWu.PART_SHA, crit_rate=0.027, def_v=23, crit_damage=0.264, hp=478),
        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_SHA, energe_recharge=0.052, crit_damage=0.202, elem_mastery=44, crit_rate=0.062),
        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_SHA, def_v=21, crit_damage=0.187, crit_rate=0.087, atk_per=0.041),
        ShengYiWu(ShengYiWu.ZHUI_YI, ShengYiWu.PART_SHA, atk=19, crit_damage=0.14, elem_mastery=33, crit_rate=0.105),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_SHA, crit_rate=0.066, atk=33, elem_mastery=40, crit_damage=0.21),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_SHA, elem_mastery=44, atk=16, energe_recharge=0.058, crit_damage=0.272),
        ShengYiWu(ShengYiWu.CHEN_LUN, ShengYiWu.PART_SHA, hp=448, crit_damage=0.311, def_per=0.073, elem_mastery=40),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_SHA, energe_recharge=0.091, crit_rate=0.163, crit_damage=0.078, hp=239),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_SHA, crit_rate=0.031, def_v=23, crit_damage=0.295, energe_recharge=0.104),

        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_SHA, hp=837, elem_mastery=16, crit_damage=0.257, atk=19),
        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_SHA, atk=18, energe_recharge=0.091, crit_damage=0.218, crit_rate=0.074),
    ],
    ShengYiWu.PART_BEI: [
        ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_BEI, crit_damage=0.132, energe_recharge=0.11, def_v=62, def_per=0.73, elem_bonus=0.466),
        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_BEI, hp_percent=0.163, crit_damage=0.14, energe_recharge=0.052, atk=27, elem_bonus=0.466),
        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_BEI, crit_rate=0.109, def_v=32, hp=478, hp_percent=0.058, elem_bonus=0.466),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_BEI, hp_percent=0.152, crit_damage=0.194, def_v=19, hp=239, elem_bonus=0.466),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_BEI, hp=717, hp_percent=0.146, def_per=0.073, crit_damage=0.07, elem_bonus=0.466),
        ShengYiWu(ShengYiWu.YUE_TUAN, ShengYiWu.PART_BEI, atk=29, crit_damage=0.241, hp=239, hp_percent=0.099, elem_bonus=0.466),
        ShengYiWu(ShengYiWu.YUE_TUAN,   ShengYiWu.PART_BEI, hp=538, crit_damage=0.078, atk_per=0.152, crit_rate=0.074, elem_bonus=0.466),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_BEI, atk=14, hp_percent=0.14, crit_damage=0.202, hp=269, elem_bonus=0.466),

        ShengYiWu(ShengYiWu.LIE_REN, ShengYiWu.PART_BEI, crit_rate=0.031, crit_damage=0.218, elem_mastery=31, def_v=37, hp_percent=0.466),
        ShengYiWu(ShengYiWu.LIE_REN, ShengYiWu.PART_BEI, energe_recharge=0.045, crit_rate=0.101, atk=18, hp=657, hp_percent=0.466),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_BEI, crit_rate=0.066, crit_damage=0.171, atk=27, energe_recharge=0.045, hp_percent=0.466),

    ],
}