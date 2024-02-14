#!/user/bin/env python3 -tt
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

import logging
import typing
import copy
import itertools
import random

from ys_syw import ShengYiWu_Score
from health_point import HealthPoint
from character import Character
from fu_ning_na_common import *

YE_LAN_NAME = "ye lan"
ZHONG_LI_NAME = "zhong li"
WAN_YE_NAME = "wan ye"

# 目前的满命芙宁娜算法采用的配队：夜芙万钟
# 手法：钟离e，芙芙q，万叶q，芙芙eaa 夜兰eqe，芙芙zaaz, 万叶e, 夜兰aaaeaa...直到芙芙大招结束，开启下一轮输出
# 使用这个配队计算的伤害，也可以作为以下满命手法模式的通解：
# 
#   芙芙qeaa，其他角色放技能等叠满层，切芙芙重击转白芙, 白芙a两刀再重击转黑芙，切其他角色输出
#
# 钟离和万叶是这个手法模式下最好的辅助，钟离能避免芙芙砍的时候被击飞，万叶就不用说了
# 夜兰是这个手法模式下最好的副C
#
# 不修改算法的情况下，只允许改变各个角色的生命值上限
g_teammates = [
    # 夜兰
    Character(YE_LAN_NAME, base_hp=14450, max_hp=43779),
    # 钟离
    Character(ZHONG_LI_NAME, base_hp=14695, max_hp=50567),
    # 万叶
    Character(WAN_YE_NAME, base_hp=13348, max_hp=23505),
]

def create_fufu():
    fufu = Character_FuFu(required_energy_recharge=110)
    # 双水
    fufu.get_hp().modify_max_hp_per(0.25)
    # 专武
    fufu.add_crit_damage(0.882)
    return fufu

def ye_fu_wan_zhong_team_qualifier(fufu: Character_FuFu):
    hp = fufu.get_hp().get_max_hp()
    a_bonus = fufu.get_a_bonus()
    e_bonus = fufu.get_e_bonus()
    q_bonus = fufu.get_q_bonus()

    # 这个固定过程的模拟计算忽略了不同初始生命值上限的芙芙的奶量对气氛值叠层速度的影响
    # 这是因为：芙芙的满命治疗在不被怪物打掉血的情况下，一般都是治疗溢出的，所以奶量对气氛值的影响很小
    damage = 0

    cur_hp = hp
    cur_q_bonus = 1 + q_bonus + 150 * 0.0031
    damage += cur_hp * fufu.Q_BEI_LV / 100 * cur_q_bonus * 1.05 * 0.487

    cur_e_bonus = 1 + e_bonus + 0.398 + 150 * 0.0031
    damage += cur_hp * fufu.E_BEI_LV / 100 * cur_e_bonus * 1.25 * 0.487

    cur_a_bonus = 1 + a_bonus + 0.398 + 150 * 0.0031
    damage += cur_hp * HEI_FU_BEI_LV / 100 * cur_a_bonus * 1.25 * 0.487

    cur_hp = hp + (0.14 * 1) * Character_FuFu.BASE_HP
    cur_a_bonus = 1 + a_bonus + 0.398 + 172.395 * 0.0031
    damage += cur_hp * HEI_FU_BEI_LV / 100 * cur_a_bonus * 1.25 * 0.487
    damage += cur_hp * HEI_FU_BEI_LV / 100 * cur_a_bonus * 1.25 * 0.487

    salon_member_bonus = 1 + e_bonus + 0.28 + 0.398 + 0.08 * 1 + 256.396 * 0.0031
    damage += cur_hp * fufu.FU_REN_BEI_LV / 100 * salon_member_bonus * 1.4 * 1.25 * 0.487
    damage += cur_hp * fufu.PANG_XIE_BEI_LV / 100 * salon_member_bonus * 1.4 * 1.25 * 0.487
    damage += cur_hp * fufu.XUN_JUE_BEI_LV / 100 * salon_member_bonus * 1.4 * 1.25 * 0.487

    cur_hp = hp + (0.14 * 2 + 0.1 * 1) * Character_FuFu.BASE_HP
    salon_member_bonus = 1 + e_bonus + 0.28 + 0.398 + 0.08 * 3 + 360.463 * 0.0031
    damage += cur_hp * fufu.FU_REN_BEI_LV / 100 * salon_member_bonus * 1.4 * 1.25 * 0.487

    cur_hp = hp + (0.14 * 2 + 0.1 * 1 + (429.971 - 400) * 0.0035) * Character_FuFu.BASE_HP
    salon_member_bonus = 1 + e_bonus + 0.28 + 0.398 + 0.08 * 3 + 400 * 0.0031
    damage += cur_hp * fufu.FU_REN_BEI_LV / 100 * salon_member_bonus * 1.4 * 1.25 * 0.487

    cur_hp = hp + (0.14 * 2 + 0.1 * 2 + (469.173 - 400) * 0.0035) * Character_FuFu.BASE_HP
    damage += cur_hp * fufu.XUN_JUE_BEI_LV / 100 * salon_member_bonus * 1.4 * 1.25 * 0.487

    cur_hp = hp + (0.14 * 2 + 0.1 * 2 + (519.565 - 400) * 0.0035) * Character_FuFu.BASE_HP
    cur_a_bonus = 1 + a_bonus + 0.398 + 400 * 0.0031
    damage += cur_hp * HEI_FU_BEI_LV / 100 * cur_a_bonus * 1.25 * 0.487
    damage += cur_hp * BAI_FU_BEI_LV / 100 * cur_a_bonus * 1.25 * 0.487

    cur_hp = hp + (0.14 * 2 + 0.1 * 2 + (533.572 - 400) * 0.0035) * Character_FuFu.BASE_HP
    damage += cur_hp * BAI_FU_BEI_LV / 100 * cur_a_bonus * 1.25 * 0.487
    damage += cur_hp * HEI_FU_BEI_LV / 100 * cur_a_bonus * 1.25 * 0.487

    cur_hp = hp + (0.14 * 2 + 0.1 * 2 + (561.584 - 400) * 0.0035) * Character_FuFu.BASE_HP
    damage += cur_hp * BAI_FU_BEI_LV / 100 * cur_a_bonus * 1.25 * 0.487

    cur_hp = hp + (0.14 * 2 + 0.1 * 2 + (662.386 - 400) * 0.0035) * Character_FuFu.BASE_HP
    damage += cur_hp * fufu.FU_REN_BEI_LV / 100 * salon_member_bonus * 1.4 * 1.25 * 0.487

    cur_hp = hp + (0.14 * 2 + 0.1 * 2 + (756.469 - 400) * 0.0035) * Character_FuFu.BASE_HP
    damage += cur_hp * fufu.XUN_JUE_BEI_LV / 100 * salon_member_bonus * 1.4 * 1.25 * 0.487
    damage += cur_hp * fufu.PANG_XIE_BEI_LV / 100 * salon_member_bonus * 1.4 * 1.25 * 0.487

    cur_hp = hp + (0.14 * 2 + 0.1 * 2 + (778.875 - 400) * 0.0035) * Character_FuFu.BASE_HP
    damage += cur_hp * fufu.FU_REN_BEI_LV / 100 * salon_member_bonus * 1.4 * 1.25 * 0.487

    cur_hp = hp + (0.14 * 2 + 0.1 * 2 + (800 - 400) * 0.0035) * Character_FuFu.BASE_HP
    damage += cur_hp * fufu.FU_REN_BEI_LV / 100 * salon_member_bonus * 1.4 * 1.25 * 0.487
    damage += cur_hp * fufu.XUN_JUE_BEI_LV / 100 * salon_member_bonus * 1.4 * 1.25 * 0.487

    cur_hp = hp + (0.14 * 2 + 0.1 * 3 + (800 - 400) * 0.0035) * Character_FuFu.BASE_HP
    damage += cur_hp * fufu.FU_REN_BEI_LV / 100 * salon_member_bonus * 1.4 * 1.25 * 0.487
    damage += cur_hp * fufu.PANG_XIE_BEI_LV / 100 * salon_member_bonus * 1.4 * 1.25 * 0.487

    cur_hp = hp + (0.14 * 2 + 0.1 * 3) * Character_FuFu.BASE_HP
    salon_member_bonus = 1 + e_bonus + 0.28 + 0.398 + 0.08 * 3
    damage += cur_hp * fufu.FU_REN_BEI_LV / 100 * salon_member_bonus * 1.4 * 1.25 * 0.487
    damage += cur_hp * fufu.XUN_JUE_BEI_LV / 100 * salon_member_bonus * 1.4 * 1.25 * 0.487
    damage += cur_hp * fufu.FU_REN_BEI_LV / 100 * salon_member_bonus * 1.4 * 1.25 * 0.487

    salon_member_bonus = 1 + e_bonus + 0.28 + 0.08 * 3
    damage += cur_hp * fufu.FU_REN_BEI_LV / 100 * salon_member_bonus * 1.4 * 1.25 * 0.487
    damage += cur_hp * fufu.XUN_JUE_BEI_LV / 100 * salon_member_bonus * 1.4 * 1.25 * 0.487
    damage += cur_hp * fufu.PANG_XIE_BEI_LV / 100 * salon_member_bonus * 1.4 * 1.05 * 0.487
    damage += cur_hp * fufu.FU_REN_BEI_LV / 100 * salon_member_bonus * 1.4 * 1.05 * 0.487
    # print(damage)

    return damage


def calculate_score_qualifier(score_data: ShengYiWu_Score):
    return qualify_syw(score_data, create_fufu, ye_fu_wan_zhong_team_qualifier)


def create_action_plan(fufu_initial_state: Character):
    plan = FuFuActionPlan(fufu_initial_state, g_teammates)

    # 这个 plan 有几个比较大的变数：
    # 1. 第三刀重击切白芙前，夫人有小概率的会扣血，使得气氛值叠层加快，后续伤害变高，实际操作4次出了一次，自动计算的概率好像更大些
    #    解决办法：人为控制扣血次数
    # 2. plan 结束时，有概率会有夫人两次出伤，实际大多数时候只有一次
    #    解决办法：人为去掉这次出伤
    # 3. 芙芙大招效果结整时，恰好有螃蟹的一次出伤，螃蟹的倍率是最大的， 能否吃到芙芙的增伤伤害会差很多，有小概率会吃不到
    #    解决办法：实测时大部分时候都吃到了，因此这里也手动强制，参见：force_add_fufu_q_bonus

    wan_ye = WanYe(elem_mastery=994, xi_fu_si_jing_lian_num=2)

    plan.add_action("钟离点按e", ZhongLiAction, 6.285, 6.453, negative=True)
    plan.add_action("芙芙q出伤", FuFu_Q_Action, 2.783, 2.884, negative=True)
    plan.add_action("万叶q", WanYeQAction, 0.616,
                    0.7, negative=True, wan_ye=wan_ye)

    plan.add_action("芙芙点按e", FuFu_E_Action,  0, 0)
    plan.add_action("第一刀", Hei_Fu_Damage_Action, 1.15, 1.284)
    three_little_first_action = "三小只开始扣血"
    plan.add_action(three_little_first_action, Action, 1.282, 1.455)
    plan.add_action("第二刀", Hei_Fu_Damage_Action,
                    0.366, 0.401, base_action="第一刀")
    plan.add_action("荒刀", Mang_Huang_Damage_Action,
                    0.55, 0.617, base_action="第一刀")

    plan.add_action("切夜兰出来", Switch_To_Character_Action,
                    0.333, 0.549, base_action="第二刀", character_name=YE_LAN_NAME)
    ye_lan_first_e = "夜兰第一个e引爆"
    plan.add_action(ye_lan_first_e, Action, 0.667, 0.7, base_action="切夜兰出来")
    plan.add_action("夜兰四命生效1", Ye_Lan_4_Ming_Action,
                    0.016, 0.083, base_action=ye_lan_first_e)
    plan.add_action("夜兰q动画开始", Q_Animation_Start_Action,
                    0.133, 0.333, base_action=ye_lan_first_e, character_name=YE_LAN_NAME)
    plan.add_action("夜兰q增伤开始", Ye_Lan_Q_Bonus_Start,
                    1.3, 1.352, base_action="夜兰q动画开始", ye_lan_name=YE_LAN_NAME)
    plan.add_action("夜兰四命生效2", Ye_Lan_4_Ming_Action,
                    0.868, 0.952, base_action="夜兰q增伤开始")

    plan.add_action("切芙芙出来", Switch_To_Character_Action,
                    0.25, 0.316, base_action="夜兰四命生效2", character_name=Character_FuFu.NAME)
    three_little_disappear = "三小只开始消失，众水的歌者出来"
    plan.add_action(three_little_disappear, Action,
                    0.751, 0.783, base_action="切芙芙出来")
    plan.add_action("第三刀重击出伤", Hei_Fu_Damage_Action,
                    0.8, 0.883, base_action="切芙芙出来")
    plan.add_action("第四刀", Bai_Fu_Damage_Action, 0.75,
                    0.767, base_action="第三刀重击出伤")
    plan.add_action("第四刀扣血", Bai_Dao_Kou_Xue_Action, 0.165, 0.230,
                    base_action="第四刀", effective_delay=plan.get_effective_delay())
    plan.add_action("第五刀", Bai_Fu_Damage_Action,
                    0.383, 0.417, base_action="第四刀")
    plan.add_action("第五刀扣血", Bai_Dao_Kou_Xue_Action, 0.165, 0.230,
                    base_action="第五刀", effective_delay=plan.get_effective_delay())
    plan.add_action("芒刀", Mang_Huang_Damage_Action,
                    0.6, 0.734, base_action="第四刀")
    plan.add_action("第六刀重击", Bai_Fu_Damage_Action,
                    0.683, 0.734, base_action="第五刀")
    plan.add_action("第六刀扣血", Bai_Dao_Kou_Xue_Action, 0.05, 0.117,
                    base_action="第六刀重击", effective_delay=plan.get_effective_delay())

    # TODO: 这里的切人时间沿用了切夜兰出来的时间，是否需要重新测试
    plan.add_action("切万叶出来", Switch_To_Character_Action,
                    0.333, 0.549, base_action="第六刀重击", character_name=WAN_YE_NAME)
    plan.add_action("万叶e扩散", Action, 1.568, 1.568, base_action="切万叶出来")

    three_little_2nd_action = "三小只再次切出来后第一次扣血"
    plan.add_action(three_little_2nd_action, Action,
                    0.916, 1.067, base_action="第六刀重击")

    plan.add_action("夜兰第三个e", Ye_Lan_4_Ming_Action,
                    10.5, 11, base_action=ye_lan_first_e)

    plan.add_action("芙芙大招效果消失", Fu_Fu_Q_Bonus_Stop_Action,
                    18.253, 18.737, "芙芙q出伤")

    # TODO: 这里的切人时间沿用了切夜兰出来的时间，实际切人时间需要进行测试统计
    second_run_turn_start = "切钟离出来"
    plan.add_action(second_run_turn_start, Switch_To_Character_Action,
                    0.033, 0.549, base_action="芙芙大招效果消失", character_name=ZHONG_LI_NAME)

    plan.add_action("夜兰大招效果消失", Ye_Lan_Q_Bonus_Stop_Actioin,
                    14.97, 14.97, "夜兰q增伤开始")
    plan.add_action("万叶增伤消失", WanYeBonusStopAction, 8, 8,
                    base_action="万叶e扩散", wan_ye=wan_ye)
    plan.add_action("风套减抗消失", FengTaoInvalidAction,
                    10, 10, base_action="万叶e扩散")

    if enable_debug:
        action_names = [a.name for a in plan.action_list]
        action_name_set = set(action_names)
        if len(action_names) != len(action_name_set):
            raise Exception("action name duplicated!")

    three_little_first_action_time = plan.find_action(
        three_little_first_action).get_timestamp()
    three_little_disappear_time = plan.find_action(
        three_little_disappear).get_timestamp()
    # print(three_little_first_action_time)
    # print(three_little_disappear_time)

    schedule_little_three(plan, FU_REN_NAME,
                          three_little_first_action_time, three_little_disappear_time,
                          Fu_Ren_Kou_Xue_Action, Fu_Ren_Damage_Action,
                          kou_xue_num=3, chu_shang_num=3)

    schedule_little_three(plan, XUN_JUE_NAME,
                          three_little_first_action_time, three_little_disappear_time,
                          Xun_Jue_Kou_Xue_Action, Xun_Jue_Damage_Action,
                          kou_xue_num=2, chu_shang_num=2)

    schedule_little_three(plan, PANG_XIE_NAME,
                          three_little_first_action_time, three_little_disappear_time,
                          Pang_Xie_Kou_Xue_Action, Pang_Xie_Damage_Action,
                          kou_xue_num=1, chu_shang_num=1)

    second_start_time = plan.find_action(
        three_little_2nd_action).get_timestamp()
    second_end_time = plan.find_action(
        second_run_turn_start).get_timestamp() + random.randint(6285, 6453) / 1000
    # print(second_start_time)
    # print(second_end_time)

    schedule_little_three(plan, FU_REN_NAME,
                          second_start_time, second_end_time,
                          Fu_Ren_Kou_Xue_Action, Fu_Ren_Damage_Action,
                          kou_xue_num=8, chu_shang_num=8)

    schedule_little_three(plan, XUN_JUE_NAME,
                          second_start_time, second_end_time,
                          Xun_Jue_Kou_Xue_Action, Xun_Jue_Damage_Action,
                          kou_xue_num=4, chu_shang_num=4)

    _, c_action_lst = schedule_little_three(plan, PANG_XIE_NAME,
                                            second_start_time, second_end_time,
                                            Pang_Xie_Kou_Xue_Action, Pang_Xie_Damage_Action,
                                            kou_xue_num=3, chu_shang_num=3)
    # 为了避免波动太大，强制让这次的螃蟹吃到芙芙q增伤
    c_action_lst[1].force_add_fufu_q_bonus = True

    ge_zhe_start_time = three_little_disappear_time
    ge_zhe_stop_time = plan.find_action("第六刀重击").get_timestamp()

    ge_zhe_cure_time = ge_zhe_start_time + random.randint(1019, 1199) / 1000
    while ge_zhe_cure_time < ge_zhe_stop_time:
        ge_zhe = Ge_Zhe_Cure_Action("众水的歌者治疗")
        ge_zhe.set_timestamp(ge_zhe_cure_time + plan.get_effective_delay())
        plan.insert_action(ge_zhe)

        # FIXME: 这里没有考虑固有天赋2，如果当前生命值上限低于4w，则治疗间隔是更长的
        # 歌者的治疗间隔目前是在这里写死的，实际应该是根据生命值上限实时决定的
        # 不过话说回来，按满命的流程，切白芙的时候，最终排名靠前的圣遗物组合应该生命值上限都在4w附近吧？
        ge_zhe_cure_time += random.randint(1612, 1783) / 1000

    # plan.sort_action()
    # print(len(plan.action_list))
    # for a in plan.action_list:
    #    self.debug(str(round(a.get_timestamp(), 3)) + ":" + a.name)

    return plan

def calculate_score_callback(score_data: ShengYiWu_Score):
    return calculate_score_common(score_data, create_fufu, create_action_plan)

# Main body
def main():
    # logging.basicConfig(filename='D:\\logs\\fufu.log', encoding='utf-8', filemode='w', level=logging.DEBUG)
    # logging.basicConfig(level=logging.DEBUG)
    print("默认算法复杂，圣遗物多的话需要执行0.5~1小时多")
    
    find_syw_for_fu_ning_na(calculate_score_callback=calculate_score_callback,
                            result_txt_file="fu_ning_na_syw.txt",
                            calculate_score_qualifier=calculate_score_qualifier
                            )

if __name__ == '__main__':
    main()