#!/user/bin/env python3 -tt
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

import sys
import os
import logging
import itertools


class ShengYiWu:
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


hua_hai_name = "HuaHai"

hua_hai = [
    ShengYiWu(hua_hai_name, 'h', elem_mastery=82, atk=19, hp_percent=0.122, def_v=19),
    ShengYiWu(hua_hai_name, "h", crit_rate=0.035, crit_damage=0.218, hp_percent=0.157, atk=31),
    ShengYiWu(hua_hai_name, 'h', crit_rate=0.14, atk_per=0.117, crit_damage=0.07, energe_recharge=0.045),
    ShengYiWu(hua_hai_name, 'h', crit_damage=0.078, crit_rate=0.148, elem_mastery=16, atk_per=0.099),
    ShengYiWu(hua_hai_name, 'h', crit_damage=0.218, def_per=0.073, hp_percent=0.105, energe_recharge=0.104),
    ShengYiWu(hua_hai_name, 'y', def_v=23, crit_rate=0.027, crit_damage=0.028, energe_recharge=0.123),
    ShengYiWu(hua_hai_name, 's', energe_recharge=0.052, crit_damage=0.202, elem_mastery=44, crit_rate=0.062),
    ShengYiWu(hua_hai_name, 'b', hp_percent=0.163, crit_damage=0.14, energe_recharge=0.052, atk=27),
    ShengYiWu(hua_hai_name, 't', crit_damage=0.622, atk=18, def_v=56, atk_per=0.105, crit_rate=0.093),
    ShengYiWu(hua_hai_name, 't', crit_damage=0.622, def_per=0.058, hp=687, hp_percent=0.111, crit_rate=0.07),
]

qian_yan_name = "QianYan"

qian_yan = [
    ShengYiWu(qian_yan_name, 'h', crit_damage=0.132, crit_rate=0.101, atk=16, energe_recharge=0.175),
    ShengYiWu(qian_yan_name, 'h', def_v=39, atk=16, crit_damage=0.241, crit_rate=0.066),
    ShengYiWu(qian_yan_name, 'h', energe_recharge=0.117, atk=14, atk_per=0.117, crit_damage=0.264),
    ShengYiWu(qian_yan_name, 'y', crit_damage=0.132, energe_recharge=0.175, crit_rate=0.101, hp_percent=0.041),
    ShengYiWu(qian_yan_name, 'y', atk_per=0.111, energe_recharge=0.117, hp_percent=0.21, def_per=0.073),
    ShengYiWu(qian_yan_name, 'y', def_v=23, crit_rate=0.031, hp=478, hp_percent=0.216),
    ShengYiWu(qian_yan_name, 's', crit_rate=0.066, atk=33, elem_mastery=40, crit_damage=0.21),
    ShengYiWu(qian_yan_name, 's', elem_mastery=44, atk=16, energe_recharge=0.058, crit_damage=0.272),
    ShengYiWu(qian_yan_name, 'b', hp=717, hp_percent=0.146, def_per=0.073, crit_damage=0.07),
    ShengYiWu(qian_yan_name, 't', hp_percent=0.466, hp=209, crit_rate=0.074, atk=18, crit_damage=0.241),
]

chen_lun_name = "ChenLun"

chen_lun = [
    ShengYiWu(chen_lun_name, 'h', crit_rate=0.066, crit_damage=0.148, hp_percent=0.146, def_per=0.109),
    ShengYiWu(chen_lun_name, 'h', crit_damage=0.054, energe_recharge=0.065, crit_rate=0.132, def_v=39),
    ShengYiWu(chen_lun_name, 'y', crit_rate=0.14, atk_per=0.053, hp=478, crit_damage=0.109),
    ShengYiWu(chen_lun_name, 'y', crit_damage=0.14, def_per=0.16, crit_rate=0.101, hp=239),
    ShengYiWu(chen_lun_name, 'y', def_v=16, crit_damage=0.117, crit_rate=0.124, atk_per=0.041),
    ShengYiWu(chen_lun_name, 'y', hp_percent=0.047, def_per=0.066, energe_recharge=0.065, crit_rate=0.167),
    ShengYiWu(chen_lun_name, 's', hp=448, crit_damage=0.311, def_per=0.073, elem_mastery=40),
    ShengYiWu(chen_lun_name, 't', crit_rate=0.311, energe_recharge=0.058, def_v=37, crit_damage=0.155, hp_percent=0.134),
    ShengYiWu(chen_lun_name, 't', crit_rate=0.311, def_v=44, crit_damage=0.225, energe_recharge=0.097, elem_mastery=23),
]

shui_xian_name = "ShuiXian"

shui_xian = [
    ShengYiWu(shui_xian_name, 'h', energe_recharge=0.123, atk=37, crit_rate=0.039, crit_damage=0.233),
    ShengYiWu(shui_xian_name, 'y', crit_damage=0.07, atk_per=0.058, energe_recharge=0.104, crit_rate=0.136),
    ShengYiWu(shui_xian_name, 's', hp=837, elem_mastery=16, crit_damage=0.257, atk=19),
    ShengYiWu(shui_xian_name, 'b', crit_rate=0.109, def_v=32, hp=478, hp_percent=0.058),
]

all_syw = {
    "h": [
        ShengYiWu('jutuan', 'h', crit_rate=0.14, atk=14, crit_damage=0.078, energe_recharge=0.168),
        ShengYiWu('jutuan', 'h', hp_percent=0.117, elem_mastery=16, crit_damage=0.163, energe_recharge=0.11),
        ShengYiWu('jutuan', 'h', crit_damage=0.14, def_per=0.131, crit_rate=0.066, atk=33),
        ShengYiWu('jutuan', 'h', crit_damage=0.21, hp_percent=0.152, crit_rate=0.031, def_v=23),
        ShengYiWu('leiren', 'h', energe_recharge=0.123, crit_rate=0.101, hp_percent=0.053, crit_damage=0.117),
        ShengYiWu('leiren', 'h', def_per=0.066, crit_damage=0.148, crit_rate=0.105, energe_recharge=0.104),
        ShengYiWu('huahai', 'h', elem_mastery=82, atk=19, hp_percent=0.122, def_v=19),
        ShengYiWu('huahai', 'h', crit_damage=0.218, crit_rate=0.035, hp_percent=0.157, atk=31),
        ShengYiWu('huahai', 'h', crit_rate=0.14, atk_per=0.117, crit_damage=0.07, energe_recharge=0.045),
        ShengYiWu('huahai', 'h', crit_damage=0.078, crit_rate=0.148, elem_mastery=16, atk_per=0.099),
        ShengYiWu('huahai', 'h', crit_damage=0.218, def_per=0.073, hp_percent=0.105, energe_recharge=0.104),
        ShengYiWu('shuixian', 'h', energe_recharge=0.123, atk=37, crit_rate=0.039, crit_damage=0.233),
        ShengYiWu('shijin', 'h', crit_damage=0.124, hp_percent=0.099, atk=14, crit_rate=0.124),
        ShengYiWu('shijin', 'h', crit_damage=0.249, energe_recharge=0.065, def_per=0.066, crit_rate=0.089),
        ShengYiWu('shijin', 'h', def_per=0.073, hp_percent=0.146, def_v=35, elem_mastery=56),
        ShengYiWu('shijin', 'h', def_v=23, crit_damage=0.272, elem_mastery=44, energe_recharge=0.065),
        ShengYiWu('shijin', 'h', crit_damage=0.28, hp_percent=0.099, atk_per=0.053, crit_rate=0.027),
        ShengYiWu('shenlin', 'h', energe_recharge=0.11, hp_percent=0.152, crit_rate=0.035, elem_mastery=70),
        ShengYiWu('shenlin', 'h', def_v=16, elem_mastery=79, hp_percent=0.093, energe_recharge=0.11),
        ShengYiWu('shenlin', 'h', elem_mastery=40, def_v=21, crit_rate=0.027, crit_damage=0.241),
        ShengYiWu('jueyuan', 'h', hp_percent=0.181, energe_recharge=0.123, def_v=23, crit_rate=0.07),
        ShengYiWu('jueyuan', 'h', atk_per=0.041, crit_rate=0.062, elem_mastery=54, crit_damage=0.21),
        ShengYiWu('jueyuan', 'h', crit_rate=0.144, crit_damage=0.078, hp_percent=0.105, elem_mastery=40),
        ShengYiWu('jueyuan', 'h', elem_mastery=44, crit_damage=0.21, def_per=0.066, energe_recharge=0.194),
        ShengYiWu('jueyuan', 'h', elem_mastery=21, crit_rate=0.066, energe_recharge=0.181, crit_damage=0.124),
        ShengYiWu('jueyuan', 'h', atk=33, crit_rate=0.066, atk_per=0.111, crit_damage=0.117),
        ShengYiWu('zhuiyi', 'h', crit_damage=0.132, crit_rate=0.152, energe_recharge=0.097, def_per=0.073),
        ShengYiWu('zhuiyi', 'h', def_v=16, crit_rate=0.035, crit_damage=0.249, atk=29),
        ShengYiWu('zhuiyi', 'h', crit_damage=0.117, hp_percent=0.146, atk_per=0.053, elem_mastery=40),
        ShengYiWu('qianyan', 'h', crit_rate=0.062, elem_mastery=51, energe_recharge=0.181, def_per=0.073),
        ShengYiWu('qianyan', 'h', crit_damage=0.132, crit_rate=0.101, atk=16, energe_recharge=0.175),
        ShengYiWu('qianyan', 'h', def_v=39, atk=16, crit_damage=0.241, crit_rate=0.066),
        ShengYiWu('qianyan', 'h', energe_recharge=0.155, atk=35, hp_percent=0.128, atk_per=0.047),
        ShengYiWu('qianyan', 'h', hp_percent=0.134, energe_recharge=0.162, crit_rate=0.074, crit_damage=0.078),
        ShengYiWu('qianyan', 'h', energe_recharge=0.117, atk=14, atk_per=0.117, crit_damage=0.264),
        ShengYiWu('qianyan', 'h', def_per=0.131, energe_recharge=0.175, def_v=37, crit_damage=0.062),
        ShengYiWu('chenlun', 'h', crit_rate=0.066, crit_damage=0.148, hp_percent=0.146, def_per=0.109),
        ShengYiWu('chenlun', 'h', crit_damage=0.054, energe_recharge=0.065, crit_rate=0.132, def_v=39),
        ShengYiWu('zongshi', 'h', def_per=0.124, crit_damage=0.062, hp_percent=0.111, energe_recharge=0.214),
        ShengYiWu('zongshi', 'h', energe_recharge=0.227, atk_per=0.058, elem_mastery=44, hp_percent=0.047),
        ShengYiWu('zongshi', 'h', crit_damage=0.14, energe_recharge=0.065, atk_per=0.099, crit_rate=0.105),
        ShengYiWu('yuetuan', 'h', elem_mastery=58, crit_damage=0.148, crit_rate=0.078, def_per=0.051),
        ShengYiWu('fengtao', 'h', elem_mastery=86, hp_percent=0.041, def_per=0.131, energe_recharge=0.123),
        ShengYiWu('fengtao', 'h', crit_damage=0.078, energe_recharge=0.065, atk_per=0.146, crit_rate=0.144),
        ShengYiWu('fengtao', 'h', elem_mastery=72, hp_percent=0.099, atk_per=0.041, energe_recharge=0.052),
        ShengYiWu('juedoushi', 'h', hp_percent=0.157, crit_damage=0.218, crit_rate=0.078, def_v=16),
        ShengYiWu('juedoushi', 'h', crit_damage=0.14, crit_rate=0.062, def_v=16, def_per=0.168),
        ShengYiWu('bingtao', 'h', atk_per=0.105, elem_mastery=19, crit_rate=0.132, energe_recharge=0.11),
        ShengYiWu('bingtao', 'h', crit_rate=0.086, crit_damage=0.202, elem_mastery=40, energe_recharge=0.052),
        ShengYiWu('bingtao', 'h', elem_mastery=16, atk_per=0.134, crit_damage=0.132, crit_rate=0.089),
        ShengYiWu('bingtao', 'h', def_v=21, atk_per=0.134, atk=27, crit_damage=0.218),
        ShengYiWu('bingtao', 'h', atk_per=0.099, hp_percent=0.099, crit_damage=0.21, energe_recharge=0.058),
        ShengYiWu('bingtao', 'h', elem_mastery=16, crit_rate=0.039, crit_damage=0.264, def_v=46),
    ],
    "y": [
        ShengYiWu('jutuan', 'y', def_v=37, elem_mastery=40, crit_damage=0.256, crit_rate=0.027),
        ShengYiWu('jutuan', 'y', def_v=37, hp_percent=0.163, def_per=0.109, crit_damage=0.14),
        ShengYiWu('jutuan', 'y', hp_percent=0.14, elem_mastery=19, crit_rate=0.097, energe_recharge=0.052),
        ShengYiWu('jutuan', 'y', elem_mastery=37, energe_recharge=0.11, crit_damage=0.14, crit_rate=0.07),
        ShengYiWu('leiren', 'y', crit_damage=0.202, crit_rate=0.031, hp_percent=0.14, hp=239),
        ShengYiWu('leiren', 'y', crit_damage=0.194, energe_recharge=0.065, crit_rate=0.062, elem_mastery=37),
        ShengYiWu('huahai', 'y', def_v=23, crit_damage=0.28, crit_rate=0.027, energe_recharge=0.123),
        ShengYiWu('huahai', 'y', energe_recharge=0.155, hp_percent=0.041, hp=717, atk_per=0.047),
        ShengYiWu('shuixian', 'y', energe_recharge=0.292, atk_per=0.111, crit_damage=0.054, def_v=19),
        ShengYiWu('shuixian', 'y', crit_damage=0.07, atk_per=0.058, energe_recharge=0.104, crit_rate=0.136),
        ShengYiWu('shijin', 'y', hp=508, atk_per=0.099, crit_rate=0.058, crit_damage=0.194),
        ShengYiWu('shijin', 'y', elem_mastery=86, atk_per=0.087, def_per=0.058, hp_percent=0.058),
        ShengYiWu('shijin', 'y', atk_per=0.105, crit_rate=0.035, energe_recharge=0.058, elem_mastery=93),
        ShengYiWu('shenlin', 'y', crit_damage=0.078, atk_per=0.041, crit_rate=0.035, elem_mastery=96),
        ShengYiWu('shenlin', 'y', energe_recharge=0.149, hp_percent=0.117, crit_rate=0.035, crit_damage=0.132),
        ShengYiWu('shenlin', 'y', def_v=37, crit_damage=0.07, crit_rate=0.144, def_per=0.066),
        ShengYiWu('shenlin', 'y', crit_damage=0.272, hp=239, crit_rate=0.07, def_v=23),
        ShengYiWu('shenlin', 'y', crit_damage=0.132, crit_rate=0.066, hp_percent=0.041, elem_mastery=56),
        ShengYiWu('jueyuan', 'y', def_per=0.073, atk_per=0.087, crit_rate=0.027, energe_recharge=0.285),
        ShengYiWu('jueyuan', 'y', crit_damage=0.148, def_per=0.117, def_v=19, crit_rate=0.148),
        ShengYiWu('jueyuan', 'y', crit_rate=0.039, crit_damage=0.35, hp_percent=0.041, def_v=39),
        ShengYiWu('jueyuan', 'y', hp=448, crit_damage=0.078, energe_recharge=0.311, hp_percent=0.053),
        ShengYiWu('jueyuan', 'y', hp=807, atk_per=0.047, energe_recharge=0.11, crit_damage=0.171),
        ShengYiWu('jueyuan', 'y', elem_mastery=16, atk_per=0.058, crit_damage=0.148, crit_rate=0.132),
        ShengYiWu('zhuiyi', 'y', hp=687, crit_damage=0.109, crit_rate=0.039, hp_percent=0.157),
        ShengYiWu('qianyan', 'y', crit_damage=0.132, energe_recharge=0.175, crit_rate=0.101, hp_percent=0.041),
        ShengYiWu('qianyan', 'y', atk_per=0.111, energe_recharge=0.117, hp_percent=0.21, def_per=0.073),
        ShengYiWu('qianyan', 'y', hp_percent=0.082, energe_recharge=0.097, atk_per=0.21, crit_rate=0.035),
        ShengYiWu('qianyan', 'y', atk_per=0.099, energe_recharge=0.246, crit_damage=0.099, crit_rate=0.035),
        ShengYiWu('qianyan', 'y', def_v=23, crit_rate=0.031, hp=478, hp_percent=0.216),
        ShengYiWu('chenlun', 'y', crit_rate=0.14, atk_per=0.053, hp=478, crit_damage=0.109),
        ShengYiWu('chenlun', 'y', hp_percent=0.053, crit_damage=0.155, hp=299, atk_per=0.262),
        ShengYiWu('chenlun', 'y', crit_damage=0.14, def_per=0.16, crit_rate=0.101, hp=239),
        ShengYiWu('chenlun', 'y', def_v=16, crit_damage=0.117, crit_rate=0.124, atk_per=0.041),
        ShengYiWu('chenlun', 'y', hp_percent=0.047, def_per=0.066, energe_recharge=0.065, crit_rate=0.167),
        ShengYiWu('zongshi', 'y', elem_mastery=47, def_v=60, hp=269, energe_recharge=0.149),
        ShengYiWu('zongshi', 'y', hp=209, hp_percent=0.157, energe_recharge=0.104, def_v=35),
        ShengYiWu('zongshi', 'y', hp_percent=0.093, crit_rate=0.07, energe_recharge=0.117, atk_per=0.111),
        ShengYiWu('rulei', 'y', crit_rate=0.066, crit_damage=0.218, elem_mastery=63, energe_recharge=0.065),
        ShengYiWu('yuetuan', 'y', elem_mastery=44, crit_damage=0.124, atk_per=0.087, crit_rate=0.101),
        ShengYiWu('fengtao', 'y', atk_per=0.093, elem_mastery=21, energe_recharge=0.233, hp=269),
        ShengYiWu('fengtao', 'y', hp=239, crit_damage=0.233, atk_per=0.093, crit_rate=0.062),
        ShengYiWu('fengtao', 'y', atk_per=0.041, def_v=42, elem_mastery=77, energe_recharge=0.058),
        ShengYiWu('juedoushi', 'y', hp_percent=0.111, crit_rate=0.167, energe_recharge=0.045, crit_damage=0.062),
        ShengYiWu('juedoushi', 'y', crit_rate=0.144, crit_damage=0.07, hp_percent=0.111, energe_recharge=0.045),
        ShengYiWu('bingtao', 'y', crit_damage=0.194, energe_recharge=0.052, elem_mastery=19, hp_percent=0.233),
        ShengYiWu('bingtao', 'y', crit_damage=0.14, elem_mastery=40, crit_rate=0.101, atk_per=0.105),
        ShengYiWu('bingtao', 'y', def_v=23, crit_rate=0.128, crit_damage=0.07, atk_per=0.099),
        ShengYiWu('bingtao', 'y', crit_damage=0.256, energe_recharge=0.097, def_per=0.058, atk_per=0.041),
        ShengYiWu('bingtao', 'y', crit_rate=0.066, crit_damage=0.21, hp=299, atk_per=0.099),

    ],
    "s": [
        ShengYiWu('jutuan', 's', energe_recharge=0.045, crit_damage=0.078, crit_rate=0.113, def_v=60),
        ShengYiWu('leiren', 's', crit_rate=0.027, def_v=23, crit_damage=0.264, hp=478),
        ShengYiWu('huahai', 's', energe_recharge=0.052, crit_damage=0.202, elem_mastery=44, crit_rate=0.062),
        ShengYiWu('shijin', 's', def_v=21, crit_damage=0.187, crit_rate=0.087, atk_per=0.041),
        ShengYiWu('zhuiyi', 's', atk=19, crit_damage=0.14, elem_mastery=33, crit_rate=0.105),
        ShengYiWu('qianyan', 's', crit_rate=0.066, atk=33, elem_mastery=40, crit_damage=0.21),
        ShengYiWu('qianyan', 's', elem_mastery=44, atk=16, energe_recharge=0.058, crit_damage=0.272),
        ShengYiWu('chenlun', 's', hp=448, crit_damage=0.311, def_per=0.073, elem_mastery=40),
        ShengYiWu('bingtao', 's', energe_recharge=0.091, crit_rate=0.163, crit_damage=0.078, hp=239),
        ShengYiWu('bingtao', 's', crit_rate=0.031, def_v=23, crit_damage=0.295, energe_recharge=0.104),
    ],
    "b": [
        ShengYiWu('jutuan', 'b', crit_damage=0.132, energe_recharge=0.11, def_v=62, def_per=0.73),
        ShengYiWu('huahai', 'b', hp_percent=0.163, crit_damage=0.14, energe_recharge=0.052, atk=27),
        ShengYiWu('shuixian', 'b', crit_rate=0.109, def_v=32, hp=478, hp_percent=0.058),
        ShengYiWu('shenlin', 'b', hp_percent=0.152, crit_damage=0.194, def_v=19, hp=239),
        ShengYiWu('qianyan', 'b', hp=717, hp_percent=0.146, def_per=0.073, crit_damage=0.07),
        ShengYiWu('yuetuan', 'b', atk=29, crit_damage=0.241, hp=239, hp_percent=0.099),
        ShengYiWu('yuetuan', 'b', hp=538, crit_damage=0.078, atk_per=0.152, crit_rate=0.074),
        ShengYiWu('bingtao', 'b', atk=14, hp_percent=0.14, crit_damage=0.202, hp=269),

    ],
    "t": [
        ShengYiWu('jutuan', 't', crit_damage=0.622, crit_rate=0.062, energe_recharge=0.097, def_v=32, def_per=0.132),
        ShengYiWu('huahai', 't', crit_damage=0.622, atk=18, def_v=56, atk_per=0.105, crit_rate=0.093),
        ShengYiWu('huahai', 't', def_per=0.058, hp=687, hp_percent=0.111, crit_damage=0.07),
        ShengYiWu('shijin', 't', hp_percent=0.169, crit_rate=0.078, elem_mastery=63, atk_per=0.053),
        ShengYiWu('shijin', 't', hp=448, atk=37, hp_percent=0.099, crit_damage=0.097),
        ShengYiWu('shijin', 't', crit_rate=0.311, def_v=21, crit_damage=0.14, atk=33, elem_mastery=58),
        ShengYiWu('shijin', 't', def_per=0.058, energe_recharge=0.227, atk_per=0.058, crit_damage=0.155),
        ShengYiWu('shijin', 't', crit_damage=0.622, atk=33, crit_rate=0.101, def_v=16, atk_per=0.087),
        ShengYiWu('shenlin', 't', crit_damage=0.622, elem_mastery=47, def_v=32, atk_per=0.152, crit_rate=0.066),
        ShengYiWu('shenlin', 't', hp_percent=0.466, energe_recharge=0.142, atk=19, crit_damage=0.132, crit_rate=0.066),
        ShengYiWu('shenlin', 't', crit_damage=0.622, atk=19, def_v=35, crit_rate=0.132, energe_recharge=0.052),
        ShengYiWu('jueyuan', 't', crit_rate=0.311, atk_per=0.047, crit_damage=0.256, energe_recharge=0.104, hp=209),
        ShengYiWu('jueyuan', 't', crit_rate=0.311, atk=31, crit_damage=0.179, def_per=0.058, energe_recharge=0.104),
        ShengYiWu('jueyuan', 't', crit_rate=0.311, crit_damage=0.218, hp_percent=0.087, elem_mastery=16, atk_per=0.099),
        ShengYiWu('zhuiyi', 't', crit_damage=0.622, hp_percent=0.041, atk=18, elem_mastery=84, crit_rate=0.062),
        ShengYiWu('zhuiyi', 't', crit_rate=0.311, elem_mastery=40, atk_per=0.053, energe_recharge=0.162, crit_damage=0.14),
        ShengYiWu('qianyan', 't', hp_percent=0.466, hp=209, crit_rate=0.074, atk=18, crit_damage=0.241),
        ShengYiWu('chenlun', 't', crit_rate=0.311, energe_recharge=0.058, def_v=37, crit_damage=0.155, hp_percent=0.134),
        ShengYiWu('chenlun', 't', crit_rate=0.311, def_v=44, crit_damage=0.225, energe_recharge=0.097, elem_mastery=23),
        ShengYiWu('zongshi', 't', crit_damage=0.622, def_per=0.109, crit_rate=0.148, atk_per=0.058, energe_recharge=0.058),
        ShengYiWu('zongshi', 't', crit_rate=0.311, def_v=60, crit_damage=0.187, hp=269, elem_mastery=47),
        ShengYiWu('rulei', 't', crit_rate=0.311, hp=777, atk=27, crit_damage=0.132, elem_mastery=23),
        ShengYiWu('yuetuan', 't', crit_rate=0.311, hp=508, crit_damage=0.14, atk=45, atk_per=0.099),
        ShengYiWu('fengtao', 't', crit_rate=0.311, crit_damage=0.272, def_v=23, hp=538, hp_percent=0.041),
        ShengYiWu('juedoushi', 't', crit_rate=0.311, atk=19, crit_damage=0.194, hp=568, atk_per=0.093),
        ShengYiWu('juedoushi', 't', crit_rate=0.311, hp_percent=0.053, crit_damage=0.303, hp=209, atk=39),
        ShengYiWu('bingtao', 't', crit_rate=0.311, atk_per=0.152, elem_mastery=44, crit_damage=0.148, def_v=23),
        ShengYiWu('bingtao', 't', crit_damage=0.622, hp=239, elem_mastery=16, crit_rate=0.086, def_v=60),
    ]
}

all_parts = {'h', 'y', 's', 'b', 't'}

YeLan_Max_Hp = 14450.0
base_hp = 32611.0
base_crit_damage = 2.382
base_water_plus = 1.466


def main():
    hua_hai_combins = list(itertools.combinations(hua_hai, 2))
    qian_yan_combins = list(itertools.combinations(qian_yan, 2))
    chen_lun_combins = list(itertools.combinations(chen_lun, 2))
    shui_xian_combins = list(itertools.combinations(shui_xian, 2))

    all_combins = hua_hai_combins + qian_yan_combins + \
        chen_lun_combins + shui_xian_combins
    two_plus_two = [(l[0] + l[1])
                    for l in list(itertools.combinations(all_combins, 2))]

    # print(two_plus_two)

    all_scores = {}

    for tt in two_plus_two:
        parts = [p.part for p in tt]
        parts_set = set(parts)
        if len(parts) != len(parts_set):
            continue

        miss_part = list(all_parts - parts_set)

        for s in all_syw[miss_part[0]]:
            combine = tt + (s, )

            crit_rate = sum([p.crit_rate for p in combine])
            if crit_rate < (0.70 - 0.242):
                continue

            hp = sum([p.hp for p in combine])
            hp_per = sum([p.hp_percent for p in combine])
            extra_crit_damage = sum([p.crit_damage for p in combine])
            extra_water_plus = 0.0
            total_energe_recharge = (sum([p.energe_recharge for p in combine]) + 1) * 100

            #if total_energe_recharge != 111:
            #   continue

            syw_names = set([p.name for p in combine])
            for n in syw_names:
                if n == hua_hai_name:
                    hp_per += 0.2
                elif n == shui_xian_name:
                    extra_water_plus += 0.15
                elif n == qian_yan_name:
                    hp_per += 0.2
                elif n == chen_lun_name:
                    extra_water_plus += 0.15

            all_hp = hp_per * YeLan_Max_Hp + hp + base_hp

            score = all_hp / base_hp * (base_crit_damage + extra_crit_damage) / base_crit_damage * (
                base_water_plus + extra_water_plus) / base_water_plus

            expect_damage = round((crit_rate + 0.242) *
                                  (base_crit_damage + extra_crit_damage - 1), 2)

            data = [int(all_hp), round(crit_rate + 0.242, 3), round(base_crit_damage +
                                                                      extra_crit_damage - 1, 3), expect_damage, round(total_energe_recharge, 1), combine]
            if score in all_scores:
                all_scores[score].append(data)
            else:
                all_scores[score] = [data]

    if all_scores:
        with open("ye_lan_syw.txt", 'w', encoding='utf-8') as f:
            for i in sorted(all_scores):
                for c in all_scores[i]:
                    # print((i, c))
                    f.write(str((round(i, 4), c, )))
                    f.write('\n')


# Main body
if __name__ == '__main__':
    main()
