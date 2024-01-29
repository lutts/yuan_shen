#!/user/bin/env python3 -tt
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

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
#         或：雷神e，芙芙eq, 琴eaq, 夜兰eqe，琴e，雷神qazazazazaz，
#             缺点：雷神没砍完，芙芙大招就可能消失了，不切琴补减抗，风套效果会提前消失，适用于夜兰输出比雷神高的旅行者
#                  芙芙练度高也不推荐，奶妈越往后就越能多叠一些芙芙二命的生命值加成
#       注：也可以芙芙e，雷神e，琴e, 芙芙q，这样更有利于叠满层，但频繁切人有点繁琐
#
#    非风系奶妈+二命芙芙+风系辅助的配队：芙芙e，风系减抗，芙芙q, 奶妈eaq，风系减抗，主C输出
#
# 对于二命以下的芙芙，打法是一样的，只不过第一轮输出会低些，但第一轮扣了很多血后，进第二轮瞬间奶满就和二命体验差不多了

FU_FU_NAME = "furina"
MAIN_CARRY = "主C"
SECONDARY_CARRY = "副C"
HEALER = "奶妈"


time_befor_fufu_e = 0

class Healer_Start_Time:
    def __init__(self, healer: Healer_Action, start_time_min, start_time_max=0):
        self.healer = healer
        self.start_time_min = start_time_min
        if start_time_max:
            self.start_time_max = start_time_max
        else:
            self.start_time_max = start_time_min

# 奶妈以及奶妈开始奶的时间，这个时间是从芙芙点按e后e技能CD刚变为19.9时开始算起的
# 目前支持的奶妈参见 healer.py
# 多次测试可以指定时间范围，只测试一次的话把最小/最大时间设置成一样就行
healer_start_times = [
    Healer_Start_Time(None, start_time_min=4.8, start_time_max=4.8)
    # Healer_Start_Time(healer2, start_time_min=4.8, start_time_max=4.8)
    # Healer_Start_Time(healer3, start_time_min=4.8, start_time_max=4.8)
]

class Character_Q_Animation:
    def __init__(self, start_time_min, duration_min, start_time_max=0, duration_max=0):
        self.start_time_min = start_time_min
        if start_time_max:
            self.start_time_max = start_time_max
        else:
            self.start_time_max = start_time_min
        self.duration_min = duration_min
        if duration_max:
            self.duration_max = duration_max
        else:
            self.duration_max = duration_min

# 队伍各个角色大招动画开始时间、持续时长
q_animation_start_end_times = {
    FU_FU_NAME: Character_Q_Animation(start_time_min=0, start_time_max=0, duration_min=0, duration_max=0),
    MAIN_CARRY: Character_Q_Animation(start_time_min=0, start_time_max=0, duration_min=0, duration_max=0),
    SECONDARY_CARRY: Character_Q_Animation(start_time_min=0, start_time_max=0, duration_min=0, duration_max=0),
    HEALER: Character_Q_Animation(start_time_min=0, start_time_max=0, duration_min=0, duration_max=0),
}

non_full_ming_zuo_team = {
    # 影宝
    MAIN_CARRY: Teammate(12907, 21650),
    # 夜兰
    SECONDARY_CARRY: Teammate(14450, 46461, elem_type=ShengYiWu.ELEM_TYPE_SHUI),
    # 琴
    HEALER: Teammate(12965, 24224)
}