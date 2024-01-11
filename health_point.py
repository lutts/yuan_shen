#!/user/bin/env python3 -c
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

class HealthPoint:
    def __init__(self, base_hp, max_hp = 0):
        self.__base_hp = base_hp
        if not max_hp:
            max_hp = base_hp

        self.__max_hp = max_hp
        self.__cur_hp = max_hp
        self.__in_q_animation = False

        self.__maxest_hp_ever = max_hp

    def __str__(self) -> str:
        return "base_hp: %i, max_hp: %i, cur_hp: %i" % (self.__base_hp, self.__max_hp, self.__cur_hp)

    def get_base_hp(self):
        return self.__base_hp
    
    def get_max_hp(self):
        return round(self.__max_hp)
    
    def get_cur_hp(self):
        return round(self.__cur_hp)
    
    def get_maxest_hp_ever(self):
        return round(self.__maxest_hp_ever)
    
    #######################

    def set_in_q_animation(self, anim = False):
        self.__in_q_animation = anim

    def set_max_hp(self, max_hp):
        self.__max_hp = max_hp

    def modify_max_hp(self, hp_changed):
        prev_max_hp = self.__max_hp
        self.__max_hp += hp_changed
        self.__cur_hp = self.__cur_hp / prev_max_hp * self.__max_hp

        if self.__max_hp > self.__maxest_hp_ever:
            self.__maxest_hp_ever = self.__max_hp

    def sub_max_hp(self, hp):
        self.modify_max_hp(0 - hp)

    def add_max_hp(self, hp):
        print("add max hp:", hp)
        self.modify_max_hp(hp)

    def sub_max_hp_per(self, hp_per):
        self.sub_max_hp(round(self.__base_hp * hp_per))

    def add_max_hp_per(self, hp_per):
        print("add max hp per:", hp_per)
        self.add_max_hp(round(self.__base_hp * hp_per))

    def regenerate_hp(self, regenerate_num):
        hp = self.__cur_hp + regenerate_num
        if hp > self.__max_hp:
            actual_regenerate_num = self.__max_hp - self.__cur_hp
            self.__cur_hp = self.__max_hp
        else:
            self.__cur_hp = hp
            actual_regenerate_num = regenerate_num

        regenerate_hp_per = actual_regenerate_num / self.__max_hp

        return (actual_regenerate_num, regenerate_hp_per)

    def decrease_hp(self, decrease_num):
        if self.__in_q_animation:
            return 0
        
        hp = self.__cur_hp - decrease_num
        if hp < 0:
            actual_decrease_num = self.__cur_hp
            self.__cur_hp = 0
        else:
            actual_decrease_num = decrease_num
            self.__cur_hp = hp

        decrease_hp_per = actual_decrease_num / self.__max_hp

        return (actual_decrease_num, decrease_hp_per)
        
    def regenerate_hp_per(self, hp_per):
        return self.regenerate_hp(round(self.__max_hp * hp_per))

    def decrease_hp_per(self, hp_per):
        return self.decrease_hp(round(self.__max_hp * hp_per))
    
    def __str__(self):
        return "hp:" + str(self.get_cur_hp()) + "/" + str(self.get_max_hp())