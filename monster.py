#!/user/bin/env python3 -c
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

import logging

class Monster:
    def __init__(self, level = 100, kang_xin = 0.1):
        """
        * level: 怪物等级
        * kang_xin: 默认参数为10%抗性

        乘区计算方法：
        0 < 抗性 < 75%: 1 - 抗性百分比
        抗性 < 0: 1 - (抗性百分比 / 2)
        例如：10%抗性，减抗50%，则抗性乘区为：1 - (10 % - 50%) / 2 = 1.2
        """

        self.level = level

        
        self.jian_fang = 0
        self.fang_yu_xi_shu = self.get_fang_yu_xi_shu()

        # 减抗
        self.jian_kang = 0
        self.kang_xin = kang_xin
        self.kang_xin_xi_su  = self.get_jian_kang_bonus()

    def get_fang_yu_xi_shu(self):
        return (90 + 100) / ( (90 + 100) + (self.level + 100) * (1 - self.jian_fang))

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

    def get_jian_kang_bonus(self):
        cur_kang_xin = self.kang_xin - self.jian_kang
        if cur_kang_xin >= 0:
            if cur_kang_xin > 0.75:
                return 1 / (1 + cur_kang_xin * 4)
            else:
                return 1 - cur_kang_xin
        else:
            return 1 - cur_kang_xin / 2
        
    def attacked(self, damage_before_jian_kang):
        # logging.debug("jian kang bonus: %s", self.get_jian_kang_bonus())
        return damage_before_jian_kang * self.kang_xin_xi_su * self.fang_yu_xi_shu
    
    def __str__(self):
        return "kang:" + str(round(self.kang_xin_xi_su, 3)) + ", fang:" + str(round(self.fang_yu_xi_shu, 3))
    

class Che_Dian_Shu(Monster):
    """
    掣电树，一个很好用的木桩
    """
    def __init__(self):
        super().__init__(level=93, kang_xin=3.1)