#!/user/bin/env python3 -c
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

import logging
import weakref
from enum import Enum

from typing import Self

from .elem_type import Ys_Elem_Type
from .weapon import Ys_Weapon
from .health_point import HealthPoint, HP_Change_Data
from .syw import ShengYiWu


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

class _ChAttributes:
    def __init__(self):
        self.valid = True
        self.reset()

    def reset(self):
        self.crit_rate = 0
        self.crit_damage = 0

        self.atk_per = 0
        self.atk = 0

        self.def_per = 0
        self.def_v = 0

        self.elem_mastery = 0
        self.healing_bonus = 0
        self.incoming_healing_bonus = 0
        self.energy_recharge = 0

        self.elem_bonus = 0
        self.normal_a_bonus = 0
        self.charged_a_bonus = 0
        self.plunging_bonus = 0
        self.e_bonus = 0
        self.q_bonus = 0


class CharacterBase:
    def __init_subclass__(cls, name, elem_type: Ys_Elem_Type=None, ming_zuo_num=0, ch_level=90, 
                          min_skill_level = 8, a_level=8, e_level=8, q_level=8, q_energy=80,
                          **kwargs):
        """
        初始化一些固定不变的属性

        ch_level: 角色等级
        min_skill_level: 为了在抄录角色倍率表时少抄些，减少工作量，min_skil_level设定技能倍率表的最小技能等级
        """
        super().__init_subclass__(**kwargs)

        cls.name = name
        cls.elem_type = elem_type
        cls.ming_zuo_num = ming_zuo_num
        cls.ch_level = ch_level

        cls.min_skill_level = min_skill_level
        cls.a_level = a_level if a_level > min_skill_level else min_skill_level
        cls.e_level = e_level if e_level > min_skill_level else min_skill_level
        cls.q_level = q_level if q_level > min_skill_level else min_skill_level
        cls.q_energy = q_energy

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if k in ["name", "elem_type", "ming_zuo_num", "ch_level", 
                     "min_skill_level", "a_level", "e_level", "q_level", 
                     "q_energy"]:
                setattr(self, k, v)
            else:
                raise Exception("unknown attribute when init CharacterBase: " + k)
            
    def a_idx(self):
        return self.a_level - self.min_skill_level
    
    def e_idx(self):
        return self.e_level - self.min_skill_level
    
    def q_idx(self):
        return self.q_level - self.min_skill_level
            
    def set_ming_zuo_num(self, ming_zuo_num):
        self.ming_zuo_num = ming_zuo_num

    # 按大招快速切人
    def q_switch(self, plan, t):
        """
        * plan: 行动轴
        * t: 角色被切到场上的时间

        * 返回值：大招动画开始时间 
        """
        plan.add_switch_action(self, t)
        return t + 0.066

class Character(CharacterBase, name="通用角色"):
    def __init__(self, 
                 weapon: Ys_Weapon = None,
                 base_hp=0, max_hp=0,
                 base_atk=0, all_atk=0, 
                 base_defence=0, all_defence=0,
                 elem_mastery=0,

                 crit_rate=0.05, crit_damage=0.5, 
                 healing_bonus=0, incoming_healing_bonus=0,
                 energy_recharge=100.0,
                 
                 normal_a_bonus=0, charged_a_bonus=0, plunging_bonus=0,
                 e_bonus=0, q_bonus=0,
                 elem_bonus=0,
                 **kwargs):
        if kwargs:
            super().__init__(**kwargs)

        # 基础攻击力：角色基础攻击力 + 武器基础攻击力
        if weapon:
            base_atk += weapon.base_atk
        self.__base_atk = base_atk

        # 基础防御力
        self.__base_defence = base_defence

        self.__hp: HealthPoint = HealthPoint(base_hp, max_hp)

        # 角色有三种属性(准确来说是四种)
        # * 固定属性：由 角色的基础属性 + 圣遗物属性 构成
        # * 可二次转化 Buff 属性：由各种能被二次转化的 Buff 附加而成
        # * 不可二次转化 Buff 属性：由各种不能被二次转化的 Buff 附加而成
        self.__fixed_attrs = _ChAttributes()
        self.buff_attrs = _ChAttributes()
        self.un_convertable_attrs = _ChAttributes()

        # 攻击力
        if all_atk:
            self.__fixed_attrs.atk = all_atk - base_atk
        # 总防御力
        if all_defence:
            self.__fixed_attrs.def_v = all_defence - base_defence

        # 元素精通
        self.__fixed_attrs.elem_mastery = elem_mastery

        self.__fixed_attrs.crit_rate = crit_rate
        self.__fixed_attrs.crit_damage = crit_damage

        # 治疗加成
        self.__fixed_attrs.healing_bonus = healing_bonus
        # 受治疗加成
        self.__fixed_attrs.incoming_healing_bonus = incoming_healing_bonus

        self.__fixed_attrs.energy_recharge = energy_recharge

        self.__fixed_attrs.elem_bonus = elem_bonus
        # 普通攻击
        self.__fixed_attrs.normal_a_bonus = normal_a_bonus
        # 重击
        if not charged_a_bonus:
            charged_a_bonus = normal_a_bonus
        self.__fixed_attrs.charged_a_bonus = charged_a_bonus
        # 下落攻击
        if not plunging_bonus:
            plunging_bonus = normal_a_bonus
        self.__fixed_attrs.plunging_bonus = plunging_bonus

        self.__fixed_attrs.e_bonus = e_bonus
        self.__fixed_attrs.q_bonus = q_bonus

        self.__weapon: Ys_Weapon = weapon

        self.__syw_combine: list[ShengYiWu] = None
        self.__syw_name_count: dict[str, int] = None

        if weapon:
            weapon.set_owner(self)
            weapon.apply_static_attributes(self)

        self.__in_foreground = False
        # 最近一次前后台切换的时间，有些 buff 是在切到前台或后台时开始计时的
        self.__last_fore_back_switch_time = None

    def reset_attrs(self):
        """
        重置除固定属性以外的其他属性
        """
        self.buff_attrs.reset()
        self.un_convertable_attrs.reset()
        self.__hp.buff_attrs.reset()

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
    
    def get_base_defence(self):
        return self.__base_defence
    
    def set_hp(self, hp: HealthPoint):
        self.__hp = hp

    def get_hp(self) -> HealthPoint:
        return self.__hp

    def regenerate_hp(self, cure_hp, healer_healing_bonus):
        """
        因为治疗者的治疗加成和受治疗者的受治疗加成是“加算”，所以需要传入治疗者的治疗加成才能确定最终的治疗量
        """
        actual_cure_hp = cure_hp * (1 + healer_healing_bonus + self.get_incoming_healing_bonus())
        # print("incoming_healing_bonus: ", round(self.get_incoming_healing_bonus(), 1))
        # print("actual_cure_hp: ", round(actual_cure_hp))
        return Character_HP_Change_Data(self, self.__hp.modify_cur_hp(actual_cure_hp))

    def regenerate_hp_per(self, hp_per, healing_bonus):
        return self.regenerate_hp(self.__hp.get_max_hp() * hp_per, healing_bonus)

    def consume_hp(self, hp):
        return Character_HP_Change_Data(self, self.__hp.modify_cur_hp(hp))

    def consume_hp_per(self, hp_per):
        return Character_HP_Change_Data(self, self.__hp.modify_cur_hp_per(hp_per))
    
    def get_atk(self, include_un_convertable=True):
        atk_per = self.__fixed_attrs.atk_per
        atk_per += self.buff_attrs.atk_per

        atk = self.__fixed_attrs.atk
        atk += self.buff_attrs.atk

        if include_un_convertable:
            atk_per += self.un_convertable_attrs.atk_per
            atk += self.un_convertable_attrs.atk

        return round(atk_per * self.__base_atk + atk)

    def get_defence(self, include_un_convertable=True):
        def_per = self.__fixed_attrs.def_per
        def_per += self.buff_attrs.def_per

        def_v = self.__fixed_attrs.def_v
        def_v += self.buff_attrs.def_v

        if include_un_convertable:
            def_per += self.un_convertable_attrs.def_per
            def_v += self.un_convertable_attrs.def_v

        return round(self.__base_defence * def_per + def_v)

    def get_elem_mastery(self, include_un_convertable=True):
        em = self.__fixed_attrs.elem_mastery + self.buff_attrs.elem_mastery
        if include_un_convertable:
            em += self.un_convertable_attrs.elem_mastery
        return em

    def get_crit_rate(self, include_un_convertable=True):
        cr = self.__fixed_attrs.crit_rate + self.buff_attrs.crit_rate
        if include_un_convertable:
            cr += self.un_convertable_attrs.crit_rate

        return cr

    def get_crit_damage(self, include_un_convertable=True):
        cd = self.__fixed_attrs.crit_damage + self.buff_attrs.crit_damage
        if include_un_convertable:
            cd += self.un_convertable_attrs.crit_damage
        return cd

    def get_healing_bonus(self, include_un_convertable=True):
        hb = self.__fixed_attrs.healing_bonus + self.buff_attrs.healing_bonus
        if include_un_convertable:
            hb += self.un_convertable_attrs.healing_bonus
        return hb

    def get_incoming_healing_bonus(self, include_un_convertable=True):
        ihb = self.__fixed_attrs.incoming_healing_bonus + self.buff_attrs.incoming_healing_bonus
        if include_un_convertable:
            ihb += self.un_convertable_attrs.incoming_healing_bonus
        return ihb

    def get_energy_recharge(self, include_un_convertable=True):
        er = self.__fixed_attrs.energy_recharge + self.buff_attrs.energy_recharge
        if include_un_convertable:
            er += self.un_convertable_attrs.energy_recharge
        return round(er, 1)
    
    def __get_base_bonus(self, include_un_convertable):
        bb = self.__fixed_attrs.elem_bonus + self.buff_attrs.elem_bonus
        if include_un_convertable:
            bb += self.un_convertable_attrs.elem_bonus
        return bb

    def get_normal_a_bonus(self, include_un_convertable=True):
        normal_a_bonus = self.__fixed_attrs.normal_a_bonus + self.buff_attrs.normal_a_bonus
        if include_un_convertable:
            normal_a_bonus += self.un_convertable_attrs.normal_a_bonus
        return self.__get_base_bonus(include_un_convertable) + normal_a_bonus

    def get_charged_a_bonus(self, include_un_convertable=True):
        charged_a_bonus = self.__fixed_attrs.charged_a_bonus + self.buff_attrs.charged_a_bonus
        if include_un_convertable:
            charged_a_bonus += self.un_convertable_attrs.charged_a_bonus
        return self.__get_base_bonus(include_un_convertable) + charged_a_bonus

    def get_plunging_bonus(self, include_un_convertable=True):
        plunging_bonus = self.__fixed_attrs.plunging_bonus + self.buff_attrs.plunging_bonus
        if include_un_convertable:
            plunging_bonus += self.un_convertable_attrs.plunging_bonus
        return self.__get_base_bonus(include_un_convertable) + plunging_bonus

    def get_a_bonus(self, include_un_convertable=True):
        return self.get_normal_a_bonus(include_un_convertable)

    def get_e_bonus(self, include_un_convertable=True):
        e_bonus = self.__fixed_attrs.e_bonus + self.buff_attrs.e_bonus
        if include_un_convertable:
            e_bonus += self.un_convertable_attrs.e_bonus
        return self.__get_base_bonus(include_un_convertable) + e_bonus

    def get_q_bonus(self, include_un_convertable=True):
        q_bonus = self.__fixed_attrs.q_bonus + self.buff_attrs.q_bonus
        if include_un_convertable:
            q_bonus += self.un_convertable_attrs.q_bonus
        return self.__get_base_bonus(include_un_convertable) + q_bonus

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

        # 花
        self.__hp.fixed_attrs.hp += 4780
        # 羽毛
        self.__fixed_attrs.atk += 311
        for syw in syw_combine:
            if syw.name in self.__syw_name_count:
                self.__syw_name_count[syw.name] += 1
            else:
                self.__syw_name_count[syw.name] = 1

            self.__hp.fixed_attrs.hp_per += syw.hp_percent
            self.__hp.fixed_attrs.hp += syw.hp

            self.__fixed_attrs.crit_rate += syw.crit_rate
            self.__fixed_attrs.crit_damage += syw.crit_damage
            self.__fixed_attrs.energy_recharge += syw.energy_recharge * 100
            self.__fixed_attrs.atk_per += syw.atk_per
            self.__fixed_attrs.atk += syw.atk
            self.__fixed_attrs.def_per += syw.def_per
            self.__fixed_attrs.def_v += syw.def_v
            self.__fixed_attrs.elem_mastery += syw.elem_mastery
            self.__fixed_attrs.elem_bonus += syw.elem_bonus

        self.__hp.on_max_hp_changed()

        # TODO: 圣遗物套装效果是否在此处理？

    def get_weapon(self) -> Ys_Weapon:
        return self.__weapon

    # def set_weapon(self, weapon: Ys_Weapon):
    #     if self.__weapon:
    #         raise Exception("不支持战斗时切换武器")
        
    #     self.__weapon = weapon
    #     weapon.set_owner(self)
    #     weapon.apply_static_attributes(self)
        

    def __str__(self):
        s = ""
        s += "atk:" + str(self.get_atk()) + ", "
        s += "def:" + str(self.get_defence()) + ", "

        em = self.get_elem_mastery()
        if em:
            s += "m:" + str(em) + ","

        s += "cc:" + str(round(self.get_crit_rate(), 3)) + ", "
        s += "cd:" + str(round(self.get_crit_damage(), 3)) + ", "

        s += "er:" + str(round(self.get_energy_recharge(), 1)) + ", "
        s += str(self.__hp) + ", "

        elem_bonus = self.__get_base_bonus()
        if elem_bonus:
            s += "b:" + str(elem_bonus) + ", "

        normal_a_bonus = self.get_normal_a_bonus()
        if normal_a_bonus:
            s += "ab:" + str(normal_a_bonus)
        
        charged_a_bonus = self.get_charged_a_bonus()
        if charged_a_bonus:
            s += "cb:" + str(charged_a_bonus) + ", "

        plunging_bonus = self.get_plunging_bonus()
        if plunging_bonus:
            s + "pb:" + str(plunging_bonus) + ", "

        e_bonus = self.get_e_bonus()
        if e_bonus:
            s += "eb:" + str(round(e_bonus, 3)) + ", "

        q_bonus = self.get_q_bonus()
        if q_bonus:
            s += "qb:" + str(round(q_bonus, 3)) + ", "

        healing_bonus = self.get_healing_bonus()
        if healing_bonus:
            s += "hb:" + str(round(healing_bonus, 1)) + ", "

        incoming_healing_bonus = self.get_incoming_healing_bonus()
        if incoming_healing_bonus:
            s += "ihb:" + str(round(incoming_healing_bonus, 1))

        if self.__in_foreground:
            s += "f, "
        else:
            s += "b, "

        return s
