#!/user/bin/env python3 -c
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

import sys
import os
import logging
import itertools
import uuid


class ShengYiWu:
    ALL_PARTS = {'h', 'y', 's', 'b', 't'}
    PART_HUA = 'h'
    PART_YU = 'y'
    PART_SHA = 's'
    PART_BEI = 'b'
    PART_TOU = 't'

    ENERGE_RECHARGE_MAX = 0.518
    BONUS_MAX = 0.466
    CRIT_RATE_MAIN = 0.311
    CRIT_DAMAGE_MAIN = 0.622
    ELEM_MASTERY_MAIN = 187

    ELEM_TYPE_WU_LI = 'elem_li'
    ELEM_TYPE_HUO = 'elem_huo'
    ELEM_TYPE_SHUI = 'elem_shui'
    ELEM_TYPE_CAO = 'elem_cao'
    ELEM_TYPE_LEI = 'elem_lei'
    ELEM_TYPE_FENG = 'elem_feng'
    ELEM_TYPE_BING = 'elem_bing'
    ELEM_TYPE_YAN = 'elem_yan'

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
    SHA_SHANG = 'sha_shang'
    QI_SHI_DAO = 'qi_shi_dao'

    def __init__(self, name, part, crit_rate=0.0, crit_damage=0.0, hp_percent=0.0, hp=0, energe_recharge=0.0,
                 atk_per=0.0, atk=0, def_per=0.0, def_v=0, elem_mastery=0, elem_bonus=0.0, elem_type=None):
        self.id = str(uuid.uuid4())
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
        self.elem_bonus = elem_bonus
        self.elem_type = elem_type

    def to_str(self):
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

        if self.elem_bonus:
            s += ', bonus:' + str(self.elem_bonus)

        s += ')'

        return s

    def __str__(self):
        return self.to_str()

    def __repr__(self) -> str:
        return self.__str__()


all_syw = {
    ShengYiWu.PART_HUA: [
        ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_HUA, crit_rate=0.14,
                  atk=14, crit_damage=0.078, energe_recharge=0.168),
        ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_HUA,
                  crit_rate=0.07, crit_damage=0.194, atk=39, def_per=0.058),
        ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_HUA, energe_recharge=0.058,
                  crit_damage=0.078, elem_mastery=54, crit_rate=0.109),
        ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_HUA, hp_percent=0.117,
                  elem_mastery=16, crit_damage=0.163, energe_recharge=0.11),
        ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_HUA, crit_damage=0.21,
                  hp_percent=0.152, crit_rate=0.031, def_v=23),

        ShengYiWu(ShengYiWu.LIE_REN, ShengYiWu.PART_HUA, crit_rate=0.066,
                  crit_damage=0.287, elem_mastery=16, atk_per=0.099),
        ShengYiWu(ShengYiWu.LIE_REN, ShengYiWu.PART_HUA, atk=16,
                  hp_percent=0.181, crit_damage=0.148, atk_per=0.058),
        ShengYiWu(ShengYiWu.LIE_REN, ShengYiWu.PART_HUA, energe_recharge=0.123,
                  crit_rate=0.101, hp_percent=0.053, crit_damage=0.117),
        ShengYiWu(ShengYiWu.LIE_REN, ShengYiWu.PART_HUA, def_per=0.066,
                  crit_damage=0.148, crit_rate=0.105, energe_recharge=0.104),

        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_HUA,
                  elem_mastery=82, atk=19, hp_percent=0.122, def_v=19),
        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_HUA,
                  crit_damage=0.218, crit_rate=0.035, hp_percent=0.157, atk=31),
        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_HUA, crit_rate=0.14,
                  atk_per=0.117, crit_damage=0.07, energe_recharge=0.045),
        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_HUA, crit_damage=0.078,
                  crit_rate=0.148, elem_mastery=16, atk_per=0.099),
        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_HUA, crit_damage=0.218,
                  def_per=0.073, hp_percent=0.105, energe_recharge=0.104),

        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_HUA,
                  elem_mastery=42, crit_rate=0.105, atk=14, hp_percent=0.134),
         ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_HUA, 
                   def_per=0.073, hp_percent=0.152, crit_rate=0.027, crit_damage=0.202),
        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_HUA, 
                  def_per=0.139, crit_rate=0.101, energe_recharge=0.058, crit_damage=0.124),
        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_HUA,
                  energe_recharge=0.123, atk=37, crit_rate=0.039, crit_damage=0.233),

        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_HUA,
                  crit_damage=0.124, hp_percent=0.099, atk=14, crit_rate=0.124),
        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_HUA, crit_damage=0.249,
                  energe_recharge=0.065, def_per=0.066, crit_rate=0.089),
        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_HUA, def_per=0.073,
                  hp_percent=0.146, def_v=35, elem_mastery=56),
        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_HUA, crit_rate=0.113,
                  energe_recharge=0.117, crit_damage=0.07, atk=37),
        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_HUA, def_v=23,
                  crit_damage=0.272, elem_mastery=44, energe_recharge=0.065),
        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_HUA, crit_damage=0.28,
                  hp_percent=0.099, atk_per=0.053, crit_rate=0.027),

        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_HUA, energe_recharge=0.11,
                  hp_percent=0.152, crit_rate=0.035, elem_mastery=70),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_HUA, def_v=16,
                  elem_mastery=79, hp_percent=0.093, energe_recharge=0.11),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_HUA,
                  crit_damage=0.288, crit_rate=0.062, def_v=21, hp_percent=0.047),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_HUA, elem_mastery=40,
                  def_v=21, crit_rate=0.027, crit_damage=0.241),

        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_HUA, hp_percent=0.181,
                  energe_recharge=0.123, def_v=23, crit_rate=0.07),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_HUA, atk_per=0.041,
                  crit_rate=0.062, elem_mastery=54, crit_damage=0.21),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_HUA, crit_rate=0.144,
                  crit_damage=0.078, hp_percent=0.105, elem_mastery=40),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_HUA, elem_mastery=44,
                  crit_damage=0.21, def_per=0.066, energe_recharge=0.194),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_HUA, elem_mastery=21,
                  crit_rate=0.066, energe_recharge=0.181, crit_damage=0.124),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_HUA, atk=33,
                  crit_rate=0.066, atk_per=0.111, crit_damage=0.117),

        ShengYiWu(ShengYiWu.ZHUI_YI, ShengYiWu.PART_HUA, crit_damage=0.132,
                  crit_rate=0.152, energe_recharge=0.097, def_per=0.073),
        ShengYiWu(ShengYiWu.ZHUI_YI, ShengYiWu.PART_HUA, def_v=16,
                  crit_rate=0.035, crit_damage=0.249, atk=29),
        ShengYiWu(ShengYiWu.ZHUI_YI, ShengYiWu.PART_HUA, crit_damage=0.117,
                  hp_percent=0.146, atk_per=0.053, elem_mastery=40),

        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_HUA, crit_rate=0.062,
                  elem_mastery=51, energe_recharge=0.181, def_per=0.073),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_HUA, crit_damage=0.132,
                  crit_rate=0.101, atk=16, energe_recharge=0.175),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_HUA, def_v=39,
                  atk=16, crit_damage=0.241, crit_rate=0.066),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_HUA,
                  energe_recharge=0.155, atk=35, hp_percent=0.128, atk_per=0.047),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_HUA, hp_percent=0.134,
                  energe_recharge=0.162, crit_rate=0.074, crit_damage=0.078),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_HUA,
                  energe_recharge=0.117, atk=14, atk_per=0.117, crit_damage=0.264),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_HUA, def_per=0.131,
                  energe_recharge=0.175, def_v=37, crit_damage=0.062),

        ShengYiWu(ShengYiWu.CHEN_LUN, ShengYiWu.PART_HUA, crit_rate=0.066,
                  crit_damage=0.148, hp_percent=0.146, def_per=0.109),
        ShengYiWu(ShengYiWu.CHEN_LUN, ShengYiWu.PART_HUA, crit_damage=0.054,
                  energe_recharge=0.065, crit_rate=0.132, def_v=39),

        ShengYiWu(ShengYiWu.ZONG_SHI, ShengYiWu.PART_HUA, def_per=0.124,
                  crit_damage=0.062, hp_percent=0.111, energe_recharge=0.214),
        ShengYiWu(ShengYiWu.ZONG_SHI, ShengYiWu.PART_HUA, energe_recharge=0.227,
                  atk_per=0.058, elem_mastery=44, hp_percent=0.047),
        ShengYiWu(ShengYiWu.ZONG_SHI, ShengYiWu.PART_HUA, crit_damage=0.14,
                  energe_recharge=0.065, atk_per=0.099, crit_rate=0.105),

        ShengYiWu(ShengYiWu.YUE_TUAN, ShengYiWu.PART_HUA, elem_mastery=58,
                  crit_damage=0.148, crit_rate=0.078, def_per=0.051),

        ShengYiWu(ShengYiWu.FENG_TAO, ShengYiWu.PART_HUA, elem_mastery=86,
                  hp_percent=0.041, def_per=0.131, energe_recharge=0.123),
        ShengYiWu(ShengYiWu.FENG_TAO, ShengYiWu.PART_HUA, crit_damage=0.078,
                  energe_recharge=0.065, atk_per=0.146, crit_rate=0.144),
        ShengYiWu(ShengYiWu.FENG_TAO, ShengYiWu.PART_HUA, elem_mastery=72,
                  hp_percent=0.099, atk_per=0.041, energe_recharge=0.052),

        ShengYiWu(ShengYiWu.JUE_DOU_SHI, ShengYiWu.PART_HUA,
                  hp_percent=0.157, crit_damage=0.218, crit_rate=0.078, def_v=16),
        ShengYiWu(ShengYiWu.JUE_DOU_SHI, ShengYiWu.PART_HUA,
                  crit_damage=0.14, crit_rate=0.062, def_v=16, def_per=0.168),

        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_HUA, crit_damage=0.194,
                  hp_percent=0.128, atk_per=0.041, energe_recharge=0.104),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_HUA, atk_per=0.105,
                  elem_mastery=19, crit_rate=0.132, energe_recharge=0.11),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_HUA, crit_rate=0.086,
                  crit_damage=0.202, elem_mastery=40, energe_recharge=0.052),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_HUA, elem_mastery=16,
                  atk_per=0.134, crit_damage=0.132, crit_rate=0.089),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_HUA, def_v=21,
                  atk_per=0.134, atk=27, crit_damage=0.218),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_HUA, crit_damage=0.078,
                  elem_mastery=40, hp_percent=0.099, crit_rate=0.105),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_HUA, atk_per=0.099,
                  hp_percent=0.099, crit_damage=0.21, energe_recharge=0.058),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_HUA, elem_mastery=16,
                  crit_rate=0.039, crit_damage=0.264, def_v=46),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_HUA, atk_per=0.163,
                  crit_rate=0.039, crit_damage=0.155, elem_mastery=40),
    ],
    ShengYiWu.PART_YU: [
        ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_YU, hp=209,
                  energe_recharge=0.123, hp_percent=0.21, crit_damage=0.124),
        ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_YU, hp=568,
                  crit_damage=0.21, hp_percent=0.053, def_v=56),
        ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_YU, def_v=37,
                  elem_mastery=40, crit_damage=0.256, crit_rate=0.027),
        ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_YU, def_v=37,
                  hp_percent=0.163, def_per=0.109, crit_damage=0.14),
        ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_YU, hp_percent=0.14,
                  elem_mastery=19, crit_rate=0.097, energe_recharge=0.052),
        ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_YU, elem_mastery=37,
                  energe_recharge=0.11, crit_damage=0.14, crit_rate=0.07),

        ShengYiWu(ShengYiWu.LIE_REN, ShengYiWu.PART_YU,
                  crit_damage=0.202, crit_rate=0.031, hp_percent=0.14, hp=239),
        ShengYiWu(ShengYiWu.LIE_REN, ShengYiWu.PART_YU,
                  hp=448, energe_recharge=0.052, crit_damage=0.14, hp_percent=0.157),
        ShengYiWu(ShengYiWu.LIE_REN, ShengYiWu.PART_YU, crit_damage=0.194,
                  energe_recharge=0.065, crit_rate=0.062, elem_mastery=37),
        ShengYiWu(ShengYiWu.LIE_REN, ShengYiWu.PART_YU, hp=448,
                  crit_damage=0.14, crit_rate=0.136, elem_mastery=16),

        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_YU, def_v=23,
                  crit_damage=0.28, crit_rate=0.027, energe_recharge=0.123),

        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_YU,
                  energe_recharge=0.292, atk_per=0.111, crit_damage=0.054, def_v=19),
        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_YU, crit_damage=0.07,
                  atk_per=0.058, energe_recharge=0.104, crit_rate=0.136),
        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_YU,
                  crit_damage=0.21, atk_per=0.169, hp=209, hp_percent=0.087),
        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_YU, def_v=23,
                  crit_rate=0.117, crit_damage=0.194, elem_mastery=23),

        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_YU, hp=508,
                  atk_per=0.099, crit_rate=0.058, crit_damage=0.194),
        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_YU, atk_per=0.105,
                  crit_rate=0.035, energe_recharge=0.058, elem_mastery=93),

        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_YU, crit_damage=0.078,
                  atk_per=0.041, crit_rate=0.035, elem_mastery=96),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_YU, energe_recharge=0.149,
                  hp_percent=0.117, crit_rate=0.035, crit_damage=0.132),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_YU, def_v=37,
                  crit_damage=0.07, crit_rate=0.144, def_per=0.066),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_YU,
                  crit_damage=0.272, hp=239, crit_rate=0.07, def_v=23),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_YU, crit_damage=0.132,
                  crit_rate=0.066, hp_percent=0.041, elem_mastery=56),

        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_YU, def_per=0.073,
                  atk_per=0.087, crit_rate=0.027, energe_recharge=0.285),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_YU,
                  crit_damage=0.148, def_per=0.117, def_v=19, crit_rate=0.148),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_YU, crit_rate=0.039,
                  crit_damage=0.35, hp_percent=0.041, def_v=39),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_YU, hp=448,
                  crit_damage=0.078, energe_recharge=ShengYiWu.CRIT_RATE_MAIN, hp_percent=0.053),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_YU, hp=807,
                  atk_per=0.047, energe_recharge=0.11, crit_damage=0.171),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_YU, elem_mastery=16,
                  atk_per=0.058, crit_damage=0.148, crit_rate=0.132),

        ShengYiWu(ShengYiWu.ZHUI_YI, ShengYiWu.PART_YU, hp=687,
                  crit_damage=0.109, crit_rate=0.039, hp_percent=0.157),

        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_YU, crit_damage=0.132,
                  energe_recharge=0.175, crit_rate=0.101, hp_percent=0.041),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_YU, atk_per=0.111,
                  energe_recharge=0.117, hp_percent=0.21, def_per=0.073),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_YU, hp_percent=0.082,
                  energe_recharge=0.097, atk_per=0.21, crit_rate=0.035),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_YU, atk_per=0.099,
                  energe_recharge=0.246, crit_damage=0.099, crit_rate=0.035),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_YU, def_v=23,
                  crit_rate=0.031, hp=478, hp_percent=0.216),

        ShengYiWu(ShengYiWu.CHEN_LUN, ShengYiWu.PART_YU,
                  crit_rate=0.14, atk_per=0.053, hp=478, crit_damage=0.109),
        ShengYiWu(ShengYiWu.CHEN_LUN, ShengYiWu.PART_YU,
                  hp_percent=0.053, crit_damage=0.155, hp=299, atk_per=0.262),
        ShengYiWu(ShengYiWu.CHEN_LUN, ShengYiWu.PART_YU,
                  crit_damage=0.14, def_per=0.16, crit_rate=0.101, hp=239),
        ShengYiWu(ShengYiWu.CHEN_LUN, ShengYiWu.PART_YU, def_v=16,
                  crit_damage=0.117, crit_rate=0.124, atk_per=0.041),
        ShengYiWu(ShengYiWu.CHEN_LUN, ShengYiWu.PART_YU, hp_percent=0.047,
                  def_per=0.066, energe_recharge=0.065, crit_rate=0.167),

        ShengYiWu(ShengYiWu.ZONG_SHI, ShengYiWu.PART_YU,
                  elem_mastery=47, def_v=60, hp=269, energe_recharge=0.149),
        ShengYiWu(ShengYiWu.ZONG_SHI, ShengYiWu.PART_YU, hp=209,
                  hp_percent=0.157, energe_recharge=0.104, def_v=35),
        ShengYiWu(ShengYiWu.ZONG_SHI, ShengYiWu.PART_YU, hp_percent=0.093,
                  crit_rate=0.07, energe_recharge=0.117, atk_per=0.111),

        ShengYiWu(ShengYiWu.RU_LEI, ShengYiWu.PART_YU, crit_rate=0.066,
                  crit_damage=0.218, elem_mastery=63, energe_recharge=0.065),

        ShengYiWu(ShengYiWu.YUE_TUAN, ShengYiWu.PART_YU, elem_mastery=44,
                  crit_damage=0.124, atk_per=0.087, crit_rate=0.101),

        ShengYiWu(ShengYiWu.FENG_TAO, ShengYiWu.PART_YU, atk_per=0.093,
                  elem_mastery=21, energe_recharge=0.233, hp=269),
        ShengYiWu(ShengYiWu.FENG_TAO, ShengYiWu.PART_YU, hp=239,
                  crit_damage=0.233, atk_per=0.093, crit_rate=0.062),
        ShengYiWu(ShengYiWu.FENG_TAO, ShengYiWu.PART_YU, atk_per=0.041,
                  def_v=42, elem_mastery=77, energe_recharge=0.058),

        ShengYiWu(ShengYiWu.JUE_DOU_SHI, ShengYiWu.PART_YU, hp_percent=0.111,
                  crit_rate=0.167, energe_recharge=0.045, crit_damage=0.062),
        ShengYiWu(ShengYiWu.JUE_DOU_SHI, ShengYiWu.PART_YU, crit_rate=0.144,
                  crit_damage=0.07, hp_percent=0.111, energe_recharge=0.045),

        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_YU, crit_damage=0.194,
                  energe_recharge=0.052, elem_mastery=19, hp_percent=0.233),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_YU, crit_damage=0.14,
                  elem_mastery=40, crit_rate=0.101, atk_per=0.105),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_YU, def_v=23,
                  crit_rate=0.128, crit_damage=0.07, atk_per=0.099),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_YU, crit_damage=0.256,
                  energe_recharge=0.097, def_per=0.058, atk_per=0.041),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_YU,
                  crit_rate=0.066, crit_damage=0.21, hp=299, atk_per=0.099),

    ],
    ShengYiWu.PART_SHA: [
        ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_SHA, hp_percent=ShengYiWu.BONUS_MAX,
                  hp=777, atk=33, crit_rate=0.058, crit_damage=0.07),
        ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_SHA, hp_percent=ShengYiWu.BONUS_MAX,
                  energe_recharge=0.045, crit_damage=0.078, crit_rate=0.113, def_v=60),

        ShengYiWu(ShengYiWu.LIE_REN, ShengYiWu.PART_SHA, energe_recharge=ShengYiWu.ENERGE_RECHARGE_MAX,
                  atk=14, crit_rate=0.14, def_v=37, crit_damage=0.148),
        ShengYiWu(ShengYiWu.LIE_REN, ShengYiWu.PART_SHA, hp_percent=ShengYiWu.BONUS_MAX,
                  crit_rate=0.027, def_v=23, crit_damage=0.264, hp=478),
        ShengYiWu(ShengYiWu.LIE_REN, ShengYiWu.PART_SHA, elem_mastery=ShengYiWu.ELEM_MASTERY_MAIN,
                  def_per=0.073, crit_rate=0.128, crit_damage=0.148, hp_percent=0.041),

        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_SHA, atk_per=ShengYiWu.BONUS_MAX,
                  crit_damage=0.21, hp=568, crit_rate=0.078, hp_percent=0.093),
        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_SHA, hp_percent=ShengYiWu.BONUS_MAX,
                  energe_recharge=0.052, crit_damage=0.202, elem_mastery=44, crit_rate=0.062),

        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_SHA, hp_percent=ShengYiWu.BONUS_MAX,
                  hp=837, elem_mastery=16, crit_damage=0.257, atk=19),
        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_SHA, hp_percent=ShengYiWu.BONUS_MAX,
                  crit_damage=0.078, atk_per=0.087, crit_rate=0.132, def_v=16),
        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_SHA, hp_percent=ShengYiWu.BONUS_MAX,
                  atk=18, energe_recharge=0.091, crit_damage=0.218, crit_rate=0.074),
        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_SHA, elem_mastery=ShengYiWu.ELEM_MASTERY_MAIN,
                  atk_per=0.058, def_v=19, crit_damage=0.062, crit_rate=0.152),

        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_SHA, hp_percent=ShengYiWu.BONUS_MAX,
                  def_v=21, crit_damage=0.187, crit_rate=0.089, atk_per=0.041),
        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_SHA, elem_mastery=ShengYiWu.ELEM_MASTERY_MAIN,
                  atk_per=0.14, def_v=35, crit_rate=0.062, atk=19),
        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_SHA, energe_recharge=ShengYiWu.ENERGE_RECHARGE_MAX,
                  elem_mastery=23, crit_damage=0.218, def_v=44, crit_rate=0.07),
        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_SHA, elem_mastery=ShengYiWu.ELEM_MASTERY_MAIN,
                  hp_percent=0.053, energe_recharge=0.045, crit_rate=0.031, hp=1404),

        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_SHA, atk_per=ShengYiWu.BONUS_MAX,
                  crit_rate=0.109, def_v=32, crit_damage=0.233, hp=209),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_SHA, elem_mastery=ShengYiWu.ELEM_MASTERY_MAIN,
                  crit_damage=0.124, hp_percent=0.198, energe_recharge=0.11, def_v=16),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_SHA, atk_per=ShengYiWu.BONUS_MAX,
                  hp=269, def_v=37, crit_damage=0.124, crit_rate=0.132),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_SHA, elem_mastery=ShengYiWu.ELEM_MASTERY_MAIN,
                  energe_recharge=0.045, crit_damage=0.093, hp=508, def_per=0.124),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_SHA, hp_percent=ShengYiWu.BONUS_MAX,
                  crit_rate=0.035, energe_recharge=0.214, atk=31, elem_mastery=19),

        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_SHA, atk_per=ShengYiWu.BONUS_MAX,
                  elem_mastery=19, hp_percent=0.105, crit_rate=0.086, crit_damage=0.202),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_SHA, energe_recharge=ShengYiWu.ENERGE_RECHARGE_MAX,
                  hp_percent=0.093, crit_damage=0.14, crit_rate=0.07, atk=35),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_SHA, energe_recharge=ShengYiWu.ENERGE_RECHARGE_MAX,
                  hp=448, crit_rate=0.07, atk_per=0.082, def_v=44),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_SHA, energe_recharge=ShengYiWu.ENERGE_RECHARGE_MAX,
                  crit_damage=0.194, elem_mastery=19, hp=508, def_per=0.117),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_SHA, energe_recharge=ShengYiWu.ENERGE_RECHARGE_MAX,
                  hp_percent=0.117, crit_rate=0.027, def_per=0.19, crit_damage=0.14),

        ShengYiWu(ShengYiWu.ZHUI_YI, ShengYiWu.PART_SHA, hp_percent=ShengYiWu.BONUS_MAX,
                  atk=19, crit_damage=0.14, elem_mastery=33, crit_rate=0.105),
        ShengYiWu(ShengYiWu.ZHUI_YI, ShengYiWu.PART_SHA, elem_mastery=ShengYiWu.ELEM_MASTERY_MAIN,
                  atk=27, crit_damage=0.218, energe_recharge=0.104, atk_per=0.041),

        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_SHA, hp_percent=ShengYiWu.BONUS_MAX,
                  crit_rate=0.066, atk=33, elem_mastery=40, crit_damage=0.21),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_SHA, hp_percent=ShengYiWu.BONUS_MAX,
                  def_v=37, energe_recharge=0.24, atk=19, crit_rate=0.07),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_SHA, elem_mastery=ShengYiWu.ELEM_MASTERY_MAIN,
                  hp=538, crit_rate=0.062, crit_damage=0.202, hp_percent=0.058),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_SHA, elem_mastery=ShengYiWu.ELEM_MASTERY_MAIN,
                  energe_recharge=0.052, crit_damage=0.202, crit_rate=0.101, def_v=19),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_SHA, energe_recharge=ShengYiWu.ENERGE_RECHARGE_MAX,
                  crit_rate=0.101, hp=508, atk_per=0.099, def_v=23),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_SHA, hp_percent=ShengYiWu.BONUS_MAX,
                  atk_per=0.099, crit_rate=0.078, elem_mastery=40, energe_recharge=0.117),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_SHA, hp_percent=ShengYiWu.BONUS_MAX,
                  elem_mastery=44, atk=16, energe_recharge=0.058, crit_damage=0.272),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_SHA, energe_recharge=ShengYiWu.ENERGE_RECHARGE_MAX,
                  hp_percent=0.105, elem_mastery=40, def_v=35, atk=35),

        ShengYiWu(ShengYiWu.CHEN_LUN, ShengYiWu.PART_SHA, hp_percent=ShengYiWu.BONUS_MAX,
                  hp=448, crit_damage=ShengYiWu.CRIT_RATE_MAIN, def_per=0.073, elem_mastery=40),

        ShengYiWu(ShengYiWu.ZONG_SHI, ShengYiWu.PART_SHA, hp_percent=ShengYiWu.BONUS_MAX,
                  atk=31, def_v=35, crit_rate=0.062, energe_recharge=0.104),
        ShengYiWu(ShengYiWu.ZONG_SHI, ShengYiWu.PART_SHA, energe_recharge=ShengYiWu.ENERGE_RECHARGE_MAX,
                  hp=508, def_v=37, crit_damage=0.078, def_per=0.182),
        ShengYiWu(ShengYiWu.ZONG_SHI, ShengYiWu.PART_SHA, energe_recharge=ShengYiWu.ENERGE_RECHARGE_MAX,
                  def_v=65, elem_mastery=37, hp_percent=0.047, atk=37),

        ShengYiWu(ShengYiWu.YUE_TUAN, ShengYiWu.PART_SHA, atk_per=ShengYiWu.BONUS_MAX,
                  def_per=0.124, crit_rate=0.101, crit_damage=0.132, atk=19),

        ShengYiWu(ShengYiWu.FENG_TAO, ShengYiWu.PART_SHA, elem_mastery=ShengYiWu.ELEM_MASTERY_MAIN,
                  atk=33, crit_rate=0.093, crit_damage=0.14, energe_recharge=0.13),
        ShengYiWu(ShengYiWu.FENG_TAO, ShengYiWu.PART_SHA, elem_mastery=ShengYiWu.ELEM_MASTERY_MAIN,
                  crit_rate=0.062, def_v=44, atk_per=0.047, energe_recharge=0.168),
        ShengYiWu(ShengYiWu.FENG_TAO, ShengYiWu.PART_SHA, elem_mastery=ShengYiWu.ELEM_MASTERY_MAIN,
                  atk_per=0.047, energe_recharge=0.168, def_v=323, atk=37),

        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_SHA, hp_percent=ShengYiWu.BONUS_MAX,
                  energe_recharge=0.091, crit_rate=0.163, crit_damage=0.078, hp=239),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_SHA, atk_per=ShengYiWu.BONUS_MAX,
                  crit_rate=0.097, hp=209, crit_damage=0.202, def_v=42),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_SHA, hp_percent=ShengYiWu.BONUS_MAX,
                  crit_rate=0.031, def_v=23, crit_damage=0.295, energe_recharge=0.104),
    ],
    ShengYiWu.PART_BEI: [
        ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_BEI, hp_percent=ShengYiWu.BONUS_MAX,
                  atk=35, def_v=23, elem_mastery=70, crit_rate=0.109),
        ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=ShengYiWu.ELEM_TYPE_SHUI,
                  crit_damage=0.132, energe_recharge=0.11, def_v=62, def_per=0.073),

        ShengYiWu(ShengYiWu.LIE_REN, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=ShengYiWu.ELEM_TYPE_BING,
                  crit_rate=0.105, elem_mastery=35, hp_percent=0.093, atk_per=0.082),
        ShengYiWu(ShengYiWu.LIE_REN, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=ShengYiWu.ELEM_TYPE_SHUI,
                  atk=16, hp_percent=0.152, energe_recharge=0.175, hp=299),
        ShengYiWu(ShengYiWu.LIE_REN, ShengYiWu.PART_BEI, hp_percent=ShengYiWu.BONUS_MAX,
                  crit_rate=0.031, crit_damage=0.218, elem_mastery=37, def_v=37),
        ShengYiWu(ShengYiWu.LIE_REN, ShengYiWu.PART_BEI, hp_percent=ShengYiWu.BONUS_MAX,
                  energe_recharge=0.045, crit_rate=0.105, atk=18, hp=657),

        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=ShengYiWu.ELEM_TYPE_BING,
                  atk=35, atk_per=0.111, elem_mastery=19, crit_rate=0.128),
        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=ShengYiWu.ELEM_TYPE_HUO,
                  crit_rate=0.035, def_v=44, atk_per=0.053, crit_damage=0.28),
        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=ShengYiWu.ELEM_TYPE_SHUI,
                  hp_percent=0.163, crit_damage=0.14, energe_recharge=0.052, atk=27),
        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=ShengYiWu.ELEM_TYPE_SHUI,
                  def_v=37, energe_recharge=0.058, hp=448, crit_rate=0.105),

        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=ShengYiWu.ELEM_TYPE_SHUI,
                  crit_rate=0.109, def_v=32, hp=478, hp_percent=0.058),
        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=ShengYiWu.ELEM_TYPE_CAO,
                  crit_rate=0.101, elem_mastery=19, crit_damage=0.179, hp=209),

        ShengYiWu(ShengYiWu.SHA_SHANG, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=ShengYiWu.ELEM_TYPE_LEI,
                  crit_rate=0.07, atk_per=0.053, atk=54, crit_damage=0.132),

        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_BEI, hp_percent=ShengYiWu.BONUS_MAX,
                  crit_damage=0.249, hp=508, crit_rate=0.031),
        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_BEI, elem_mastery=ShengYiWu.ELEM_MASTERY_MAIN,
                  atk_per=0.053, def_per=0.16, hp=0.058, energe_recharge=0.175),

        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=ShengYiWu.ELEM_TYPE_BING,
                  hp=239, crit_rate=0.066, atk_per=0.21, atk=37),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_BEI, hp_percent=ShengYiWu.BONUS_MAX,
                  crit_rate=0.066, crit_damage=0.171, atk=27, energe_recharge=0.045),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=ShengYiWu.ELEM_TYPE_FENG,
                  crit_damage=0.148, atk=14, crit_rate=0.121, def_v=19),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=ShengYiWu.ELEM_TYPE_SHUI,
                  hp_percent=0.152, crit_damage=0.194, def_v=21, hp=239),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=ShengYiWu.ELEM_TYPE_HUO,
                  crit_rate=0.062, crit_damage=0.28, atk=14, def_v=16),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_BEI, elem_mastery=ShengYiWu.ELEM_MASTERY_MAIN,
                  crit_rate=0.035, crit_damage=0.194, hp=717, hp_percent=0.053),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=ShengYiWu.ELEM_TYPE_CAO,
                  hp_percent=0.163, energe_recharge=0.045, elem_mastery=40, crit_rate=0.074),

        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_BEI, elem_mastery=ShengYiWu.ELEM_MASTERY_MAIN,
                  atk=16, crit_rate=0.089, hp_percent=0.187, hp=239),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=ShengYiWu.ELEM_TYPE_LEI,
                  crit_damage=0.179, elem_mastery=91, atk=19, def_per=0.073),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=ShengYiWu.ELEM_TYPE_YAN,
                  crit_damage=0.14, def_per=0.233, crit_rate=0.027, atk_per=0.047),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=ShengYiWu.ELEM_TYPE_CAO,
                  elem_mastery=54, atk_per=0.053, atk=33, crit_damage=0.155),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_BEI, elem_mastery=ShengYiWu.ELEM_MASTERY_MAIN,
                  energe_recharge=0.149, hp=478, crit_damage=0.062, atk=33),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_BEI, atk_per=ShengYiWu.BONUS_MAX,
                  crit_damage=0.218, crit_rate=0.066, def_v=39, energe_recharge=0.058),

        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_BEI, atk_per=ShengYiWu.BONUS_MAX,
                  energe_recharge=0.214, atk=33, crit_damage=0.07, crit_rate=0.035),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=ShengYiWu.ELEM_TYPE_FENG,
                  hp_percent=0.093, def_v=16, energe_recharge=0.162, hp=538),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=ShengYiWu.ELEM_TYPE_SHUI,
                  hp=717, hp_percent=0.146, def_per=0.073, crit_damage=0.07),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_BEI, hp_percent=ShengYiWu.BONUS_MAX,
                  energe_recharge=0.13, def_per=0.204, hp=568, def_v=16),

        ShengYiWu(ShengYiWu.CHEN_LUN, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=ShengYiWu.ELEM_TYPE_CAO,
                  crit_damage=0.21,  elem_mastery=16, def_v=32, hp_percent=0.099),
        ShengYiWu(ShengYiWu.CHEN_LUN, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=ShengYiWu.ELEM_TYPE_BING,
                  def_per=0.058, crit_rate=0.07, crit_damage=0.218, atk=33),

        ShengYiWu(ShengYiWu.QI_SHI_DAO, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=ShengYiWu.ELEM_TYPE_CAO,
                  elem_mastery=40, energe_recharge=0.058, crit_damage=0.241, hp_percent=0.047),

        ShengYiWu(ShengYiWu.ZONG_SHI, ShengYiWu.PART_BEI, atk_per=ShengYiWu.BONUS_MAX,
                  crit_damage=0.194, def_per=0.124, def_v=42, energe_recharge=0.117),
        ShengYiWu(ShengYiWu.ZONG_SHI, ShengYiWu.PART_BEI, hp_percent=ShengYiWu.BONUS_MAX,
                  energe_recharge=0.117, hp=568, def_v=58, crit_damage=0.07),
        ShengYiWu(ShengYiWu.ZONG_SHI, ShengYiWu.PART_BEI,
                  hp_percent=ShengYiWu.BONUS_MAX, hp=269, def_v=72, elem_mastery=44, atk=14),

        ShengYiWu(ShengYiWu.YUE_TUAN, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=ShengYiWu.ELEM_TYPE_SHUI,
                  atk=29, crit_damage=0.241, hp=239, hp_percent=0.099),
        ShengYiWu(ShengYiWu.YUE_TUAN, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=ShengYiWu.ELEM_TYPE_HUO,
                  hp_percent=0.041, crit_damage=0.14, crit_rate=0.105, hp=568),
        ShengYiWu(ShengYiWu.YUE_TUAN, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=ShengYiWu.ELEM_TYPE_SHUI,
                  hp=538, crit_damage=0.078, atk_per=0.152, crit_rate=0.074),

        ShengYiWu(ShengYiWu.JUE_DOU_SHI, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=ShengYiWu.ELEM_TYPE_HUO,
                  atk_per=0.163, energe_recharge=0.065, atk=29, crit_damage=0.202),
        ShengYiWu(ShengYiWu.JUE_DOU_SHI, ShengYiWu.PART_BEI, hp_percent=ShengYiWu.BONUS_MAX,
                  crit_rate=0.062, atk=14, energe_recharge=0.162, def_v=37),

        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=ShengYiWu.ELEM_TYPE_HUO,
                  crit_damage=0.256, def_per=0.139, energe_recharge=0.091, atk_per=0.058),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=ShengYiWu.ELEM_TYPE_BING,
                  crit_damage=0.14, hp=956, def_v=21, energe_recharge=0.052),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=ShengYiWu.ELEM_TYPE_SHUI,
                  atk=14, hp_percent=0.14, crit_damage=0.202, hp=269),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=ShengYiWu.ELEM_TYPE_HUO,
                  crit_rate=0.031, energe_recharge=0.097, elem_mastery=21, crit_damage=0.256),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=ShengYiWu.ELEM_TYPE_LEI,
                  energe_recharge=0.123, crit_damage=0.148, atk_per=0.105, crit_rate=0.066),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_BEI, elem_mastery=ShengYiWu.ELEM_MASTERY_MAIN,
                  hp_percent=0.053, crit_damage=0.202, energe_recharge=0.052, crit_rate=0.097),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=ShengYiWu.ELEM_TYPE_BING,
                  atk_per=0.192, hp=299, energe_recharge=0.11, atk=16),
    ],
    ShengYiWu.PART_TOU: [
        ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_TOU, hp_percent=ShengYiWu.BONUS_MAX,
                  crit_damage=0.202, crit_rate=0.074, def_per=0.066, def_v=63),
        ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_TOU,
                  crit_rate=ShengYiWu.CRIT_RATE_MAIN, def_v=37, hp=239, atk=33, hp_percent=0.157),
        ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_TOU, crit_rate=ShengYiWu.CRIT_RATE_MAIN,
                  def_v=39, elem_mastery=44, hp=896, crit_damage=0.078),
        ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_TOU, crit_damage=ShengYiWu.CRIT_DAMAGE_MAIN,
                  hp=478, hp_percent=0.111, atk_per=0.087, crit_rate=0.066),
        ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_TOU, crit_damage=ShengYiWu.CRIT_DAMAGE_MAIN,
                  crit_rate=0.062, energe_recharge=0.097, def_v=32, def_per=0.132),

        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_TOU, crit_damage=ShengYiWu.CRIT_DAMAGE_MAIN,
                  atk=18, def_v=56, atk_per=0.105, crit_rate=0.093),
        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_TOU, crit_damage=ShengYiWu.CRIT_DAMAGE_MAIN,
                  def_per=0.058, hp=687, hp_percent=0.111, crit_rate=0.07),

        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_TOU, crit_damage=ShengYiWu.CRIT_DAMAGE_MAIN,
                  hp_percent=0.169, crit_rate=0.078, elem_mastery=63, atk_per=0.053),
        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_TOU, crit_damage=ShengYiWu.CRIT_DAMAGE_MAIN,
                  hp=448, atk=37, hp_percent=0.099, crit_rate=0.097),
        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_TOU, crit_rate=ShengYiWu.CRIT_RATE_MAIN,
                  def_v=21, crit_damage=0.14, atk=33, elem_mastery=58),
        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_TOU, crit_rate=ShengYiWu.CRIT_RATE_MAIN,
                  def_per=0.058, energe_recharge=0.227, atk_per=0.058, crit_damage=0.155),
        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_TOU, crit_damage=ShengYiWu.CRIT_DAMAGE_MAIN,
                  atk=33, crit_rate=0.101, def_v=16, atk_per=0.087),

        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_TOU, crit_damage=ShengYiWu.CRIT_DAMAGE_MAIN,
                  elem_mastery=47, def_v=32, atk_per=0.152, crit_rate=0.066),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_TOU, hp_percent=ShengYiWu.BONUS_MAX,
                  energe_recharge=0.142, atk=19, crit_damage=0.132, crit_rate=0.066),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_TOU, crit_damage=ShengYiWu.CRIT_DAMAGE_MAIN,
                  atk=19, def_v=35, crit_rate=0.132, energe_recharge=0.052),

        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_TOU, crit_rate=ShengYiWu.CRIT_RATE_MAIN,
                  atk_per=0.047, crit_damage=0.256, energe_recharge=0.104, hp=209),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_TOU, crit_rate=ShengYiWu.CRIT_RATE_MAIN,
                  atk=31, crit_damage=0.179, def_per=0.058, energe_recharge=0.104),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_TOU, crit_rate=ShengYiWu.CRIT_RATE_MAIN,
                  crit_damage=0.218, hp_percent=0.087, elem_mastery=16, atk_per=0.099),

        ShengYiWu(ShengYiWu.ZHUI_YI, ShengYiWu.PART_TOU, crit_damage=ShengYiWu.CRIT_DAMAGE_MAIN,
                  hp_percent=0.041, atk=18, elem_mastery=84, crit_rate=0.062),
        ShengYiWu(ShengYiWu.ZHUI_YI, ShengYiWu.PART_TOU, crit_rate=ShengYiWu.CRIT_RATE_MAIN,
                  elem_mastery=40, atk_per=0.053, energe_recharge=0.162, crit_damage=0.14),

        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_TOU, hp_percent=ShengYiWu.BONUS_MAX,
                  hp=209, crit_rate=0.074, atk=18, crit_damage=0.241),

        ShengYiWu(ShengYiWu.CHEN_LUN, ShengYiWu.PART_TOU, crit_rate=ShengYiWu.CRIT_RATE_MAIN,
                  energe_recharge=0.058, def_v=37, crit_damage=0.155, hp_percent=0.134),
        ShengYiWu(ShengYiWu.CHEN_LUN, ShengYiWu.PART_TOU, crit_rate=ShengYiWu.CRIT_RATE_MAIN,
                  def_v=44, crit_damage=0.225, energe_recharge=0.097, elem_mastery=23),

        ShengYiWu(ShengYiWu.ZONG_SHI, ShengYiWu.PART_TOU, crit_rate=ShengYiWu.CRIT_RATE_MAIN,
                  hp=299, atk=16, def_per=0.321, crit_damage=0.14),
        ShengYiWu(ShengYiWu.ZONG_SHI, ShengYiWu.PART_TOU, crit_damage=ShengYiWu.CRIT_DAMAGE_MAIN,
                  def_per=0.109, crit_rate=0.148, atk_per=0.058, energe_recharge=0.058),
        ShengYiWu(ShengYiWu.ZONG_SHI, ShengYiWu.PART_TOU, crit_rate=ShengYiWu.CRIT_RATE_MAIN,
                  def_v=60, crit_damage=0.187, hp=269, elem_mastery=47),

        ShengYiWu(ShengYiWu.RU_LEI, ShengYiWu.PART_TOU, crit_rate=ShengYiWu.CRIT_RATE_MAIN,
                  hp=777, atk=27, crit_damage=0.132, elem_mastery=23),

        ShengYiWu(ShengYiWu.YUE_TUAN, ShengYiWu.PART_TOU, crit_rate=ShengYiWu.CRIT_RATE_MAIN,
                  hp=508, crit_damage=0.14, atk=45, atk_per=0.099),

        ShengYiWu(ShengYiWu.FENG_TAO, ShengYiWu.PART_TOU, crit_rate=ShengYiWu.CRIT_RATE_MAIN,
                  crit_damage=0.272, def_v=23, hp=538, hp_percent=0.041),

        ShengYiWu(ShengYiWu.JUE_DOU_SHI, ShengYiWu.PART_TOU, crit_rate=ShengYiWu.CRIT_RATE_MAIN,
                  atk=19, crit_damage=0.194, hp=568, atk_per=0.093),
        ShengYiWu(ShengYiWu.JUE_DOU_SHI, ShengYiWu.PART_TOU, crit_rate=ShengYiWu.CRIT_RATE_MAIN,
                  hp_percent=0.053, crit_damage=0.303, hp=209, atk=39),

        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_TOU, crit_damage=ShengYiWu.CRIT_DAMAGE_MAIN,
                  atk=14, energe_recharge=0.188, elem_mastery=56, crit_rate=0.078),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_TOU, hp_percent=ShengYiWu.BONUS_MAX,
                  hp=747, atk_per=0.053, crit_damage=0.132, crit_rate=0.105),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_TOU, crit_damage=ShengYiWu.CRIT_DAMAGE_MAIN, crit_rate=0.078,
                  def_v=32, energe_recharge=0.104, atk_per=0.087),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_TOU, atk_per=ShengYiWu.BONUS_MAX,
                  crit_rate=0.101, crit_damage=0.124, elem_mastery=40, hp_percent=0.047),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_TOU, crit_rate=ShengYiWu.CRIT_RATE_MAIN,
                  atk_per=0.152, elem_mastery=44, crit_damage=0.148, def_v=23),
    ]
}


def find_syw(match_syw_callback):
    matched_syw = []
    for sl in all_syw.values():
        for s in sl:
            if match_syw_callback(s):
                matched_syw.append(s)
    return matched_syw


def calculate_score(find_combine_callback, match_sha_callback, match_bei_callback, calculate_score_callbak, result_txt_file):
    # all_syw = {}
    # all_syw.update(all_syw_exclude_s_b)
    # all_syw.update(syw_s_b)

    all_combins_4 = find_combine_callback()
    print(len(all_combins_4))

    all_score_data = []
    max_crit_score = 0
    max_expect_score = 0

    all_combins_5 = {}
    for c in all_combins_4:
        parts = [p.part for p in c]
        parts_set = set(parts)
        if len(parts) != len(parts_set):
            continue

        miss_part = list(ShengYiWu.ALL_PARTS - parts_set)

        for s in all_syw[miss_part[0]]:
            if s.part == ShengYiWu.PART_SHA:
                if not match_sha_callback(s):
                    continue
            elif s.part == ShengYiWu.PART_BEI:
                if not match_bei_callback(s):
                    continue

            combine = c + (s, )
            sorted_combine = [None, None, None, None, None]

            for p in combine:
                if p.part == ShengYiWu.PART_HUA:
                    sorted_combine[0] = p
                elif p.part == ShengYiWu.PART_YU:
                    sorted_combine[1] = p
                elif p.part == ShengYiWu.PART_SHA:
                    sorted_combine[2] = p
                elif p.part == ShengYiWu.PART_BEI:
                    sorted_combine[3] = p
                else:
                    sorted_combine[4] = p

            scid = ""
            for sc in sorted_combine:
                scid += sc.id

            if scid not in all_combins_5:
                all_combins_5[scid] = sorted_combine

    print(len(all_combins_5))
    for c in all_combins_5.values():
        score_data = calculate_score_callbak(c)
        if not score_data:
            continue

        expect_score = score_data[0]
        if expect_score > max_expect_score:
            max_expect_score = expect_score

        crit_score = score_data[1]
        if crit_score > max_crit_score:
            max_crit_score = crit_score

        all_score_data.append(score_data)

    if all_score_data:
        # print(len(all_score_data))
        score_dict = {}
        for score_data in all_score_data:
            expect_score = score_data[0]
            crit_score = score_data[1]
            score_data[0] = str(
                expect_score) + '(' + str(round(expect_score / max_expect_score, 4)) + ')'
            score_data[1] = str(
                crit_score) + '(' + str(round(crit_score / max_crit_score, 4)) + ')'

            score = expect_score / max_expect_score + crit_score / max_crit_score
            if score < 1.8: #0.85 * 2:
                continue

            if score in score_dict:
                score_dict[score].append(score_data)
            else:
                score_dict[score] = [score_data]

        with open(result_txt_file, 'w', encoding='utf-8') as f:
            for i in sorted(score_dict):
                for c in score_dict[i]:
                    # print((i, c))
                    f.write(str((round(i, 4), c, )))
                    f.write('\n\n')

            f.write("expect_max: " + str(max_expect_score))
            f.write('\n')
            f.write("crit_max: " + str(max_crit_score))
            f.write('\n')

    return score_dict
