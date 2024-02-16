#!/user/bin/env python3 -tt
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

import sys
import os
import logging
import itertools

from ys_basic import Ys_Elem_Type, Ys_Weapon, ys_expect_damage, ys_crit_damage
from ys_reaction import Ys_Reaction, Ys_No_Reaction, Ys_Reaction_ZhengFa
from ys_syw import ShengYiWu, ShengYiWu_Score, calculate_score, Syw_Combine_Desc, find_syw_combine
from character import Character
from monster import Monster
from ban_ni_te import BanNiTe_Q_Action
from characters import Ying_Bao_Ch
from wan_ye import get_wan_ye_q_bonus
from ys_weapon import Yu_Huo


enable_debug = False
# 蒸发率
zheng_fa_ratio = 0.66

class Xiang_Ling_Ch(Character, name="香菱", elem_type=Ys_Elem_Type.HUO, ming_zuo_num=6, q_level=13, q_energy=80):
    # 注：大招等级至少点到 9 级
    q_multiplier = [
        (122/100, 150/100, 186/100, 190/100), # 9
        (130/100, 158/100, 197/100, 202/100), # 10
        (137/100, 167/100, 208/100, 213/100), # 11
        (144/100, 176/100, 219/100, 224/100), # 12
        (153/100, 187/100, 233/100, 238/100), # 13
    ]
    def __init__(self, weapon: Ys_Weapon, syw_combine):
        super().__init__(base_atk=225, weapon=weapon)

        if self.q_level < 9:
            self.q_level = 9

        self.add_elem_mastery(96) # 突破加成

        self.set_syw_combine(syw_combine)
        self.add_energy_recharge(0.2) # 绝缘两件套效果

        self.panel_crit_ratae = self.get_crit_rate()
        self.panel_atk = self.get_atk()

        weapon.apply_combat_attributes(self)
        weapon.apply_passive(self)

        energy_recharge = self.get_energy_recharge()
        jue_yuan_bonus = min(energy_recharge / 4 / 100, 0.75)
        self.add_q_bonus(jue_yuan_bonus)

    def add_shuang_huo_bonus(self):
        self.add_atk_per(0.25)

    def add_lei_shen_bonus(self):
        self.add_q_bonus(Ying_Bao_Ch.get_bonus_to_q(self.q_energy))

    def add_wan_ye_bonus(self, monster: Monster):
        self.add_q_bonus(get_wan_ye_q_bonus())
        monster.add_jian_kang(0.4)

    def add_xia_wo_lei_bonus(self, monster: Monster):
        monster.add_jian_kang(0.4)
        self.add_atk_per(0.4)
        # TODO: 夏沃蕾满命效果香菱吃不了多少，要不要加？

    def get_guo_ba_damage(self, reaction: Ys_Reaction):
        base_damage = self.get_atk() * 189 / 100
        return reaction.do_damage(base_damage, self.get_e_bonus())

    def __get_q_damage(self, multiplier, reaction: Ys_Reaction):
        base_damage = self.get_atk() * multiplier

        return reaction.do_damage(base_damage, self.get_q_bonus())

    def get_hui_wu_damage(self, phrase, reaction: Ys_Reaction):
        multiplier = Xiang_Ling_Ch.q_multiplier[self.q_level - 9][phrase - 1]
        return self.__get_q_damage(multiplier, reaction)
    
    def get_huo_lun_damage(self, reaction: Ys_Reaction):
        multiplier = Xiang_Ling_Ch.q_multiplier[self.q_level - 9][-1]
        return self.__get_q_damage(multiplier, reaction)

def print_damages(xiang_ling_init: Xiang_Ling_Ch):
    import copy
    xiang_ling = copy.deepcopy(xiang_ling_init)

    crit_damage = xiang_ling.get_crit_damage()

    monster = Monster(level=93)

    xiang_ling.add_lei_shen_bonus()
    xiang_ling.add_shuang_huo_bonus()

    print(xiang_ling)
    
    ban_ni_te = BanNiTe_Q_Action.create_instance()
    # 前两段挥舞能吃到宗室加成
    xiang_ling.add_atk_per(ban_ni_te.atk_per_bonus)
    
    no_reaction = Ys_No_Reaction(xiang_ling, monster)
    zheng_fa_reaction = Ys_Reaction_ZhengFa(xiang_ling, monster)

    # 前两段挥舞吃不到班尼特的加成
    hui_wu_1 = xiang_ling.get_hui_wu_damage(1, no_reaction)
    hui_wu_2 = xiang_ling.get_hui_wu_damage(2, no_reaction)
    hui_wu_3 = xiang_ling.get_hui_wu_damage(3, no_reaction)

    hui_wu_1_zf = xiang_ling.get_hui_wu_damage(1, zheng_fa_reaction)
    hui_wu_2_zf = xiang_ling.get_hui_wu_damage(2, zheng_fa_reaction)
    hui_wu_3_zf = xiang_ling.get_hui_wu_damage(3, zheng_fa_reaction)

    print(f"三段挥舞直伤：{hui_wu_1:.0f}, {hui_wu_2:.0f}, {hui_wu_3:.0f}")
    hui_wu_1 = ys_crit_damage(hui_wu_1, crit_damage)
    hui_wu_2 = ys_crit_damage(hui_wu_2, crit_damage)
    hui_wu_3 = ys_crit_damage(hui_wu_3, crit_damage)
    print(f"三段挥舞直伤(暴击)：{hui_wu_1:.0f}, {hui_wu_2:.0f}, {hui_wu_3:.0f}")

    print(f"三段挥舞蒸发：{hui_wu_1_zf:.0f}, {hui_wu_2_zf:.0f}, {hui_wu_3_zf:.0f}")
    hui_wu_1_zf = ys_crit_damage(hui_wu_1_zf, crit_damage)
    hui_wu_2_zf = ys_crit_damage(hui_wu_2_zf, crit_damage)
    hui_wu_3_zf = ys_crit_damage(hui_wu_3_zf, crit_damage)
    print(f"三段挥舞蒸发(暴击)：{hui_wu_1_zf:.0f}, {hui_wu_2_zf:.0f}, {hui_wu_3_zf:.0f}")

    xiang_ling.add_atk(ban_ni_te.atk_bonus)

    guo_ba_zhi_shang = xiang_ling.get_guo_ba_damage(no_reaction)
    guo_ba_zheng_fa = xiang_ling.get_guo_ba_damage(zheng_fa_reaction)
    print(f"锅巴首次直伤：{guo_ba_zhi_shang:.0f}, 蒸发: {guo_ba_zheng_fa:.0f}")
    guo_ba_zhi_shang = ys_crit_damage(guo_ba_zhi_shang, crit_damage)
    guo_ba_zheng_fa = ys_crit_damage(guo_ba_zheng_fa, crit_damage)
    print(f"锅巴首次直伤(暴击)：{guo_ba_zhi_shang:.0f}, 蒸发: {guo_ba_zheng_fa:.0f}")

    huo_lun_zhi_shang = xiang_ling.get_huo_lun_damage(no_reaction)
    huo_lun_zheng_fa = xiang_ling.get_huo_lun_damage(zheng_fa_reaction)
    print(f"火轮直伤: {huo_lun_zhi_shang:.0f}, 火轮蒸发: {huo_lun_zheng_fa:.0f}")
    huo_lun_zhi_shang = ys_crit_damage(huo_lun_zhi_shang, crit_damage)
    huo_lun_zheng_fa = ys_crit_damage(huo_lun_zheng_fa, crit_damage)
    print(f"火轮直伤(暴击): {huo_lun_zhi_shang:.0f}, 火轮蒸发(暴击): {huo_lun_zheng_fa:.0f}")

    if xiang_ling.ming_zuo_num >= 1:
        monster.add_jian_kang(0.15)

    guo_ba_zhi_shang = xiang_ling.get_guo_ba_damage(no_reaction)
    guo_ba_zheng_fa = xiang_ling.get_guo_ba_damage(zheng_fa_reaction)
    print(f"锅巴后续直伤：{guo_ba_zhi_shang:.0f}, 蒸发: {guo_ba_zheng_fa:.0f}")
    guo_ba_zhi_shang = ys_crit_damage(guo_ba_zhi_shang, crit_damage)
    guo_ba_zheng_fa = ys_crit_damage(guo_ba_zheng_fa, crit_damage)
    print(f"锅巴后续直伤(暴击)：{guo_ba_zhi_shang:.0f}, 蒸发: {guo_ba_zheng_fa:.0f}")

    huo_lun_zhi_shang = xiang_ling.get_huo_lun_damage(no_reaction)
    huo_lun_zheng_fa = xiang_ling.get_huo_lun_damage(zheng_fa_reaction)
    print(f"锅巴减抗后：火轮直伤: {huo_lun_zhi_shang:.0f}, 火轮蒸发: {huo_lun_zheng_fa:.0f}")
    huo_lun_zhi_shang = ys_crit_damage(huo_lun_zhi_shang, crit_damage)
    huo_lun_zheng_fa = ys_crit_damage(huo_lun_zheng_fa, crit_damage)
    print(f"锅巴减抗后：火轮直伤(暴击): {huo_lun_zhi_shang:.0f}, 火轮蒸发(暴击): {huo_lun_zheng_fa:.0f}")


def calculate_score_callback(score_data: ShengYiWu_Score):
    weapon = Yu_Huo(base_atk=510, jing_lian_rank=5, energy_recharge=0.459)
    xiang_ling = Xiang_Ling_Ch(weapon, score_data.syw_combine)

    crit_rate = round(xiang_ling.get_crit_rate(), 3)
    if crit_rate < 0.6:
        return None
    
    elem_mastery = round(xiang_ling.get_elem_mastery(), 1)
    if elem_mastery < 180:
        return None
    
    energy_recharge = xiang_ling.get_energy_recharge()
    if energy_recharge < 230:
        return None
    
    if enable_debug:
        print_damages(xiang_ling)
    
    monster = Monster()
    no_reaction = Ys_No_Reaction(xiang_ling, monster)
    zheng_fa_reaction = Ys_Reaction_ZhengFa(xiang_ling, monster)
    
    xiang_ling.add_lei_shen_bonus()

    xiang_ling.add_shuang_huo_bonus()
    ban_ni_te = BanNiTe_Q_Action.create_instance()
    # 前两段挥舞能吃到宗室加成
    xiang_ling.add_atk_per(ban_ni_te.atk_per_bonus)
    xiang_ling.add_atk(ban_ni_te.atk_bonus)

    if xiang_ling.ming_zuo_num >= 1:
        monster.add_jian_kang(0.15)
    
    huo_lun_zhi_shang = xiang_ling.get_huo_lun_damage(no_reaction)
    huo_lun_zheng_fa = xiang_ling.get_huo_lun_damage(zheng_fa_reaction)
    huo_lun_damage = huo_lun_zhi_shang * (1 - zheng_fa_ratio) + huo_lun_zheng_fa * zheng_fa_ratio

    cd = xiang_ling.get_crit_damage()
    score_data.damage_to_score(huo_lun_damage, xiang_ling.get_crit_rate(), cd)

    huo_lun_zheng_fa_crit = ys_crit_damage(huo_lun_zheng_fa, cd)
    score_data.extra_score = huo_lun_zheng_fa_crit

    score_data.custom_data = [ys_crit_damage(huo_lun_zhi_shang, cd), huo_lun_zheng_fa_crit,
                              elem_mastery, int(xiang_ling.get_atk()), int(xiang_ling.panel_atk),
                              round(xiang_ling.panel_crit_ratae, 3), round(cd, 3),
                              round(energy_recharge, 1)]
    
    return True


result_description = ["火轮直伤暴击伤害", "火轮蒸发暴击伤害", "元素精通", "实战攻击力", "双火面板攻击力", "面板暴击率", "暴击伤害", "充能效率", 
                      "extra_score为火轮蒸发暴击伤害"]


def match_sha_callback(syw: ShengYiWu):
    return syw.energy_recharge == ShengYiWu.ENERGY_RECHARGE_MAX


def match_bei_callback(syw: ShengYiWu):
    return syw.elem_type == Ys_Elem_Type.HUO # or syw.atk_per == ShengYiWu.BONUS_MAX


def match_tou_callback(syw: ShengYiWu):
    return syw.crit_rate == ShengYiWu.CRIT_RATE_MAIN or syw.crit_damage == ShengYiWu.CRIT_DAMAGE_MAIN


def get_debug_raw_score_list():
    # [(jue_yuan, h, cd:0.21, re:0.194, defp:0.066, elem:44),
    #  (jue_yuan, y, cc:0.132, cd:0.148, atkp:0.058, elem:16),
    #  (jue_yuan, s, cc:0.07, cd:0.14, hpp:0.093, re:0.518, atk:35),
    #  (bing_tao, b, cc:0.031, cd:0.256, re:0.097, elem:21, bonus:0.466),
    #  (jue_yuan, t, cc:0.311, cd:0.218, hpp:0.087, atkp:0.099, elem:16)]
    syw_combine = [
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_HUA,
                  crit_damage=0.21, energy_recharge=0.194, def_per=0.066, elem_mastery=44),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_YU,
                  crit_rate=0.132, crit_damage=0.148, atk_per=0.058, elem_mastery=16),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_SHA, energy_recharge=ShengYiWu.ENERGY_RECHARGE_MAX,
                  crit_rate=0.07, crit_damage=0.14, hp_percent=0.093, atk=35),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=Ys_Elem_Type.HUO,
                  crit_rate=0.031, crit_damage=0.256, energy_recharge=0.097, elem_mastery=21),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_TOU, crit_rate=ShengYiWu.CRIT_RATE_MAIN,
                  crit_damage=0.218, hp_percent=0.087, atk_per=0.099, elem_mastery=16)
    ]
    return [ShengYiWu_Score(syw_combine)]


def find_syw_for_xiang_ling():
    if enable_debug:
        raw_score_list = get_debug_raw_score_list()
    else:
        raw_score_list = find_syw_combine([Syw_Combine_Desc(set1_name=ShengYiWu.JUE_YUAN, set1_num=4)],
                                        match_sha_callback=match_sha_callback,
                                        match_bei_callback=match_bei_callback,
                                        match_tou_callback=match_tou_callback)
        print(len(raw_score_list))

    return calculate_score(raw_score_list,
                           calculate_score_callbak=calculate_score_callback,
                           result_txt_file="xiang_ling_syw.txt",
                           result_description=result_description)

# Main body
if __name__ == '__main__':
    find_syw_for_xiang_ling()