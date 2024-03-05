#!/user/bin/env python3 -tt
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

import sys
import os
import logging
import itertools
from character_impl.ban_ni_te import BanNiTe_Q_Action

from ys_basic import Ys_Elem_Type, ys_crit_damage
from character import Character
from monster import Monster
from characters import Ying_Bao_Ch
from ys_weapon import Ji_Li_Sword
from ys_syw import ShengYiWu, ShengYiWu_Score, calculate_score, Syw_Combine_Desc, find_syw_combine

enable_debug = False

class Xing_Qiu_Ch(Character, name="行秋", elem_type=Ys_Elem_Type.SHUI, ming_zuo_num=6, e_level=12, q_level=13, q_energy=80):
    E_MIN_LEVEL = 8
    Q_MIN_LEVEL = 9

    e_multiplier = [
        (269/100, 306/100), # 8
        (286/100, 325/100), # 9
        (302/100, 344/100), # 10
        (319/100, 363/100), # 11
        (336/100, 382/100), # 12
        (357/100, 406/100), # 13
    ]

    q_multiplier = [
        # 从 9 级 q 开始，9级以下不计算
        92.3/100, 97.7/100, 103.1/100, 108.5/100, 115.3/100
    ]

    def __init__(self, weapon, syw_combine):
        super().__init__(base_atk=202, weapon=weapon)
        if self.e_level < Xing_Qiu_Ch.E_MIN_LEVEL:
            self.e_level = Xing_Qiu_Ch.E_MIN_LEVEL

        if self.q_level < Xing_Qiu_Ch.Q_MIN_LEVEL:
            self.q_level = Xing_Qiu_Ch.Q_MIN_LEVEL

        # 突破加成
        self.add_atk_per(0.24)
        # 固有天赋 2
        self.add_all_bonus(0.2)

        self.set_syw_combine(syw_combine)

        weapon.apply_combat_attributes(self)
        weapon.apply_passive(self)

    def get_e_damage(self, monster:Monster, after_q=False):
        multiplier = Xing_Qiu_Ch.e_multiplier[self.e_level - Xing_Qiu_Ch.E_MIN_LEVEL]
        m1 = multiplier[0]
        m2 = multiplier[1]

        ming_4_multiplier = 1
        if after_q and self.ming_zuo_num >= 4:
            ming_4_multiplier = 1.5

        if enable_debug:
            damage1 = monster.attacked(self.get_atk() * m1 * (1 + self.get_e_bonus()) * ming_4_multiplier)
            damage2 = monster.attacked(self.get_atk() * m2 * (1 + self.get_e_bonus()) * ming_4_multiplier)
            damage1_crit = ys_crit_damage(damage1, self.get_crit_damage())
            damage2_crit = ys_crit_damage(damage2, self.get_crit_damage())
            print(f"e伤害: {damage1:.0f} + {damage2:.0f}, 暴击: {damage1_crit:.0f} + {damage2_crit:.0f}, after_q: {after_q}")

        damage = self.get_atk() * (m1 + m2) * (1 + self.get_e_bonus()) * ming_4_multiplier
        return monster.attacked(damage)

    def get_q_damage(self, monster: Monster):
        multiplier = Xing_Qiu_Ch.q_multiplier[self.q_level - Xing_Qiu_Ch.Q_MIN_LEVEL]
        damage = self.get_atk() * multiplier * (1 + self.get_q_bonus())
        damage = monster.attacked(damage)

        if enable_debug:
            damage_crit = ys_crit_damage(damage, self.get_crit_damage())
            print(f"q伤害: {damage:.0f}, 暴击: {damage_crit:.0f}")

        return damage


def create_instance(syw_combine) -> Xing_Qiu_Ch:
    weapon = Ji_Li_Sword(base_atk=454, energy_recharge=0.613)
    return Xing_Qiu_Ch(weapon, syw_combine)

def create_for_lei_guo(syw_combine):
    xing_qiu = create_instance(syw_combine)
    xing_qiu.add_q_bonus(Ying_Bao_Ch.get_bonus_to_q(xing_qiu.q_energy))

    ban_ni_te = BanNiTe_Q_Action.create_instance()
    xing_qiu.add_atk_per(ban_ni_te.atk_per_bonus)
    xing_qiu.add_atk(ban_ni_te.atk_bonus)


def calculate_score_callback(score_data: ShengYiWu_Score):
    xing_qiu = create_instance(score_data.syw_combine)

    crit_rate = round(xing_qiu.get_crit_rate(), 3)
    if crit_rate < 0.55:
        return None

    name_count = xing_qiu.get_syw_name_count()
    # print(name_count)
    for n in name_count:
        if name_count[n] < 2:  # 散件不计算套装效果
            continue

        if n == ShengYiWu.CHEN_LUN:
            xing_qiu.add_all_bonus(0.2)
        elif n == ShengYiWu.SHUI_XIAN:
            xing_qiu.add_all_bonus(0.2)
        elif n == ShengYiWu.ZONG_SHI:
            xing_qiu.add_q_bonus(0.2)
        elif n == ShengYiWu.ZHUI_YI:
            xing_qiu.add_atk_per(0.18)
        elif n == ShengYiWu.JUE_DOU_SHI:
            xing_qiu.add_atk_per(0.18)
        elif n == ShengYiWu.JUE_YUAN:
            xing_qiu.add_energy_recharge(0.2)
            if name_count[n] >= 4:
                energy_recharge = xing_qiu.get_energy_recharge()
                jue_yuan_bonus = min(energy_recharge / 4 / 100, 0.75)
                xing_qiu.add_q_bonus(jue_yuan_bonus)

    energy_recharge = xing_qiu.get_energy_recharge()
    if energy_recharge < 200:
        return None

    monster = Monster()

    # 手法: eqe
    e_damage_1 = xing_qiu.get_e_damage(monster)
    e_damage_2 = xing_qiu.get_e_damage(monster, after_q=True)
    e_damage = e_damage_1 + e_damage_2

    # 一开始两箭吃不到四命减抗
    q_damage = xing_qiu.get_q_damage(monster) * 2

    if xing_qiu.ming_zuo_num >= 2:
        monster.add_jian_kang(0.15)

    q_num = 3 + 5 + 2 + 3 + 5 + 2 + 3 + 5 + 2 + 3 + 5
    q_damage_k = xing_qiu.get_q_damage(monster)

    q_damage += q_damage_k * q_num

    all_damage = e_damage + q_damage

    cd = xing_qiu.get_crit_damage()
    score_data.damage_to_score(all_damage, xing_qiu.get_crit_rate(), cd)

    q_damage_k = ys_crit_damage(q_damage_k, cd)
    score_data.extra_score = q_damage_k

    score_data.custom_data = [int(xing_qiu.get_atk()), 
                              round(e_damage_1), round(e_damage_2), round(q_damage_k), 
                              crit_rate, round(cd, 3), energy_recharge]

    return True


result_description = ["攻击力", "q前e伤害", "q后e伤害", "q一箭伤害", "暴击率", "暴击伤害", "充能效率", "extra_score为 q 一箭伤害"]


def match_sha_callback(syw: ShengYiWu):
    return syw.atk_per == ShengYiWu.BONUS_MAX


def match_bei_callback(syw: ShengYiWu):
    return syw.elem_type == Ys_Elem_Type.SHUI


def match_tou_callback(syw: ShengYiWu):
    return syw.crit_rate == ShengYiWu.CRIT_RATE_MAIN or syw.crit_damage == ShengYiWu.CRIT_DAMAGE_MAIN


def get_debug_raw_score_list():
    syw_combine_str_lst = ["(jue_yuan, h, cc:0.066, cd:0.117, atkp:0.111, atk:33)",
                           "(jue_yuan, y, cd:0.171, hp:807, re:0.11, atkp:0.047)",
                           "(jue_yuan, s, cc:0.086, cd:0.202, hpp:0.105, atkp:0.466, elem:19)",
                           "(yue_tuan, b, cc:0.074, cd:0.078, hp:538, atkp:0.152, bonus:0.466)",
                           "(jue_yuan, t, cc:0.311, cd:0.179, re:0.104, atk:31, defp:0.058)"]
    return [ShengYiWu_Score(ShengYiWu.string_to_syw_combine(syw_combine_str_lst))]

def find_syw_for_xing_qiu():
    if enable_debug:
        raw_score_list = get_debug_raw_score_list()
    else:
        combine_desc_lst = Syw_Combine_Desc.any_2p2([ShengYiWu.JUE_YUAN,
                                                    ShengYiWu.ZONG_SHI,
                                                    ShengYiWu.CHEN_LUN,
                                                    ShengYiWu.SHUI_XIAN,
                                                    ShengYiWu.ZHUI_YI,
                                                    ShengYiWu.JUE_DOU_SHI])

        combine_desc_lst.append(Syw_Combine_Desc(
            set1_name=ShengYiWu.JUE_YUAN, set1_num=4))

        raw_score_list = find_syw_combine(combine_desc_lst,
                                        match_sha_callback=match_sha_callback,
                                        match_bei_callback=match_bei_callback,
                                        match_tou_callback=match_tou_callback)
        print(len(raw_score_list))

    return calculate_score(raw_score_list,
                           calculate_score_callbak=calculate_score_callback,
                           result_txt_file="xing_qiu_syw.txt",
                           result_description=result_description)


# Main body
if __name__ == '__main__':
    find_syw_for_xing_qiu()
