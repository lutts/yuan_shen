#!/user/bin/env python3 -c
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

import logging
from .attribute_hub import AttributeHub

class Monster:
    def __init__(self, level = 100, kang_xin = 0.1, character_level=90):
        """
        * level: 怪物等级
        * kang_xin: 默认参数为10%抗性
        * character_level: 角色等级
        """

        self.level = level
        self.character_level = character_level

        self.__jian_fang = 0
        # 影宝的无视防御
        self.__ignore_defence_ratio = 0
        # 减抗
        self.__jian_kang = 0
        self.__kang_xin = kang_xin
        self.__attribute_hub: AttributeHub = None

        # 上一次被扩散反应的时间：扩散反应是有内置CD的，大约为1.2秒, 每个怪独立计时
        self.last_kuo_san_time = None

    def set_attribute_hub(self, hub):
        self.__attribute_hub = hub

    def unset_attribute_hub(self):
        self.__attribute_hub = None

    def set_level(self, lv):
        self.level = lv

    def set_ignore_defence(self, ignore_ratio):
        self.__ignore_defence_ratio = ignore_ratio

    def add_ignore_defence(self, ignore_ratio):
        self.__ignore_defence_ratio += ignore_ratio

    def sub_ignore_defence(self, ignore_ratio):
        self.__ignore_defence_ratio -= ignore_ratio

    def set_jian_fang(self, jian_fang):
        self.__jian_fang = jian_fang

    def add_jian_fang(self, jian_fang):
        self.__jian_fang += jian_fang

    def sub_jian_fang(self, jian_fang):
        self.__jian_fang -= jian_fang

    def set_jian_kang(self, jian_kang):
        self.__jian_kang = jian_kang

    def add_jian_kang(self, jian_kang):
        self.__jian_kang += jian_kang

    def sub_jian_kang(self, jian_kang):
        self.__jian_kang -= jian_kang

    def set_kang_xin(self, kx):
        self.__kang_xin = kx

    def do_kuo_san(self, cur_time):
        if not self.last_kuo_san_time:
            self.last_kuo_san_time = cur_time
            return True
        
        if cur_time - self.last_kuo_san_time > 1.2:
            self.last_kuo_san_time = cur_time
            return True
        else:
            return False

    # FIXME: 是否需要区分不同元素类型的抗性？ 目前我们还不支持整队伤害计算，原神也暂时没有双元素属性的主C，似乎暂时没必要支持
    def get_kang_xin_cheng_shang(self):
        cur_kang_xin = self.__kang_xin - self.__jian_kang
        if self.__attribute_hub:
            cur_kang_xin -= self.__attribute_hub.get_jian_kang()

        if cur_kang_xin >= 0:
            if cur_kang_xin > 0.75:
                return 1 / (1 + cur_kang_xin * 4)
            else:
                return 1 - cur_kang_xin
        else:
            return 1 - cur_kang_xin / 2
        
    def get_fang_yu_xi_shu(self):
        jian_fang = self.__jian_fang
        ignore_defence_ratio = self.__ignore_defence_ratio

        if self.__attribute_hub:
            jian_fang += self.__attribute_hub.get_jian_fang()
            ignore_defence_ratio += self.__attribute_hub.get_ignore_fang()

        return (self.character_level + 100) / ( (self.character_level + 100) + (self.level + 100) * (1 - jian_fang) * (1 - ignore_defence_ratio))
    
    def attacked(self, raw_damage):
        return raw_damage * self.get_kang_xin_cheng_shang() * self.get_fang_yu_xi_shu()
    
    def __str__(self):
        return "kang:" + str(round(self.get_kang_xin_cheng_shang(), 3)) + ", fang:" + str(round(self.get_fang_yu_xi_shu(), 3))