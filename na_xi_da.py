#!/user/bin/env python3 -tt
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

import copy
from ys_basic import Ys_Elem_Type
from character import Character
from monster import Monster
from ys_reaction import *
from ys_syw import ShengYiWu, ShengYiWu_Score, calculate_score, Syw_Combine_Desc, find_syw_combine

enable_debug = False

# 久岐忍实战精通可供纳西妲大招转换的部分
# 40：小草神专武
# 150: 4饰金
jiu_qi_ren_elem_mastery = 789 + 40 + 150
jiu_qi_ren_max_hp = 39270
# 阿忍带圣显，叠三层
sheng_xian_elem_mastery = round(jiu_qi_ren_max_hp * 0.002)

# 纳西妲 tips:
# 
# * 普攻遵循3hit2.5s, 弱草附着，连着四段的话，就是第一段和第四段有弱草附着，触发蔓激化
# * 重击为独立附着
# * 战技本身为独立附着
# * 对怪的第一个e吃不到二命减防以及四草套减抗
# * 灭净三业是独立中草附着，附着cd为1秒，触发间隔默认2.5秒，一个雷时13级大间隔1.97秒，两个雷间隔为1.71
# * 灭净三业对于没有被激化的目标，只有直伤
# * 首次放e的同时触发的灭净三业吃不到四命的精通加成
# * 阿忍开e时，虽然触发了原激化，但当次触发的灭净三业仍然吃不到二命减抗
# * 满命六下遵循3hit2.5s
#
# eq还是qe的问题：开局如果是纳西妲起手，则eq和qe是无所谓的，因为e本身的伤害不高，此时又触发不了元素反应，也就触发不了灭净三业和蔓激化
#               只要怪不换波次，纳西妲的e效果肯定是常驻的，也无所谓eq还是qe，因为e总是在的，灭净三业的伤害丢不了
#
# TODO：是否需要考虑以下对群时的圣遗物组合方案？ 对群时多少目标会被激化？让阿忍尽量扫到更多目标？

class Na_Xi_Da_Ch(Character, name="纳西妲", elem_type=Ys_Elem_Type.CAO, ming_zuo_num=6,
                  e_level=13, q_level=13):
    short_e_multiplier = [
        98.4/100, # 1
        105.8/100, # 2
        113.2/100, # 3
        123.0/100, # 4
        130.4/100, # 5
        137.8/100, # 6
        147.6/100, # 7
        157.4/100, # 8
        167.3/100, # 9
        177.1/100, # 10
        187.0/100, # 11
        196.8/100, # 12
        209.1/100, # 13
    ]
    # 长按倍率
    long_e_multiplier = [
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

    def __init__(self, teammate_types: list[Ys_Elem_Type],
                 base_atk=841, has_zhuan_wu=True):
        if len(teammate_types) > 3:
            raise Exception("队友不能超过3个")
        
        if self.ming_zuo_num >= 1:
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

        if self.ming_zuo_num >= 4:
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
        
        super().__init__(base_atk=base_atk,
                         elem_mastery=elem_mastery, base_bonus=bonus)
        
        self.teammate_types = teammate_types
        
        self.q_exist = False
        self.extra_mie_jing_san_ye_bonus = 0
        if huo_num > 0:
            if huo_num > 2:
                huo_num = 2
        
            self.extra_mie_jing_san_ye_bonus += Na_Xi_Da_Ch.q_huo_bonus[self.q_level - 1][huo_num - 1]
        
        # self.mie_jing_san_ye_interval = 2.5
        # if lei_num > 0:
        #     if lei_num > 2:
        #         lei_num = 2

        #     self.mie_jing_san_ye_interval -= Na_Xi_Da_Ch.q_lei_intervals[q_level - 1][lei_num - 1]

        # self.q_duration = 15
        # if shui_num > 0:
        #     if shui_num > 2:
        #         shui_num = 2

        #     self.q_duration += Na_Xi_Da_Ch.q_shui_durations[q_level - 1][shui_num - 1]

        self.total_damage = 0

    def get_real_crit_rate(self):
        return self.get_crit_rate() + min((self.get_elem_mastery() - 200) * 0.0003, 0.24)
    
    def get_a_damage(self, phrase, reaction: Ys_Reaction):
        # 6级普攻
        if phrase == 1:
            multiplier = 56.4/100
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
    
    def __get_e_damage(self, reaction: Ys_Reaction, multiplier):
        base_damage = self.get_atk() * multiplier
        bonus = self.get_e_bonus()
        return reaction.do_damage(base_damage, bonus)
    
    def get_short_e_damage(self, reaction: Ys_Reaction):
        multiplier = Na_Xi_Da_Ch.short_e_multiplier[self.e_level - 1]
        return self.__get_e_damage(reaction, multiplier)
    
    def get_long_e_damage(self, reaction: Ys_Reaction):
        multiplier = Na_Xi_Da_Ch.long_e_multiplier[self.e_level - 1]
        return self.__get_e_damage(reaction, multiplier)
    
    def __get_mie_jing_san_ye_damage(self, reaction, multiplier):
        # print("灭净三业倍率：", str(multiplier))
        base_damage = self.get_atk() * multiplier[0] + self.get_elem_mastery() * multiplier[1]

        em_to_bonus =  min((self.get_elem_mastery() - 200) * 0.001, 0.8)
        bonus = self.get_e_bonus() + em_to_bonus
        if self.q_exist:
            bonus += self.extra_mie_jing_san_ye_bonus
        # print("base_damage: {}, bonus: {}, monster: {}".format(base_damage, round(bonus, 3), str(reaction.monster)))
        return reaction.do_damage(base_damage, bonus)
    
    def get_mie_jing_san_ye_damage(self, reaction: Ys_Reaction):
        multiplier = Na_Xi_Da_Ch.mie_jing_san_ye_multiplier[self.e_level - 1]
        return self.__get_mie_jing_san_ye_damage(reaction, multiplier)
    
    def get_6_ming_damage(self, reaction: Ys_Reaction):
        return self.__get_mie_jing_san_ye_damage(reaction, multiplier=(200/100, 400/100))

    def scan_syw_combine(self, syw_combine: list[ShengYiWu], in_front):
        self.set_syw_combine(syw_combine)

        name_count = self.get_syw_name_count()
        # print(name_count)
        for n in name_count:
            if name_count[n] < 2:  # 散件不计算套装效果
                continue

            if n == ShengYiWu.SHEN_LIN:
                self.add_all_bonus(0.15)            
            elif n == ShengYiWu.SHI_JIN:
                self.add_elem_mastery(80)
                if name_count[n] >= 4:
                    for t in self.teammate_types:
                        if t is Ys_Elem_Type.CAO:
                            self.add_atk_per(0.14)
                        else:
                            self.add_elem_mastery(50)
            elif n == ShengYiWu.JU_TUAN:
                self.add_all_bonus(0.2)
                if name_count[n] >= 4:
                    self.add_all_bonus(0.25)
                    if not in_front:
                        self.add_all_bonus(0.25)
            elif n == ShengYiWu.YUE_TUAN:
                self.add_elem_mastery(80)

    def is_syw_ok(self):
        crit_rate = self.get_real_crit_rate()
        crit_rate = round(crit_rate, 3)
        if crit_rate < 0.64:
            return False
        
        return True


def print_damage(nxd: Na_Xi_Da_Ch, prefix, damage):
    print(prefix + ": 不暴 {}, 暴击 {}".format(round(damage), round(damage * (1 + nxd.get_crit_damage()))))

def print_na_xi_da_in_front(nxd, no_reaction, man_ji_hua):
    # 站场e
    damage = nxd.get_short_e_damage(no_reaction)
    print_damage(nxd, "短按e技能直伤", damage)

    damage = nxd.get_short_e_damage(man_ji_hua)
    print_damage(nxd, "短按e技能蔓激化", damage)

    damage = nxd.get_long_e_damage(no_reaction)
    print_damage(nxd, "长按e技能直伤", damage)

    damage = nxd.get_long_e_damage(man_ji_hua)
    print_damage(nxd, "长按e技能蔓激化", damage)

    for i in range(1, 5 ):
        damage = nxd.get_a_damage(i, no_reaction)
        print_damage(nxd, "普攻 {} 段直伤".format(i), damage)
        damage = nxd.get_a_damage(i, man_ji_hua)
        print_damage(nxd, "普攻 {} 段蔓激化".format(i), damage)

    damage = nxd.get_mie_jing_san_ye_damage(no_reaction)
    print("站场灭净三业直伤: 不暴{}, 暴击{}".format(round(damage), round(damage * (1 + nxd.get_crit_damage()))))
    damage = nxd.get_mie_jing_san_ye_damage(man_ji_hua)
    print("站场灭净三业蔓激化: 不暴{}, 暴击{}".format(round(damage), round(damage * (1 + nxd.get_crit_damage()))))

    damage = nxd.get_6_ming_damage(no_reaction)
    print("满命业障除直伤：不暴{}, 暴击{}".format(round(damage), round(damage * (1 + nxd.get_crit_damage()))))

    damage = nxd.get_6_ming_damage(man_ji_hua)
    print("满命业障除蔓激化：不暴{}, 暴击{}".format(round(damage), round(damage * (1 + nxd.get_crit_damage()))))


def print_jiu_qi_ren_damage(monster: Monster):
    a_ren_elem_mastery = [829, 
                          829 + 150,
                          829 + 150 + jiu_qi_ren_max_hp * 0.0012,
                          829 + 150 + jiu_qi_ren_max_hp * 0.0012 * 2,
                          829 + 150 + jiu_qi_ren_max_hp * 0.0012 * 3 + jiu_qi_ren_max_hp * 0.002
                          ]
    print("阿忍可能的精通值：", str(a_ren_elem_mastery))
    a_ren_damages = [round(1446.85 * 3 * (1 + 16 * em / (em + 2000)) * monster.kang_xin_xi_su) for em in a_ren_elem_mastery]
    a_ren_crit_damages = [round(d * 2) for d in a_ren_damages]
    print("阿忍可能的种子伤害：", str(a_ren_damages))
    print("种子暴击伤害:", str(a_ren_crit_damages))

def print_cao_xing_jiu_zhong_damages(nxd_init: Na_Xi_Da_Ch):
    nxd = copy.deepcopy(nxd_init)

    monster = Monster(level=93)
    #monster.set_kang_xin(2.1)
    print(monster)
    # 钟离 e
    monster.add_jian_kang(0.2)

    no_reaction = Ys_No_Reaction(nxd, monster)
    man_ji_hua = Ys_Reaction_JiHua(nxd, monster, JiHua_Type.Man_JiHua)

    # 手法1(阿忍苍古): 钟离 e, 纳西妲 eq, 行秋 eqea 久岐忍 e，纳西妲 aaaaaa......
    # 手法2(阿忍圣显)：钟离 e, 纳西妲 e, 行秋 eqea，久岐忍 eaaaa，纳西妲 q aaaaaaa
    #   优点：阿忍先叠层，纳西妲开大加更多精通，而且纳西妲q后有足够的时间打6下
    #   缺点：阿忍叠层期间会点两次种子，伤害会少，不过仅限于开局第一轮
    # 手法3(阿忍圣显)：钟离 e，纳西妲 e，行秋 eqea，纳西妲 q, 久岐忍eaaaa，纳西妲 aaaaaaa
    #   优点：阿忍吃到纳西妲q精通加成，两次种子伤害高些
    #   缺点：纳西妲开q时，阿忍才829精通，q的精通加成会少37左右，蔓激化伤害会少1.8%左右
    # 默认的算法没有小数，为了伤害数字更准确些，这里都写死了
    #（注：需配合get_debug_raw_score_list里的圣遗物组合、阿忍的面板、纳西妲命座进行调整)

    # 对应：get_debug_raw_score_list_1
    # nxd.set_atk(1352.58)
    # init_elem_mastery = 668.75
    # e_with_sheng_xian_mastery = 847.29
    # full_elem_mastery =  1092

    # 对应： get_debug_raw_score_list_2
    init_elem_mastery = 713
    e_with_sheng_xian_mastery = 713 + 100 + jiu_qi_ren_max_hp * 0.002 
    full_elem_mastery =  713 + 100 +  jiu_qi_ren_max_hp * 0.002 + jiu_qi_ren_elem_mastery * 0.25
    
    nxd.set_elem_mastery(init_elem_mastery)

    # 对怪的第一个e吃不到二命减防以及四草套减抗
    damage = nxd.get_short_e_damage(no_reaction)
    print_damage(nxd, "首次短按e技能直伤", damage)

    damage = nxd.get_long_e_damage(no_reaction)
    print_damage(nxd, "首次长按e技能直伤", damage)

    if nxd.ming_zuo_num >= 4:
        # 对单测试
        nxd.set_elem_mastery(init_elem_mastery + 100)

    # 草套减抗生效
    monster.add_jian_kang(0.3)

    # 行秋触发绽放，进而触发灭净三业，但此时没有激化，只有直伤，且二命减防不生效
    damage = nxd.get_mie_jing_san_ye_damage(no_reaction)
    print_damage(nxd, "行秋触发灭净三业", damage)

    # 久岐忍e后站场等圣显叠层，触发灭净三业，激化，二命减防生效
    if nxd.ming_zuo_num >= 2:
        monster.add_jian_fang(0.3)
    print(monster)
    
    damage = nxd.get_mie_jing_san_ye_damage(no_reaction)
    print_damage(nxd, "二命减防后灭净三业直伤", damage)
    damage = nxd.get_mie_jing_san_ye_damage(man_ji_hua)
    print_damage(nxd, "二命减防后灭净三业蔓激化", damage)

    nxd.q_exist = True
    damage = nxd.get_mie_jing_san_ye_damage(no_reaction)
    print_damage(nxd, "二命减防后灭净三业直伤(大)", damage)
    damage = nxd.get_mie_jing_san_ye_damage(man_ji_hua)
    print_damage(nxd, "二命减防后灭净三业蔓激化(大)", damage)
    nxd.q_exist = False

    # 种子伤害不受防御影响，阿忍出场了，计算一下种子伤害
    print("有钟离盾时种子伤害：")
    print_jiu_qi_ren_damage(monster)
    monster.sub_jian_kang(0.2)
    print("无钟离盾时种子伤害：")
    print_jiu_qi_ren_damage(monster)
    monster.add_jian_kang(0.2)

    nxd.set_elem_mastery(e_with_sheng_xian_mastery)
    damage = nxd.get_mie_jing_san_ye_damage(no_reaction)
    print_damage(nxd, "圣显叠满层后灭净三业直伤", damage)
    damage = nxd.get_mie_jing_san_ye_damage(man_ji_hua)
    print_damage(nxd, "圣显叠满层后灭净三业蔓激化", damage)

    # 纳西妲开Q：注意看留给纳西妲的站场时间
    nxd.q_exist = True

    damage = nxd.get_mie_jing_san_ye_damage(no_reaction)
    print_damage(nxd, "圣显叠满层后灭净三业直伤(大)", damage)
    damage = nxd.get_mie_jing_san_ye_damage(man_ji_hua)
    print_damage(nxd, "圣显叠满层后灭净三业蔓激化大", damage)

    # 切纳西妲站场
    nxd.set_elem_mastery(full_elem_mastery)

    print("纳西妲站场，有钟离盾：")
    print_na_xi_da_in_front(nxd, no_reaction, man_ji_hua)

    print("纳西妲站场，无钟离盾：")
    monster.sub_jian_kang(0.2)
    print_na_xi_da_in_front(nxd, no_reaction, man_ji_hua)

def calc_na_xi_da_damage_in_front(nxd: Na_Xi_Da_Ch, monster: Monster):
    # 下面的计算统一按吃到以下 buff 计算，虽然第一轮时，有些伤害是吃不到这些 buff 的
    # 默认大招都在
    nxd.q_exist = True
    
    # 默认有纳西妲二命减防
    if nxd.ming_zuo_num >= 2:
        monster.add_jian_fang(0.3)
    # 默认吃到四草套减抗
    monster.add_jian_kang(0.3)
    # 默认阿忍圣显叠满层
    nxd.add_elem_mastery(sheng_xian_elem_mastery)
    
    # 一轮伤害构成：
    # 纳西妲不在前台：灭净三业直伤3次
    # 纳西妲在前台：
    #   2个短e: 1 次直伤，1 次蔓激化
    #   普攻：三轮四段普攻，其中 3 次蔓激化
    #   灭净三业：共计 6 次，其中 3 次蔓激化
    #   满命业障除：共计 6 次，其中 2 次蔓激化

    no_reaction = Ys_No_Reaction(nxd, monster)
    man_ji_hua = Ys_Reaction_JiHua(nxd, monster, JiHua_Type.Man_JiHua)
    
    nxd.total_damage = 0

    nxd.total_damage += nxd.get_mie_jing_san_ye_damage(no_reaction) * 3
   
    # 纳西妲站场
    gu_you_tian_fu_1 = min(250, round(jiu_qi_ren_elem_mastery * 0.25))
    nxd.add_elem_mastery(gu_you_tian_fu_1)

    nxd.total_damage += nxd.get_short_e_damage(no_reaction)
    nxd.total_damage += nxd.get_short_e_damage(man_ji_hua)

    # 普攻本身伤害不计算，只计算蔓激化，这里都按第一段来
    nxd.total_damage += nxd.get_a_damage(1, man_ji_hua) * 3

    nxd.total_damage += nxd.get_mie_jing_san_ye_damage(no_reaction) * 3
    nxd.total_damage += nxd.get_mie_jing_san_ye_damage(man_ji_hua) * 3

    if nxd.ming_zuo_num >= 6:
        nxd.total_damage += nxd.get_6_ming_damage(no_reaction) * 4
        nxd.total_damage += nxd.get_6_ming_damage(man_ji_hua) * 2


def calc_damage_of_cao_xin_jiu_zhong(syw_combine: list[ShengYiWu]) -> Na_Xi_Da_Ch:
    nxd = Na_Xi_Da_Ch(teammate_types=[Ys_Elem_Type.LEI, Ys_Elem_Type.SHUI, Ys_Elem_Type.YAN])
    # 作为前台站场主C使用
    nxd.scan_syw_combine(syw_combine=syw_combine, in_front=True)
    if not nxd.is_syw_ok():
        return None
    
    if enable_debug:
        print_cao_xing_jiu_zhong_damages(nxd)

    monster = Monster()

    # 钟离 e
    monster.add_jian_kang(0.2)
    # 钟离四千岩，不过钟离柱子的覆盖率不高
    # nxd.add_atk_per(0.2)

    calc_na_xi_da_damage_in_front(nxd, monster)

    return nxd


def calc_damage_of_cao_xing_jiu_yao(syw_combine: list[ShengYiWu]) -> Na_Xi_Da_Ch:
    nxd = Na_Xi_Da_Ch(teammate_types=[Ys_Elem_Type.LEI, Ys_Elem_Type.SHUI, Ys_Elem_Type.CAO])
    # 作为前台站场主C使用
    nxd.scan_syw_combine(syw_combine=syw_combine, in_front=True)
    if not nxd.is_syw_ok():
        return None

    monster = Monster()

    # 瑶瑶 e
    nxd.add_all_bonus(0.15) # 瑶瑶一命
    # 瑶瑶带千岩4件套，因为纳西妲一般是帖着怪输出的，覆盖率不错
    nxd.add_atk_per(0.2)

    calc_na_xi_da_damage_in_front(nxd, monster)

    return nxd

def calculate_score_callback(score_data: ShengYiWu_Score):
    nxd = calc_damage_of_cao_xin_jiu_zhong(score_data.syw_combine)
    #nxd = calc_damage_of_cao_xing_jiu_yao(score_data.syw_combine)
    if not nxd:
        return False

    score_data.damage_to_score(nxd.total_damage, nxd.get_real_crit_rate(), nxd.get_crit_damage())
    score_data.custom_data = [ nxd.get_elem_mastery(), int(nxd.get_atk()), 
                              round(nxd.get_crit_rate(), 3), round(nxd.get_real_crit_rate(), 3), 
                              round(nxd.get_crit_damage(), 3), 
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

def get_debug_raw_score_list_2():
    # [(shen_lin, h, cc:0.078, cd:0.225, atkp:0.087, elem:37), 
    #  (ru_lei, y, cc:0.066, cd:0.218, re:0.065, elem:63), 
    #  (shen_lin, s, cc:0.128, cd:0.117, hp:538, re:0.045, elem:187), 
    #  (shen_lin, b, cc:0.113, hpp:0.087, re:0.123, atk:19, bonus:0.466), 
    #  (shen_lin, t, cc:0.066, cd:0.622, atkp:0.152, def:32, elem:47)]
    syw_combine = [
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_HUA,
                  crit_rate=0.078, crit_damage=0.225, atk_per=0.087, elem_mastery=37),
        ShengYiWu(ShengYiWu.RU_LEI, ShengYiWu.PART_YU,
                  crit_rate=0.066, crit_damage=0.218, energy_recharge=0.065, elem_mastery=63),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_SHA, elem_mastery=ShengYiWu.ELEM_MASTERY_MAIN,
                  crit_rate=0.128, crit_damage=0.117, hp=538, energy_recharge=0.045),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_BEI, elem_bonus=ShengYiWu.BONUS_MAX, elem_type=Ys_Elem_Type.CAO,
                  crit_rate=0.113, hp_percent=0.087, energy_recharge=0.123, atk=19),
        ShengYiWu(ShengYiWu.SHEN_LIN, ShengYiWu.PART_TOU, crit_damage=ShengYiWu.CRIT_DAMAGE_MAIN,
                  crit_rate=0.066, atk_per=0.152, def_v=332, elem_mastery=47)
    ]

    return [ShengYiWu_Score(syw_combine)]

def get_debug_raw_score_list_1():
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
        return get_debug_raw_score_list_2()
    
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
