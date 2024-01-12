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

        self.__prev_max_hp = max_hp
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

    def __update_cur_hp_after_max_hp_changed(self):
        if self.__prev_max_hp == self.__max_hp:
            return
        
        self.__cur_hp = self.__cur_hp / self.__prev_max_hp * self.__max_hp
        self.__prev_max_hp = self.__max_hp

    def set_max_hp(self, max_hp):
        self.__max_hp = max_hp
        self.__update_cur_hp_after_max_hp_changed()

    def modify_max_hp(self, hp):
        self.__max_hp += hp
        self.__update_cur_hp_after_max_hp_changed()
        if self.__max_hp > self.__maxest_hp_ever:
            self.__maxest_hp_ever = self.__max_hp

    def modify_max_hp_per(self, hp_per):
        self.modify_max_hp(round(self.__base_hp * hp_per))

    def sub_max_hp(self, hp):
        self.modify_max_hp(0 - hp)

    def add_max_hp(self, hp):
        self.modify_max_hp(hp)

    def sub_max_hp_per(self, hp_per):
        self.modify_max_hp_per(0 - hp_per)

    def add_max_hp_per(self, hp_per):
        self.modify_max_hp_per(hp_per)

    def modify_cur_hp(self, hp_changed) -> tuple[float, float]:
        # 大招动画的时候不会掉血
        if hp_changed < 0 and self.__in_q_animation:
            return (0, 0)
        
        cur_hp = self.__cur_hp + hp_changed
        if cur_hp > self.__max_hp:
            actual_modified_hp = self.__max_hp - self.__cur_hp
            self.__cur_hp = self.__max_hp
        elif cur_hp < 0:
            actual_modified_hp = 0 - self.__cur_hp
            self.__cur_hp = 0
        else:
            actual_modified_hp = hp_changed
            self.__cur_hp = cur_hp

        actual_modified_hp_per = actual_modified_hp / self.__max_hp

        return (actual_modified_hp, actual_modified_hp_per)

    def modify_cur_hp_per(self, hp_per) -> tuple[float, float]:
        return self.modify_cur_hp(round(self.__max_hp * hp_per))
    
    def regenerate_hp(self, regenerate_num):
        return self.modify_cur_hp(regenerate_num)

    def decrease_hp(self, decrease_num):
        return self.modify_cur_hp(0 - decrease_num)
        
    def regenerate_hp_per(self, hp_per):
        return self.modify_cur_hp_per(hp_per)

    def decrease_hp_per(self, hp_per):
        return self.modify_cur_hp_per(0 - hp_per)

    def __str__(self):
        return "hp:" + str(self.get_cur_hp()) + "/" + str(self.get_max_hp())