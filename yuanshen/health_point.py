#!/user/bin/env python3 -c
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

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

class HealthPoint:
    def __init__(self, base_hp: int, max_hp: int = 0):
        # 确保为整数
        base_hp = round(base_hp)
        max_hp = round(max_hp)

        self.__base_hp: int = base_hp
        if not max_hp:
            # 最少为白字生命值 + 圣遗物花
            max_hp = base_hp + 4780
        
        self.__self_max_hp: int = max_hp
        self.__cur_real_max_hp: int = max_hp
        self.__cur_hp: int = max_hp
        self.__cur_hp_per = 1.0
        self.__in_q_animation = False

        self.__get_extra_max_hp_func = None

        self.__maxest_hp_ever: int = max_hp

    def __str__(self) -> str:
        return "base_hp: %i, max_hp: %i, cur_hp: %i" % (self.__base_hp, self.get_max_hp(), self.__cur_hp)

    def get_base_hp(self):
        return self.__base_hp
    
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

    def set_extra_max_hp_func(self, func):
        self.__get_extra_max_hp_func = func
        self.__update_cur_hp_after_max_hp_changed()

    def unset_extra_max_hp_func(self):
        self.__get_extra_max_hp_func = None
        self.__update_cur_hp_after_max_hp_changed()

    def get_max_hp(self):
        if not self.__get_extra_max_hp_func:
            return self.__self_max_hp
        else:
            self.__update_cur_hp_after_max_hp_changed()
            return self.__cur_real_max_hp

    def __update_cur_hp_after_max_hp_changed(self):
        new_max_hp = self.__self_max_hp
        if self.__get_extra_max_hp_func:
            new_max_hp += round(self.__get_extra_max_hp_func())
 
        if self.__cur_real_max_hp == new_max_hp:
            return
        
        # 不直接乘法，避免可能的浮点运算问题
        if self.__cur_hp_per == 1:
            self.__cur_hp = new_max_hp
        else:
            self.__cur_hp = new_max_hp * self.__cur_hp_per
        
        self.__cur_real_max_hp = new_max_hp

        if new_max_hp > self.__maxest_hp_ever:
            self.__maxest_hp_ever = new_max_hp

    def set_max_hp(self, max_hp):
        self.__self_max_hp = round(max_hp)
        self.__update_cur_hp_after_max_hp_changed()

    def modify_max_hp(self, hp):
        if hp == 0:
            return
        
        self.__self_max_hp += round(hp)
        self.__update_cur_hp_after_max_hp_changed()

    def modify_max_hp_per(self, hp_per):
        if hp_per == 0:
            return
        
        self.modify_max_hp(self.__base_hp * hp_per)

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
        
        if hp_changed == 0:
            return not_changed_data
        
        cur_max_hp = self.get_max_hp()
        
        if hp_changed > 0 and self.__cur_hp == cur_max_hp:
            return HP_Change_Data(0, 0, hp_changed)
        
        over_heal_num = 0
        hp_changed = round(hp_changed)

        cur_hp = self.__cur_hp + hp_changed
        if cur_hp >= cur_max_hp:
            actual_modified_hp = cur_max_hp - self.__cur_hp
            over_heal_num = cur_hp - cur_max_hp
            self.__cur_hp = cur_max_hp
            self.__cur_hp_per = 1
        elif cur_hp > 0:   # 0 < cur_hp < cur_max_hp
            actual_modified_hp = cur_hp - self.__cur_hp
            self.__cur_hp = cur_hp
            self.__cur_hp_per = round(self.__cur_hp / cur_max_hp, 3)
        else:   # cur_hp <= 0
            actual_modified_hp = 0 - self.__cur_hp
            self.__cur_hp = 0
            self.__cur_hp_per = 0

        actual_modified_hp_per = actual_modified_hp / cur_max_hp

        return HP_Change_Data(actual_modified_hp, actual_modified_hp_per, over_heal_num)

    def modify_cur_hp_per(self, hp_per):
        return self.modify_cur_hp(self.get_max_hp() * hp_per)

    def __str__(self):
        return "hp:" + str(self.get_cur_hp()) + "/" + str(self.get_max_hp())