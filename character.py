#!/user/bin/env python3 -c
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

import logging
import weakref
from enum import Enum

from typing import Self
from ys_basic import Ys_Elem_Type, Ys_Weapon
from health_point import HealthPoint, HP_Change_Data
from ys_syw import ShengYiWu
from attribute_hub import AttributeHub


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

class NormalAttackType(Enum):
    HIT_FIRST = "普攻第一段"
    HIT_2ND = "普攻第二段"
    HIT_3ND = "普攻第三段"
    HIT_4TH = "普攻第四段"
    HIT_5TH = "普攻第五段"

    CHARGED = "重击"
    PLUNGE = "下坠期间"
    LOW_PLUNGE = "低空坠地冲击"
    HIGH_PLUNGE = "高空坠地冲击"

class CharacterBase:
    def __init_subclass__(cls, name, elem_type: Ys_Elem_Type=None, ming_zuo_num=0, ch_level=90, a_level=1, e_level=1, q_level=1, q_energy=80,
                          **kwargs):
        """
        初始化一些固定不变的属性

        ch_level: 角色等级
        """
        super().__init_subclass__(**kwargs)

        cls.name = name
        cls.elem_type = elem_type
        cls.ming_zuo_num = ming_zuo_num
        cls.ch_level = ch_level
        cls.a_level = a_level
        cls.e_level = e_level
        cls.q_level = q_level
        cls.q_energy = q_energy

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if k in ["name", "elem_type", "ming_zuo_num", 
                     "ch_level", "a_level", "e_level", "q_level", 
                     "q_energy"]:
                setattr(self, k, v)
            else:
                raise Exception("unknown attribute when init CharacterBase: " + k)
            
    def set_ming_zuo_num(self, ming_zuo_num):
        self.ming_zuo_num = ming_zuo_num
        

class Character(CharacterBase, name="通用角色"):
    def __init__(self, 
                 base_hp=0, max_hp=0,
                 base_atk=0, all_atk=0, weapon: Ys_Weapon = None,
                 base_defence=0, all_defence=0,
                 elem_mastery=0,

                 crit_rate=0.05, crit_damage=0.5, 
                 healing_bonus=0, incoming_healing_bonus=0,
                 energy_recharge=100.0,
                 
                 normal_a_bonus=0, charged_a_bonus=0, plunging_bonus=0,
                 e_bonus=0, q_bonus=0,
                 base_bonus=0,
                 **kwargs):
        if kwargs:
            super().__init__(**kwargs)

        self.__hp: HealthPoint = HealthPoint(base_hp, max_hp)

        # 基础攻击力：角色基础攻击力 + 武器基础攻击力
        if weapon:
            base_atk += weapon.base_atk
        self.__base_atk = base_atk
        # 总攻击力
        if not all_atk:
            # 最少为白字攻击力 + 圣遗物羽毛
            all_atk = base_atk + 311
        self.__all_atk = all_atk

        # 基础防御力
        self.__base_defence = base_defence
        # 总防御力
        if not all_defence:
            all_defence = base_defence
        self.__all_defence = all_defence

        # 元素精通
        self.__elem_mastery = elem_mastery

        self.__crit_rate = crit_rate
        self.__crit_damage = crit_damage

        # 治疗加成
        self.__healing_bonus = healing_bonus
        # 受治疗加成
        self.__incomming_healing_bonus = incoming_healing_bonus

        self.__energy_recharge = energy_recharge

        # 普通攻击
        self.__normal_a_bonus = base_bonus + normal_a_bonus
        # 重击
        self.__charged_a_bonus = base_bonus + charged_a_bonus
        # 下落攻击
        self.__plunging_bonus = base_bonus + plunging_bonus

        self.__e_bonus = base_bonus + e_bonus
        self.__q_bonus = base_bonus + q_bonus

        self.__in_foreground = False
        self.__last_fore_back_switch_time = None

        self.__weapon: Ys_Weapon = weapon

        self.__syw_combine: list[ShengYiWu] = None
        self.__syw_name_count: dict[str, int] = None

        self.__teammates = None

        self.__attribute_hub: AttributeHub = None

        if weapon:
            weapon.set_owner(self)
            weapon.apply_static_attributes(self)

    def get_teammates(self) -> list[Self|None]:
        tms = []
        for t in self.__teammates:
            ch = t()
            if ch is not None:
                tms.append(ch)

        return tms
    
    def set_teammates(self, teammates: list[Self]):
        self.__teammates = [weakref.ref(t) for t in teammates]

    def set_attribute_hub(self, hub):
        self.__attribute_hub = hub

        def inner():
            return self.__attribute_hub.get_max_hp(self)
        
        self.__hp.set_extra_max_hp_func(inner)

    def unset_attribute_hub(self):
        self.__attribute_hub = None
        self.__hp.unset_extra_max_hp_func()

    def get_base_hp(self):
        return self.__hp.get_base_hp()

    def get_cur_hp(self):
        return self.__hp.get_cur_hp()
    
    def get_cur_hp_per(self):
        return self.__hp.get_cur_hp_per()
    
    def get_max_hp(self):
        return self.__hp.get_max_hp()

    def get_base_atk(self):
        return self.__base_atk

    def get_atk(self):
        atk = self.__all_atk
        if self.__attribute_hub:
            atk += self.__attribute_hub.get_atk(self)
        
        return round(atk)

    def set_atk(self, atk):
        self.__all_atk = atk

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
        defence = self.__all_defence
        if self.__attribute_hub:
            defence += self.__attribute_hub.get_defence(self)
        
        return round(defence)

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
        em = self.__elem_mastery
        if self.__attribute_hub:
            em += self.__attribute_hub.get_elem_mastery(self)

        return em

    def set_elem_mastery(self, em):
        self.__elem_mastery = em

    def modify_elem_mastery(self, em):
        self.__elem_mastery += em

    def add_elem_mastery(self, em):
        self.modify_elem_mastery(em)

    def sub_elem_mastery(self, em):
        self.modify_elem_mastery(0 - em)

    def get_crit_rate(self):
        cr = self.__crit_rate
        if self.__attribute_hub:
            cr += self.__attribute_hub.get_crit_rate(self)

        return cr

    def set_crit_rate(self, crit_rate):
        self.__crit_rate = crit_rate

    def modify_crit_rate(self, cr):
        self.__crit_rate += cr

    def add_crit_rate(self, crit_rate):
        self.modify_crit_rate(crit_rate)

    def sub_crit_rate(self, crit_rate):
        self.modify_crit_rate(0 - crit_rate)

    def get_crit_damage(self):
        cd = self.__crit_damage
        if self.__attribute_hub:
            cd += self.__attribute_hub.get_crit_damage(self)

        return cd

    def set_crit_damage(self, crit_damage):
        self.__crit_damage = crit_damage

    def modify_crit_damage(self, cd):
        self.__crit_damage += cd

    def add_crit_damage(self, cd):
        self.modify_crit_damage(cd)

    def sub_crit_damage(self, cd):
        self.modify_crit_damage(0 - cd)

    def get_healing_bonus(self):
        bonus = self.__healing_bonus
        if self.__attribute_hub:
            bonus += self.__attribute_hub.get_healing_bonus(self)

        return bonus

    def set_healing_bonus(self, bonus):
        self.__healing_bonus = bonus

    def modify_healing_bonus(self, bonus):
        self.__healing_bonus += bonus

    def add_healing_bonus(self, bonus):
        self.modify_healing_bonus(bonus)

    def sub_healing_bonus(self, bonus):
        self.modify_healing_bonus(0 - bonus)

    def get_incoming_healing_bonus(self):
        bonus = self.__incomming_healing_bonus
        if self.__attribute_hub:
            bonus += self.__attribute_hub.get_incoming_healing_bonus(self)

        return bonus

    def set_incoming_headling_bonus(self, bonus):
        self.__incomming_healing_bonus = bonus

    def modify_incoming_healing_bonus(self, bonus):
        self.__incomming_healing_bonus += bonus

    def add_incoming_healing_bonus(self, bonus):
        self.modify_incoming_healing_bonus(bonus)

    def sub_incoming_healing_bonus(self, bonus):
        self.modify_incoming_healing_bonus(0 - bonus)

    def get_energy_recharge(self):
        er = self.__energy_recharge
        if self.__attribute_hub:
            er += self.__attribute_hub.get_energy_recharge(self)

        return round(er, 1)

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
        actual_cure_hp = cure_hp * (1 + healing_bonus + self.get_incoming_healing_bonus())
        # print("incoming_healing_bonus: ", round(self.get_incoming_healing_bonus(), 1))
        # print("actual_cure_hp: ", round(actual_cure_hp))
        return Character_HP_Change_Data(self, self.__hp.modify_cur_hp(actual_cure_hp))

    def regenerate_hp_per(self, hp_per, healing_bonus):
        return self.regenerate_hp(self.__hp.get_max_hp() * hp_per, healing_bonus)

    def consume_hp(self, hp):
        return Character_HP_Change_Data(self, self.__hp.modify_cur_hp(hp))

    def consume_hp_per(self, hp_per):
        return Character_HP_Change_Data(self, self.__hp.modify_cur_hp_per(hp_per))

    def get_normal_a_bonus(self):
        bonus = self.__normal_a_bonus
        if self.__attribute_hub:
            bonus += self.__attribute_hub.get_normal_a_bonus(self)

        return bonus

    def set_normal_a_bonus(self, bonus):
        self.__normal_a_bonus = bonus

    def modify_normal_a_bonus(self, bonus):
        self.__normal_a_bonus += bonus

    def add_normal_a_bonus(self, bonus):
        self.modify_normal_a_bonus(bonus)

    def sub_normal_a_bonus(self, bonus):
        self.modify_normal_a_bonus(0 - bonus)

    def get_charged_a_bonus(self):
        bonus = self.__charged_a_bonus
        if self.__attribute_hub:
            bonus += self.__attribute_hub.get_charged_a_bonus(self)

        return bonus

    def set_charged_a_bonus(self, bonus):
        self.__charged_a_bonus = bonus

    def modify_charged_a_bonus(self, bonus):
        self.__charged_a_bonus += bonus

    def add_charged_a_bonus(self, bonus):
        self.__charged_a_bonus += bonus

    def sub_charged_a_bonus(self, bonus):
        self.__charged_a_bonus -= bonus

    def get_plunging_bonus(self):
        bonus = self.__plunging_bonus
        if self.__attribute_hub:
            bonus += self.__attribute_hub.get_plunging_bonus(self)
        
        return bonus

    def set_plunging_bonus(self, bonus):
        self.__plunging_bonus = bonus

    def modify_plunging_bonus(self, bonus):
        self.__plunging_bonus += bonus

    def add_plunging_bonus(self, bonus):
        self.__plunging_bonus += bonus

    def sub_plunging_bonus(self, bonus):
        self.__plunging_bonus -= bonus

    def get_a_bonus(self):
        return self.get_normal_a_bonus()

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
        bonus = self.__e_bonus
        if self.__attribute_hub:
            bonus += self.__attribute_hub.get_e_bonus(self)

        return bonus

    def set_e_bonus(self, bonus):
        self.__e_bonus = bonus

    def modify_e_bonus(self, bonus):
        self.__e_bonus += bonus

    def add_e_bonus(self, bonus):
        self.__e_bonus += bonus

    def sub_e_bonus(self, bonus):
        self.__e_bonus -= bonus

    def get_q_bonus(self):
        bonus = self.__q_bonus
        if self.__attribute_hub:
            bonus += self.__attribute_hub.get_q_bonus(self)

        return bonus

    def set_q_bonus(self, bonus):
        self.__q_bonus = bonus

    def modify_q_bonus(self, bonus):
        # logging.debug("modify q bonus: %s", round(bonus, 3))
        self.__q_bonus += bonus

    def add_q_bonus(self, bonus):
        # logging.debug("add q bonus, %s", round(bonus, 3))
        self.__q_bonus += bonus

    def sub_q_bonus(self, bonus):
        # logging.debug("sub q bonus, %s", round(bonus, 3))
        self.__q_bonus -= bonus

    def modify_all_elem_bonus(self, bonus):
        # logging.debug("modify all elem bonus: %s", round(bonus, 3))
        self.modify_a_bonus(bonus)
        self.modify_e_bonus(bonus)
        self.modify_q_bonus(bonus)

    def add_all_bonus(self, bonus):
        # logging.debug("add all elem bonus: %s", round(bonus, 3))
        self.add_a_bonus(bonus)
        self.add_e_bonus(bonus)
        self.add_q_bonus(bonus)

    def sub_all_bonus(self, bonus):
        # logging.debug("sub all elem bonus: %s", round(bonus, 3))
        self.sub_a_bonus(bonus)
        self.sub_e_bonus(bonus)
        self.sub_q_bonus(bonus)

    def is_in_foreground(self):
        return self.__in_foreground
    
    def get_last_fore_back_switch_time(self):
        return self.__last_fore_back_switch_time

    def switch_to_foreground(self, switch_time):
        self.__in_foreground = True
        self.__last_fore_back_switch_time = switch_time

    def switch_to_background(self, switch_time):
        self.__in_foreground = False
        self.__last_fore_back_switch_time = switch_time

    def get_syw_combine(self):
        return self.__syw_combine

    def get_syw_name_count(self):
        return self.__syw_name_count

    def set_syw_combine(self, syw_combine: list[ShengYiWu]):
        self.__syw_combine = syw_combine
        self.__syw_name_count = {}
        for syw in syw_combine:
            if syw.name in self.__syw_name_count:
                self.__syw_name_count[syw.name] += 1
            else:
                self.__syw_name_count[syw.name] = 1

            self.add_crit_rate(syw.crit_rate)
            self.add_crit_damage(syw.crit_damage)
            self.__hp.modify_max_hp_per(syw.hp_percent)
            self.__hp.modify_max_hp(syw.hp)
            self.add_energy_recharge(syw.energy_recharge)
            self.add_atk_per(syw.atk_per)
            self.add_atk(syw.atk)
            self.add_defence_per(syw.def_per)
            self.add_defence(syw.def_v)
            self.add_elem_mastery(syw.elem_mastery)
            self.add_all_bonus(syw.elem_bonus)

        # TODO: 圣遗物套装效果是否在此处理？

    def get_weapon(self) -> Ys_Weapon:
        return self.__weapon

    def set_weapon(self, weapon: Ys_Weapon):
        if self.__weapon:
            raise Exception("原神不支持战斗时切换武器")
        
        self.__weapon = weapon
        weapon.set_owner(self)
        weapon.apply_static_attributes(self)
        

    def __str__(self):
        s = ""
        if self.__all_atk:
            s += "atk:" + str(self.get_atk()) + ", "

        if self.__all_defence:
            s += "def:" + str(self.get_defence()) + ", "

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
