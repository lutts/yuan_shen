#!/user/bin/env python3 -tt
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

from typing import Self
from ys_basic import Ys_Elem_Type
from character import Character
from monster import Monster
from ys_reaction import *
from base_syw import ShengYiWu, ShengYiWu_Score, calculate_score, Syw_Combine_Desc, find_syw_combine

enable_debug = False

class Na_Xi_Da_Ch(Character):
    # 长按倍率
    e_multiplier = [
        130.4/100, # 1 
        140.2/100, # 2
        150/100, # 3
        163/100, # 4
        172.8/100, # 5
        182.6/100, # 6
        195.6/100, # 7
        208.6/100, # 8
        221.7/100, # 9
        234.7/100, # 10
        247.8/100, # 11
        260.8/100, # 12
        277.1/100, # 13
    ]

    mie_jing_san_ye_multiplier = [
        (103.2/100, 206.4/100), # 1
        (110.9/100, 221.9/100), # 2
        (118.7/100, 237.4/100), # 3
        (129.0/100, 258.0/100), # 4
        (136.7/100, 273.5/100), # 5
        (144.5/100, 289.0/100), # 6
        (154.8/100, 309.6/100), # 7
        (165.1/100, 330.2/100), # 8
        (175.4/100, 350.9/100), # 9
        (185.8/100, 371.5/100), # 10
        (196.1/100, 392.2/100), # 11
        (206.4/100, 412.8/100), # 12
        (219.3/100, 438.6/100), # 13
    ]

    q_huo_bonus = [
        (14.9/100, 22.3/100), # 1
        (16.0/100, 24.0/100), # 2
        (17.1/100, 25.7/100), # 3
        (18.6/100, 27.9/100), # 4
        (19.7/100, 29.6/100), # 5
        (20.8/100, 31.3/100), # 6
        (22.3/100, 33.5/100), # 7
        (23.8/100, 35.7/100), # 8
        (25.3/100, 37.9/100), # 9
        (26.8/100, 40.2/100), # 10
        (28.27/100, 42.41/100), # 11
        (29.8/100, 44.6/100), # 12
        (31.6/100, 47.4/100), # 13
    ]

    q_lei_intervals = [
        (0.24, 0.37), # 1
        (0.27, 0.4), # 2
        (0.29, 0.43), # 3
        (0.31, 0.47), # 4
        (0.33, 0.49), # 5
        (0.35, 0.52), # 6
        (0.37, 0.56), # 7
        (0.4, 0.6), # 8
        (0.42, 0.63), # 9
        (0.45, 0.67), # 10
        (0.47, 0.7), # 11
        (0.5, 0.74), # 12
        (0.53, 0.79), # 13
    ]

    q_shui_durations = [
        (3.34, 5.02), # 1
        (3.59, 5.39), # 2
        (3.85, 5.77), # 3
        (4.18, 6.27), # 4
        (4.43, 6.65), # 5
        (4.68, 7.02), # 6
        (5.02, 7.52), # 7
        (5.35, 8.03), # 8
        (5.68, 8.53), # 9
        (6.02, 9.03), # 10
        (6.35, 9.53), # 11
        (6.69, 10.03), # 12
        (7.11, 10.66), # 13
    ]

    # TODO: 站场平A能增加多少伤害？

    @classmethod
    def get_instance(cls, teammate_types: list[Ys_Elem_Type], 
                     base_atk = 841, has_zhuan_wu=True,
                     ming_zuo_num=6, e_level=13, q_level=13) -> Self:
        if len(teammate_types) > 3:
            raise Exception("队友不能超过3个")
        
        if ming_zuo_num >= 1:
            huo_num = 1
            lei_num = 1
            shui_num = 1
        else:
            huo_num = 0
            lei_num = 0
            shui_num = 0

        cao_num = 0

        for t in teammate_types:
            if t is Ys_Elem_Type.HUO:
                huo_num += 1
            elif t is Ys_Elem_Type.LEI:
                lei_num += 1
            elif t is Ys_Elem_Type.SHUI:
                shui_num += 1
            elif t is Ys_Elem_Type.CAO:
                cao_num += 1

        elem_mastery = 115 # 突破加成
        if ming_zuo_num >= 4:
            # 只考虑对单的情形
            elem_mastery += 100

        bonus = 0
        if has_zhuan_wu:
            base_atk = 299 + 542

            elem_mastery += 265 + 32 * cao_num
            bonus += 0.1 * (3 - cao_num)

        if cao_num > 0:
            # 双草共鸣
            elem_mastery += (50 + 30 + 20)

        nxd = cls("纳西妲", elem_type=Ys_Elem_Type.CAO, ming_zuo_num=ming_zuo_num, 
                           e_level=e_level, q_level=q_level, base_atk=base_atk,
                           elem_mastery=elem_mastery, base_bonus=bonus,
                           )
        
        nxd.teammate_types = teammate_types
        
        nxd.extra_mie_jing_san_ye_bonus = 0
        if huo_num > 0:
            if huo_num > 2:
                huo_num = 2
        
            nxd.extra_mie_jing_san_ye_bonus += Na_Xi_Da_Ch.q_huo_bonus[q_level - 1][huo_num - 1]
        
        nxd.mie_jing_san_ye_interval = 2.5
        if lei_num > 0:
            if lei_num > 2:
                lei_num = 2

            nxd.mie_jing_san_ye_interval -= Na_Xi_Da_Ch.q_lei_intervals[q_level - 1][lei_num - 1]

        nxd.q_duration = 15
        if shui_num > 0:
            if shui_num > 2:
                shui_num = 2

            nxd.q_duration += Na_Xi_Da_Ch.q_shui_durations[q_level - 1][shui_num - 1]
        
        return nxd

    def get_real_crit_rate(self):
        return self.get_crit_rate() + min((self.get_elem_mastery() - 200) * 0.0003, 0.24)
    
    def get_a_damage(self, phrase, reaction: Ys_Reaction):
        # 6级普攻
        if phrase == 1:
            multiplier = 56.4 / 100
        elif phrase == 2:
            multiplier = 51.8/100
        elif phrase == 3: 
            multiplier = 64.2/100
        elif phrase == 4:
            multiplier = 81.8/100
        else:
            raise Exception("只有四段普攻")
        
        base_damage = self.get_atk() * multiplier
        return reaction.do_damage(base_damage, self.get_a_bonus())
    
    def get_e_damage(self, reaction: Ys_Reaction):
        multiplier = Na_Xi_Da_Ch.e_multiplier[self.e_level - 1]
        base_damage = self.get_atk() * multiplier
        bonus = self.get_e_bonus()
        return reaction.do_damage(base_damage, bonus)
    
    def get_mie_jing_san_ye_damage(self, reaction: Ys_Reaction):
        multiplier = Na_Xi_Da_Ch.mie_jing_san_ye_multiplier[self.e_level - 1]
        base_damage = self.get_atk() * multiplier[0] + self.get_elem_mastery() * multiplier[1]

        em_to_bonus =  min((self.get_elem_mastery() - 200) * 0.001, 0.8)
        bonus = self.extra_mie_jing_san_ye_bonus + self.get_e_bonus() + em_to_bonus

        return reaction.do_damage(base_damage, bonus)

    def set_as_main_carrier(self, max_elem_mastery_in_team):
        """
        作为前台站场主C使用

        * max_elem_mastery_in_team: 队伍里精通最大值
        """
        gu_you_tian_fu_1 = min(250, round(max_elem_mastery_in_team * 0.25))
        self.add_elem_mastery(gu_you_tian_fu_1)
        self.switch_to_foreground()

# 久岐忍实战精通可供纳西妲大招转换的部分
# 40：小草神专武
# 150: 4饰金
jiu_qi_ren_elem_mastery = 789 + 40 + 150
# 阿忍带圣显，叠三层
sheng_xian_elem_mastery = round(39270 * 0.002)

def na_xi_da_in_cao_xin_jiu_zhong() -> Na_Xi_Da_Ch:
    nxd = Na_Xi_Da_Ch.get_instance(teammate_types=[Ys_Elem_Type.LEI, Ys_Elem_Type.SHUI, Ys_Elem_Type.YAN])
    nxd.add_elem_mastery(sheng_xian_elem_mastery)
    # 有钟离在，纳西妲作为站场主C使用
    nxd.set_as_main_carrier(max_elem_mastery_in_team=jiu_qi_ren_elem_mastery)

    return nxd


def na_xi_da_in_cao_xing_jiu_yao() -> Na_Xi_Da_Ch:
    nxd = Na_Xi_Da_Ch.get_instance(teammate_types=[Ys_Elem_Type.LEI, Ys_Elem_Type.SHUI, Ys_Elem_Type.CAO])
    nxd.add_elem_mastery(sheng_xian_elem_mastery)
    # 草行久瑶队里作为站场主C
    nxd.set_as_main_carrier(max_elem_mastery_in_team=jiu_qi_ren_elem_mastery)
    nxd.add_all_bonus(0.15) # 瑶瑶一命
    nxd.add_atk_per(0.2) # 千岩

    return nxd


def calculate_score_callback(score_data: ShengYiWu_Score):
    monster = Monster()

    # nxd = na_xi_da_in_cao_xin_jiu_zhong()
    # monster.add_jian_kang(0.2) # 钟离

    nxd = na_xi_da_in_cao_xing_jiu_yao()

    if nxd.ming_zuo_num >= 2:
        monster.add_jian_fang(0.3)

    combine = score_data.syw_combine
    nxd.set_syw_combine(combine)

    name_count = nxd.get_syw_name_count()
    # print(name_count)
    for n in name_count:
        if name_count[n] < 2:  # 散件不计算套装效果
            continue

        if n == ShengYiWu.SHEN_LIN:
            nxd.add_all_bonus(0.15)
        elif n == ShengYiWu.SHI_JIN:
            nxd.add_elem_mastery(80)
            if name_count[n] >= 4:
                for t in nxd.teammate_types:
                    if t is Ys_Elem_Type.CAO:
                        nxd.add_atk_per(0.14)
                    else:
                        nxd.add_elem_mastery(50)
        elif n == ShengYiWu.JU_TUAN:
            nxd.add_all_bonus(0.2)
            if name_count[n] >= 4:
                nxd.add_all_bonus(0.25)
                if not nxd.is_in_foreground():
                    nxd.add_all_bonus(0.25)
        elif n == ShengYiWu.YUE_TUAN:
            nxd.add_elem_mastery(80)


    crit_rate = nxd.get_real_crit_rate()
    crit_rate = round(crit_rate, 3)
    if crit_rate < 0.64:
        return None
    
    no_reaction = Ys_No_Reaction(nxd, monster)

    damage = nxd.get_mie_jing_san_ye_damage(no_reaction)

    score_data.damage_to_score(damage, nxd.get_real_crit_rate(), nxd.get_crit_damage())
    score_data.custom_data = [ nxd.get_elem_mastery(), int(nxd.get_atk()), 
                              round(nxd.get_crit_rate(), 3), round(crit_rate, 3), round(nxd.get_crit_damage(), 3), 
                              round(nxd.get_energy_recharge(), 3)]
    return True


result_description = ["实战精通", "实战攻击力", "面板暴击率", "实战暴击率", "暴伤", "充能效率"]

def match_sha_callback(syw: ShengYiWu):
    return syw.elem_mastery == ShengYiWu.ELEM_MASTERY_MAIN

def match_bei_callback(syw: ShengYiWu):
    # or syw.atk_per == ShengYiWu.BONUS_MAX or syw.elem_mastery == ShengYiWu.ELEM_MASTERY_MAIN
    return syw.elem_type == Ys_Elem_Type.CAO

def match_tou_callback(syw: ShengYiWu):
    return syw.crit_rate == ShengYiWu.CRIT_RATE_MAIN or syw.crit_damage == ShengYiWu.CRIT_DAMAGE_MAIN

def get_debug_raw_score_list():
    # [(shen_lin, h, cc:0.078, cd:0.225, atkp:0.087, elem:37), 
    #  (shen_lin, y, cc:0.07, cd:0.272, hp:239, def:21), 
    #  (shen_lin, s, cc:0.128, cd:0.117, hp:538, re:0.045, elem:187), 
    #  (shui_xian, b, cc:0.101, cd:0.179, hp:209, elem:19, bonus:0.466), 
    #  (shen_lin, t, cc:0.066, cd:0.622, atkp:0.152, def:32, elem:47)]
    syw_combine = [
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_HUA,
                  crit_rate=0.078, crit_damage=0.225, atk_per=0.087, elem_mastery=37),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_YU,
                  crit_rate=0.07, crit_damage=0.272, hp=239, def_v=21),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_SHA, elem_mastery=ShengYiWu.ELEM_MASTERY_MAIN,
                  crit_rate=0.128, crit_damage=0.117, hp=538, energy_recharge=0.045),
        ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=Ys_Elem_Type.CAO,
                  crit_rate=0.101, crit_damage=0.179, hp=209, elem_mastery=19),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_TOU, crit_damage=ShengYiWu.CRIT_DAMAGE_MAIN,
                  crit_rate=0.066, atk_per=0.152, def_v=32, elem_mastery=47)
    ]
    return [ShengYiWu_Score(syw_combine)]

def get_raw_score_list(only_shen_lin=True):
    if enable_debug:
        return get_debug_raw_score_list()
    
    combine_desc_lst = []

    if not only_shen_lin:
        combine_desc_lst = Syw_Combine_Desc.any_2p2([ShengYiWu.SHEN_LIN,
                                                    ShengYiWu.SHI_JIN,
                                                    ShengYiWu.JU_TUAN,
                                                    ShengYiWu.YUE_TUAN])
        combine_desc_lst.append(Syw_Combine_Desc(set1_name=ShengYiWu.SHI_JIN, set1_num=4))
        combine_desc_lst.append(Syw_Combine_Desc(set1_name=ShengYiWu.JU_TUAN, set1_num=4))

    combine_desc_lst.append(Syw_Combine_Desc(set1_name=ShengYiWu.SHEN_LIN, set1_num=4))

    raw_score_list = find_syw_combine(combine_desc_lst,
                                      match_sha_callback=match_sha_callback,
                                      match_bei_callback=match_bei_callback,
                                      match_tou_callback=match_tou_callback)
    print(len(raw_score_list))
    return raw_score_list

def find_syw_for_na_xi_da_all():
    return calculate_score(get_raw_score_list(only_shen_lin=False),
                           calculate_score_callbak=calculate_score_callback,
                           result_txt_file="na_xi_da_syw_all.txt",
                           result_description=result_description
                           )

def find_syw_for_na_xi_da():
    return calculate_score(get_raw_score_list(only_shen_lin=True),
                           calculate_score_callbak=calculate_score_callback,
                           result_txt_file="na_xi_da_syw_shen_lin.txt",
                           result_description=result_description)

# Main body
if __name__ == '__main__':
    find_syw_for_na_xi_da()
