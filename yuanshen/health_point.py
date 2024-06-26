#!/user/bin/env python3 -c
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

from typing import Self

class HP_Change_Data:
    def __init__(self, hp, hp_per, over_heal_num):
        self.hp = hp
        self.hp_per = hp_per
        self.over_heal_num = over_heal_num

    def has_changed(self):
        return self.hp != 0
    
    def is_over_healed(self):
        return self.over_heal_num > 0
    
    def __str__(self):
        return "hp changed: " + str(round(self.hp)) + "(" + str(round(self.hp_per, 3)) + "), over_heal_num:" + str(round(self.over_heal_num))
    
not_changed_data = HP_Change_Data(0, 0, 0)

class HpBuffAttributes:
    def __init__(self):
        self.reset()

    def reset(self):
        self.hp_per = 0
        self.hp = 0

    def merge(self, other: Self):
        self.hp_per += other.hp_per
        self.hp += other.hp

    def get_max_hp(self, base_hp):
        return base_hp * self.hp_per + self.hp


class HealthPoint:
    def __init__(self, base_hp: int, max_hp: int = 0):
        # 确保为整数
        base_hp = round(base_hp)
        max_hp = round(max_hp)

        self.__base_hp = base_hp

        self.fixed_attrs = HpBuffAttributes()
        self.buff_attrs = HpBuffAttributes()
        # NOTE: 生命值上限止前似乎没有不可转化的
        # self.un_convertable_attrs = HpBuffAttributes()
        
        if max_hp:
            self.fixed_attrs.hp = max_hp - base_hp
        self.__maxest_hp_ever: int = max_hp
        self.__cur_max_hp = max_hp

        self.__cur_hp: int = max_hp
        self.__cur_hp_per = 1.0

        self.__in_q_animation = False

    def get_base_hp(self):
        return self.__base_hp
    
    def get_max_hp(self):
        return self.__cur_max_hp
    
    def get_cur_hp(self):
        return self.__cur_hp
    
    def get_cur_hp_per(self):
        return self.__cur_hp_per
    
    def get_maxest_hp_ever(self):
        return round(self.__maxest_hp_ever)
    
    def is_full(self):
        return 1 == self.__cur_hp_per
    
    #######################

    def set_in_q_animation(self, anim = False):
        self.__in_q_animation = anim
        
    def on_max_hp_changed(self):
        cur_max_hp = int(self.__base_hp + self.fixed_attrs.get_max_hp(self.__base_hp) + self.buff_attrs.get_max_hp(self.__base_hp))
        # fixed_max_hp = self.fixed_attrs.get_max_hp(self.__base_hp)
        # print(f"base_hp:{self.__base_hp}, fixed_max_hp:{fixed_max_hp}, cur_max_hp:{cur_max_hp}")
        if cur_max_hp == self.__cur_max_hp:
            return
        
        self.__cur_max_hp = cur_max_hp
        
        # 不直接乘法，避免可能的浮点运算问题
        if self.__cur_hp_per == 1:
            self.__cur_hp = cur_max_hp
        else:
            self.__cur_hp = cur_max_hp * self.__cur_hp_per

        if cur_max_hp > self.__maxest_hp_ever:
            self.__maxest_hp_ever = cur_max_hp

    def modify_cur_hp(self, hp_changed) -> HP_Change_Data:
        """
        返回值说明：
        [0]: 实际变化 hp
        [1]: 实际变化百分比 hp
        [2]: 治疗溢出量
        """
        # 大招动画的时候不会掉血
        if hp_changed < 0 and self.__in_q_animation:
            return not_changed_data
        
        hp_changed = round(hp_changed)
        
        if hp_changed == 0:
            return not_changed_data
        
        if hp_changed > 0 and self.__cur_hp == self.__cur_max_hp:
            return HP_Change_Data(0, 0, hp_changed)
        
        over_heal_num = 0
        
        cur_hp = self.__cur_hp + hp_changed
        if cur_hp >= self.__cur_max_hp:
            actual_modified_hp = self.__cur_max_hp - self.__cur_hp
            over_heal_num = cur_hp - self.__cur_max_hp
            self.__cur_hp = self.__cur_max_hp
            self.__cur_hp_per = 1
        elif cur_hp > 0:   # 0 < cur_hp < self.__cur_max_hp
            actual_modified_hp = hp_changed
            self.__cur_hp = cur_hp
            self.__cur_hp_per = round(self.__cur_hp / self.__cur_max_hp, 3)
        else:   # cur_hp <= 0
            actual_modified_hp = 0 - self.__cur_hp
            self.__cur_hp = 0
            self.__cur_hp_per = 0

        actual_modified_hp_per = actual_modified_hp / self.__cur_max_hp

        return HP_Change_Data(actual_modified_hp, actual_modified_hp_per, over_heal_num)

    def modify_cur_hp_per(self, hp_per):
        return self.modify_cur_hp(self.__cur_max_hp * hp_per)

    def __str__(self):
        return "hp:" + str(self.__cur_hp) + "/" + str(self.__cur_max_hp)