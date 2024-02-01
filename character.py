#!/user/bin/env python3 -c
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

import logging
from health_point import HealthPoint, HP_Change_Data

class Character_HP_Change_Data:
    def __init__(self, ch, data: HP_Change_Data):
        self.character = ch
        self.data = data

    def has_changed(self):
        return self.data.has_changed()
    
    def is_over_healed(self):
        return self.data.is_over_healed()
    
    def __str__(self):
        return self.character.name + " " + str(self.data)

class Character:
    def __init__(self, name, base_atk=0, base_hp=0, base_defence=0):
        self.name = name
        # 基础攻击力：角色基础攻击力 + 武器基础攻击力
        self.__base_atk = base_atk
        # 总攻击力
        self.__all_atk = 0

        # 基础防御力
        self.__base_defence = base_defence
        # 总防御力
        self.__all_defence = 0

        # 元素精通
        self.__elem_mastery = 0

        self.__crit_rate = 0.05
        self.__crit_damage = 0.5

        # 治疗加成
        self.__healing_bonus = 0
        # 受治疗加成
        self.__incomming_healing_bonus = 0

        self.__energy_recharge = 100.0

        self.__hp: HealthPoint = HealthPoint(base_hp, 0)

        # 普通攻击
        self.__normal_a_bonus = 0
        # 重击
        self.__charged_a_bonus = 0
        # 下落攻击
        self.__plunging_bonus = 0

        self.__e_bonus = 0
        self.__q_bonus = 0

        self.__in_foreground = 0
        self.__swy_names = None

    def get_base_atk(self):
        return self.__base_atk

    def get_atk(self):
        return round(self.__all_atk)
    
    def modify_atk(self, atk):
        self.__all_atk += atk

    def modify_atk_per(self, atk_per):
        self.modify_atk(self.__base_atk * atk_per)

    def add_atk(self, atk):
        self.modify_atk(atk)

    def sub_atk(self, atk):
        self.modify_atk(0 - atk)

    def add_atk_per(self, atk_per):
        self.modify_atk_per(atk_per)

    def sub_atk_per(self, atk_per):
        self.modify_atk_per(0 - atk_per)

    def get_base_defence(self):
        return self.__base_defence

    def get_defence(self):
        return round(self.__all_defence)
    
    def modify_defence(self, defence):
        self.__all_defence += defence

    def modify_defence_per(self, def_per):
        self.modify_defence(self.__base_defence * def_per)

    def add_defence(self, defence):
        self.modify_defence(defence)

    def sub_defence(self, defence):
        self.modify_defence(0 - defence)

    def add_defence_per(self, def_per):
        self.modify_defence_per(def_per)

    def sub_defence_per(self, def_per):
        self.modify_defence_per(0 - def_per)

    def get_elem_mastery(self):
        return self.__elem_mastery

    def set_elem_mastery(self, em):
        self.__elem_mastery = em

    def modify_elem_mastery(self, em):
        self.__elem_mastery += em

    def add_elem_mastery(self, em):
        self.modify_elem_mastery(em)

    def sub_elem_mastery(self, em):
        self.modify_elem_mastery(0 - em)

    def get_crit_rate(self):
        return self.__crit_rate

    def set_crit_rate(self, crit_rate):
        self.__crit_rate = crit_rate

    def modify_crit_rate(self, cr):
        self.__crit_rate += cr

    def add_crit_rate(self, crit_rate):
        self.modify_crit_rate(crit_rate)

    def sub_crit_rate(self, crit_rate):
        self.modify_crit_rate(0 - crit_rate)

    def get_crit_damage(self):
        return self.__crit_damage

    def set_crit_damage(self, crit_damage):
        self.__crit_damage = crit_damage

    def modify_crit_damage(self, cd):
        self.__crit_damage += cd

    def add_crit_damage(self, cd):
        self.modify_crit_damage(cd)

    def sub_crit_damage(self, cd):
        self.modify_crit_damage(0 - cd)

    def get_healing_bonus(self):
        return self.__healing_bonus

    def set_healing_bonus(self, bonus):
        self.__healing_bonus = bonus

    def modify_healing_bonus(self, bonus):
        self.__healing_bonus += bonus

    def add_healing_bonus(self, bonus):
        self.modify_healing_bonus(bonus)

    def sub_healing_bonus(self, bonus):
        self.modify_healing_bonus(0 - bonus)

    def get_incoming_healing_bonus(self):
        return self.__incomming_healing_bonus

    def set_incoming_headling_bonus(self, bonus):
        self.__incomming_healing_bonus = bonus

    def modify_incoming_healing_bonus(self, bonus):
        self.__incomming_healing_bonus += bonus

    def add_incoming_healing_bonus(self, bonus):
        self.modify_incoming_healing_bonus(bonus)

    def sub_incoming_healing_bonus(self, bonus):
        self.modify_incoming_healing_bonus(0 - bonus)

    def get_energy_recharge(self):
        return round(self.__energy_recharge, 1)

    def set_energy_recharge(self, er):
        self.__energy_recharge = er * 100

    def modify_energy_recharge(self, er):
        self.__energy_recharge += er * 100

    def add_energy_recharge(self, er):
        self.modify_energy_recharge(er)

    def sub_energy_recharge(self, er):
        self.modify_energy_recharge(0 - er)
    
    def set_hp(self, hp: HealthPoint):
        self.__hp = hp

    def get_hp(self) -> HealthPoint:
        return self.__hp
    
    def regenerate_hp(self, cure_hp, healing_bonus):
        actual_cure_hp = round(cure_hp * (1 + healing_bonus + self.get_incoming_healing_bonus()))
        #print("incoming_healing_bonus: ", round(self.get_incoming_healing_bonus(), 1))
        #print("actual_cure_hp: ", round(actual_cure_hp))
        return Character_HP_Change_Data(self, self.__hp.modify_cur_hp(actual_cure_hp))
    
    def regenerate_hp_per(self, hp_per, healing_bonus):
        return self.regenerate_hp(self.__hp.get_max_hp() * hp_per, healing_bonus)
    
    def consume_hp(self, hp):
        return Character_HP_Change_Data(self, self.__hp.modify_cur_hp(hp))
    
    def consume_hp_per(self, hp_per):
        return Character_HP_Change_Data(self, self.__hp.modify_cur_hp_per(hp_per))

    def get_normal_a_bonus(self):
        return self.__normal_a_bonus

    def set_normal_a_bonus(self, bonus):
        self.__normal_a_bonus = bonus

    def modify_normal_a_bonus(self, bonus):
        self.__normal_a_bonus += bonus

    def add_normal_a_bonus(self, bonus):
        self.modify_normal_a_bonus(bonus)

    def sub_normal_a_bonus(self, bonus):
        self.modify_normal_a_bonus(0 - bonus)

    def get_charged_a_bonus(self):
        return self.__charged_a_bonus

    def set_charged_a_bonus(self, bonus):
        self.__charged_a_bonus = bonus

    def modify_charged_a_bonus(self, bonus):
        self.__charged_a_bonus += bonus

    def add_charged_a_bonus(self, bonus):
        self.__charged_a_bonus += bonus

    def sub_charged_a_bonus(self, bonus):
        self.__charged_a_bonus -= bonus

    def get_plunging_bonus(self):
        return self.__plunging_bonus

    def set_plunging_bonus(self, bonus):
        self.__plunging_bonus = bonus

    def modify_plunging_bonus(self, bonus):
        self.__plunging_bonus += bonus

    def add_plunging_bonus(self, bonus):
        self.__plunging_bonus += bonus

    def sub_plunging_bonus(self, bonus):
        self.__plunging_bonus -= bonus

    def get_a_bonus(self):
        return self.__normal_a_bonus

    def set_a_bonus(self, bonus):
        self.set_normal_a_bonus(bonus)
        self.set_charged_a_bonus(bonus)
        self.set_plunging_bonus(bonus)

    def modify_a_bonus(self, bonus):
        self.modify_normal_a_bonus(bonus)
        self.modify_charged_a_bonus(bonus)
        self.modify_plunging_bonus(bonus)

    def add_a_bonus(self, bonus):
        self.add_normal_a_bonus(bonus)
        self.add_charged_a_bonus(bonus)
        self.add_plunging_bonus(bonus)

    def sub_a_bonus(self, bonus):
        self.sub_normal_a_bonus(bonus)
        self.sub_charged_a_bonus(bonus)
        self.sub_plunging_bonus(bonus)

    def get_e_bonus(self):
        return self.__e_bonus

    def set_e_bonus(self, bonus):
        self.__e_bonus = bonus

    def modify_e_bonus(self, bonus):
        self.__e_bonus += bonus

    def add_e_bonus(self, bonus):
        self.__e_bonus += bonus

    def sub_e_bonus(self, bonus):
        self.__e_bonus -= bonus

    def get_q_bonus(self):
        return self.__q_bonus

    def set_q_bonus(self, bonus):
        self.__q_bonus = bonus

    def modify_q_bonus(self, bonus):
        #logging.debug("modify q bonus: %s", round(bonus, 3))
        self.__q_bonus += bonus

    def add_q_bonus(self, bonus):
        #logging.debug("add q bonus, %s", round(bonus, 3))
        self.__q_bonus += bonus

    def sub_q_bonus(self, bonus):
        #logging.debug("sub q bonus, %s", round(bonus, 3))
        self.__q_bonus -= bonus

    def modify_all_elem_bonus(self, bonus):
        #logging.debug("modify all elem bonus: %s", round(bonus, 3))
        self.modify_a_bonus(bonus)
        self.modify_e_bonus(bonus)
        self.modify_q_bonus(bonus)

    def add_all_bonus(self, bonus):
        #logging.debug("add all elem bonus: %s", round(bonus, 3))
        self.add_a_bonus(bonus)
        self.add_e_bonus(bonus)
        self.add_q_bonus(bonus)

    def sub_all_bonus(self, bonus):
        #logging.debug("sub all elem bonus: %s", round(bonus, 3))
        self.sub_a_bonus(bonus)
        self.sub_e_bonus(bonus)
        self.sub_q_bonus(bonus)

    def is_in_foreground(self):
        return self.__in_foreground

    def switch_to_foreground(self):
        self.__in_foreground = True

    def switch_to_background(self):
        self.__in_foreground = False

    def set_syw_names(self, syw_names):
        self.__swy_names = syw_names

    def get_syw_names(self, syw_names):
        return self.__swy_names

    def __str__(self):
        s = ""
        if self.__all_atk:
            s += "atk:" + str(self.get_all_atk()) + ", "

        if self.__all_defence:
            s += "def:" + str(self.get_all_defence()) + ", "

        if self.__elem_mastery:
            s += "m:" + str(self.__elem_mastery) + ","

        s += "cc:" + str(round(self.__crit_rate, 3)) + ", "
        s += "cd:" + str(round(self.__crit_damage, 3)) + ", "

        s += "er:" + str(round(self.__energy_recharge, 1)) + ", "
        s += str(self.__hp) + ", "

        if self.__normal_a_bonus:
            if self.__charged_a_bonus == self.__normal_a_bonus and self.__plunging_bonus == self.__normal_a_bonus:
                s += "ab:"
            else:
                s += "nab:"
            s += str(round(self.__normal_a_bonus, 3)) + ", "

        if self.__charged_a_bonus != 0 and self.__charged_a_bonus != self.__normal_a_bonus:
            s += "cab:" + str(round(self.__charged_a_bonus, 3)) + ", "
            
        if self.__plunging_bonus != 0 and self.__plunging_bonus != self.__plunging_bonus:
            s += "pb:" + str(round(self.__plunging_bonus, 3)) + ", "

        if self.__e_bonus:
            s += "eb:" + str(round(self.__e_bonus, 3)) + ", "
        
        if self.__q_bonus:
            s += "qb:" + str(round(self.__q_bonus, 3)) + ", "

        if self.__healing_bonus:
            s += "hb:" + str(round(self.__healing_bonus, 1)) + ", "

        if self.__incomming_healing_bonus:
            s += "ihb:" + str(round(self.__incomming_healing_bonus, 1))

        if self.__in_foreground:
            s += "f, "
        else:
            s += "b, "

        return s

       
