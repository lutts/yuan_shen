#!/user/bin/env python3 -tt
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

from ys_basic import Ys_Elem_Type, ys_expect_damage, ys_crit_damage
from monster import Monster
from characters import Ying_Bao_Ch, Jiu_Tiao_Sha_Luo_Ch, BanNiTe_Q_Action
from ys_syw import ShengYiWu, ShengYiWu_Score, calculate_score, set_score_threshold, Syw_Combine_Desc, find_syw_combine
from wan_ye import get_wan_ye_q_bonus, get_wan_ye_e_bonus


enable_debug = False

def get_damage_in_lei_jiu_wan_ban(jiu_tiao: Jiu_Tiao_Sha_Luo_Ch, monster: Monster, score_data: ShengYiWu_Score):
    # 影宝 e， 但暂时吃不到

    # 班尼特 q
    ban_ni_te = BanNiTe_Q_Action.create_instance()
    jiu_tiao.add_atk_per(ban_ni_te.atk_per_bonus)
    jiu_tiao.add_atk(ban_ni_te.atk_bonus)

    # 万叶 q
    monster.add_jian_kang(0.4)
    jiu_tiao.add_all_bonus(get_wan_ye_q_bonus())

    crit_rate = jiu_tiao.get_crit_rate()
    cd = jiu_tiao.get_crit_damage()

    # 九条 e-重击
    e_damage = monster.attacked(jiu_tiao.get_e_damage())
    e_expect = ys_expect_damage(e_damage, crit_rate, cd)
    e_crit = ys_crit_damage(e_damage, cd)
    # print("jiu_tiao:", str(jiu_tiao))
    # print("monster:", monster)
    # print(f"e_damage:{e_damage:.0f}, e_crit_damage:{e_crit:.0f}")

    # 重击本身有时候吃不到乌羽加成
    charged_a_damage = monster.attacked(jiu_tiao.get_charged_a_damage())
    charged_a_expect = ys_expect_damage(charged_a_damage, crit_rate, cd)
    charged_a_crit = ys_crit_damage(charged_a_damage, cd)
    # print(f"charged_a_damage:{charged_a_damage:.0f}, charged_a_crit:{charged_a_crit:.0f}")

    # 吃到自已本身的加成
    jiu_tiao.add_atk(jiu_tiao.get_atk_bonus())
    if jiu_tiao.ming_zuo_num >= 6:
        cd += 0.6

    wu_yu_damage = monster.attacked(jiu_tiao.get_wu_yu_damage())
    wu_yu_expect = ys_expect_damage(wu_yu_damage, crit_rate, cd)
    wu_yu_crit = ys_crit_damage(wu_yu_damage, cd)
    # print("jiu_tiao:", str(jiu_tiao))
    # print(f"wu_yu_damage:{wu_yu_damage:.0f}, wu_yu_crit:{wu_yu_crit:.0f}")

    # 影宝 e 加成
    jiu_tiao.add_q_bonus(Ying_Bao_Ch.get_bonus_to_q(jiu_tiao.q_energy))

    jue_yuan_bonus = min(jiu_tiao.get_energy_recharge() / 4 / 100, 0.75) # 四绝缘
    jiu_tiao.add_q_bonus(jue_yuan_bonus)

    q_damage = monster.attacked(jiu_tiao.get_q_damage())
    q_expect = ys_expect_damage(q_damage, crit_rate, cd)
    q_crit = ys_crit_damage(q_damage, cd)
    # print("jiu_tiao:", str(jiu_tiao))
    # print(f"q_damage:{q_damage:.0f}, q_crit:{q_crit:.0f}")

    score_data.expect_score = e_expect + charged_a_expect + wu_yu_expect + q_expect
    score_data.crit_score = e_crit + charged_a_crit + wu_yu_crit + q_crit

def calculate_score_callback(score_data: ShengYiWu_Score):
    jiu_tiao = Jiu_Tiao_Sha_Luo_Ch.create_instance(score_data.syw_combine)

    crit_rate = round(jiu_tiao.get_crit_rate(), 3)
    if crit_rate < 0.6:
        return None
    
    if jiu_tiao.get_energy_recharge() < 220:
        return None

    monster = Monster(character_level=jiu_tiao.ch_level)
    #monster.set_kang_xin(2.1)

    get_damage_in_lei_jiu_wan_ban(jiu_tiao, monster, score_data)

    score_data.custom_data = [int(jiu_tiao.panel_atk), 
                              crit_rate, round(jiu_tiao.get_crit_damage(), 3),
                              jiu_tiao.get_energy_recharge()]

    return True
    

result_description = ["总评分", "期望伤害评分", "暴击伤害评分", "面板攻击力", "暴击率", "暴击伤害", "充能效率"]


def match_sha_callback(syw: ShengYiWu):
    return syw.energy_recharge == ShengYiWu.ENERGY_RECHARGE_MAX 


def match_bei_callback(syw: ShengYiWu):
    return syw.elem_type == Ys_Elem_Type.LEI


def match_tou_callback(syw: ShengYiWu):
    return syw.crit_rate == ShengYiWu.CRIT_RATE_MAIN or syw.crit_damage == ShengYiWu.CRIT_DAMAGE_MAIN

def get_debug_raw_score_list():
    # [(jue_yuan, h, cc:0.066, cd:0.124, re:0.181, elem:21),
    #  (jue_yuan, y, cc:0.027, re:0.285, atkp:0.087, defp:0.073),
    #  (jue_yuan, s, cd:0.194, hp:508, re:0.518, defp:0.117, elem:19),
    #  (jue_yuan, b, cd:0.179, atk:19, defp:0.073, elem:91, bonus:0.466),
    #  (shi_jin, t, cc:0.311, cd:0.155, re:0.227, atkp:0.058, defp:0.058)]
    syw_combine = [
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_HUA, 
                  crit_rate=0.066, crit_damage=0.124, energy_recharge=0.181, elem_mastery=21),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_YU,
                  crit_rate=0.027, energy_recharge=0.285, atk_per=0.087, def_per=0.073),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_SHA, energy_recharge=ShengYiWu.ENERGY_RECHARGE_MAX,
                  crit_damage=0.194, hp=508, def_per=0.117, elem_mastery=19),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=Ys_Elem_Type.LEI,
                  crit_damage=0.179, atk=19, def_per=0.073, elem_mastery=91),
        ShengYiWu(ShengYiWu.SHI_JIN, ShengYiWu.PART_TOU, crit_rate=ShengYiWu.CRIT_RATE_MAIN,
                  crit_damage=0.155, energy_recharge=0.227, atk_per=0.058, def_per=0.058)
    ]

    return [ShengYiWu_Score(syw_combine)]

def find_syw_for_jiu_tiao_sha_luo():
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
                           result_txt_file="jiu_tiao_sha_luo_syw.txt",
                           result_description=result_description)

# Main body
if __name__ == '__main__':
    set_score_threshold(1.7)
    find_syw_for_jiu_tiao_sha_luo()
    