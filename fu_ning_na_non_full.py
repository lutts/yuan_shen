#!/user/bin/env python3 -tt
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

from base_syw import ShengYiWu_Score
from health_point import HealthPoint
from character import Character
from healer import Qin_Heal_Action
from action import Action, ActionPlan
from fu_ning_na_common import *

# 非满命算法针对以下手法模式：
#
#   芙芙eq，副 C 放技能，切奶妈奶全队，切主C站场输出直到芙芙大招结束，开启下一轮循环
#
# 下面是芙芙和沙龙成员的行动序列，奶妈不同介入时间的气氛值叠层情况
#
#  芙芙eq:  q期间三小只扣血，但芙芙大招期间不扣血，因此扣血情况是： 其他人扣7.6%
#  夫人扣血：基本是紧接在芙芙q动画结束的，二命以上：1.6 * 4 * 3.5 + 150 = 172.4, 一命：1.6 * 4 + 150 = 156.4
#  夫人扣血：二命：172.4 + 1.6 * 4 * 3.5 = 194.8，一命: 1.6 * 4 + 156.4 = 162.8
#  勋爵扣血：二命：194.8 + 2.4 * 4 * 3.5 = 228.4,一命：2.4 * 4 + 162.8 = 172.4
#          二命的话，此时就可以奶全队，228.4 + 7.6 * 3 * 3.5 + (1.6 + 1.6 + 2.4) * 4 * 3.5 = 386.6
#          虽然没满层，但也不差多少了，但如果芙芙的练度高，建议把全队奶再推后一些，多叠一些芙芙二命的生命值加成
#  夫人扣血：我们假设此前副C在放q，则之前夫人和勋爵扣不了放q的角色的血，则一命: 172.4 - (1.6 + 2.4) + 1.6 * 4 = 174.8
#  螃蟹扣血: 一命: 174.8 + 3.6 * 4 = 189.2
#  夫人扣血：一命：189.2 + 1.6 * 4 = 195.6
#          如果此时奶全队，则 195.6 + 7.6 * 3 + 1.6 * 4 + (1.6 + 2.4) * 3 + (1.6 + 3.6 + 1.6) * 4 = 264层
#
# 根据以上分析，对于二命芙芙，几个配队的第一轮打法如下：
#   注：奶妈e后都a了一下，是为了拖时间，确保放q的时候勋爵会扣血
#
#    影夜芙琴: 雷神e，芙芙eq，夜兰eq(e), 琴eaq，雷神qazazazazaz
#             缺点：芙芙大招消失前大约3秒，风套减抗会失效
#         或：雷神e，芙芙eq, 琴eaq, 夜兰eqe，琴e，雷神qazazazazaz，
#             缺点：雷神没砍完，芙芙大招就可能消失了，不切琴补减抗，风套效果会提前消失，适用于夜兰输出比雷神高的旅行者
#                  芙芙练度高也不推荐，奶妈越往后就越能多叠一些芙芙二命的生命值加成
#       注：也可以芙芙e，雷神e，琴e, 芙芙q，这样更有利于叠满层，但频繁切人有点繁琐
#
#    非风系奶妈+二命芙芙+风系辅助的配队：芙芙e，风系减抗，芙芙q, 奶妈eaq，风系减抗，主C输出
#
# 对于二命以下的芙芙，打法是一样的，只不过第一轮输出会低些，但第一轮扣了很多血后，进第二轮瞬间奶满就和二命体验差不多了

ch_yin_bao = Character("影宝", base_hp=12907, max_hp=21650, q_energy=90)
ch_ye_lan = Character("夜兰", base_hp=14450, max_hp=46461, q_energy=70)
ch_qin = Character("琴", base_hp=12965, max_hp=24224, 
                   base_atk=665, all_atk=1764, q_level=9, 
                   q_energy=80, healing_bonus=0.166)

g_teammates = [ch_yin_bao, ch_ye_lan, ch_qin]

class YinBao_E_Action(Action):
    def do_impl(self, plan: FuFuActionPlan):
        # for ch in plan.characters:
        #     ch.add_q_bonus(ch.q_energy * 0.3 / 100)
        fufu = plan.get_fufu()
        bonus = fufu.q_energy *  0.3 / 100
        fufu.add_q_bonus(fufu.q_energy * 0.3 / 100)
        plan.extra_q_bonus += bonus
        plan.damage_record_bonus()

def create_fufu():
    fufu = Character_FuFu(required_energy_recharge=110)
    # 双水
    fufu.get_hp().modify_max_hp_per(0.25)
    # 专武
    fufu.add_crit_damage(0.882)
    return fufu

def ying_ye_fu_qin_team_qualifier(fufu: Character_FuFu):
    hp = fufu.get_hp().get_max_hp()
    e_bonus = fufu.get_e_bonus()
    q_bonus = fufu.get_q_bonus()
    damage = 0
    
    cur_hp = hp
    cur_e_bonus = 1 + e_bonus
    damage += cur_hp * fufu.E_BEI_LV / 100 * cur_e_bonus * 0.9 * 0.487

    cur_hp = hp + (0.14 * 1) * Character_FuFu.BASE_HP
    salon_member_bonus = 1 + e_bonus + 0.28
    damage += cur_hp * fufu.FU_REN_BEI_LV / 100 * salon_member_bonus * 1.4 * 0.9 * 0.487
    damage += cur_hp * fufu.XUN_JUE_BEI_LV / 100 * salon_member_bonus * 1.4 * 0.9 * 0.487
    damage += cur_hp * fufu.PANG_XIE_BEI_LV / 100 * salon_member_bonus * 1.4 * 0.9 * 0.487

    cur_q_bonus = 1 + q_bonus + 0.18 + 150 * 0.0031
    damage += cur_hp * fufu.Q_BEI_LV / 100 * cur_q_bonus * 0.9 * 0.487

    cur_hp = hp + (0.14 * 2) * Character_FuFu.BASE_HP
    salon_member_bonus = 1 + e_bonus + 0.28 + 0.08 * 1 + 172.394 * 0.0031
    damage += cur_hp * fufu.FU_REN_BEI_LV / 100 * salon_member_bonus * 1.4 * 0.9 * 0.487

    cur_hp = hp + (0.14 * 2 + 0.1 * 1) * Character_FuFu.BASE_HP
    salon_member_bonus = 1 + e_bonus + 0.28 + 0.08 * 3 + 189.191 * 0.0031
    damage += cur_hp * fufu.FU_REN_BEI_LV / 100 * salon_member_bonus * 1.4 * 0.9 * 0.487

    salon_member_bonus = 1 + e_bonus + 0.28 + 0.08 * 3 + 214.393 * 0.0031
    damage += cur_hp * fufu.XUN_JUE_BEI_LV / 100 * salon_member_bonus * 1.4 * 0.9 * 0.487

    cur_hp = hp + (0.14 * 2 + 0.1 * 2) * Character_FuFu.BASE_HP
    salon_member_bonus = 1 + e_bonus + 0.28 + 0.08 * 3 + 236.798 * 0.0031
    damage += cur_hp * fufu.FU_REN_BEI_LV / 100 * salon_member_bonus * 1.4 * 0.9 * 0.487

    salon_member_bonus = 1 + e_bonus + 0.28 + 0.08 * 3 + 287.19 * 0.0031
    damage += cur_hp * fufu.PANG_XIE_BEI_LV / 100 * salon_member_bonus * 1.4 * 1.15 * 0.487

    salon_member_bonus = 1 + e_bonus + 0.28 + 0.08 * 3 + 334.8 * 0.0031
    damage += cur_hp * fufu.FU_REN_BEI_LV / 100 * salon_member_bonus * 1.4 * 1.15 * 0.487

    cur_hp = hp + (0.14 * 2 + 0.1 * 2 + (599.392 - 400) * 0.0035) * Character_FuFu.BASE_HP
    salon_member_bonus = 1 + e_bonus + 0.28 + 0.08 * 3 + 400 * 0.0031
    damage += cur_hp * fufu.XUN_JUE_BEI_LV / 100 * salon_member_bonus * 1.4 * 1.15 * 0.487

    cur_hp = hp + (0.14 * 2 + 0.1 * 2 + (621.801 - 400) * 0.0035) * Character_FuFu.BASE_HP
    damage += cur_hp * fufu.FU_REN_BEI_LV / 100 * salon_member_bonus * 1.4 * 1.15 * 0.487

    cur_hp = hp + (0.14 * 2 + 0.1 * 2 + (661.012 - 400) * 0.0035) * Character_FuFu.BASE_HP
    damage += cur_hp * fufu.FU_REN_BEI_LV / 100 * salon_member_bonus * 1.4 * 1.15 * 0.487

    cur_hp = hp + (0.14 * 2 + 0.1 * 2 + (769.413 - 400) * 0.0035) * Character_FuFu.BASE_HP
    damage += cur_hp * fufu.XUN_JUE_BEI_LV / 100 * salon_member_bonus * 1.4 * 1.15 * 0.487
    damage += cur_hp * fufu.PANG_XIE_BEI_LV / 100 * salon_member_bonus * 1.4 * 1.15 * 0.487

    cur_hp = hp + (0.14 * 2 + 0.1 * 2 + (791.818 - 400) * 0.0035) * Character_FuFu.BASE_HP
    damage += cur_hp * fufu.FU_REN_BEI_LV / 100 * salon_member_bonus * 1.4 * 1.15 * 0.487

    cur_hp = hp + (0.14 * 2 + 0.1 * 2 + (800 - 400) * 0.0035) * Character_FuFu.BASE_HP
    damage += cur_hp * fufu.FU_REN_BEI_LV / 100 * salon_member_bonus * 1.4 * 1.15 * 0.487
    damage += cur_hp * fufu.XUN_JUE_BEI_LV / 100 * salon_member_bonus * 1.4 * 1.15 * 0.487
    damage += cur_hp * fufu.FU_REN_BEI_LV / 100 * salon_member_bonus * 1.4 * 1.15 * 0.487
    damage += cur_hp * fufu.PANG_XIE_BEI_LV / 100 * salon_member_bonus * 1.4 * 0.9 * 0.487
    damage += cur_hp * fufu.FU_REN_BEI_LV / 100 * salon_member_bonus * 1.4 * 0.9 * 0.487
    damage += cur_hp * fufu.XUN_JUE_BEI_LV / 100 * salon_member_bonus * 1.4 * 0.9 * 0.487
    damage += cur_hp * fufu.FU_REN_BEI_LV / 100 * salon_member_bonus * 1.4 * 0.9 * 0.487

    cur_hp = hp + (0.14 * 2 + 0.1 * 2) * Character_FuFu.BASE_HP
    salon_member_bonus = 1 + e_bonus + 0.28 + 0.08 * 3
    damage += cur_hp * fufu.FU_REN_BEI_LV / 100 * salon_member_bonus * 1.4 * 0.9 * 0.487

    #print(damage)

    return damage


def calculate_score_qualifier(score_data: ShengYiWu_Score):
    return qualify_syw(score_data, create_fufu, ying_ye_fu_qin_team_qualifier)


def create_action_plan(fufu_initial_state: Character):
    plan = FuFuActionPlan(fufu_initial_state, g_teammates)

    plan.add_action("芙芙点按e", FuFu_E_Action, 0, 0)

    # 注意：因为是基于芙芙e的统计，这两个action实际在芙芙e之前，但代码里顺序是反的
    plan.add_action("切芙芙出来", Switch_To_Character_Action, 0.183, 0.357, 
                    negative=True, character_name=Character_FuFu.NAME)
    plan.add_action("影宝e", YinBao_E_Action, 0.866, 1.202, negative=True,
                    base_action="切芙芙出来")
    
    three_little_first_action = "三小只开始扣血"
    plan.add_action(three_little_first_action, Action, 1.282, 1.455)
    plan.add_action("芙芙大招动画开始", Q_Animation_Start_Action, 0.733, 0.9,
                    character_name=Character_FuFu.NAME)
    plan.add_action("芙芙q出伤", FuFu_Q_Action, 1.8, 1.8, base_action="芙芙大招动画开始")
    plan.add_action("芙芙大招动画结束", Q_Animation_Stop_Action, 1.9, 1.9,
                    base_action="芙芙大招动画开始", character_name=Character_FuFu.NAME)
    plan.add_action("切夜兰出来", Switch_To_Character_Action, 0.35, 0.467,
                    base_action="芙芙大招动画结束", character_name=ch_ye_lan.name)
    plan.add_action("夜兰e生效一层", Ye_Lan_4_Ming_Action, 0.734, 0.784,
                    base_action="切夜兰出来")
    plan.add_action("夜兰大招动画开始", Q_Animation_Start_Action, 0.1, 0.167,
                    base_action="夜兰e生效一层", character_name=ch_ye_lan.name)
    plan.add_action("夜兰大招动画结束", Q_Animation_Stop_Action, 1.482, 1.552,
                    base_action="夜兰大招动画开始", character_name=ch_ye_lan.name)
    plan.add_action("夜兰e生效二层", Ye_Lan_4_Ming_Action, 0.684, 0.835,
                    base_action="夜兰大招动画结束")
    plan.add_action("切琴出来", Switch_To_Character_Action, 0.233, 0.419,
                    base_action="夜兰e生效二层", character_name=ch_qin.name)
    plan.add_action("琴e出扩散", FengTaoEffectiveAction, 0.464, 0.55, 
                    base_action="切琴出来")
    plan.add_action("风套减抗消失", FengTaoInvalidAction, 10, 10, base_action="琴e出扩散")
    plan.add_action("琴大招动画开始", Q_Animation_Start_Action, 1.399, 1.767,
                    base_action="切琴出来", character_name=ch_qin.name)
    plan.add_action("琴治疗全队", Qin_Heal_Action, 0.683, 0.783,
                    base_action="琴大招动画开始", qin=ch_qin)
    plan.add_action("琴大招动画结束", Q_Animation_Stop_Action, 1.433, 1.433,
                    base_action="琴大招动画开始", character_name=ch_qin.name)
    plan.add_action("切影宝出来", Switch_To_Character_Action, 0.9, 1.133,
                    base_action="琴大招动画结束", character_name=ch_yin_bao.name)
    plan.add_action("影宝大招动画开始", Q_Animation_Start_Action, 0.083, 0.083,
                    base_action="切影宝出来", character_name=ch_yin_bao.name)
    plan.add_action("影宝大招动画结束", Q_Animation_Stop_Action, 1.8, 1.834,
                    base_action="影宝大招动画开始", character_name=ch_yin_bao.name)
    
    plan.add_action("芙芙大招效果消失", Fu_Fu_Q_Bonus_Stop_Action,
                    18.253, 18.737, "芙芙q出伤")
    # 注：这里假设芙芙大招效果消失时影宝e
    plan.add_action("下轮循环-切芙芙出来", Action, 0.866, 1.202, base_action="芙芙大招效果消失")
    plan.add_action("下轮循环-芙芙点按e",  Switch_To_Character_Action, 0.183, 0.357, 
                    base_action="下轮循环-切芙芙出来", character_name=Character_FuFu.NAME)
    
    if enable_debug:
        action_names = [a.name for a in plan.action_list]
        action_name_set = set(action_names)
        if len(action_names) != len(action_name_set):
            raise Exception("action name duplicated!")
        
    salon_member_start_time = plan.find_action(three_little_first_action).get_timestamp()
    salon_member_end_time = plan.find_action("下轮循环-芙芙点按e").get_timestamp()

    schedule_little_three(plan, FU_REN_NAME,
                          salon_member_start_time, salon_member_end_time,
                          Fu_Ren_Kou_Xue_Action, Fu_Ren_Damage_Action,
                          kou_xue_num=13, chu_shang_num=13)

    schedule_little_three(plan, XUN_JUE_NAME,
                          salon_member_start_time, salon_member_end_time,
                          Xun_Jue_Kou_Xue_Action, Xun_Jue_Damage_Action,
                          kou_xue_num=6, chu_shang_num=6)

    schedule_little_three(plan, PANG_XIE_NAME,
                          salon_member_start_time, salon_member_end_time,
                          Pang_Xie_Kou_Xue_Action, Pang_Xie_Damage_Action,
                          kou_xue_num=4, chu_shang_num=4)


    # plan.sort_action()
    # print(len(plan.action_list))
    # for a in plan.action_list:
    #    print(str(round(a.get_timestamp(), 3)) + ":" + a.name)
    

    return plan

def calculate_score_callback(score_data: ShengYiWu_Score):
    return calculate_score_common(score_data, create_fufu, create_action_plan)

# Main body
if __name__ == '__main__':
    # logging.basicConfig(filename='D:\\logs\\fufu.log', encoding='utf-8', filemode='w', level=logging.DEBUG)
    # logging.basicConfig(level=logging.DEBUG)
    print("默认算法复杂，圣遗物多的话需要执行0.5~1小时多")
    find_syw_for_fu_ning_na(calculate_score_callback=calculate_score_callback,
                            result_txt_file="fu_ning_na_syw_non_full.txt",
                            calculate_score_qualifier=calculate_score_qualifier
                            )
