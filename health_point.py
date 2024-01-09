#!/user/bin/env python3 -c
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

class HealthPoint:
    def __init__(self, base_hp, max_hp):
        self.__base_hp = base_hp
        self.__max_hp = max_hp
        self.__cur_hp = max_hp

    def __str__(self) -> str:
        return "base_hp: %i, max_hp: %i, cur_hp: %i" % (self.__base_hp, self.__max_hp, self.__cur_hp)

    def get_base_hp(self):
        return self.__base_hp
    
    def get_max_hp(self):
        return self.__max_hp
    
    def get_cur_hp(self):
        return self.__cur_hp

    def modify_max_hp(self, hp_changed):
        prev_max_hp = self.__max_hp
        self.__max_hp += hp_changed
        self.__cur_hp = self.__cur_hp / prev_max_hp * self.__max_hp

    def sub_max_hp(self, hp):
        self.modify_max_hp(self, 0 - hp)

    def add_max_hp(self, hp):
        self.modify_max_hp(self, hp)

    def sub_max_hp_per(self, hp_per):
        self.sub_max_hp(round(self.__base_hp * hp_per))

    def add_max_hp_per(self, hp_per):
        self.add_max_hp(round(self.__base_hp * hp_per))

    def restore_hp(self, restore_num):
        hp = self.__cur_hp + restore_num
        if hp > self.__max_hp:
            actual_restore_num = self.__max_hp - self.__cur_hp
            self.__cur_hp = self.__max_hp
        else:
            self.__cur_hp = hp
            actual_restore_num = restore_num

        return actual_restore_num

    def decrease_hp(self, decrease_num):
        hp = self.__cur_hp - decrease_num
        if hp < 0:
            actual_decrease_num = self.__cur_hp
            self.__cur_hp = 0
        else:
            actual_decrease_num = decrease_num
            self.__cur_hp = hp

        return actual_decrease_num
        
    def restore_hp_per(self, hp_per):
        return self.restore_hp(round(self.__max_hp * hp_per))

    def decrease_hp_per(self, hp_per):
        return self.decrease_hp(round(self.__max_hp * hp_per))
    
    def convert_hp_to_percent(self, hp):
        return hp / self.__max_hp
