#!/user/bin/env python3 -tt
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

import sys
import os
import logging
import itertools

from ys_basic import Ys_Elem_Type, Ys_Weapon, ys_crit_damage
from monster import Monster
from character import Character
from ys_weapon import Ti_Cao_Zhi_Dao_Guang
from ys_syw import ShengYiWu, ShengYiWu_Score, calculate_score, Syw_Combine_Desc, find_syw_combine
from ye_lan import YeLan_Q_Bonus_Action
from action import Action, ActionPlan, ActionPlanAttributes
from ban_ni_te import BanNiTe_Q_Action
from wan_ye import get_wan_ye_q_bonus
from characters import Ying_Bao_Ch, Jiu_Tiao_Sha_Luo_Ch

enable_debug = False
use_5az = False
ye_lan_ming_zuo_num = 1

def create_ying_bao(syw_combine: list[ShengYiWu]) -> Ying_Bao_Ch:
    weapon = Ti_Cao_Zhi_Dao_Guang(base_atk=608, energy_recharge=0.551)
    ying_bao = Ying_Bao_Ch(weapon)
    ying_bao.set_syw_combine(syw_combine)
    ying_bao.do_post_set_syw_combine()

    crit_rate = round(ying_bao.get_crit_rate(), 3)
    if crit_rate < 0.65:
        return None
    
    if ying_bao.panel_energy_recharge < 260:
        return None
    
    return ying_bao

def add_action_for_5az(plan: ActionPlan, ying_bao: Ying_Bao_Ch, time_shift=0):
    """
    5a重手法

    time_shift: 时间戳偏移，这里的时间戳是从 12.104 开始的，如果实际流程时间不一样，进行偏移即可

    注：没有夜兰、芙芙这样会随时间改变增伤的辅助时，时间戳是无效的
    """
    plan.add_action_obj(ying_bao.get_q_action(), 12.104 + time_shift, 12.104 + time_shift)

    action_sequence = [
        (12.937, ying_bao.get_a_action(1)),
        (13.554, ying_bao.get_charged_a_action(sub_phrase=1)),
        (13.704, ying_bao.get_charged_a_action(sub_phrase=2)),

        (14.404, ying_bao.get_a_action(1)),
        (15.038, ying_bao.get_charged_a_action(sub_phrase=1)),
        (15.221, ying_bao.get_charged_a_action(sub_phrase=2)),

        (15.887, ying_bao.get_a_action(1)),
        (16.554, ying_bao.get_charged_a_action(sub_phrase=1)),
        (16.637, ying_bao.get_charged_a_action(sub_phrase=2)),

        (17.321, ying_bao.get_a_action(1)),
        (17.953, ying_bao.get_charged_a_action(sub_phrase=1)),
        (18.071, ying_bao.get_charged_a_action(sub_phrase=2)),

        (18.771, ying_bao.get_a_action(1)),
        (19.354, ying_bao.get_charged_a_action(sub_phrase=1)),
        (19.554, ying_bao.get_charged_a_action(sub_phrase=2))
    ]

    for t, action in action_sequence:
        plan.add_action_obj(action, t + time_shift, t + time_shift)

def add_action_for_only_normal_a(plan: ActionPlan, ying_bao: Ying_Bao_Ch, time_shift=0):
    """
    全程普攻，不使用重击

    time_shift: 时间戳偏移，这里的时间戳是从 11.686 开始的，如果实际流程时间不一样，进行偏移即可

    注：没有夜兰、芙芙这样会随时间改变增伤的辅助时，时间戳是无效的
    """
    plan.add_action_obj(ying_bao.get_q_action(), 11.686 + time_shift, 11.686 + time_shift)

    action_sequence = [
        (12.271, ying_bao.get_a_action(1)),
        (12.704, ying_bao.get_a_action(2)),
        (12.954, ying_bao.get_a_action(3)),
        (13.487, ying_bao.get_a_action(phrase=4, sub_phrase=1)),
        (13.741, ying_bao.get_a_action(phrase=4, sub_phrase=2)),
        (14.454, ying_bao.get_a_action(5)),

        (15.187, ying_bao.get_a_action(1)),
        (15.671, ying_bao.get_a_action(2)),
        (16.02, ying_bao.get_a_action(3)),
        (16.437, ying_bao.get_a_action(phrase=4, sub_phrase=1)),
        (16.737, ying_bao.get_a_action(phrase=4, sub_phrase=2)),
        (17.471, ying_bao.get_a_action(5)),

        (18.171, ying_bao.get_a_action(1)),
        (18.537, ying_bao.get_a_action(2)),
        (18.904, ying_bao.get_a_action(3)),
        (19.403, ying_bao.get_a_action(phrase=4, sub_phrase=1)),
        (19.604, ying_bao.get_a_action(phrase=4, sub_phrase=2))
    ]

    for t, action in action_sequence:
        plan.add_action_obj(action, t + time_shift, t + time_shift)

def create_plan_for_lei_ye_wan_ban(ying_bao: Ying_Bao_Ch, monster: Monster) -> ActionPlan:
    # 假设万叶的风套和增伤一直在
    monster.add_jian_kang(0.4)
    ying_bao.add_all_bonus(get_wan_ye_q_bonus())

    plan = ActionPlan(None, monster=monster)

    if ye_lan_ming_zuo_num == 6:
        plan.add_action("夜兰Q增伤开始", YeLan_Q_Bonus_Action, 3.567, 3.567)
        plan.add_action_obj(BanNiTe_Q_Action.create_instance(), 11.319 - 1.883, 11.319 - 1.883)

        # 和满命夜兰配队不能采用az打法，因为时间只够打2次az，虽然2次az比5a伤害还高些，但只能触发两次回能，5a能触发3次
        # 和满命夜兰配队本来就因为影宝砍不满导致充能压力大，所以5a是最理想的

        action_sequence = [
            (11.319, ying_bao.get_q_action()),

            (11.752, ying_bao.get_a_action(1)),
            (12.053, ying_bao.get_a_action(2)),
            (12.453, ying_bao.get_a_action(3)),
            (13.137, ying_bao.get_a_action(phrase=4, sub_phrase=1)),
            (13.137, ying_bao.get_a_action(phrase=4, sub_phrase=2)),
            (13.871, ying_bao.get_a_action(5))
        ]

        for t, action in action_sequence:
            plan.add_action_obj(action, t, t)
    else:
        if use_5az:
            plan.add_action("夜兰Q增伤开始", YeLan_Q_Bonus_Action, 4.369, 4.369)
            plan.add_action_obj(BanNiTe_Q_Action.create_instance(), 12.104 - 1.883, 12.104 - 1.883)

            add_action_for_5az(plan, ying_bao)
        else: # 全程普攻
            plan.add_action("夜兰Q增伤开始", YeLan_Q_Bonus_Action, 3.884, 3.884)
            plan.add_action_obj(BanNiTe_Q_Action.create_instance(), 11.686 - 1.883, 11.686 - 1.883)

            add_action_for_only_normal_a(plan, ying_bao)

    return plan

def create_plan_for_lei_jiu_wan_ban(ying_bao: Ying_Bao_Ch, monster: Monster):
    # 假设万叶的风套和增伤一直在
    monster.add_jian_kang(0.4)
    ying_bao.add_all_bonus(get_wan_ye_q_bonus())

    jiu_tiao = Jiu_Tiao_Sha_Luo_Ch.create_instance([])
    ying_bao.add_atk(jiu_tiao.get_atk_bonus())
    ying_bao.add_crit_damage(jiu_tiao.get_crit_damage_bonus())

    plan = ActionPlan(None, monster=monster)
    plan.add_action_obj(BanNiTe_Q_Action.create_instance(), 0, 0)

    if use_5az:
        add_action_for_5az(plan, ying_bao)
    else:
        add_action_for_only_normal_a(plan, ying_bao)

    return plan

def create_plan_for_lei_xia_xiang_ban(ying_bao: Ying_Bao_Ch, monster: Monster):
    # 双火
    ying_bao.add_atk_per(0.25)

    # 夏沃蕾
    monster.add_jian_kang(0.4)
    ying_bao.add_atk_per(0.4)
    # TODO：没满命，满命数据待补充

    plan = ActionPlan(None, monster=monster)
    plan.add_action_obj(BanNiTe_Q_Action.create_instance(), 0, 0)

    if use_5az:
        add_action_for_5az(plan, ying_bao)
    else:
        add_action_for_only_normal_a(plan, ying_bao)

    return plan


def create_plan_for_lei_guo(ying_bao: Ying_Bao_Ch, monster: Monster):
    # 双火
    ying_bao.add_atk_per(0.25)

    plan = ActionPlan(None, monster=monster)
    plan.add_action_obj(BanNiTe_Q_Action.create_instance(), 0, 0)

    if use_5az:
        add_action_for_5az(plan, ying_bao)
    else:
        add_action_for_only_normal_a(plan, ying_bao)

    return plan

def create_plan_for_ying_ye_fu_qin(ying_bao: Ying_Bao_Ch, monster: Monster):
    # 琴风套减抗
    monster.add_jian_kang(0.4)

    # 二命及以上的芙芙影宝基本能吃到满增伤
    # TODO: 芙芙0~1命目前程序还无法模拟
    ying_bao.add_all_bonus(400 * 0.0025)

    plan = ActionPlan(None, monster=monster)

    plan.add_action("夜兰Q增伤开始", YeLan_Q_Bonus_Action, 0, 0)

    if use_5az:
        add_action_for_5az(plan, ying_bao, time_shift=7.1 - 12.104)
    else: # 全程普攻
        add_action_for_only_normal_a(plan, ying_bao, time_shift=7.1 - 11.686)

    return plan

def calculate_score_callback(score_data: ShengYiWu_Score):
    ying_bao = create_ying_bao(score_data.syw_combine)
    if not ying_bao:
        return None
    
    monster = Monster()
    #monster.set_kang_xin(3.7)
    if ying_bao.ming_zuo_num >= 2:
        monster.set_ignore_defence(0.6)
    
    # plan = create_plan_for_lei_ye_wan_ban(ying_bao, monster)
    # plan = create_plan_for_ying_ye_fu_qin(ying_bao, monster)
    plan = create_plan_for_lei_jiu_wan_ban(ying_bao, monster)
    # plan = create_plan_for_lei_guo(ying_bao, monster)
    # plan = create_plan_for_lei_xia_xiang_ban(ying_bao, monster)

    plan.run()

    score_data.damage_to_score(plan.total_damage, ying_bao.get_crit_rate(), ying_bao.get_crit_damage())
    score_data.extra_score = ying_bao.meng_xiang_yi_dao_damage
    score_data.custom_data = [ying_bao.meng_xiang_yi_dao_damage, int(plan.get_atk(ying_bao)), int(ying_bao.panel_atk),
                              round(ying_bao.panel_bonus, 3), 
                              round(ying_bao.get_crit_rate(), 3), round(ying_bao.panel_crit_damage, 3), 
                              round(ying_bao.panel_energy_recharge, 1)]
    
    return True


result_description = ["梦想一刀暴击伤害", "实战攻击力", "面板攻击力", "实战最大伤害加成", "暴击率", "暴击伤害", "面板充能效率"]

def match_sha_callback(syw: ShengYiWu):
    return syw.energy_recharge == ShengYiWu.ENERGY_RECHARGE_MAX


def match_bei_callback(syw: ShengYiWu):
    return syw.atk_per == ShengYiWu.BONUS_MAX or syw.elem_type == Ys_Elem_Type.LEI

def match_tou_callback(syw: ShengYiWu):
    return syw.crit_rate == ShengYiWu.CRIT_RATE_MAIN or syw.crit_damage == ShengYiWu.CRIT_DAMAGE_MAIN

def get_debug_raw_score_list():
    # [(jue_yuan, h, cc:0.062, cd:0.21, atkp:0.041, elem:54), 
    # (jue_yuan, y, cc:0.039, cd:0.35, hpp:0.041, def:39), 
    # (lie_ren, s, cc:0.14, cd:0.148, re:0.518, atk:14, def:37),
    # (jue_yuan, b, cc:0.066, cd:0.218, re:0.058, atkp:0.466, def:39), 
    # (jue_yuan, t, cc:0.311, cd:0.256, hp:209, re:0.104, atkp:0.047)]
    syw_combine = [
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_HUA,
                  crit_rate=0.062, crit_damage=0.21, atk_per=0.041, elem_mastery=54),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_YU,
                  crit_rate=0.039, crit_damage=0.35, hp_percent=0.041, def_v=39),
        ShengYiWu(ShengYiWu.LIE_REN, ShengYiWu.PART_SHA, energy_recharge=ShengYiWu.ENERGY_RECHARGE_MAX,
                  crit_rate=0.14, crit_damage=0.148, atk=14, def_v=37),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_BEI, atk_per=ShengYiWu.BONUS_MAX,
                  crit_rate=0.066, crit_damage=0.218, energy_recharge=0.058, def_v=39),
        ShengYiWu(ShengYiWu.JUE_YUAN, ShengYiWu.PART_TOU, crit_rate=ShengYiWu.CRIT_RATE_MAIN,
                  crit_damage=0.256, hp=209, energy_recharge=0.104, atk_per=0.047)
    ]
    return [ShengYiWu_Score(syw_combine)]


def find_syw_for_lei_shen():
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
                           result_txt_file="lei_shen_syw.txt",
                           result_description=result_description)

# Main body
if __name__ == '__main__':
    find_syw_for_lei_shen()