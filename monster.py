#!/user/bin/env python3 -c
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

import logging

class Monster:
    def __init__(self, level = 100, kang_xin = 0.1, character_level=90):
        """
        * level: 怪物等级
        * kang_xin: 默认参数为10%抗性

        乘区计算方法：
        0 < 抗性 < 75%: 1 - 抗性百分比
        抗性 < 0: 1 - (抗性百分比 / 2)
        例如：10%抗性，减抗50%，则抗性乘区为：1 - (10 % - 50%) / 2 = 1.2
        """

        self.level = level

        self.character_level = character_level
        self.jian_fang = 0
        # 影宝的无视防御
        self.ignore_defence_ratio = 0
        self.fang_yu_xi_shu = self.get_fang_yu_xi_shu()

        # 减抗
        self.jian_kang = 0
        self.kang_xin = kang_xin
        self.kang_xin_xi_su  = self.get_jian_kang_bonus()

    def set_level(self, lv):
        self.level = lv
        self.fang_yu_xi_shu = self.get_fang_yu_xi_shu()

    def get_fang_yu_xi_shu(self, extra_jian_fang=0, extra_ignore_defence_ratio=0):
        jian_fang = self.jian_fang + extra_jian_fang
        ignore_defence_ratio = self.ignore_defence_ratio + extra_ignore_defence_ratio
        return (self.character_level + 100) / ( (self.character_level + 100) + (self.level + 100) * (1 - jian_fang) * (1 - ignore_defence_ratio))
    
    def set_ignore_defence(self, ignore_ratio):
        self.ignore_defence_ratio = ignore_ratio
        self.fang_yu_xi_shu = self.get_fang_yu_xi_shu()

    def set_jian_fang(self, jian_fang):
        self.jian_fang = jian_fang
        self.fang_yu_xi_shu = self.get_fang_yu_xi_shu()

    def add_jian_fang(self, jian_fang):
        self.jian_fang += jian_fang
        self.fang_yu_xi_shu = self.get_fang_yu_xi_shu()

    def sub_jian_fang(self, jian_fang):
        self.jian_fang -= jian_fang
        self.fang_yu_xi_shu = self.get_fang_yu_xi_shu()

    def set_jian_kang(self, jian_kang):
        self.jian_kang = jian_kang
        self.kang_xin_xi_su = self.get_jian_kang_bonus()

    def add_jian_kang(self, jian_kang):
        self.jian_kang += jian_kang
        self.kang_xin_xi_su = self.get_jian_kang_bonus()

    def sub_jian_kang(self, jian_kang):
        self.jian_kang -= jian_kang
        self.kang_xin_xi_su = self.get_jian_kang_bonus()

    def set_kang_xin(self, kx):
        self.kang_xin = kx
        self.kang_xin_xi_su = self.get_jian_kang_bonus()

    # FIXME: 是否需要区分不同元素类型的抗性？ 目前我们还不支持整队伤害计算，原神也暂时没有双元素属性的主C，似乎暂时没必要支持
    def get_jian_kang_bonus(self, extra_jian_kang=0):
        cur_kang_xin = self.kang_xin - self.jian_kang - extra_jian_kang
        if cur_kang_xin >= 0:
            if cur_kang_xin > 0.75:
                return 1 / (1 + cur_kang_xin * 4)
            else:
                return 1 - cur_kang_xin
        else:
            return 1 - cur_kang_xin / 2
        
    def attacked(self, raw_damage):
        # logging.debug("jian kang bonus: %s", self.get_jian_kang_bonus())
        return raw_damage * self.kang_xin_xi_su * self.fang_yu_xi_shu
    
    def __str__(self):
        return "kang:" + str(round(self.kang_xin_xi_su, 3)) + ", fang:" + str(round(self.fang_yu_xi_shu, 3))
    

class Che_Dian_Shu(Monster):
    """
    掣电树，一个很好用的木桩
    """
    def __init__(self):
        super().__init__(level=93, kang_xin=3.1)