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
        self.fang_yu_xi_shu = (90 + 100) / ( (90 + 100) + (self.level + 100) )

        self.kang_xin = kang_xin
        # 减抗
        self.jian_kang = 0

    def set_jian_fang(self, jian_fang):
        self.fang_yu_xi_shu = (90 + 100) / ( (90 + 100) + (self.level + 100) * (1 - jian_fang))

    def set_jian_kang(self, jian_kang):
        self.jian_kang = jian_kang

    def add_jian_kang(self, jian_kang):
        self.jian_kang += jian_kang

    def sub_jian_kang(self, jian_kang):
        self.jian_kang -= jian_kang

    def get_jian_kang_bonus(self):
        cur_kang_xin = self.kang_xin - self.jian_kang
        if cur_kang_xin >= 0:
            return 1 - cur_kang_xin
        else:
            return 1 - cur_kang_xin / 2
        
    def attacked(self, damage_before_jian_kang):
        # logging.debug("jian kang bonus: %s", self.get_jian_kang_bonus())
        return damage_before_jian_kang * self.get_jian_kang_bonus() * self.fang_yu_xi_shu