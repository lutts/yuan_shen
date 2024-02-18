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
from ys_weapon import Wu_Qie_Zhi_Hui_Guang
from character import Character
from monster import Monster
from wan_ye import get_wan_ye_q_bonus, get_wan_ye_e_bonus
from ys_syw import ShengYiWu, ShengYiWu_Score, calculate_score, Syw_Combine_Desc, find_syw_combine

enable_debug = False

class Ling_Hua_Ch(Character, name="神里绫华", elem_type=Ys_Elem_Type.BING, ming_zuo_num=4, a_level=10, e_level=10, q_level=13, q_energy=80):
    MIN_LEVEL = 8

    a_multiplier = [
        (78.2/100, 83.2/100, 107.0/100, 38.7*3/100, 133.6/100, 3*94.2/100), # 8
        (84.0/100, 89.4/100, 115.1/100, 41.6*3/100, 143.6/100, 3*101.3/100), # 9
        (90.4/100, 96.2/100, 123.8/100, 44.8*3/100, 154.6/100, 3*109.0/100), # 10
    ]

    e_multiplier = [
        383/100, 407/100, 431/100, 454/100, 478/100, 508/100
    ]

    q_qie_ge_multiplier = [
        180/100, 191/100, 202/100, 213/100, 225/100, 239/100
    ]

    q_zhan_fang_multiplier = [
        270/100, 286/100, 303/100, 320/100, 337/100, 358/100
    ]
    def __init__(self, weapon: Ys_Weapon, syw_combine: list[ShengYiWu]):
        super().__init__(base_atk=342, weapon=weapon, crit_damage=0.884)

        if self.a_level < Ling_Hua_Ch.MIN_LEVEL:
            self.a_level = Ling_Hua_Ch.MIN_LEVEL

        if self.e_level < Ling_Hua_Ch.MIN_LEVEL:
            self.e_level = Ling_Hua_Ch.MIN_LEVEL

        if self.q_level < Ling_Hua_Ch.MIN_LEVEL:
            self.q_level = Ling_Hua_Ch.MIN_LEVEL

        self.set_syw_combine(syw_combine)
        self.add_all_bonus(0.15) # 冰套2件套效果

        weapon.apply_combat_attributes(self)

        self.panel_bonus = self.get_q_bonus()
        self.panel_crit_rate = self.get_crit_rate()
        self.panel_atk = self.get_atk()

        # e 后普攻和重击伤害加成
        self.add_a_bonus(0.3)

        # 霰步结束冰伤加成
        self.add_all_bonus(0.18)

        # 双冰共鸣
        self.add_crit_rate(0.15)
        # 冰套四件套一半效果，不考虑没法上冰的雷音权限之类的怪
        self.add_crit_rate(0.2) 

        weapon.apply_passive(self)

    def get_normal_a_damage(self, phrase, monster: Monster):
        multiplier = Ling_Hua_Ch.a_multiplier[self.a_level - Ling_Hua_Ch.MIN_LEVEL][phrase - 1]
        damage = self.get_atk() * multiplier * (1 + self.get_normal_a_bonus())
        return monster.attacked(damage)

    def get_charged_a_damage(self, monster: Monster):
        multiplier = Ling_Hua_Ch.a_multiplier[self.a_level - Ling_Hua_Ch.MIN_LEVEL][-1]
        damage = self.get_atk() * multiplier * (1 + self.get_charged_a_bonus())
        return monster.attacked(damage)
    
    def get_e_damage(self, monster: Monster):
        multiplier = Ling_Hua_Ch.e_multiplier[self.e_level - Ling_Hua_Ch.MIN_LEVEL]
        damage = self.get_atk() * multiplier * (1 + self.get_e_bonus())
        return monster.attacked(damage)

    def get_q_qie_ge_damage(self, monster: Monster):
        multiplier = Ling_Hua_Ch.q_qie_ge_multiplier[self.q_level - Ling_Hua_Ch.MIN_LEVEL]
        damage = self.get_atk() * multiplier * (1 + self.get_q_bonus())
        return monster.attacked(damage)
    
    def get_q_zhan_fang_damage(self, monster: Monster):
        multiplier = Ling_Hua_Ch.q_zhan_fang_multiplier[self.q_level - Ling_Hua_Ch.MIN_LEVEL]
        damage = self.get_atk() * multiplier * (1 + self.get_q_bonus())
        return monster.attacked(damage)


def create_lin_hua(syw_combine: list[ShengYiWu]):
    weapon = Wu_Qie_Zhi_Hui_Guang(base_atk=674, crit_damage=0.441)
    return Ling_Hua_Ch(weapon, syw_combine)

def print_damages(ling_hua_init: Ling_Hua_Ch):
    import copy
    ling_hua = copy.deepcopy(ling_hua_init)

    monster = Monster(level=93)
    #monster.set_kang_xin(3.1)

    cd = ling_hua.get_crit_damage()

    # e_damage = ling_hua.get_e_damage(monster)
    # e_crit = ys_crit_damage(e_damage, cd)
    # print(f"e伤害: {e_damage:.0f}, 暴击: {e_crit:.0f}")

    # q_qie_ge_damage = ling_hua.get_q_qie_ge_damage()   
    # qie_ge_real = monster.attacked(q_qie_ge_damage)
    # qie_ge_real_crit = ys_crit_damage(qie_ge_real, cd)
    # print(f"切害伤害: {qie_ge_real:.0f}, 暴击:{qie_ge_real_crit:.0f}")

    # monster.add_jian_fang(0.3)

    # q_qie_ge_damage = ling_hua.get_q_qie_ge_damage()   
    # qie_ge_real = monster.attacked(q_qie_ge_damage)
    # qie_ge_real_crit = ys_crit_damage(qie_ge_real, cd)
    # print(f"减防后，切害伤害: {qie_ge_real:.0f}, 暴击:{qie_ge_real_crit:.0f}")

    # monster.sub_jian_fang(0.3)

    # print("叠buff前: ", ling_hua)
    # 猫猫 q，宗室四件套
    ling_hua.add_atk_per(0.2)

    # 万叶 q
    wan_ye_bonus = get_wan_ye_q_bonus()
    ling_hua.add_all_bonus(wan_ye_bonus)
    monster.add_jian_kang(0.4)

    # 莫娜 e, 千岩四件套，讨龙
    ling_hua.add_atk_per(0.2 + 0.48)
    # TODO: 莫娜泡影
    # ling_hua.add_all_bonus(0.58)
    # print("有泡影星异")

    print("buff叠满: ", ling_hua)

    e_damage = ling_hua.get_e_damage(monster)
    e_crit = ys_crit_damage(e_damage, cd)
    print(f"e伤害: {e_damage:.0f}, 暴击: {e_crit:.0f}")

    q_qie_ge_damage = ling_hua.get_q_qie_ge_damage(monster)
    qie_ge_crit = ys_crit_damage(q_qie_ge_damage, cd)
    print(f"切割伤害: {q_qie_ge_damage:.0f}, 暴击:{qie_ge_crit:.0f}")

    monster.add_jian_fang(0.3)

    e_damage = ling_hua.get_e_damage(monster)
    e_crit = ys_crit_damage(e_damage, cd)
    print(f"(四命减防)e伤害: {e_damage:.0f}, 暴击: {e_crit:.0f}")

    q_qie_ge_damage = ling_hua.get_q_qie_ge_damage(monster)
    qie_ge_crit = ys_crit_damage(q_qie_ge_damage, cd)
    print(f"(四命减防)切割伤害: {q_qie_ge_damage:.0f}, 暴击:{qie_ge_crit:.0f}")

    q_zhan_fang_damage = ling_hua.get_q_zhan_fang_damage(monster)
    zhan_fang_crit = ys_crit_damage(q_zhan_fang_damage, cd)
    print(f"(四命减防)绽放伤害: {q_zhan_fang_damage:.0f}, 暴击: {zhan_fang_crit:.0f}")

    a1_damage = ling_hua.get_normal_a_damage(1, monster)
    a1_crit = ys_crit_damage(a1_damage, cd)
    print(f"(满buff)普攻一段伤害: {a1_damage:.0f} 暴击: {a1_crit:.0f}")

    z_damage = ling_hua.get_charged_a_damage(monster) / 3
    z_crit = ys_crit_damage(z_damage, cd)
    print(f"(满buff)重击伤害: {z_damage:.0f} 暴击: {z_crit:.0f}")

    print("-----如果大招期间风套效果消失,则--------")
    monster.sub_jian_kang(0.4)

    q_qie_ge_damage = ling_hua.get_q_qie_ge_damage(monster)
    qie_ge_real_crit = ys_crit_damage(q_qie_ge_damage, cd)
    print(f"(无风套)切割伤害: {q_qie_ge_damage:.0f}, 暴击:{qie_ge_real_crit:.0f}")

    q_zhan_fang_damage = ling_hua.get_q_zhan_fang_damage(monster)
    zhan_fang_real_crit = ys_crit_damage(q_zhan_fang_damage, cd)
    print(f"(无风套)绽放伤害: {q_zhan_fang_damage:.0f}, 暴击: {zhan_fang_real_crit:.0f}")

    monster.add_jian_kang(0.4)

    print("-------有风套减抗,无万叶增伤,有四命减防时: e, az伤害-----")

    ling_hua.sub_all_bonus(wan_ye_bonus)

    e_damage = ling_hua.get_e_damage(monster)
    e_crit = ys_crit_damage(e_damage, cd)
    print(f"e伤害: {e_damage:.0f}, 暴击: {e_crit:.0f}")

    a1_damage = ling_hua.get_normal_a_damage(1, monster)
    a1_crit = ys_crit_damage(a1_damage, cd)
    print(f"普攻一段伤害: {a1_damage:.0f} 暴击: {a1_crit:.0f}")

    z_damage = ling_hua.get_charged_a_damage(monster) / 3
    z_crit = ys_crit_damage(z_damage, cd)
    print(f"重击伤害: {z_damage:.0f} 暴击: {z_crit:.0f}")

    print("-------无风套减抗,无万叶增伤,有四命减防时,e, az伤害-------")
    monster.sub_jian_kang(0.4)
    

    e_damage = ling_hua.get_e_damage(monster)
    e_crit = ys_crit_damage(e_damage, cd)
    print(f"e伤害: {e_damage:.0f}, 暴击: {e_crit:.0f}")

    a1_damage = ling_hua.get_normal_a_damage(1, monster)
    a1_crit = ys_crit_damage(a1_damage, cd)
    print(f"普攻一段伤害: {a1_damage:.0f} 暴击: {a1_crit:.0f}")

    z_damage = ling_hua.get_charged_a_damage(monster) / 3
    z_crit = ys_crit_damage(z_damage, cd)
    print(f"重击伤害: {z_damage:.0f} 暴击: {z_crit:.0f}")

    print("----------宗室和千岩效果也消失, 四命减防还在--------")
    ling_hua.sub_atk_per(0.2 + 0.2)

    e_damage = ling_hua.get_e_damage(monster)
    e_crit = ys_crit_damage(e_damage, cd)
    print(f"e伤害: {e_damage:.0f}, 暴击: {e_crit:.0f}")

    a1_damage = ling_hua.get_normal_a_damage(1, monster)
    a1_crit = ys_crit_damage(a1_damage, cd)
    print(f"普攻一段伤害: {a1_damage:.0f} 暴击: {a1_crit:.0f}")

    z_damage = ling_hua.get_charged_a_damage(monster) / 3
    z_crit = ys_crit_damage(z_damage, cd)
    print(f"重击伤害: {z_damage:.0f} 暴击: {z_crit:.0f}")
    

    print("---------无风套减抗, 无万叶增伤,无四命减防时, e az伤害---------")
    monster.sub_jian_fang(0.3)
    ling_hua.sub_atk_per(0.48)
    ling_hua.sub_all_bonus(0.12)
    print(monster)
    print(ling_hua)
    
    e_damage = ling_hua.get_e_damage(monster)
    e_crit = ys_crit_damage(e_damage, cd)
    print(f"e伤害: {e_damage:.0f}, 暴击: {e_crit:.0f}")

    a1_damage = ling_hua.get_normal_a_damage(1, monster)
    a1_crit = ys_crit_damage(a1_damage, cd)
    print(f"普攻一段伤害: {a1_damage:.0f} 暴击: {a1_crit:.0f}")

    z_damage = ling_hua.get_charged_a_damage(monster) / 3
    z_crit = ys_crit_damage(z_damage, cd)
    print(f"重击伤害: {z_damage:.0f} 暴击: {z_crit:.0f}")


def get_damage_for_shen_mo_wan_mao(ling_hua: Ling_Hua_Ch):
    if enable_debug:
        print_damages(ling_hua)

    monster = Monster()
    # monster.set_kang_xin(3.1)

    # 猫猫 q，宗室四件套
    ling_hua.add_atk_per(0.2)

    # 万叶 q，在猫猫 6 命时，二命万叶 q 和 e 的加成是一样的，如果猫猫没满命，可能用 e_bonus 更合理些
    ling_hua.add_all_bonus(get_wan_ye_q_bonus())
    monster.add_jian_kang(0.4)

    # 莫娜 e, 千岩四件套，讨龙
    ling_hua.add_atk_per(0.2 + 0.48)
    # TODO: 莫娜泡影
    ling_hua.add_all_bonus(0.58)

    all_damage = 0

    # 绫华 遁地 a qe az az az 切猫猫ee，切绫华吃球 eaz 
    # 充能循环有保障的情况下，此时所有角色大招的充能就又都好了，开始下一轮循环
    # 不同的武器 eq 顺序可能不同，但 e 不是主要伤害，总体差别不大
    
    all_damage += ling_hua.get_normal_a_damage(1, monster)

    q_qie_ge_damage_no_jian_fang = ling_hua.get_q_qie_ge_damage(monster)
    all_damage += q_qie_ge_damage_no_jian_fang

    if ling_hua.ming_zuo_num >= 4:
        monster.add_jian_fang(0.3)
        q_qie_ge_damage_jian_fang = ling_hua.get_q_qie_ge_damage(monster)
    else:
        q_qie_ge_damage_jian_fang = q_qie_ge_damage_no_jian_fang

    all_damage += q_qie_ge_damage_jian_fang * 12

    # ea
    all_damage += ling_hua.get_e_damage(monster)
    all_damage += ling_hua.get_normal_a_damage(1, monster)

    # 第14段：莫娜星异效果消失
    ling_hua.sub_all_bonus(0.58)
    q_qie_ge_no_xin_yi = ling_hua.get_q_qie_ge_damage(monster)
    q_qie_ge_no_xin_yi *= 3
    all_damage += q_qie_ge_no_xin_yi

    # 第17~19段：风套减抗消失
    monster.sub_jian_kang(0.4)
    q_qie_ge_no_jian_kang = ling_hua.get_q_qie_ge_damage(monster)
    all_damage += q_qie_ge_no_jian_kang * 3

    # 绽放:风套减抗不在
    q_zhan_fang_damage = ling_hua.get_q_zhan_fang_damage(monster)
    all_damage += q_zhan_fang_damage

    # 下面单独计算 az 的伤害
    # 第一个重击:莫娜效果消失,无万叶增伤,但风套减抗还在

    monster.add_jian_kang(0.4)
    # 万叶增伤消失
    ling_hua.sub_all_bonus(get_wan_ye_q_bonus())
    
    all_damage += ling_hua.get_charged_a_damage(monster)
    
    # 第二个 az 时风套减抗一般都还在
    all_damage += ling_hua.get_normal_a_damage(1, monster)
    all_damage += ling_hua.get_charged_a_damage(monster)

    # 风套效果消失
    monster.sub_jian_kang(0.4)
    # 第三个 a 千岩宗室还在
    all_damage += ling_hua.get_normal_a_damage(1, monster)
    
    # 第三次重击千岩宗室效果不在了
    ling_hua.sub_atk_per(0.2 + 0.2)
    all_damage += ling_hua.get_charged_a_damage(monster)

    # 讨龙效果消失
    ling_hua.sub_atk_per(0.48)
    # 雾切掉一层
    ling_hua.sub_all_bonus(0.12)
    # 四命减防消失
    monster.sub_jian_fang(0.3)
    all_damage += ling_hua.get_e_damage(monster)
    all_damage += ling_hua.get_normal_a_damage(1, monster)
    all_damage += ling_hua.get_charged_a_damage(monster)

    return (all_damage, q_qie_ge_damage_jian_fang)


def calculate_score_callback(score_data: ShengYiWu_Score):
    ling_hua = create_lin_hua(score_data.syw_combine)

    crit_rate = round(ling_hua.panel_crit_rate, 3)
    if crit_rate < 0.4 or crit_rate > 0.5:
        return None
    
    energy_recharge = ling_hua.get_energy_recharge()
    if energy_recharge <= 116.5:
        return None
    
    damage, q_qie_ge_damage_jian_fang = get_damage_for_shen_mo_wan_mao(ling_hua)

    score_data.damage_to_score(damage, ling_hua.get_crit_rate(), ling_hua.get_crit_damage())
    q_qie_ge_damage_jian_fang = ys_crit_damage(q_qie_ge_damage_jian_fang, ling_hua.get_crit_damage())
    score_data.extra_score = q_qie_ge_damage_jian_fang
    score_data.custom_data = [int(ling_hua.panel_atk), q_qie_ge_damage_jian_fang,
                              round(crit_rate, 3), round(ling_hua.get_crit_damage(), 3), 
                              energy_recharge]

    return True


result_description = ["面板攻击力", "大招一转最大伤害" "暴击率", "暴击伤害", "充能效率"]

def match_sha_callback(syw: ShengYiWu):
    return syw.atk_per == ShengYiWu.BONUS_MAX


def match_bei_callback(syw: ShengYiWu):
    return syw.atk_per == ShengYiWu.BONUS_MAX or syw.elem_type == Ys_Elem_Type.BING

def match_tou_callback(syw: ShengYiWu):
    return syw.crit_rate == ShengYiWu.CRIT_RATE_MAIN or syw.crit_damage == ShengYiWu.CRIT_DAMAGE_MAIN

def get_debug_raw_score_list():
    syw_combine_str_lst = ["(bing_tao, h, cc:0.089, cd:0.132, atkp:0.134, elem:16)",
                           "(bing_tao, y, cc:0.066, cd:0.21, hp:299, atkp:0.099)",
                           "(bing_tao, s, cc:0.097, cd:0.202, hp:209, atkp:0.466, def:42)",
                           "(bing_tao, b, cd:0.21, hpp:0.058, re:0.155, atkp:0.047, bonus:0.466)",
                           "(zong_shi, t, cc:0.148, cd:0.622, re:0.058, atkp:0.058, defp:0.109)"]
    
    return [ShengYiWu_Score(ShengYiWu.string_to_syw_combine(syw_combine_str_lst))]

def get_debug_raw_score_list_2():
    syw_combine = [
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_HUA),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_YU,
                  crit_rate=0.062, crit_damage=0.132, atk_per=0.093, energy_recharge=0.162),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_SHA),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_BEI),
        ShengYiWu(ShengYiWu.BING_TAO, ShengYiWu.PART_TOU, crit_rate=ShengYiWu.CRIT_RATE_MAIN,
                  def_per=0.073, energy_recharge=0.045, hp=478, crit_damage=0.264),
    ]

    return [ShengYiWu_Score(syw_combine)]

def find_syw_for_ling_hua():
    if enable_debug:
        raw_score_list = get_debug_raw_score_list()
    else:
        raw_score_list = find_syw_combine([Syw_Combine_Desc(set1_name=ShengYiWu.BING_TAO, set1_num=4)],
                                        match_sha_callback=match_sha_callback,
                                        match_bei_callback=match_bei_callback,
                                        match_tou_callback=match_tou_callback)
        print(len(raw_score_list))

    return calculate_score(raw_score_list,
                           calculate_score_callbak=calculate_score_callback,
                           result_txt_file="ling_hua_syw.txt",
                           result_description=result_description)

# Main body
if __name__ == '__main__':
    find_syw_for_ling_hua()