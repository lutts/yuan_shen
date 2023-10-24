#!/user/bin/env python3 -c
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

import sys
import os
import logging
import itertools

class ShengYiWu:
    ALL_PARTS = {'h', 'y', 's', 'b', 't'}
    PART_HUA = 'h'
    PART_YU = 'y'
    PART_SHA = 's'
    PART_BEI = 'b'
    PART_TOU = 't'

    JU_TUAN = 'ju_tuan'
    LIE_REN = 'lie_ren'
    HUA_HAI = 'hua_hai'
    SHUI_XIAN = 'shui_xian'
    LE_YUAN = 'le_yuan'
    SHI_JIN = 'shi_jin'
    SHEN_LIN = 'shen_lin'
    JUE_YUAN = 'jue_yuan'
    ZHUI_YI = 'zhui_yi'
    QIAN_YAN = 'qian_yan'
    CHEN_LUN = 'chen_lun'
    BING_TAO = 'bing_tao'
    RU_LEI = 'ru_lei'
    FENG_TAO = 'feng_tao'
    ZONG_SHI = 'zong_shi'
    YUE_TUAN = 'yue_tuan'
    JUE_DOU_SHI = 'jue_dou_shi'


    def __init__(self, name, part, crit_rate=0.0, crit_damage=0.0, hp_percent=0.0, hp=0, energe_recharge=0.0, atk_per=0.0, atk=0, def_per=0.0, def_v=0, elem_mastery=0):
        self.name = name
        self.part = part
        self.crit_rate = crit_rate
        self.crit_damage = crit_damage
        self.hp_percent = hp_percent
        self.hp = hp
        self.energe_recharge = energe_recharge
        self.atk_per = atk_per
        self.atk = atk
        self.def_per = def_per
        self.def_v = def_v
        self.elem_mastery = elem_mastery

    def __str__(self):
        s = '(' + self.name + ', ' + self.part
        if self.crit_rate:
            s += ', cc:' + str(self.crit_rate)
        
        if self.crit_damage:
            s += ', cd:' + str(self.crit_damage)

        if self.hp_percent:
            s += ', hpp:' + str(self.hp_percent)

        if self.hp:
            s += ', hp:' + str(self.hp)

        if self.energe_recharge:
            s += ', re:' + str(self.energe_recharge)
        
        if self.atk_per:
            s += ', atkp:' + str(self.atk_per)

        if self.atk:
            s += ', atk:' + str(self.atk)
        
        if self.def_per:
            s += ', defp:' + str(self.def_per)

        if self.def_v:
            s += ', def:' + str(self.def_v)

        if self.elem_mastery:
            s += ', elem:' + str(self.elem_mastery)

        s += ')'

        return s

    def __repr__(self) -> str:
        return self.__str__()


all_syw_exclude_s_b = {
    "h": [
        ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_HUA, crit_rate=0.14, atk=14, crit_damage=0.078, energe_recharge=0.168),
        ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_HUA, hp_percent=0.117, elem_mastery=16, crit_damage=0.163, energe_recharge=0.11),
        ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_HUA, crit_damage=0.14, def_per=0.131, crit_rate=0.066, atk=33),
        ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_HUA, crit_damage=0.21, hp_percent=0.152, crit_rate=0.031, def_v=23),
        ShengYiWu(ShengYiWu.LIE_REN, ShengYiWu.PART_HUA, energe_recharge=0.123, crit_rate=0.101, hp_percent=0.053, crit_damage=0.117),
        ShengYiWu(ShengYiWu.LIE_REN, ShengYiWu.PART_HUA, def_per=0.066, crit_damage=0.148, crit_rate=0.105, energe_recharge=0.104),
        ShengYiWu(ShengYiWu.LIE_REN, ShengYiWu.PART_HUA, crit_rate=0.066, crit_damage=0.287, elem_mastery=16, atk_per=0.099),
        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_HUA, elem_mastery=82, atk=19, hp_percent=0.122, def_v=19),
        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_HUA, crit_damage=0.218, crit_rate=0.035, hp_percent=0.157, atk=31),
        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_HUA, crit_rate=0.14, atk_per=0.117, crit_damage=0.07, energe_recharge=0.045),
        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_HUA, crit_damage=0.078, crit_rate=0.148, elem_mastery=16, atk_per=0.099),
        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_HUA, crit_damage=0.218, def_per=0.073, hp_percent=0.105, energe_recharge=0.104),
        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_HUA, energe_recharge=0.123, atk=37, crit_rate=0.039, crit_damage=0.233),
        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_HUA, crit_damage=0.124, hp_percent=0.099, atk=14, crit_rate=0.124),
        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_HUA, crit_damage=0.249, energe_recharge=0.065, def_per=0.066, crit_rate=0.089),
        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_HUA, def_per=0.073, hp_percent=0.146, def_v=35, elem_mastery=56),
        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_HUA, def_v=23, crit_damage=0.272, elem_mastery=44, energe_recharge=0.065),
        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_HUA, crit_damage=0.28, hp_percent=0.099, atk_per=0.053, crit_rate=0.027),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_HUA, energe_recharge=0.11, hp_percent=0.152, crit_rate=0.035, elem_mastery=70),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_HUA, def_v=16, elem_mastery=79, hp_percent=0.093, energe_recharge=0.11),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_HUA, elem_mastery=40, def_v=21, crit_rate=0.027, crit_damage=0.241),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_HUA, hp_percent=0.181, energe_recharge=0.123, def_v=23, crit_rate=0.07),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_HUA, atk_per=0.041, crit_rate=0.062, elem_mastery=54, crit_damage=0.21),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_HUA, crit_rate=0.144, crit_damage=0.078, hp_percent=0.105, elem_mastery=40),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_HUA, elem_mastery=44, crit_damage=0.21, def_per=0.066, energe_recharge=0.194),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_HUA, elem_mastery=21, crit_rate=0.066, energe_recharge=0.181, crit_damage=0.124),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_HUA, atk=33, crit_rate=0.066, atk_per=0.111, crit_damage=0.117),
        ShengYiWu(ShengYiWu.ZHUI_YI, ShengYiWu.PART_HUA, crit_damage=0.132, crit_rate=0.152, energe_recharge=0.097, def_per=0.073),
        ShengYiWu(ShengYiWu.ZHUI_YI, ShengYiWu.PART_HUA, def_v=16, crit_rate=0.035, crit_damage=0.249, atk=29),
        ShengYiWu(ShengYiWu.ZHUI_YI, ShengYiWu.PART_HUA, crit_damage=0.117, hp_percent=0.146, atk_per=0.053, elem_mastery=40),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_HUA, crit_rate=0.062, elem_mastery=51, energe_recharge=0.181, def_per=0.073),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_HUA, crit_damage=0.132, crit_rate=0.101, atk=16, energe_recharge=0.175),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_HUA, def_v=39, atk=16, crit_damage=0.241, crit_rate=0.066),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_HUA, energe_recharge=0.155, atk=35, hp_percent=0.128, atk_per=0.047),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_HUA, hp_percent=0.134, energe_recharge=0.162, crit_rate=0.074, crit_damage=0.078),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_HUA, energe_recharge=0.117, atk=14, atk_per=0.117, crit_damage=0.264),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_HUA, def_per=0.131, energe_recharge=0.175, def_v=37, crit_damage=0.062),
        ShengYiWu(ShengYiWu.CHEN_LUN, ShengYiWu.PART_HUA, crit_rate=0.066, crit_damage=0.148, hp_percent=0.146, def_per=0.109),
        ShengYiWu(ShengYiWu.CHEN_LUN, ShengYiWu.PART_HUA, crit_damage=0.054, energe_recharge=0.065, crit_rate=0.132, def_v=39),
        ShengYiWu(ShengYiWu.ZONG_SHI, ShengYiWu.PART_HUA, def_per=0.124, crit_damage=0.062, hp_percent=0.111, energe_recharge=0.214),
        ShengYiWu(ShengYiWu.ZONG_SHI, ShengYiWu.PART_HUA, energe_recharge=0.227, atk_per=0.058, elem_mastery=44, hp_percent=0.047),
        ShengYiWu(ShengYiWu.ZONG_SHI, ShengYiWu.PART_HUA, crit_damage=0.14, energe_recharge=0.065, atk_per=0.099, crit_rate=0.105),
        ShengYiWu(ShengYiWu.YUE_TUAN, ShengYiWu.PART_HUA, elem_mastery=58, crit_damage=0.148, crit_rate=0.078, def_per=0.051),
        ShengYiWu(ShengYiWu.FENG_TAO, ShengYiWu.PART_HUA, elem_mastery=86, hp_percent=0.041, def_per=0.131, energe_recharge=0.123),
        ShengYiWu(ShengYiWu.FENG_TAO, ShengYiWu.PART_HUA, crit_damage=0.078, energe_recharge=0.065, atk_per=0.146, crit_rate=0.144),
        ShengYiWu(ShengYiWu.FENG_TAO, ShengYiWu.PART_HUA, elem_mastery=72, hp_percent=0.099, atk_per=0.041, energe_recharge=0.052),
        ShengYiWu(ShengYiWu.JUE_DOU_SHI, ShengYiWu.PART_HUA, hp_percent=0.157, crit_damage=0.218, crit_rate=0.078, def_v=16),
        ShengYiWu(ShengYiWu.JUE_DOU_SHI, ShengYiWu.PART_HUA, crit_damage=0.14, crit_rate=0.062, def_v=16, def_per=0.168),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_HUA, atk_per=0.105, elem_mastery=19, crit_rate=0.132, energe_recharge=0.11),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_HUA, crit_rate=0.086, crit_damage=0.202, elem_mastery=40, energe_recharge=0.052),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_HUA, elem_mastery=16, atk_per=0.134, crit_damage=0.132, crit_rate=0.089),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_HUA, def_v=21, atk_per=0.134, atk=27, crit_damage=0.218),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_HUA, atk_per=0.099, hp_percent=0.099, crit_damage=0.21, energe_recharge=0.058),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_HUA, elem_mastery=16, crit_rate=0.039, crit_damage=0.264, def_v=46),
    ],
    "y": [
        ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_YU, def_v=37, elem_mastery=40, crit_damage=0.256, crit_rate=0.027),
        ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_YU, def_v=37, hp_percent=0.163, def_per=0.109, crit_damage=0.14),
        ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_YU, hp_percent=0.14, elem_mastery=19, crit_rate=0.097, energe_recharge=0.052),
        ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_YU, elem_mastery=37, energe_recharge=0.11, crit_damage=0.14, crit_rate=0.07),
        ShengYiWu(ShengYiWu.LIE_REN, ShengYiWu.PART_YU, crit_damage=0.202, crit_rate=0.031, hp_percent=0.14, hp=239),
        ShengYiWu(ShengYiWu.LIE_REN, ShengYiWu.PART_YU, crit_damage=0.194, energe_recharge=0.065, crit_rate=0.062, elem_mastery=37),
        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_YU, def_v=23, crit_damage=0.28, crit_rate=0.027, energe_recharge=0.123),
        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_YU, energe_recharge=0.155, hp_percent=0.041, hp=717, atk_per=0.047),
        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_YU, energe_recharge=0.292, atk_per=0.111, crit_damage=0.054, def_v=19),
        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_YU, crit_damage=0.07, atk_per=0.058, energe_recharge=0.104, crit_rate=0.136),
        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_YU, hp=508, atk_per=0.099, crit_rate=0.058, crit_damage=0.194),
        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_YU, elem_mastery=86, atk_per=0.087, def_per=0.058, hp_percent=0.058),
        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_YU, atk_per=0.105, crit_rate=0.035, energe_recharge=0.058, elem_mastery=93),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_YU, crit_damage=0.078, atk_per=0.041, crit_rate=0.035, elem_mastery=96),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_YU, energe_recharge=0.149, hp_percent=0.117, crit_rate=0.035, crit_damage=0.132),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_YU, def_v=37, crit_damage=0.07, crit_rate=0.144, def_per=0.066),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_YU, crit_damage=0.272, hp=239, crit_rate=0.07, def_v=23),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_YU, crit_damage=0.132, crit_rate=0.066, hp_percent=0.041, elem_mastery=56),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_YU, def_per=0.073, atk_per=0.087, crit_rate=0.027, energe_recharge=0.285),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_YU, crit_damage=0.148, def_per=0.117, def_v=19, crit_rate=0.148),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_YU, crit_rate=0.039, crit_damage=0.35, hp_percent=0.041, def_v=39),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_YU, hp=448, crit_damage=0.078, energe_recharge=0.311, hp_percent=0.053),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_YU, hp=807, atk_per=0.047, energe_recharge=0.11, crit_damage=0.171),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_YU, elem_mastery=16, atk_per=0.058, crit_damage=0.148, crit_rate=0.132),
        ShengYiWu(ShengYiWu.ZHUI_YI, ShengYiWu.PART_YU, hp=687, crit_damage=0.109, crit_rate=0.039, hp_percent=0.157),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_YU, crit_damage=0.132, energe_recharge=0.175, crit_rate=0.101, hp_percent=0.041),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_YU, atk_per=0.111, energe_recharge=0.117, hp_percent=0.21, def_per=0.073),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_YU, hp_percent=0.082, energe_recharge=0.097, atk_per=0.21, crit_rate=0.035),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_YU, atk_per=0.099, energe_recharge=0.246, crit_damage=0.099, crit_rate=0.035),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_YU, def_v=23, crit_rate=0.031, hp=478, hp_percent=0.216),
        ShengYiWu(ShengYiWu.CHEN_LUN, ShengYiWu.PART_YU, crit_rate=0.14, atk_per=0.053, hp=478, crit_damage=0.109),
        ShengYiWu(ShengYiWu.CHEN_LUN, ShengYiWu.PART_YU, hp_percent=0.053, crit_damage=0.155, hp=299, atk_per=0.262),
        ShengYiWu(ShengYiWu.CHEN_LUN, ShengYiWu.PART_YU, crit_damage=0.14, def_per=0.16, crit_rate=0.101, hp=239),
        ShengYiWu(ShengYiWu.CHEN_LUN, ShengYiWu.PART_YU, def_v=16, crit_damage=0.117, crit_rate=0.124, atk_per=0.041),
        ShengYiWu(ShengYiWu.CHEN_LUN, ShengYiWu.PART_YU, hp_percent=0.047, def_per=0.066, energe_recharge=0.065, crit_rate=0.167),
        ShengYiWu(ShengYiWu.ZONG_SHI, ShengYiWu.PART_YU, elem_mastery=47, def_v=60, hp=269, energe_recharge=0.149),
        ShengYiWu(ShengYiWu.ZONG_SHI, ShengYiWu.PART_YU, hp=209, hp_percent=0.157, energe_recharge=0.104, def_v=35),
        ShengYiWu(ShengYiWu.ZONG_SHI, ShengYiWu.PART_YU, hp_percent=0.093, crit_rate=0.07, energe_recharge=0.117, atk_per=0.111),
        ShengYiWu(ShengYiWu.RU_LEI, ShengYiWu.PART_YU, crit_rate=0.066, crit_damage=0.218, elem_mastery=63, energe_recharge=0.065),
        ShengYiWu(ShengYiWu.YUE_TUAN, ShengYiWu.PART_YU, elem_mastery=44, crit_damage=0.124, atk_per=0.087, crit_rate=0.101),
        ShengYiWu(ShengYiWu.FENG_TAO, ShengYiWu.PART_YU, atk_per=0.093, elem_mastery=21, energe_recharge=0.233, hp=269),
        ShengYiWu(ShengYiWu.FENG_TAO, ShengYiWu.PART_YU, hp=239, crit_damage=0.233, atk_per=0.093, crit_rate=0.062),
        ShengYiWu(ShengYiWu.FENG_TAO, ShengYiWu.PART_YU, atk_per=0.041, def_v=42, elem_mastery=77, energe_recharge=0.058),
        ShengYiWu(ShengYiWu.JUE_DOU_SHI, ShengYiWu.PART_YU, hp_percent=0.111, crit_rate=0.167, energe_recharge=0.045, crit_damage=0.062),
        ShengYiWu(ShengYiWu.JUE_DOU_SHI, ShengYiWu.PART_YU, crit_rate=0.144, crit_damage=0.07, hp_percent=0.111, energe_recharge=0.045),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_YU, crit_damage=0.194, energe_recharge=0.052, elem_mastery=19, hp_percent=0.233),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_YU, crit_damage=0.14, elem_mastery=40, crit_rate=0.101, atk_per=0.105),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_YU, def_v=23, crit_rate=0.128, crit_damage=0.07, atk_per=0.099),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_YU, crit_damage=0.256, energe_recharge=0.097, def_per=0.058, atk_per=0.041),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_YU, crit_rate=0.066, crit_damage=0.21, hp=299, atk_per=0.099),

    ],
    "t": [
        ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_TOU, crit_damage=0.622, crit_rate=0.062, energe_recharge=0.097, def_v=32, def_per=0.132),
        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_TOU, crit_damage=0.622, atk=18, def_v=56, atk_per=0.105, crit_rate=0.093),
        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_TOU, def_per=0.058, hp=687, hp_percent=0.111, crit_damage=0.07),
        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_TOU, hp_percent=0.169, crit_rate=0.078, elem_mastery=63, atk_per=0.053),
        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_TOU, hp=448, atk=37, hp_percent=0.099, crit_damage=0.097),
        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_TOU, crit_rate=0.311, def_v=21, crit_damage=0.14, atk=33, elem_mastery=58),
        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_TOU, def_per=0.058, energe_recharge=0.227, atk_per=0.058, crit_damage=0.155),
        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_TOU, crit_damage=0.622, atk=33, crit_rate=0.101, def_v=16, atk_per=0.087),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_TOU, crit_damage=0.622, elem_mastery=47, def_v=32, atk_per=0.152, crit_rate=0.066),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_TOU, hp_percent=0.466, energe_recharge=0.142, atk=19, crit_damage=0.132, crit_rate=0.066),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_TOU, crit_damage=0.622, atk=19, def_v=35, crit_rate=0.132, energe_recharge=0.052),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_TOU, crit_rate=0.311, atk_per=0.047, crit_damage=0.256, energe_recharge=0.104, hp=209),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_TOU, crit_rate=0.311, atk=31, crit_damage=0.179, def_per=0.058, energe_recharge=0.104),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_TOU, crit_rate=0.311, crit_damage=0.218, hp_percent=0.087, elem_mastery=16, atk_per=0.099),
        ShengYiWu(ShengYiWu.ZHUI_YI, ShengYiWu.PART_TOU, crit_damage=0.622, hp_percent=0.041, atk=18, elem_mastery=84, crit_rate=0.062),
        ShengYiWu(ShengYiWu.ZHUI_YI, ShengYiWu.PART_TOU, crit_rate=0.311, elem_mastery=40, atk_per=0.053, energe_recharge=0.162, crit_damage=0.14),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_TOU, hp_percent=0.466, hp=209, crit_rate=0.074, atk=18, crit_damage=0.241),
        ShengYiWu(ShengYiWu.CHEN_LUN, ShengYiWu.PART_TOU, crit_rate=0.311, energe_recharge=0.058, def_v=37, crit_damage=0.155, hp_percent=0.134),
        ShengYiWu(ShengYiWu.CHEN_LUN, ShengYiWu.PART_TOU, crit_rate=0.311, def_v=44, crit_damage=0.225, energe_recharge=0.097, elem_mastery=23),
        ShengYiWu(ShengYiWu.ZONG_SHI, ShengYiWu.PART_TOU, crit_damage=0.622, def_per=0.109, crit_rate=0.148, atk_per=0.058, energe_recharge=0.058),
        ShengYiWu(ShengYiWu.ZONG_SHI, ShengYiWu.PART_TOU, crit_rate=0.311, def_v=60, crit_damage=0.187, hp=269, elem_mastery=47),
        ShengYiWu(ShengYiWu.RU_LEI, ShengYiWu.PART_TOU, crit_rate=0.311, hp=777, atk=27, crit_damage=0.132, elem_mastery=23),
        ShengYiWu(ShengYiWu.YUE_TUAN, ShengYiWu.PART_TOU, crit_rate=0.311, hp=508, crit_damage=0.14, atk=45, atk_per=0.099),
        ShengYiWu(ShengYiWu.FENG_TAO, ShengYiWu.PART_TOU, crit_rate=0.311, crit_damage=0.272, def_v=23, hp=538, hp_percent=0.041),
        ShengYiWu(ShengYiWu.JUE_DOU_SHI, ShengYiWu.PART_TOU, crit_rate=0.311, atk=19, crit_damage=0.194, hp=568, atk_per=0.093),
        ShengYiWu(ShengYiWu.JUE_DOU_SHI, ShengYiWu.PART_TOU, crit_rate=0.311, hp_percent=0.053, crit_damage=0.303, hp=209, atk=39),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_TOU, crit_rate=0.311, atk_per=0.152, elem_mastery=44, crit_damage=0.148, def_v=23),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_TOU, crit_damage=0.622, hp=239, elem_mastery=16, crit_rate=0.086, def_v=60),
    ]
}



def find_swy(swy_s_b, find_combins_callback, calculate_score_callbak, result_txt_file):
    all_syw = {}
    all_syw.update(all_syw_exclude_s_b)
    all_syw.update(swy_s_b)

    all_combins = find_combins_callback(all_syw)

    all_scores = {}

    for c in all_combins:
        parts = [p.part for p in c]
        parts_set = set(parts)
        if len(parts) != len(parts_set):
            continue

        miss_part = list(ShengYiWu.ALL_PARTS - parts_set)

        for s in all_syw[miss_part[0]]:
            combine = c + (s, )

            score_data = calculate_score_callbak(combine)
            if not score_data:
                continue

            score, data = score_data
            if score in all_scores:
                all_scores[score].append(data)
            else:
                all_scores[score] = [data]

    if all_scores:
        with open(result_txt_file, 'w', encoding='utf-8') as f:
            for i in sorted(all_scores):
                for c in all_scores[i]:
                    # print((i, c))
                    f.write(str((round(i, 4), c, )))
                    f.write('\n')
