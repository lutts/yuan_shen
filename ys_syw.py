#!/user/bin/env python3 -c
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

import sys
import os
import logging
import itertools
import copy
import uuid
import concurrent.futures
import traceback
from math import ceil
from collections.abc import Callable

from ys_basic import Ys_Elem_Type, Ys_Attributes, ys_expect_damage, ys_crit_damage


def chunk_into_n(lst, n):
    size = ceil(len(lst) / n)
    return list(
        map(lambda x: lst[x * size:x * size + size],
            list(range(n)))
    )

class ShengYiWu(Ys_Attributes):
    ALL_PARTS = ['h', 'y', 's', 'b', 't']
    PART_HUA = 'h'
    PART_YU = 'y'
    PART_SHA = 's'
    PART_BEI = 'b'
    PART_TOU = 't'

    PART_TO_POSITION = {
        PART_HUA: 0,
        PART_YU: 1,
        PART_SHA: 2,
        PART_BEI: 3,
        PART_TOU: 4
    }

    ENERGY_RECHARGE_MAX = 0.518
    BONUS_MAX = 0.466
    CRIT_RATE_MAIN = 0.311
    CRIT_DAMAGE_MAIN = 0.622
    ELEM_MASTERY_MAIN = 187

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
    HUI_SHENG = "hui_sheng"

    def __init__(self, name, part, crit_rate=0.0, crit_damage=0.0, hp_percent=0.0, hp=0, energy_recharge=0.0,
                 atk_per=0.0, atk=0, def_per=0.0, def_v=0, elem_mastery=0, elem_bonus=0.0, elem_type: Ys_Elem_Type=None):
        self.id = str(uuid.uuid4())
        self.name = name
        self.part = part
        self.position = ShengYiWu.PART_TO_POSITION[part]
        # TODO: 圣遗物属性有隐藏小数点，有空的时候可以研究一下，不过影响不大，不急

        super().__init__(crit_rate=crit_rate, crit_damage=crit_damage, hp_percent=hp_percent, hp=hp,
                         atk_per=atk_per, atk=atk, def_per=def_per, def_v=def_v,
                         elem_mastery=elem_mastery, elem_bonus=elem_bonus,
                         energy_recharge=energy_recharge)
        self.elem_type: Ys_Elem_Type = elem_type

    @classmethod
    def from_string(cls, syw_str: str):
        # (jue_yuan, h, cc:0.066, cd:0.117, atkp:0.111, atk:33)
        syw_str = syw_str.strip('() ')
        attrs = syw_str.split(", ")
        if len(attrs) < 6:
            return None
        
        name = attrs[0]
        part = attrs[1]
        syw = ShengYiWu(name, part)
        for i in range(2, len(attrs)):
            attr = attrs[i]
            key, value = attr.split(':')

            try:
                fvalue = float(value)
            except:
                pass

            if key == "cc":
                syw.crit_rate = fvalue
            elif key == "cd":
                syw.crit_damage = fvalue
            elif key == "hpp":
                syw.hp_percent = fvalue
            elif key == "hp":
                syw.hp = int(value)
            elif key == "re":
                syw.energy_recharge = fvalue
            elif key == "atkp":
                syw.atk_per = fvalue
            elif key == "atk":
                syw.atk = int(value)
            elif key == "defp":
                syw.def_per = fvalue
            elif key == "def":
                syw.def_v = int(value)
            elif key == "elem":
                syw.elem_mastery = int(value)
            elif key == "bonus":
                syw.elem_bonus = fvalue
            elif key == "et":
                syw.elem_type = Ys_Elem_Type(value)

        return syw
    
    @classmethod
    def string_to_syw_combine(cls, syw_combine_str: str | list[str]):
        if isinstance(syw_combine_str, list):
            syw_str_lst = syw_combine_str
        else:
            syw_str_lst = syw_combine_str.split("), (")
        syw_combine = []
        for syw_str in syw_str_lst:
            syw = ShengYiWu.from_string(syw_str)
            if syw:
                syw_combine.append(syw)
            else:
                raise Exception("parse syw combine string failed on " + syw_str)
            
        return syw_combine

    def __str__(self):
        s = '(' + self.name + ', ' + self.part + ", "
        s += super().__str__()
        if self.elem_type:
            s += ", et:" + self.elem_type.value
        s += ')'
        return s

    def __repr__(self) -> str:
        return self.__str__()


all_syw = {
    ShengYiWu.PART_HUA: [
        ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_HUA, crit_rate=0.14,
                  atk=14, crit_damage=0.078, energy_recharge=0.168),
        ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_HUA,
                  crit_rate=0.07, crit_damage=0.194, atk=39, def_per=0.058),
        ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_HUA, energy_recharge=0.058,
                  crit_damage=0.078, elem_mastery=54, crit_rate=0.109),
        ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_HUA, crit_damage=0.21,
                  hp_percent=0.152, crit_rate=0.031, def_v=23),

        ShengYiWu(ShengYiWu.LIE_REN, ShengYiWu.PART_HUA, crit_rate=0.066,
                  crit_damage=0.287, elem_mastery=16, atk_per=0.099),
        ShengYiWu(ShengYiWu.LIE_REN, ShengYiWu.PART_HUA, atk=16,
                  hp_percent=0.181, crit_damage=0.148, atk_per=0.058),
        ShengYiWu(ShengYiWu.LIE_REN, ShengYiWu.PART_HUA, energy_recharge=0.123,
                  crit_rate=0.101, hp_percent=0.053, crit_damage=0.117),
        ShengYiWu(ShengYiWu.LIE_REN, ShengYiWu.PART_HUA, def_per=0.066,
                  crit_damage=0.148, crit_rate=0.105, energy_recharge=0.104),

        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_HUA,
                  energy_recharge=0.045, hp_percent=0.053, crit_damage=0.326, atk_per=0.099),
        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_HUA,
                  crit_damage=0.218, crit_rate=0.035, hp_percent=0.157, atk=31),
        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_HUA,
                  crit_rate=0.097, crit_damage=0.132, elem_mastery=21, atk=29),
        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_HUA,
                  crit_damage=0.14, def_per=0.051, hp_percent=0.146, crit_rate=0.07),
        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_HUA, crit_rate=0.14,
                  atk_per=0.117, crit_damage=0.07, energy_recharge=0.045),
        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_HUA, crit_damage=0.078,
                  crit_rate=0.148, elem_mastery=16, atk_per=0.099),
        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_HUA, crit_damage=0.218,
                  def_per=0.073, hp_percent=0.105, energy_recharge=0.104),

        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_HUA,
                  crit_rate=0.128, crit_damage=0.225,  def_per=0.066, elem_mastery=16),
        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_HUA,
                  crit_rate=0.035, crit_damage=0.249, energy_recharge=0.117, atk_per=0.099),
        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_HUA,
                  atk=35, def_v=42, crit_rate=0.039, crit_damage=0.303),
        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_HUA,
                  elem_mastery=42, crit_rate=0.105, atk=14, hp_percent=0.134),
        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_HUA,
                  crit_damage=0.155, hp_percent=0.053, atk=35, crit_rate=0.105),
        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_HUA,
                  def_per=0.073, hp_percent=0.152, crit_rate=0.027, crit_damage=0.202),
        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_HUA,
                  def_per=0.139, crit_rate=0.101, energy_recharge=0.058, crit_damage=0.124),

        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_HUA,
                  crit_damage=0.124, hp_percent=0.099, atk=14, crit_rate=0.124),
        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_HUA, crit_damage=0.249,
                  energy_recharge=0.065, def_per=0.066, crit_rate=0.089),
        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_HUA, def_v=23,
                  crit_damage=0.272, elem_mastery=44, energy_recharge=0.065),
        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_HUA, crit_damage=0.28,
                  hp_percent=0.099, atk_per=0.053, crit_rate=0.027),

        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_HUA,
                  elem_mastery=44, crit_rate=0.105, crit_damage=0.124, def_v=44),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_HUA,
                  crit_rate=0.078, atk_per=0.087, elem_mastery=37, crit_damage=0.225),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_HUA, energy_recharge=0.11,
                  hp_percent=0.152, crit_rate=0.035, elem_mastery=70),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_HUA, def_v=16,
                  elem_mastery=79, hp_percent=0.093, energy_recharge=0.11),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_HUA,
                  crit_damage=0.288, crit_rate=0.062, def_v=21, hp_percent=0.047),

        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_HUA, hp_percent=0.181,
                  energy_recharge=0.123, def_v=23, crit_rate=0.07),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_HUA, atk_per=0.041,
                  crit_rate=0.062, elem_mastery=54, crit_damage=0.21),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_HUA, crit_rate=0.144,
                  crit_damage=0.078, hp_percent=0.105, elem_mastery=40),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_HUA, elem_mastery=44,
                  crit_damage=0.21, def_per=0.066, energy_recharge=0.194),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_HUA, elem_mastery=21,
                  crit_rate=0.066, energy_recharge=0.181, crit_damage=0.124),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_HUA, atk=33,
                  crit_rate=0.066, atk_per=0.111, crit_damage=0.117),

        ShengYiWu(ShengYiWu.ZHUI_YI, ShengYiWu.PART_HUA, crit_damage=0.132,
                  crit_rate=0.152, energy_recharge=0.097, def_per=0.073),
        ShengYiWu(ShengYiWu.ZHUI_YI, ShengYiWu.PART_HUA, def_v=16,
                  crit_rate=0.035, crit_damage=0.249, atk=29),

        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_HUA, crit_damage=0.132,
                  crit_rate=0.101, atk=16, energy_recharge=0.175),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_HUA, def_v=39,
                  atk=16, crit_damage=0.241, crit_rate=0.066),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_HUA,
                  energy_recharge=0.155, atk=35, hp_percent=0.128, atk_per=0.047),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_HUA, hp_percent=0.134,
                  energy_recharge=0.162, crit_rate=0.074, crit_damage=0.078),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_HUA,
                  energy_recharge=0.117, atk=14, atk_per=0.117, crit_damage=0.264),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_HUA, def_per=0.131,
                  energy_recharge=0.175, def_v=37, crit_damage=0.062),

        ShengYiWu(ShengYiWu.CHEN_LUN, ShengYiWu.PART_HUA, crit_rate=0.066,
                  crit_damage=0.148, hp_percent=0.146, def_per=0.109),
        ShengYiWu(ShengYiWu.CHEN_LUN, ShengYiWu.PART_HUA, crit_damage=0.054,
                  energy_recharge=0.065, crit_rate=0.132, def_v=39),

        ShengYiWu(ShengYiWu.ZONG_SHI, ShengYiWu.PART_HUA, def_per=0.124,
                  crit_damage=0.062, hp_percent=0.111, energy_recharge=0.214),
        ShengYiWu(ShengYiWu.ZONG_SHI, ShengYiWu.PART_HUA, energy_recharge=0.227,
                  atk_per=0.058, elem_mastery=44, hp_percent=0.047),
        ShengYiWu(ShengYiWu.ZONG_SHI, ShengYiWu.PART_HUA, crit_damage=0.14,
                  energy_recharge=0.065, atk_per=0.099, crit_rate=0.105),

        ShengYiWu(ShengYiWu.YUE_TUAN, ShengYiWu.PART_HUA, elem_mastery=58,
                  crit_damage=0.148, crit_rate=0.078, def_per=0.051),

        ShengYiWu(ShengYiWu.FENG_TAO, ShengYiWu.PART_HUA, crit_damage=0.078,
                  energy_recharge=0.065, atk_per=0.146, crit_rate=0.144),
        ShengYiWu(ShengYiWu.FENG_TAO, ShengYiWu.PART_HUA,
                  atk_per=0.099, crit_rate=0.066, crit_damage=0.202, atk=18),

        ShengYiWu(ShengYiWu.JUE_DOU_SHI, ShengYiWu.PART_HUA,
                  hp_percent=0.157, crit_damage=0.218, crit_rate=0.078, def_v=16),
        ShengYiWu(ShengYiWu.JUE_DOU_SHI, ShengYiWu.PART_HUA,
                  crit_damage=0.14, crit_rate=0.062, def_v=16, def_per=0.168),

        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_HUA, crit_damage=0.194,
                  hp_percent=0.128, atk_per=0.041, energy_recharge=0.104),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_HUA, atk_per=0.105,
                  elem_mastery=19, crit_rate=0.132, energy_recharge=0.11),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_HUA, crit_rate=0.086,
                  crit_damage=0.202, elem_mastery=40, energy_recharge=0.052),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_HUA, elem_mastery=16,
                  atk_per=0.134, crit_damage=0.132, crit_rate=0.089),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_HUA, def_v=21,
                  atk_per=0.134, atk=27, crit_damage=0.218),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_HUA,
                  crit_rate=0.097, energy_recharge=0.13, atk_per=0.111, crit_damage=0.07),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_HUA,
                  atk_per=0.099, atk=14, crit_damage=0.187, energy_recharge=0.11),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_HUA, atk_per=0.163,
                  crit_rate=0.039, crit_damage=0.155, elem_mastery=40),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_HUA, atk_per=0.099,
                  hp_percent=0.099, crit_damage=0.21, energy_recharge=0.058),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_HUA, elem_mastery=16,
                  crit_rate=0.039, crit_damage=0.264, def_v=46), 
    ],
    ShengYiWu.PART_YU: [
        ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_YU, hp=209,
                  energy_recharge=0.123, hp_percent=0.21, crit_damage=0.124),
        ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_YU, hp=568,
                  crit_damage=0.21, hp_percent=0.053, def_v=56),
        ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_YU, def_v=37,
                  elem_mastery=40, crit_damage=0.256, crit_rate=0.027),
        ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_YU, hp_percent=0.14,
                  elem_mastery=19, crit_rate=0.097, energy_recharge=0.052),
        ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_YU, elem_mastery=37,
                  energy_recharge=0.11, crit_damage=0.14, crit_rate=0.07),

        ShengYiWu(ShengYiWu.LIE_REN, ShengYiWu.PART_YU,
                  crit_damage=0.202, crit_rate=0.031, hp_percent=0.14, hp=239),
        ShengYiWu(ShengYiWu.LIE_REN, ShengYiWu.PART_YU,
                  hp=239, energy_recharge=0.065, crit_damage=0.132, hp_percent=0.181),
        ShengYiWu(ShengYiWu.LIE_REN, ShengYiWu.PART_YU, crit_damage=0.194,
                  energy_recharge=0.065, crit_rate=0.062, elem_mastery=37),
        ShengYiWu(ShengYiWu.LIE_REN, ShengYiWu.PART_YU, hp=448,
                  crit_damage=0.14, crit_rate=0.136, elem_mastery=16),

        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_YU,
                  hp=568, crit_rate=0.062, hp_percent=0.093, crit_damage=0.187),
        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_YU,
                  hp=508, crit_rate=0.113, crit_damage=0.117, def_v=42),
        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_YU,
                  energy_recharge=0.065, crit_damage=0.295, hp=269, hp_percent=0.093),
        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_YU,
                  atk_per=0.047, hp=538, crit_damage=0.295, crit_rate=0.031),
        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_YU, def_v=23,
                  crit_damage=0.28, crit_rate=0.027, energy_recharge=0.123),

        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_YU,
                  crit_rate=0.089, hp=478, hp_percent=0.047, crit_damage=0.187),
        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_YU,
                  hp=508, def_per=0.131, hp_percent=0.093, crit_damage=0.225),
        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_YU,
                  hp_percent=0.058, crit_rate=0.062, crit_damage=0.132, energy_recharge=0.162),
        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_YU, def_v=23,
                  crit_rate=0.117, crit_damage=0.194, elem_mastery=23),
        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_YU, crit_damage=0.07,
                  atk_per=0.058, energy_recharge=0.104, crit_rate=0.136),

        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_YU, hp=508,
                  atk_per=0.099, crit_rate=0.058, crit_damage=0.194),
        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_YU, atk_per=0.105,
                  crit_rate=0.035, energy_recharge=0.058, elem_mastery=93),

        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_YU, crit_damage=0.078,
                  atk_per=0.041, crit_rate=0.035, elem_mastery=96),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_YU, energy_recharge=0.149,
                  hp_percent=0.117, crit_rate=0.035, crit_damage=0.132),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_YU, def_v=37,
                  crit_damage=0.07, crit_rate=0.144, def_per=0.066),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_YU,
                  crit_damage=0.272, hp=239, crit_rate=0.07, def_v=21),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_YU, crit_damage=0.132,
                  crit_rate=0.066, hp_percent=0.041, elem_mastery=56),

        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_YU, def_per=0.073,
                  atk_per=0.087, crit_rate=0.027, energy_recharge=0.285),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_YU,
                  crit_damage=0.148, def_per=0.117, def_v=19, crit_rate=0.148),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_YU, crit_rate=0.039,
                  crit_damage=0.35, hp_percent=0.041, def_v=39),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_YU, hp=448,
                  crit_damage=0.078, energy_recharge=0.311, hp_percent=0.053),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_YU, hp=807,
                  atk_per=0.047, energy_recharge=0.11, crit_damage=0.171),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_YU, elem_mastery=16,
                  atk_per=0.058, crit_damage=0.148, crit_rate=0.132),

        ShengYiWu(ShengYiWu.ZHUI_YI, ShengYiWu.PART_YU, 
                  atk_per=0.041, energy_recharge=0.117, crit_damage=0.124, crit_rate=0.093),

        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_YU, crit_damage=0.132,
                  energy_recharge=0.175, crit_rate=0.101, hp_percent=0.041),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_YU, atk_per=0.111,
                  energy_recharge=0.117, hp_percent=0.21, def_per=0.073),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_YU, hp_percent=0.082,
                  energy_recharge=0.097, atk_per=0.21, crit_rate=0.035),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_YU, atk_per=0.099,
                  energy_recharge=0.246, crit_damage=0.099, crit_rate=0.035),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_YU, def_v=23,
                  crit_rate=0.031, hp=478, hp_percent=0.216),

        ShengYiWu(ShengYiWu.CHEN_LUN, ShengYiWu.PART_YU,
                  crit_rate=0.14, atk_per=0.053, hp=478, crit_damage=0.109),
        ShengYiWu(ShengYiWu.CHEN_LUN, ShengYiWu.PART_YU,
                  crit_damage=0.14, def_per=0.16, crit_rate=0.101, hp=239),
        ShengYiWu(ShengYiWu.CHEN_LUN, ShengYiWu.PART_YU, def_v=16,
                  crit_damage=0.117, crit_rate=0.124, atk_per=0.041),
        ShengYiWu(ShengYiWu.CHEN_LUN, ShengYiWu.PART_YU, hp_percent=0.047,
                  def_per=0.066, energy_recharge=0.065, crit_rate=0.167),

        ShengYiWu(ShengYiWu.ZONG_SHI, ShengYiWu.PART_YU,
                  elem_mastery=47, def_v=60, hp=269, energy_recharge=0.149),
        ShengYiWu(ShengYiWu.ZONG_SHI, ShengYiWu.PART_YU, hp=209,
                  hp_percent=0.157, energy_recharge=0.104, def_v=35),
        ShengYiWu(ShengYiWu.ZONG_SHI, ShengYiWu.PART_YU, hp_percent=0.093,
                  crit_rate=0.07, energy_recharge=0.117, atk_per=0.111),

        ShengYiWu(ShengYiWu.RU_LEI, ShengYiWu.PART_YU, crit_rate=0.066,
                  crit_damage=0.218, elem_mastery=63, energy_recharge=0.065),

        ShengYiWu(ShengYiWu.YUE_TUAN, ShengYiWu.PART_YU, elem_mastery=44,
                  crit_damage=0.124, atk_per=0.087, crit_rate=0.101),

        ShengYiWu(ShengYiWu.FENG_TAO, ShengYiWu.PART_YU, hp=239,
                  crit_damage=0.233, atk_per=0.093, crit_rate=0.062),

        ShengYiWu(ShengYiWu.JUE_DOU_SHI, ShengYiWu.PART_YU, hp_percent=0.111,
                  crit_rate=0.167, energy_recharge=0.045, crit_damage=0.062),
        ShengYiWu(ShengYiWu.JUE_DOU_SHI, ShengYiWu.PART_YU, crit_rate=0.144,
                  crit_damage=0.07, hp_percent=0.111, energy_recharge=0.045),

        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_YU,
                  crit_rate=0.062, crit_damage=0.132, atk_per=0.093, energy_recharge=0.162),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_YU,
                  def_per=0.139, crit_damage=0.124, elem_mastery=44, crit_rate=0.093),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_YU,
                  crit_rate=0.113, def_v=42, energy_recharge=0.091, crit_damage=0.124),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_YU,
                  def_v=23, crit_damage=0.295, hp=538, crit_rate=0.07),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_YU, crit_damage=0.194,
                  energy_recharge=0.052, elem_mastery=19, hp_percent=0.233),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_YU, crit_damage=0.14,
                  elem_mastery=40, crit_rate=0.101, atk_per=0.105),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_YU, hp_percent=0.128,
                  crit_rate=0.031, crit_damage=0.194, energy_recharge=0.052),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_YU, def_v=23,
                  crit_rate=0.128, crit_damage=0.07, atk_per=0.099),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_YU, crit_damage=0.256,
                  energy_recharge=0.097, def_per=0.058, atk_per=0.041),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_YU,
                  crit_rate=0.066, crit_damage=0.21, hp=299, atk_per=0.099),

        ShengYiWu(ShengYiWu.HUI_SHENG, ShengYiWu.PART_YU,
                  energy_recharge=0.097, elem_mastery=40, hp=299, crit_damage=0.218)

    ],
    ShengYiWu.PART_SHA: [
        ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_SHA, atk_per=ShengYiWu.BONUS_MAX,
                  def_per=0.051, crit_damage=0.194, crit_rate=0.093, hp=269),
        ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_SHA, hp_percent=ShengYiWu.BONUS_MAX,
                  energy_recharge=0.045, crit_damage=0.078, crit_rate=0.113, def_v=60),

        ShengYiWu(ShengYiWu.LIE_REN, ShengYiWu.PART_SHA, energy_recharge=ShengYiWu.ENERGY_RECHARGE_MAX,
                  atk=14, crit_rate=0.14, def_v=37, crit_damage=0.148),
        ShengYiWu(ShengYiWu.LIE_REN, ShengYiWu.PART_SHA, def_per=ShengYiWu.BONUS_MAX,
                  hp=508, crit_damage=0.132, crit_rate=0.058, atk=37),
        ShengYiWu(ShengYiWu.LIE_REN, ShengYiWu.PART_SHA, hp_percent=ShengYiWu.BONUS_MAX,
                  crit_rate=0.027, def_v=23, crit_damage=0.264, hp=478),
        ShengYiWu(ShengYiWu.LIE_REN, ShengYiWu.PART_SHA, elem_mastery=ShengYiWu.ELEM_MASTERY_MAIN,
                  def_per=0.073, crit_rate=0.128, crit_damage=0.148, hp_percent=0.041),

        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_SHA, hp_percent=ShengYiWu.BONUS_MAX,
                  energy_recharge=0.052, crit_damage=0.202, elem_mastery=44, crit_rate=0.062),

        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_SHA, def_per=ShengYiWu.BONUS_MAX,
                  energy_recharge=0.11, crit_damage=0.202, atk_per=0.093, crit_rate=0.062),
        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_SHA, hp_percent=ShengYiWu.BONUS_MAX,
                  crit_damage=0.319, def_v=19, crit_rate=0.031, energy_recharge=0.11),
        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_SHA, def_per=ShengYiWu.BONUS_MAX,
                  crit_damage=0.117, atk=14, crit_rate=0.113, energy_recharge=0.058),
        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_SHA, hp_percent=ShengYiWu.BONUS_MAX,
                  crit_rate=0.07, hp=568, crit_damage=0.21, atk=16),
        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_SHA, hp_percent=ShengYiWu.BONUS_MAX,
                  crit_damage=0.078, atk_per=0.087, crit_rate=0.132, def_v=16),
        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_SHA, hp_percent=ShengYiWu.BONUS_MAX,
                  atk=18, energy_recharge=0.091, crit_damage=0.218, crit_rate=0.074),
        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_SHA, elem_mastery=ShengYiWu.ELEM_MASTERY_MAIN,
                  atk_per=0.058, def_v=19, crit_damage=0.062, crit_rate=0.152),

        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_SHA, elem_mastery=ShengYiWu.ELEM_MASTERY_MAIN,
                  crit_rate=0.027, energy_recharge=0.11, def_per=0.204, crit_damage=0.21),
        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_SHA, elem_mastery=ShengYiWu.ELEM_MASTERY_MAIN,
                  crit_rate=0.128, atk=0.047, crit_damage=0.078, def_per=0.124),
        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_SHA, elem_mastery=ShengYiWu.ELEM_MASTERY_MAIN,
                  atk_per=0.14, def_v=35, crit_rate=0.062, atk=19),
        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_SHA, energy_recharge=ShengYiWu.ENERGY_RECHARGE_MAX,
                  elem_mastery=23, crit_damage=0.218, def_v=44, crit_rate=0.07),

        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_SHA, elem_mastery=ShengYiWu.ELEM_MASTERY_MAIN,
                  crit_damage=0.117, crit_rate=0.128, hp=538, energy_recharge=0.045),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_SHA, atk_per=ShengYiWu.BONUS_MAX,
                  crit_rate=0.109, def_v=32, crit_damage=0.233, hp=209),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_SHA, elem_mastery=ShengYiWu.ELEM_MASTERY_MAIN,
                  crit_damage=0.124, hp_percent=0.198, energy_recharge=0.11, def_v=16),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_SHA, atk_per=ShengYiWu.BONUS_MAX,
                  hp=269, def_v=37, crit_damage=0.124, crit_rate=0.132),

        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_SHA, atk_per=ShengYiWu.BONUS_MAX,
                  elem_mastery=19, hp_percent=0.105, crit_rate=0.086, crit_damage=0.202),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_SHA, energy_recharge=ShengYiWu.ENERGY_RECHARGE_MAX,
                  hp_percent=0.093, crit_damage=0.14, crit_rate=0.07, atk=35),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_SHA, energy_recharge=ShengYiWu.ENERGY_RECHARGE_MAX,
                  hp=448, crit_rate=0.07, atk_per=0.082, def_v=44),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_SHA, energy_recharge=ShengYiWu.ENERGY_RECHARGE_MAX,
                  crit_damage=0.194, elem_mastery=19, hp=508, def_per=0.117),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_SHA, energy_recharge=ShengYiWu.ENERGY_RECHARGE_MAX,
                  hp_percent=0.117, crit_rate=0.027, def_per=0.19, crit_damage=0.14),

        ShengYiWu(ShengYiWu.ZHUI_YI, ShengYiWu.PART_SHA, def_per=ShengYiWu.BONUS_MAX,
                  elem_mastery=42, crit_damage=0.187, crit_rate=0.097, atk=18),
        ShengYiWu(ShengYiWu.ZHUI_YI, ShengYiWu.PART_SHA, elem_mastery=ShengYiWu.ELEM_MASTERY_MAIN,
                  crit_damage=0.194, def_v=23, atk_per=0.047, crit_rate=0.101),
        ShengYiWu(ShengYiWu.ZHUI_YI, ShengYiWu.PART_SHA, elem_mastery=ShengYiWu.ELEM_MASTERY_MAIN,
                  crit_damage=0.054, atk=33, def_v=19, crit_rate=0.132),
        ShengYiWu(ShengYiWu.ZHUI_YI, ShengYiWu.PART_SHA, hp_percent=ShengYiWu.BONUS_MAX,
                  atk=19, crit_damage=0.14, elem_mastery=33, crit_rate=0.105),
        ShengYiWu(ShengYiWu.ZHUI_YI, ShengYiWu.PART_SHA, def_per=ShengYiWu.BONUS_MAX,
                  elem_mastery=40, crit_damage=0.14, crit_rate=0.066, energy_recharge=0.117),
        ShengYiWu(ShengYiWu.ZHUI_YI, ShengYiWu.PART_SHA, elem_mastery=ShengYiWu.ELEM_MASTERY_MAIN,
                  atk=27, crit_damage=0.218, energy_recharge=0.104, atk_per=0.041),

        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_SHA, hp_percent=ShengYiWu.BONUS_MAX,
                  crit_rate=0.066, atk=33, elem_mastery=40, crit_damage=0.21),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_SHA, hp_percent=ShengYiWu.BONUS_MAX,
                  def_v=37, energy_recharge=0.24, atk=19, crit_rate=0.07),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_SHA, elem_mastery=ShengYiWu.ELEM_MASTERY_MAIN,
                  energy_recharge=0.052, crit_damage=0.202, crit_rate=0.101, def_v=19),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_SHA, energy_recharge=ShengYiWu.ENERGY_RECHARGE_MAX,
                  crit_rate=0.101, hp=508, atk_per=0.099, def_v=23),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_SHA, hp_percent=ShengYiWu.BONUS_MAX,
                  atk_per=0.099, crit_rate=0.078, elem_mastery=40, energy_recharge=0.117),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_SHA, hp_percent=ShengYiWu.BONUS_MAX,
                  elem_mastery=44, atk=16, energy_recharge=0.058, crit_damage=0.272),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_SHA, energy_recharge=ShengYiWu.ENERGY_RECHARGE_MAX,
                  hp_percent=0.105, elem_mastery=40, def_v=35, atk=35),

        ShengYiWu(ShengYiWu.CHEN_LUN, ShengYiWu.PART_SHA, hp_percent=ShengYiWu.BONUS_MAX,
                  hp=448, crit_damage=ShengYiWu.CRIT_RATE_MAIN, def_per=0.073, elem_mastery=40),

        ShengYiWu(ShengYiWu.ZONG_SHI, ShengYiWu.PART_SHA, energy_recharge=ShengYiWu.ENERGY_RECHARGE_MAX,
                  hp=508, def_v=37, crit_damage=0.078, def_per=0.182),
        ShengYiWu(ShengYiWu.ZONG_SHI, ShengYiWu.PART_SHA, energy_recharge=ShengYiWu.ENERGY_RECHARGE_MAX,
                  def_v=65, elem_mastery=37, hp_percent=0.047, atk=37),

        ShengYiWu(ShengYiWu.YUE_TUAN, ShengYiWu.PART_SHA, atk_per=ShengYiWu.BONUS_MAX,
                  def_per=0.124, crit_rate=0.101, crit_damage=0.132, atk=19),

        ShengYiWu(ShengYiWu.FENG_TAO, ShengYiWu.PART_SHA, elem_mastery=ShengYiWu.ELEM_MASTERY_MAIN,
                  atk=33, crit_rate=0.093, crit_damage=0.14, energy_recharge=0.13),

        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_SHA, atk_per=ShengYiWu.BONUS_MAX,
                  atk=14, def_v=37, crit_damage=0.14, crit_rate=0.124),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_SHA, hp_percent=ShengYiWu.BONUS_MAX,
                  energy_recharge=0.091, crit_rate=0.163, crit_damage=0.078, hp=239),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_SHA, atk_per=ShengYiWu.BONUS_MAX,
                  crit_rate=0.097, hp=209, crit_damage=0.202, def_v=42),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_SHA, hp_percent=ShengYiWu.BONUS_MAX,
                  crit_rate=0.109, atk_per=0.053, crit_damage=0.21, def_v=21),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_SHA, hp_percent=ShengYiWu.BONUS_MAX,
                  crit_rate=0.031, def_v=23, crit_damage=0.295, energy_recharge=0.104),
    ],
    ShengYiWu.PART_BEI: [
        ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_BEI, hp_percent=ShengYiWu.BONUS_MAX,
                  atk=35, def_v=23, elem_mastery=70, crit_rate=0.109),
        ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=Ys_Elem_Type.LEI,
                  atk_per=0.082, atk=35, energy_recharge=0.045, crit_damage=0.225),
        ShengYiWu(ShengYiWu.JU_TUAN, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=Ys_Elem_Type.SHUI,
                  crit_damage=0.132, energy_recharge=0.11, def_v=62, def_per=0.073),

        ShengYiWu(ShengYiWu.LIE_REN, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=Ys_Elem_Type.YAN,
                  energy_recharge=0.065, hp=1046, crit_damage=0.21, atk=19),
        ShengYiWu(ShengYiWu.LIE_REN, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=Ys_Elem_Type.BING,
                  crit_rate=0.105, elem_mastery=35, hp_percent=0.093, atk_per=0.082),
        ShengYiWu(ShengYiWu.LIE_REN, ShengYiWu.PART_BEI, hp_percent=ShengYiWu.BONUS_MAX,
                  crit_rate=0.031, crit_damage=0.218, elem_mastery=37, def_v=37),
        ShengYiWu(ShengYiWu.LIE_REN, ShengYiWu.PART_BEI, hp_percent=ShengYiWu.BONUS_MAX,
                  energy_recharge=0.045, crit_rate=0.105, atk=18, hp=657),

        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_BEI, hp_percent=ShengYiWu.BONUS_MAX,
                  crit_rate=0.093, def_per=0.131, def_v=23, crit_damage=0.21),
        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=Ys_Elem_Type.BING,
                  atk=35, atk_per=0.111, elem_mastery=19, crit_rate=0.128),
        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=Ys_Elem_Type.CAO,
                  def_v=16, crit_damage=0.07, crit_rate=0.167, hp=239),
        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_BEI, hp_percent=ShengYiWu.BONUS_MAX,
                  atk=27, def_per=0.066, crit_damage=0.132, crit_rate=0.097),
        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=Ys_Elem_Type.HUO,
                  crit_rate=0.035, def_v=44, atk_per=0.053, crit_damage=0.28),
        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=Ys_Elem_Type.SHUI,
                  hp_percent=0.163, crit_damage=0.14, energy_recharge=0.052, atk=27),

        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=Ys_Elem_Type.YAN,
                  def_v=37, hp=508, crit_rate=0.101, crit_damage=0.14),
        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_BEI, hp_percent=ShengYiWu.BONUS_MAX,
                  atk=33, energy_recharge=0.097, crit_rate=0.144, elem_mastery=21),
        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=Ys_Elem_Type.FENG,
                  crit_rate=0.086, energy_recharge=0.065, crit_damage=0.218, def_per=0.131),
        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=Ys_Elem_Type.BING,
                  atk_per=0.158, crit_damage=0.132, energy_recharge=0.065, elem_mastery=40),
        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=Ys_Elem_Type.SHUI,
                  atk=16, crit_rate=0.074, hp_percent=0.204, hp=209),
        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=Ys_Elem_Type.FENG,
                  crit_damage=0.194, elem_mastery=44, energy_recharge=0.052, crit_rate=0.062),
        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=Ys_Elem_Type.LEI,
                  hp_percent=0.111, crit_rate=0.066, crit_damage=0.225, def_v=21),
        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=Ys_Elem_Type.SHUI,
                  crit_rate=0.109, def_v=32, hp=478, hp_percent=0.058),
        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=Ys_Elem_Type.CAO,
                  crit_rate=0.101, elem_mastery=19, crit_damage=0.179, hp=209),

        ShengYiWu(ShengYiWu.SHA_SHANG, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=Ys_Elem_Type.LEI,
                  crit_rate=0.07, atk_per=0.053, atk=54, crit_damage=0.132),

        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=Ys_Elem_Type.HUO,
                  crit_damage=0.202, elem_mastery=40, hp=239, crit_rate=0.058),

        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=Ys_Elem_Type.BING,
                  hp=239, crit_rate=0.066, atk_per=0.21, atk=37),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=Ys_Elem_Type.CAO,
                  atk=19, energy_recharge=0.123, crit_rate=0.113, hp_percent=0.087),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=Ys_Elem_Type.FENG,
                  crit_damage=0.148, atk=14, crit_rate=0.121, def_v=19),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=Ys_Elem_Type.HUO,
                  crit_rate=0.062, crit_damage=0.28, atk=14, def_v=16),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=Ys_Elem_Type.CAO,
                  hp_percent=0.163, energy_recharge=0.045, elem_mastery=40, crit_rate=0.074),

        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=Ys_Elem_Type.LEI,
                  crit_damage=0.179, elem_mastery=91, atk=19, def_per=0.073),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=Ys_Elem_Type.HUO,
                  hp_percent=0.058, elem_mastery=23, atk_per=0.204, crit_rate=0.074),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=Ys_Elem_Type.YAN,
                  crit_damage=0.14, def_per=0.233, crit_rate=0.027, atk_per=0.047),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_BEI, atk_per=ShengYiWu.BONUS_MAX,
                  crit_damage=0.218, crit_rate=0.066, def_v=39, energy_recharge=0.058),

        ShengYiWu(ShengYiWu.ZHUI_YI, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=Ys_Elem_Type.BING,
                  atk_per=0.105, elem_mastery=33,  atk=33, crit_damage=0.187),

        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_BEI, atk_per=ShengYiWu.BONUS_MAX,
                  energy_recharge=0.214, atk=33, crit_damage=0.07, crit_rate=0.035),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=Ys_Elem_Type.FENG,
                  hp_percent=0.093, def_v=16, energy_recharge=0.162, hp=538),
        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=Ys_Elem_Type.SHUI,
                  hp=717, hp_percent=0.146, def_per=0.073, crit_damage=0.07),

        ShengYiWu(ShengYiWu.CHEN_LUN, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=Ys_Elem_Type.BING,
                  def_per=0.058, crit_rate=0.07, crit_damage=0.218, atk=33),

        ShengYiWu(ShengYiWu.QI_SHI_DAO, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=Ys_Elem_Type.CAO,
                  elem_mastery=40, energy_recharge=0.058, crit_damage=0.241, hp_percent=0.047),

        ShengYiWu(ShengYiWu.ZONG_SHI, ShengYiWu.PART_BEI, atk_per=ShengYiWu.BONUS_MAX,
                  crit_damage=0.194, def_per=0.124, def_v=42, energy_recharge=0.117),
        ShengYiWu(ShengYiWu.ZONG_SHI, ShengYiWu.PART_BEI, hp_percent=ShengYiWu.BONUS_MAX,
                  energy_recharge=0.117, hp=568, def_v=58, crit_damage=0.07),
        ShengYiWu(ShengYiWu.ZONG_SHI, ShengYiWu.PART_BEI,
                  hp_percent=ShengYiWu.BONUS_MAX, hp=269, def_v=72, elem_mastery=44, atk=14),

        ShengYiWu(ShengYiWu.YUE_TUAN, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=Ys_Elem_Type.BING,
                  crit_damage=0.179, crit_rate=0.105, atk=14, elem_mastery=40),
        ShengYiWu(ShengYiWu.YUE_TUAN, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=Ys_Elem_Type.SHUI,
                  atk=29, crit_damage=0.241, hp=239, hp_percent=0.099),
        ShengYiWu(ShengYiWu.YUE_TUAN, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=Ys_Elem_Type.HUO,
                  hp_percent=0.041, crit_damage=0.14, crit_rate=0.105, hp=568),
        ShengYiWu(ShengYiWu.YUE_TUAN, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=Ys_Elem_Type.SHUI,
                  hp=538, crit_damage=0.078, atk_per=0.152, crit_rate=0.074),

        ShengYiWu(ShengYiWu.JUE_DOU_SHI, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=Ys_Elem_Type.HUO,
                  atk_per=0.163, energy_recharge=0.065, atk=29, crit_damage=0.202),

        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=Ys_Elem_Type.YAN,
                  atk=33, def_per=0.117, energy_recharge=0.13, crit_rate=0.101),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_BEI, hp_percent=ShengYiWu.BONUS_MAX,
                  atk=27, crit_damage=0.225, crit_rate=0.058, def_v=46),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_BEI, hp_percent=ShengYiWu.BONUS_MAX,
                  crit_rate=0.07, energy_recharge=0.091, atk_per=0.105, crit_damage=0.148),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=Ys_Elem_Type.BING,
                  crit_damage=0.21, hp_percent=0.058, energy_recharge=0.155, atk_per=0.047),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=Ys_Elem_Type.SHUI,
                  atk=14, hp_percent=0.14, crit_damage=0.202, hp=269),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=Ys_Elem_Type.HUO,
                  crit_rate=0.031, energy_recharge=0.097, elem_mastery=21, crit_damage=0.256),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=Ys_Elem_Type.LEI,
                  energy_recharge=0.123, crit_damage=0.148, atk_per=0.105, crit_rate=0.066),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_BEI, elem_mastery=ShengYiWu.ELEM_MASTERY_MAIN,
                  hp_percent=0.053, crit_damage=0.202, energy_recharge=0.052, crit_rate=0.097),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=Ys_Elem_Type.BING,
                  atk_per=0.192, hp=299, energy_recharge=0.11, atk=16),
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

        ShengYiWu(ShengYiWu.LIE_REN, ShengYiWu.PART_TOU, crit_rate=ShengYiWu.CRIT_RATE_MAIN,
                  def_v=42, crit_damage=0.202, def_per=0.102, elem_mastery=16),

        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_TOU, crit_rate=ShengYiWu.CRIT_RATE_MAIN,
                  crit_damage=0.14, def_v=56, hp=269, energy_recharge=0.168),
        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_TOU, crit_damage=ShengYiWu.CRIT_DAMAGE_MAIN,
                  atk=18, def_v=56, atk_per=0.105, crit_rate=0.093),
        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_TOU, crit_rate=ShengYiWu.CRIT_RATE_MAIN,
                  crit_damage=0.132, atk=53, hp_percent=0.105, atk_per=0.041),
        ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_TOU, crit_damage=ShengYiWu.CRIT_DAMAGE_MAIN,
                  def_per=0.058, hp=687, hp_percent=0.111, crit_rate=0.07),

        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_TOU, crit_rate=ShengYiWu.CRIT_RATE_MAIN,
                  def_v=21, crit_damage=0.124, hp_percent=0.204, hp=538),
        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_TOU, crit_rate=ShengYiWu.CRIT_RATE_MAIN,
                  atk_per=0.093, atk=19, crit_damage=0.187, elem_mastery=68),
        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_TOU, crit_rate=ShengYiWu.CRIT_RATE_MAIN,
                  energy_recharge=0.155, atk=14, hp=508, crit_damage=0.132),

        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_TOU, crit_damage=ShengYiWu.CRIT_DAMAGE_MAIN,
                  hp_percent=0.169, crit_rate=0.078, elem_mastery=63, atk_per=0.053),
        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_TOU, crit_damage=ShengYiWu.CRIT_DAMAGE_MAIN,
                  hp=448, atk=37, hp_percent=0.099, crit_rate=0.097),
        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_TOU, crit_rate=ShengYiWu.CRIT_RATE_MAIN,
                  def_v=21, crit_damage=0.14, atk=33, elem_mastery=58),
        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_TOU, crit_rate=ShengYiWu.CRIT_RATE_MAIN,
                  def_per=0.058, energy_recharge=0.227, atk_per=0.058, crit_damage=0.155),
        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_TOU, crit_damage=ShengYiWu.CRIT_DAMAGE_MAIN,
                  atk=33, crit_rate=0.101, def_v=16, atk_per=0.087),

        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_TOU, crit_damage=ShengYiWu.CRIT_DAMAGE_MAIN,
                  elem_mastery=47, def_v=32, atk_per=0.152, crit_rate=0.066),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_TOU, hp_percent=ShengYiWu.BONUS_MAX,
                  def_v=21, crit_damage=0.202, crit_rate=0.097, hp=239),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_TOU, hp_percent=ShengYiWu.BONUS_MAX,
                  energy_recharge=0.142, atk=19, crit_damage=0.132, crit_rate=0.066),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_TOU, crit_damage=ShengYiWu.CRIT_DAMAGE_MAIN,
                  atk=19, def_v=35, crit_rate=0.132, energy_recharge=0.052),

        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_TOU, crit_rate=ShengYiWu.CRIT_RATE_MAIN,
                  atk_per=0.047, crit_damage=0.256, energy_recharge=0.104, hp=209),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_TOU, crit_rate=ShengYiWu.CRIT_RATE_MAIN,
                  atk=31, crit_damage=0.179, def_per=0.058, energy_recharge=0.104),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_TOU, crit_rate=ShengYiWu.CRIT_RATE_MAIN,
                  crit_damage=0.218, hp_percent=0.087, elem_mastery=16, atk_per=0.099),

        ShengYiWu(ShengYiWu.ZHUI_YI, ShengYiWu.PART_TOU, crit_damage=ShengYiWu.CRIT_DAMAGE_MAIN,
                  hp_percent=0.041, atk=18, elem_mastery=84, crit_rate=0.062),
        ShengYiWu(ShengYiWu.ZHUI_YI, ShengYiWu.PART_TOU, crit_rate=ShengYiWu.CRIT_RATE_MAIN,
                  elem_mastery=40, atk_per=0.053, energy_recharge=0.162, crit_damage=0.14),

        ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_TOU, hp_percent=ShengYiWu.BONUS_MAX,
                  hp=209, crit_rate=0.074, atk=18, crit_damage=0.241),

        ShengYiWu(ShengYiWu.CHEN_LUN, ShengYiWu.PART_TOU, crit_rate=ShengYiWu.CRIT_RATE_MAIN,
                  energy_recharge=0.058, def_v=37, crit_damage=0.155, hp_percent=0.134),
        ShengYiWu(ShengYiWu.CHEN_LUN, ShengYiWu.PART_TOU, crit_rate=ShengYiWu.CRIT_RATE_MAIN,
                  def_v=44, crit_damage=0.225, energy_recharge=0.097, elem_mastery=23),

        ShengYiWu(ShengYiWu.ZONG_SHI, ShengYiWu.PART_TOU, crit_rate=ShengYiWu.CRIT_RATE_MAIN,
                  hp=299, atk=16, def_per=0.321, crit_damage=0.14),
        ShengYiWu(ShengYiWu.ZONG_SHI, ShengYiWu.PART_TOU, crit_damage=ShengYiWu.CRIT_DAMAGE_MAIN,
                  def_per=0.109, crit_rate=0.148, atk_per=0.058, energy_recharge=0.058),
        ShengYiWu(ShengYiWu.ZONG_SHI, ShengYiWu.PART_TOU, crit_rate=ShengYiWu.CRIT_RATE_MAIN,
                  def_v=60, crit_damage=0.187, hp=269, elem_mastery=47),

        ShengYiWu(ShengYiWu.RU_LEI, ShengYiWu.PART_TOU, crit_rate=ShengYiWu.CRIT_RATE_MAIN,
                  hp=777, atk=27, crit_damage=0.132, elem_mastery=23),

        ShengYiWu(ShengYiWu.FENG_TAO, ShengYiWu.PART_TOU, crit_rate=ShengYiWu.CRIT_RATE_MAIN,
                  crit_damage=0.272, def_v=23, hp=538, hp_percent=0.041),

        ShengYiWu(ShengYiWu.JUE_DOU_SHI, ShengYiWu.PART_TOU, crit_rate=ShengYiWu.CRIT_RATE_MAIN,
                  atk=19, crit_damage=0.194, hp=568, atk_per=0.093),
        ShengYiWu(ShengYiWu.JUE_DOU_SHI, ShengYiWu.PART_TOU, crit_rate=ShengYiWu.CRIT_RATE_MAIN,
                  hp_percent=0.053, crit_damage=0.303, hp=209, atk=39),

        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_TOU, crit_damage=ShengYiWu.CRIT_DAMAGE_MAIN,
                  hp_percent=0.041, crit_rate=0.124, def_v=58, atk=14),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_TOU, crit_damage=ShengYiWu.CRIT_DAMAGE_MAIN,
                  atk=14, energy_recharge=0.188, elem_mastery=56, crit_rate=0.078),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_TOU, crit_rate=ShengYiWu.CRIT_RATE_MAIN,
                  def_per=0.073, energy_recharge=0.045, hp=478, crit_damage=0.264),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_TOU, crit_damage=ShengYiWu.CRIT_DAMAGE_MAIN, 
                  atk_per=0.058, def_per=0.292, crit_rate=0.031, def_v=46),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_TOU, crit_damage=ShengYiWu.CRIT_DAMAGE_MAIN, 
                  crit_rate=0.078, def_v=32, energy_recharge=0.104, atk_per=0.087),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_TOU, atk_per=ShengYiWu.BONUS_MAX,
                  crit_rate=0.101, crit_damage=0.124, elem_mastery=40, hp_percent=0.047),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_TOU, crit_rate=ShengYiWu.CRIT_RATE_MAIN,
                  atk_per=0.152, elem_mastery=44, crit_damage=0.148, def_v=23),
    ]
}

all_syw_by_position = [all_syw[ShengYiWu.PART_HUA],
                       all_syw[ShengYiWu.PART_YU],
                       all_syw[ShengYiWu.PART_SHA],
                       all_syw[ShengYiWu.PART_BEI],
                       all_syw[ShengYiWu.PART_TOU]
                       ]


def debug_set_syw(part, syw_lst):
    all_syw[part] = syw_lst


def debug_add_syw(syw: ShengYiWu):
    all_syw[syw.part].append(syw)

def debug_find_by_id(id):
    for syw_lst in all_syw.values():
        for syw in syw_lst:
            if syw.id == id:
                return syw

def find_syw(match_syw_callback):
    matched_syw = []
    for sl in all_syw.values():
        for s in sl:
            if match_syw_callback(s):
                matched_syw.append(s)
    return matched_syw

qualifier_threshold = 1.5
score_threshold = 1.8


def set_score_threshold(new_threashold):
    global score_threshold
    score_threshold = new_threashold


def set_qualifier_threshold(new_threashold):
    global qualifier_threshold
    qualifier_threshold = new_threashold


class ShengYiWu_Score:
    def __init__(self, syw_combine: list[ShengYiWu]):
        self.__expect_score = 0
        self.__crit_score = 0

        self.__overall_score = 0

        self.__extra_score = 0
        self.__custom_data = None
        self.__syw_combine: list[ShengYiWu] = syw_combine

    def damage_to_score(self, damage, crit_rate, crit_damage):
        self.__expect_score = ys_expect_damage(damage, crit_rate, crit_damage)
        self.__crit_score = ys_crit_damage(damage, crit_damage)

    @property
    def expect_score(self):
        return self.__expect_score

    @expect_score.setter
    def expect_score(self, score):
        self.__expect_score = score

    @property
    def crit_score(self):
        return self.__crit_score

    @crit_score.setter
    def crit_score(self, score):
        self.__crit_score = score

    @property
    def overall_score(self):
        return self.__overall_score

    @overall_score.setter
    def overall_score(self, score):
        self.__overall_score = score

    @property
    def extra_score(self):
        return self.__extra_score
    
    @extra_score.setter
    def extra_score(self, score):
        self.__extra_score = score

    @property
    def custom_data(self):
        return self.__custom_data

    @custom_data.setter
    def custom_data(self, data):
        self.__custom_data = data

    @property
    def syw_combine(self):
        return self.__syw_combine

    @syw_combine.setter
    def syw_combine(self, c):
        self.__syw_combine = c


class Score_List:
    def __init__(self):
        self.__max_expect_score = 0
        self.__max_crit_score = 0
        self.__max_extra_score = 0
        self.__score_list: list[ShengYiWu_Score] = []

    @property
    def max_expect_score(self):
        return self.__max_expect_score

    @max_expect_score.setter
    def max_expect_score(self, score):
        self.__max_expect_score = score

    @property
    def max_crit_score(self):
        return self.__max_crit_score

    @max_crit_score.setter
    def max_crit_score(self, score):
        self.__max_crit_score = score

    @property
    def max_extra_score(self):
        return self.__max_extra_score
    
    @max_extra_score.setter
    def max_extra_score(self, score):
        self.__max_extra_score = score

    @property
    def score_list(self):
        return self.__score_list

    def merge(self, another_lst):
        if another_lst.max_expect_score != self.max_expect_score or another_lst.max_crit_score != self.max_crit_score:
            raise Exception(
                "Score_List merge: max_expect_score or max_crit_score not match!")
        
        self.__score_list.extend(another_lst.score_list)

    def add_score(self, score: ShengYiWu_Score):
        self.__score_list.append(score)

        if score.expect_score > self.__max_expect_score:
            self.__max_expect_score = score.expect_score

        if score.crit_score > self.__max_crit_score:
            self.__max_crit_score = score.crit_score

        if score.extra_score > self.__max_extra_score:
            self.__max_extra_score = score.extra_score

    def discard_below_threshold(self, threshold, min_remain=30):
        above_list: list[ShengYiWu_Score] = []
        below_list: list[ShengYiWu_Score] = []
        for score in self.__score_list:
            overall_score = score.expect_score / self.__max_expect_score
            overall_score += score.crit_score / self.__max_crit_score
            score.overall_score = overall_score

            if overall_score >= threshold:
                above_list.append(score)
            else:
                below_list.append(score)

        num_above = len(above_list)
        if num_above < min_remain:
            below_list.sort(key=lambda x: x.overall_score)
            extra_num = 30 - num_above
            above_list.extend(below_list[-extra_num:])

        self.__score_list = above_list

    def write_to_file(self, result_txt_file, result_description):
        if not self.__score_list:
            return
        
        self.__score_list.sort(key=lambda x: x.overall_score)
        print("write num:", len(self.__score_list))

        desc = "总评分, 期望伤害评分, 暴击伤害评分, " + str(result_description) + ", 圣遗物组合" 

        with open(result_txt_file, 'w', encoding='utf-8') as f:
            for score in self.__score_list:
                expect_score_str = str(score.expect_score) + '(' + str(round(score.expect_score / self.__max_expect_score, 4)) + ')'
                crit_score_str = str(score.crit_score) + '(' + str(round(score.crit_score / self.__max_crit_score, 4)) + ')'
                write_lst = [str(round(score.overall_score, 4)), expect_score_str, crit_score_str, 
                             str(score.custom_data), 
                             str(score.syw_combine)]
                # print((i, c))
                # f.write(str((round(score, 4), c, )))
                f.write(", ".join(write_lst))
                f.write('\n\n')

            f.write(str(desc))
            f.write('\n\n')
            f.write("最大期望伤害: " + str(self.__max_expect_score))
            f.write('\n')
            f.write("最大暴击伤害: " + str(self.__max_crit_score))
            f.write('\n')
            f.write("max_extra_score: " + str(self.__max_extra_score))
            f.write('\n')

# 各种套装组合的模式，分别有四件套，2+2，2件套+3散件
# 
# 前面四个表示 set1 应该出现的位置，后一个表示散件应该出现的位置
SET4_PATTERN = [[[0, 1, 2, 3], [4]], [[0, 1, 2, 4], [3]], [[0, 1, 3, 4], [2]], [[0, 2, 3, 4], [1]], [[1, 2, 3, 4], [0]]]
# 前面两个为 set1 应该出现的位置，中间两个表示 set2 应该出现的位置，最后一个表示散件应该出现的位置
SET2P2_PATTERN = [[[0, 1], [3, 4], [2]], [[1, 4], [0, 3], [2]], [[2, 4], [0, 3], [1]], 
                    [[2, 3], [1, 4], [0]], [[1, 2], [3, 4], [0]], [[3, 4], [0, 1], [2]], 
                    [[0, 2], [1, 4], [3]], [[0, 4], [1, 2], [3]], [[1, 4], [2, 3], [0]], 
                    [[2, 4], [1, 3], [0]], [[1, 3], [0, 2], [4]], [[0, 1], [2, 4], [3]], 
                    [[0, 2], [3, 4], [1]], [[1, 4], [0, 2], [3]], [[0, 3], [2, 4], [1]], 
                    [[3, 4], [1, 2], [0]], [[0, 2], [1, 3], [4]], [[2, 3], [0, 1], [4]], 
                    [[1, 2], [0, 4], [3]], [[0, 4], [2, 3], [1]], [[2, 3], [0, 4], [1]], 
                    [[0, 3], [1, 2], [4]], [[2, 4], [0, 1], [3]], [[0, 1], [2, 3], [4]], 
                    [[1, 3], [0, 4], [2]], [[3, 4], [0, 2], [1]], [[1, 3], [2, 4], [0]], 
                    [[0, 4], [1, 3], [2]], [[0, 3], [1, 4], [2]], [[1, 2], [0, 3], [4]]
                    ]
# 前面两件表示 set1 应该出现的位置，后面三个表示散件应该出现的位置
SET2_PATTERN = [[[0, 1], [2, 3, 4]], [[0, 2], [1, 3, 4]], [[0, 3], [1, 2, 4]], 
                [[0, 4], [1, 2, 3]], [[1, 2], [0, 3, 4]], [[1, 3], [0, 2, 4]], 
                [[1, 4], [0, 2, 3]], [[2, 3], [0, 1, 4]], [[2, 4], [0, 1, 3]], 
                [[3, 4], [0, 1, 2]]]

SAN_JIAN_SET_NAME = "散件"
SAN_JIAN_SET_PATTERNS = [[SAN_JIAN_SET_NAME, SAN_JIAN_SET_NAME, SAN_JIAN_SET_NAME, SAN_JIAN_SET_NAME, SAN_JIAN_SET_NAME]]

class Syw_Combine_Desc:
    def __init__(self, set1_name=None, set1_num=0, set2_name=None, set2_num=0):
        """
        set1_num 和 set2_num 允许的组合模式为: 0+0, 2+2, 4+0, 0+4, 2+0, 0+2
        
        其中 0+0 比较特殊：
        
        * 如果同时指定了 set1_name 和 set2_name，则等价于 2+2
        * 如果 set1_name 和 set2_name 都没指定，则表示全散件
        """
        if set1_num + set2_num > 4:
            raise Exception("set1_num + set2_num > 4")
        elif set1_num == 0 and set2_num == 0:   # 0+0
            if set1_name and set2_name:
                set1_num = 2
                set2_num = 2
            elif set1_name or set2_name:
                raise Exception("set1_num and set2_num is 0, but set1_name and set2_name not both specified or un-specified")
        elif set1_num == 2 and set2_num == 2:   # 2+2
            if not set1_name or not set2_name:
                raise Exception("2+2, but set1_name or set2_name not specified")
        elif set1_num == 4: # 4+0
            if set2_name:
                raise Exception("set1_num is 4, but set2_name is not None")
            elif not set1_name:
                raise Exception("set1_num is 4, but set1_name is not specified")
            else:
                single_set_name = set1_name
        elif set2_num == 4 and set1_name: # 0+4
            if set1_name:
                raise Exception("set2_num is 4, but set1_name is not None")
            elif not set2_name:
                raise Exception("set2_num is 4, but set2_name is not specified")
            else:
                single_set_name = set2_name
        elif set1_num == 2 and set2_num == 0:   # 2+0
            if set2_name:
                raise Exception("2+0, but set2_name is specified")
            elif not set1_name:
                raise Exception("2+0, but set1_name is not specified")
            else:
                single_set_name = set1_name
        elif set1_num == 0 and set2_num == 2:   # 0+2
            if set1_name:
                raise Exception("0+2, but set1_name is specified")
            elif not set2_name:
                raise Exception("0+2, but set2_name is not specified")
            else:
                single_set_name = set2_name
        elif set1_name == set2_name:
            raise Exception("set1_name == set2_name")
        
        self.set1_name = set1_name
        self.set1_num = set1_num

        self.set2_name = set2_name
        self.set2_num = set2_num

        self.set_patterns = []
        if self.set1_num == 4 or set2_num == 4:
            for pos_pattern in SET4_PATTERN:
                # eg: pos_pattern = [[0, 1, 2, 3], [4]]
                pattern = [None, None, None, None, None]
                for pos in pos_pattern[0]:
                    pattern[pos] = single_set_name

                for pos in pos_pattern[1]:
                    pattern[pos] = SAN_JIAN_SET_NAME

                self.set_patterns.append(pattern)
        elif self.set1_num == 2 and self.set2_num == 2:
            for pos_pattern in SET2P2_PATTERN:
                # eg: pos_pattern = [[0, 1], [3, 4], [2]]
                pattern = [None, None, None, None, None]
                for pos in pos_pattern[0]:
                    pattern[pos] = set1_name

                for pos in pos_pattern[1]:
                    pattern[pos] = set2_name

                for pos in pos_pattern[2]:
                    pattern[pos] = SAN_JIAN_SET_NAME

                self.set_patterns.append(pattern)
        elif self.set1_num == 2 or self.set2_num == 2:
            for pos_pattern in SET2_PATTERN:
                # eg: pos_pattern = [[0, 1], [2, 3, 4]]
                pattern = [None, None, None, None, None]
                for pos in pos_pattern[0]:
                    pattern[pos] = single_set_name

                for pos in pos_pattern[1]:
                    pattern[pos] = SAN_JIAN_SET_NAME

                self.set_patterns.append(pattern)
        else:
            self.set_patterns = SAN_JIAN_SET_PATTERNS

    @staticmethod
    def any_2p2(set_names: list[str]):
        set_names = set(set_names)
        all_2p2 = list(itertools.combinations(set_names, 2))
        descs = []
        for set1_name, set2_name in all_2p2:
            # print(set1_name, set2_name)
            descs.append(Syw_Combine_Desc(set1_name=set1_name, set2_name=set2_name))

        return descs

def match_syw(s: ShengYiWu, expect_name, matcher=None) -> bool:
    if s.name != expect_name:
        return False
    
    if matcher:
        return matcher(s)
    else:
        return True
        

# 花和羽毛没有 match callback，因为正常来说，没有双暴的花和羽毛不会列入 all_syw 集合中的
def find_syw_combine(combine_desc_lst: list[Syw_Combine_Desc],
                     match_sha_callback=None, match_bei_callback=None, match_tou_callback=None):
    sha_list: list[ShengYiWu] = []
    bei_list: list[ShengYiWu] = []
    tou_list: list[ShengYiWu] = []

    if match_sha_callback:
        for syw in all_syw[ShengYiWu.PART_SHA]:
            if match_sha_callback(syw):
                sha_list.append(syw)
    else:
        sha_list = all_syw[ShengYiWu.PART_SHA]

    if match_bei_callback:
        for syw in all_syw[ShengYiWu.PART_BEI]:
            if match_bei_callback(syw):
                bei_list.append(syw)
    else:
        bei_list = all_syw[ShengYiWu.PART_BEI]

    if match_tou_callback:
        for syw in all_syw[ShengYiWu.PART_TOU]:
            if match_tou_callback(syw):
                tou_list.append(syw)
    else:
        tou_list = all_syw[ShengYiWu.PART_TOU]

    # 散件集合
    syw_set_dict: dict[str, list[list[ShengYiWu]]] = {
        SAN_JIAN_SET_NAME: [all_syw[ShengYiWu.PART_HUA], all_syw[ShengYiWu.PART_YU], sha_list, bei_list, tou_list]
    }

    # 接下来扫描套装
    for combine_desc in combine_desc_lst:
        set_names = []
        if combine_desc.set1_name:
            set_names.append(combine_desc.set1_name)
        if combine_desc.set2_name:
            set_names.append(combine_desc.set2_name)

        for name in set_names:
            if name not in syw_set_dict:
                syw_set_dict[name] = [
                    [syw for syw in all_syw_by_position[0] if match_syw(syw, name)],
                    [syw for syw in all_syw_by_position[1] if match_syw(syw, name)],
                    [syw for syw in all_syw_by_position[2] if match_syw(syw, name, match_sha_callback)],
                    [syw for syw in all_syw_by_position[3] if match_syw(syw, name, match_bei_callback)],
                    [syw for syw in all_syw_by_position[4] if match_syw(syw, name, match_tou_callback)],
                ]

    # 接下来按照 set pattern组合圣遗物
    
    all_combins_5 = {}
    raw_score_list: list[ShengYiWu_Score] = []

    for combine_desc in combine_desc_lst:
        for pattern in combine_desc.set_patterns:
            syw_lst_lst = [syw_set_dict[pattern[0]][0],
                           syw_set_dict[pattern[1]][1],
                           syw_set_dict[pattern[2]][2],
                           syw_set_dict[pattern[3]][3],
                           syw_set_dict[pattern[4]][4]]
            for c0 in syw_lst_lst[0]:
                for c1 in syw_lst_lst[1]:
                    for c2 in syw_lst_lst[2]:
                        for c3 in syw_lst_lst[3]:
                            for c4 in syw_lst_lst[4]:
                                combine = [c0, c1, c2, c3, c4]
                                # TODO: 有更好的去重复算法么？总感觉这样用字符串 dict 很费时
                                scid = c0.id + c1.id + c2.id + c3.id + c4.id
                                if scid not in all_combins_5:
                                    all_combins_5[scid] = True
                                    raw_score_list.append(ShengYiWu_Score(combine))
    
    return raw_score_list

def calc_score_1st_phrase(raw_score_list: list[ShengYiWu_Score], 
                          calculate_score_callbak: Callable[[ShengYiWu_Score], bool]) -> Score_List:
    score_list = Score_List()

    for score in raw_score_list:
        if not calculate_score_callbak(score):
            continue

        score_list.add_score(score)

    return score_list


def calc_score_2nd_phrase(score_list: Score_List, threshold) -> Score_List:
    score_list.discard_below_threshold(threshold)
    return score_list


def calc_score_multi_proc(raw_score_list, calculate_score_callbak, threshold) -> Score_List:
    all_combines_chunks = chunk_into_n(raw_score_list, 5)

    final_score_list = Score_List()

    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [executor.submit(
            calc_score_1st_phrase, lst, calculate_score_callbak) for lst in all_combines_chunks]

        score_list_lst: list[Score_List] = []
        for future in concurrent.futures.as_completed(futures):
            try:
                score_list = future.result()
                if score_list.max_expect_score > final_score_list.max_expect_score:
                    final_score_list.max_expect_score = score_list.max_expect_score

                if score_list.max_crit_score > final_score_list.max_crit_score:
                    final_score_list.max_crit_score = score_list.max_crit_score

                if score_list.max_extra_score > final_score_list.max_extra_score:
                    final_score_list.max_extra_score = score_list.max_extra_score

                score_list_lst.append(score_list)
            except Exception as exc:
                print('1st generated an exception: %s' % (exc))
                traceback.print_exc()

        for score_list in score_list_lst:
            score_list.max_expect_score = final_score_list.max_expect_score
            score_list.max_crit_score = final_score_list.max_crit_score
            score_list.max_extra_score = final_score_list.max_extra_score

        futures = [executor.submit(calc_score_2nd_phrase, lst, threshold) for lst in score_list_lst]
        for future in concurrent.futures.as_completed(futures):
            try:
                final_score_list.merge(future.result())
            except Exception as exc:
                print('1st generated an exception: %s' % (exc))
                traceback.print_exc()

    return final_score_list


def calc_score_inline(raw_score_list, calculate_score_callbak, threshold) -> Score_List:
    score_list = calc_score_1st_phrase(raw_score_list, calculate_score_callbak)
    return calc_score_2nd_phrase(score_list, threshold)


def calculate_score(raw_score_list: list[ShengYiWu_Score],
                    calculate_score_callbak,
                    result_txt_file, result_description,
                    calculate_score_qualifier=None):
    lst_len = len(raw_score_list)

    if calculate_score_qualifier:
        if lst_len > 10000:
            score_list = calc_score_multi_proc(
                raw_score_list, calculate_score_qualifier, qualifier_threshold)
        else:
            score_list = calc_score_inline(
                raw_score_list, calculate_score_qualifier, qualifier_threshold)


        raw_score_list = score_list.score_list
        lst_len = len(raw_score_list)
        print("qualified remain: ", lst_len)

    if lst_len > 10000:
        score_list = calc_score_multi_proc(raw_score_list, calculate_score_callbak, score_threshold)
    else:
        score_list = calc_score_inline(raw_score_list, calculate_score_callbak, score_threshold)

    score_list.write_to_file(result_txt_file, result_description)

    return score_list


def test_find_syw_combines():
    combine_desc_lst = Syw_Combine_Desc.any_2p2([ShengYiWu.JU_TUAN, 
                                                 ShengYiWu.HUA_HAI,
                                                 ShengYiWu.QIAN_YAN,
                                                 ShengYiWu.CHEN_LUN,
                                                 ShengYiWu.SHUI_XIAN])
    
    def match_sha_callback(syw: ShengYiWu): return syw.hp_percent == 0.466 or syw.energy_recharge == ShengYiWu.ENERGY_RECHARGE_MAX
    def match_bei_callback(syw: ShengYiWu): return syw.hp_percent == 0.466 or syw.elem_type == Ys_Elem_Type.SHUI

    combine_desc_lst.append(Syw_Combine_Desc(set1_name=ShengYiWu.JU_TUAN, set1_num=4))
    raw_score_list = find_syw_combine(combine_desc_lst, 
                                      match_sha_callback=match_sha_callback,
                                      match_bei_callback=match_bei_callback)
    print(len(raw_score_list))
    return raw_score_list

# Main body
if __name__ == '__main__':
    test_find_syw_combines()