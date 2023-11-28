#!/user/bin/env python3 -tt
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

import sys
import os
import logging
import itertools
from base_syw import ShengYiWu, calculate_score, find_syw


ming_zuo_num = 6
include_extra = False    # 某些配队，在芙芙大招结束后还继续输出，不切芙芙出来续大，此时将include_extra置为True
has_na_wei_lai_te = False

if ming_zuo_num < 6:
    only_e = True
else:
    only_e = False

e_extra_damage = 1.4  # 队友大于50%血量，e技能伤害为原来的1.4倍 （注：实测为1.542倍)

if ming_zuo_num >= 2:
    ming_2_hp_bonus_max = 1.4  # 140%
else:
    ming_2_hp_bonus_max = 0

if ming_zuo_num >= 3:
    FU_REN_BEI_LV = 6.87
    XUN_JUE_BEI_LV = 12.67
    PANG_XIE_BEI_LV = 17.61
else:
    FU_REN_BEI_LV = 5.82
    XUN_JUE_BEI_LV = 10.73
    PANG_XIE_BEI_LV = 14.92

if ming_zuo_num >= 5:
    shui_shen_q_bonus_bei_lv = 0.0031
else:
    shui_shen_q_bonus_bei_lv = 0.0025

shui_shen_q_bonus = 400 * shui_shen_q_bonus_bei_lv
fu_ning_na_Max_Hp = 15307.0


def match_sha_callback(syw: ShengYiWu):
    return syw.hp_percent == 0.466


def match_bei_callback(syw: ShengYiWu):
    return syw.hp_percent == 0.466 or syw.elem_type == ShengYiWu.ELEM_TYPE_SHUI


def match_syw(s: ShengYiWu, expect_name):
    if s.name != expect_name:
        return False

    if s.part == ShengYiWu.PART_SHA:
        return match_sha_callback(s)
    elif s.part == ShengYiWu.PART_BEI:
        return match_bei_callback(s)
    else:
        return True


def find_combine_callback():
    # return [
    #     (ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_HUA, 
    #               crit_rate=0.035, crit_damage=0.218, hp_percent=0.157, atk=31),
    #     ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_YU, 
    #               crit_rate=0.117, crit_damage=0.194, def_v=23, elem_mastery=23),
    #     ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_SHA,
    #               crit_rate=0.074, crit_damage=0.218, hp_percent=ShengYiWu.BONUS_MAX, energe_recharge=0.091,  atk=18),
    #     ShengYiWu(ShengYiWu.JUE_DOU_SHI, ShengYiWu.PART_TOU, crit_rate=ShengYiWu.CRIT_RATE_MAIN,
    #               crit_damage=0.303, hp_percent=0.053, hp=209, atk=39))
    # ]

    ju_tuan = find_syw(
        match_syw_callback=lambda s: match_syw(s, ShengYiWu.JU_TUAN))
    hua_hai = find_syw(
        match_syw_callback=lambda s: match_syw(s, ShengYiWu.HUA_HAI))
    qian_yan = find_syw(
        match_syw_callback=lambda s: match_syw(s, ShengYiWu.QIAN_YAN))
    chen_lun = find_syw(
        match_syw_callback=lambda s: match_syw(s, ShengYiWu.CHEN_LUN))
    shui_xian = find_syw(
        match_syw_callback=lambda s: match_syw(s, ShengYiWu.SHUI_XIAN))

    ju_tuan_4_combins = list(itertools.combinations(ju_tuan, 4))

    ju_tuan_2_combins = list(itertools.combinations(ju_tuan, 2))
    hua_hai_combins = list(itertools.combinations(hua_hai, 2))
    qian_yan_combins = list(itertools.combinations(qian_yan, 2))
    chen_lun_combins = list(itertools.combinations(chen_lun, 2))
    shui_xian_combins = list(itertools.combinations(shui_xian, 2))

    all_combins_2 = hua_hai_combins + qian_yan_combins + \
        chen_lun_combins + shui_xian_combins + ju_tuan_2_combins
    all_combins = [(l[0] + l[1])
                   for l in list(itertools.combinations(all_combins_2, 2))] + ju_tuan_4_combins

    # print(len(all_combins))
    # print(len(set(all_combins)))
    return all_combins




# 三小只行动模式
# 占按e:  00:00:06.764
# e出伤害数字: 00:00:07.164
# 以下时间戳都是以打不动的怪物时出伤害数字为准，括号中为距离点按e的时间
# 夫人：00:00:08.564			(1.8s)
# 螃蟹：00:00:08.964			(2.2s)
# 勋爵：00:00:09.164			(2.4s)
# 夫人：00:00:10.204			(3.44s)
# 2~6命时：叠满
# 夫人：00:00:11.923			(5.159s)
# 勋爵：00:00:12.524			(5.76s)
# 夫人：00:00:13.484			(6.72s)
# 螃蟹：00:00:14.364			(7.6s)
# 夫人：00:00:15.164			(8.4s)
# 0~1命时叠满1/4，有那维莱特时，以下三次各多加16/32/48点气氛值
# 勋爵：00:00:15.844			(9.08s)
# 夫人：00:00:16.764			(10s)
# 2~6命时叠满140%生命
# 夫人：00:00:18.364			(11.6s)
# 0~1命时叠满2/4
# 勋爵：00:00:19.164			(12.4s)
# 螃蟹：00:00:19.484			(12.72)
# 夫人：00:00:20.124			(13.36)
# 有那维莱特时，此时3/4，以下3次各多加48点， 再多加16/32/48点
# 夫人：00:00:21.804			(15.04)
# 勋爵：00:00:22.644			(15.88)
# 夫人：00:00:23.444			(16.68)
# 0~1命时叠满3/4，有水龙王时，此时叠满
# 螃蟹：00:00:24.684			(17.92)
# 夫人：00:00:25.084			(18.32)
# 勋爵：00:00:25.923			(19.159)
# 夫人：00:00:26.684			(19.92)
# 0~5命，eq起手时，此时大招消失
# 满命，qea起手时，大招差不多也是此时消失
# 夫人：00:00:28.204			(21.44)
# 勋爵：00:00:29.404			(22.64)
# 夫人：00:00:29.724			(22.96)
# 螃蟹：00:00:29.764			(23)

# 一轮循环按24秒算，以下的输出为一些特殊配队才有
# 夫人：00:00:31.204			(24.44)
# 勋爵：00:00:32.564			(25.8)
# 夫人：00:00:32.724			(25.96)
# 夫人：00:00:34.364			(27.6)
# 螃蟹：00:00:35.084			(28.32)
# 勋爵：00:00:35.804			(29.04)
# 夫人：00:00:35.884			(29.12)
# 三小只消失：00:00:36.123，从点按e到消失，共计29.359秒
#
# 0~1命：影响伤害量的有两个因素，一是圣遗物的好杯，二是配队手法叠层的速度
# eq起手+奶妈
# ========
# 点按e: 01:50:11.923
# 点按q: 01:50:12.844  (0.921)
# 全队奶：01:50:20.204     (8.281)
# 1/4: 01:50:20.444		（8.521）
# 2/4: 01:50:24.124		（12.201）
# 3/4: 01:50:29.004		（17.081）
# 大招消失：01:50:32.534   （20.611）
#
# 有那维莱特这样会烧血回血队友时
# 点按e: 00:00:01.268
# 点按q: 00:00:04.867
# 00:00:08.146 那维莱特第一次，此时满血，因此只有接下来的三秒16/32/48
# 1/4: 00:00:08.268     (7)
# 2/4: 00:00:12.701     (11.433)
# 3/4: 00:00:15.668     (14.4)
# 00:00:15.733:  那维莱特第二次，瞬间48层，接下来的三秒16/32/48
# 叠满: 00:00:18.134     (16.866)
# 大招消失：00:00:24.4
#
# 2~5命：即便不带奶奶，也能6秒左右叠满层，带奶妈的情况下就更快了
# 同样，我们还是只计算第一轮，叠满层也以4.5秒计算，
# 2命叠满后，血量接着会变化，一般5.5秒左右面能叠满140%血量，因为此时不挨打又没奶妈，比叠满层慢一些
#
# 满命：一般是不带奶妈的，采用qea的方式，叠满层4.5秒左右
# 点按q: 00:00:02.05
# 点按e: 00:00:04.286   (2.236)
#
# 注：一轮循环按24秒计算

class e_damage_component:
    def __init__(self, bei_lv, hp, bonus, is_extra=False):
        self.bei_lv = bei_lv
        self.__hp = hp
        self.bonus = bonus
        self.is_extra = is_extra

    def score(self):
        return self.__hp * self.bei_lv / 100 * e_extra_damage * self.bonus

class Qi:
    FU_RE_QI_FEN_ZHI = 1.6
    XUN_JUE_QI_FEN_ZHI = 2.4
    PANG_XIE_QI_FEN_ZHI = 3.6

    MING_2_HP_BEI_LV =  0.0035

    def __init__(self, hp, e_bonus):
        self.q_stopped = False
        if ming_zuo_num > 0:
            self.initial_qi = 150
        else:
            self.initial_qi = 0

        self.__qi = self.initial_qi
        #print("inital qi: " + str(self.__qi))

        self.__hp = hp
        self.__extra_qi = 0
        self.e_bonus_withoud_q = e_bonus - shui_shen_q_bonus

    def append(self, new_qi, bei_lv = 0):
        if ming_zuo_num >= 2 and bei_lv == 0:
            new_qi *= 3.5
        else:
            new_qi *= bei_lv
        self.__qi += new_qi

        if ming_zuo_num > 0 and self.__qi > 400:
            if ming_zuo_num >= 2:
                self.__extra_qi += self.__qi - 400
                if self.__extra_qi > 400:
                    self.__extra_qi = 400
            self.__qi = 400
        
        if ming_zuo_num == 0 and self.__qi > 300:
            self.__qi = 300

    def append_fu_ren(self, is_extra = False):
        edc = e_damage_component(FU_REN_BEI_LV, self.hp(), self.e_bonus(), is_extra)
        self.append(4 * Qi.FU_RE_QI_FEN_ZHI)
        return edc

    def append_xun_jue(self, is_extra = False):
        edc = e_damage_component(XUN_JUE_BEI_LV, self.hp(), self.e_bonus(), is_extra)
        self.append(4 * Qi.XUN_JUE_QI_FEN_ZHI)
        return edc

    def append_pang_xie(self, is_extra = False):
        edc = e_damage_component(PANG_XIE_BEI_LV, self.hp(), self.e_bonus(), is_extra)
        self.append(4 * Qi.PANG_XIE_QI_FEN_ZHI)
        return edc

    def stop(self):
        self.q_stopped = True

    def qi(self):
        return self.__qi
    
    def extra_qi(self):
        return self.__extra_qi
    
    def e_bonus(self):
        if self.q_stopped:
            return self.e_bonus_withoud_q
        else:
            return self.e_bonus_withoud_q + self.__qi * shui_shen_q_bonus_bei_lv
    
    def hp(self):
        if self.q_stopped:
            return self.__hp
        else:
            return int(self.__hp + self.__extra_qi * Qi.MING_2_HP_BEI_LV * fu_ning_na_Max_Hp)
        
    def __str__(self):
        return str(self.qi()) +  "(" + str(self.extra_qi()) + ")" + ", " + str(self.e_bonus()) + ", " + str(self.hp())

    def __repr__(self) -> str:
        return self.__str__()

def construct_e_damage_list_for_0_5_ming(hp, e_bonus):
    e_damage_patter_0_5_ming = []
    qi = Qi(hp, e_bonus)

    # 夫人：00:00:08.564			(1.8s)
    e_damage_patter_0_5_ming.append(qi.append_fu_ren())
    # 螃蟹：00:00:08.964			(2.2s)
    e_damage_patter_0_5_ming.append(qi.append_pang_xie())
    # 勋爵：00:00:09.164			(2.4s)
    e_damage_patter_0_5_ming.append(qi.append_xun_jue())
    # 夫人：00:00:10.204			(3.44s)
    e_damage_patter_0_5_ming.append(qi.append_fu_ren())

    # 夫人：00:00:11.923			(5.159s)
    e_damage_patter_0_5_ming.append(qi.append_fu_ren())

    # 全队奶，假设能奶满
    exhausted_hp_per = qi.qi() - qi.initial_qi
    # print("checkpoint1: " + str(qi) + ", exhausted_hp_per:" + str(exhausted_hp_per))
    qi.append(exhausted_hp_per, 1)

    # print("checkpoint2: " + str(qi))

    # 勋爵：00:00:12.524			(5.76s)
    e_damage_patter_0_5_ming.append(qi.append_xun_jue())
    # 夫人：00:00:13.484			(6.72s)
    e_damage_patter_0_5_ming.append(qi.append_fu_ren())
    # 螃蟹：00:00:14.364			(7.6s)
    e_damage_patter_0_5_ming.append(qi.append_pang_xie())
    # 夫人：00:00:15.164			(8.4s)
    e_damage_patter_0_5_ming.append(qi.append_fu_ren())

    # 此时那维莱特满血，所以没有回血的48加成
    if has_na_wei_lai_te:
        qi.append(16)
    
    # 勋爵：00:00:15.844			(9.08s)
    e_damage_patter_0_5_ming.append(qi.append_xun_jue())
    # 夫人：00:00:16.764			(10s)
    if has_na_wei_lai_te:
        qi.append(16)
    e_damage_patter_0_5_ming.append(qi.append_fu_ren())
    # 夫人：00:00:18.364			(11.6s)
    if has_na_wei_lai_te:
        qi.append(16)
    e_damage_patter_0_5_ming.append(qi.append_fu_ren())
    # 勋爵：00:00:19.164			(12.4s)
    e_damage_patter_0_5_ming.append(qi.append_xun_jue())
    # 螃蟹：00:00:19.484			(12.72)
    e_damage_patter_0_5_ming.append(qi.append_pang_xie())
    # 夫人：00:00:20.124			(13.36)
    e_damage_patter_0_5_ming.append(qi.append_fu_ren())

    # 有那维莱特时，以下3次各多加48点， 再多加16/32/48点
    if has_na_wei_lai_te:
        qi.append(48 + 16)

    # 夫人：00:00:21.804			(15.04)
    e_damage_patter_0_5_ming.append(qi.append_fu_ren())
    # 勋爵：00:00:22.644			(15.88)
    if has_na_wei_lai_te:
        qi.append(16)
    e_damage_patter_0_5_ming.append(qi.append_xun_jue())
    # 夫人：00:00:23.444			(16.68)
    if has_na_wei_lai_te:
        qi.append(16)
    e_damage_patter_0_5_ming.append(qi.append_fu_ren())
    # 0~1命时叠满3/4，有水龙王时，此时叠满
    # 螃蟹：00:00:24.684			(17.92)
    e_damage_patter_0_5_ming.append(qi.append_pang_xie())
    # 夫人：00:00:25.084			(18.32)
    e_damage_patter_0_5_ming.append(qi.append_fu_ren())
    # 勋爵：00:00:25.923			(19.159)
    e_damage_patter_0_5_ming.append(qi.append_xun_jue())
    # 夫人：00:00:26.684			(19.92)
    e_damage_patter_0_5_ming.append(qi.append_fu_ren())

    # 大招消失
    #print("before q stop: " + str(qi))
    qi.stop()
    #print("after q stop: " + str(qi))

    # 夫人：00:00:28.204			(21.44)
    e_damage_patter_0_5_ming.append(qi.append_fu_ren())
    # 勋爵：00:00:29.404			(22.64)
    e_damage_patter_0_5_ming.append(qi.append_xun_jue())
    # 夫人：00:00:29.724			(22.96)
    e_damage_patter_0_5_ming.append(qi.append_fu_ren())
    # 螃蟹：00:00:29.764			(23)
    e_damage_patter_0_5_ming.append(qi.append_pang_xie())

    # 一轮循环按24秒算，以下的输出为一些特殊配队才有
    # 夫人：00:00:31.204			(24.44)
    e_damage_patter_0_5_ming.append(qi.append_fu_ren(is_extra=True))
    # 勋爵：00:00:32.564			(25.8)
    e_damage_patter_0_5_ming.append(qi.append_xun_jue(is_extra=True))
    # 夫人：00:00:32.724			(25.96)
    e_damage_patter_0_5_ming.append(qi.append_fu_ren(is_extra=True))
    # 夫人：00:00:34.364			(27.6)
    e_damage_patter_0_5_ming.append(qi.append_fu_ren(is_extra=True))
    # 螃蟹：00:00:35.084			(28.32)
    e_damage_patter_0_5_ming.append(qi.append_pang_xie(is_extra=True))
    # 勋爵：00:00:35.804			(29.04)
    e_damage_patter_0_5_ming.append(qi.append_xun_jue(is_extra=True))
    # 夫人：00:00:35.884			(29.12)
    e_damage_patter_0_5_ming.append(qi.append_fu_ren(is_extra=True))

    return e_damage_patter_0_5_ming

def construct_e_damage_list_for_bai_fu(hp, e_bonus):
    full_hp = hp + int(fu_ning_na_Max_Hp * ming_2_hp_bonus_max)
    e_bonus_withoud_q = e_bonus - shui_shen_q_bonus

    e_damage_list_man_ming_bai_fu = [
        # 满命，切白芙砍三刀，再切回黑芙时，三小只的行动模式
        # 测试方法：钟离长e, 芙芙qea，琴e，夜兰eqe，芙芙zaaaz然后站场观察三小只的行动模式
        e_damage_component(FU_REN_BEI_LV, hp,
                           e_bonus_withoud_q + 200 * shui_shen_q_bonus_bei_lv),
        e_damage_component(PANG_XIE_BEI_LV, hp,
                           e_bonus_withoud_q + 200 * shui_shen_q_bonus_bei_lv),
        e_damage_component(XUN_JUE_BEI_LV, hp,
                           e_bonus_withoud_q + 200 * shui_shen_q_bonus_bei_lv),

        e_damage_component(FU_REN_BEI_LV, hp,
                           e_bonus_withoud_q + 300 * shui_shen_q_bonus_bei_lv),
        # 第五次夫人的攻击无限接近满层
        e_damage_component(FU_REN_BEI_LV, hp,
                           e_bonus_withoud_q + 400 * shui_shen_q_bonus_bei_lv),

        # 增伤满层，但二命的生命还会继续叠层
        e_damage_component(XUN_JUE_BEI_LV, hp + \
                           int(0.3 * fu_ning_na_Max_Hp), e_bonus),
        e_damage_component(FU_REN_BEI_LV, hp + \
                           int(0.399 * fu_ning_na_Max_Hp), e_bonus),

        # 切白芙，三小只消失
        # 再切黑芙，三小只出来，行动模式重置
        e_damage_component(FU_REN_BEI_LV, hp + \
                           int(1.3 * fu_ning_na_Max_Hp), e_bonus),
        e_damage_component(PANG_XIE_BEI_LV, full_hp, e_bonus),
        e_damage_component(XUN_JUE_BEI_LV, full_hp, e_bonus),
        e_damage_component(FU_REN_BEI_LV, full_hp, e_bonus),
        e_damage_component(FU_REN_BEI_LV, full_hp, e_bonus),
        e_damage_component(XUN_JUE_BEI_LV, full_hp, e_bonus),
        e_damage_component(FU_REN_BEI_LV, full_hp, e_bonus),

        # 大招消失了，但芙芙的血量没变化，气氛值还在
        e_damage_component(PANG_XIE_BEI_LV, full_hp, e_bonus),

        # 大招结束
        e_damage_component(FU_REN_BEI_LV, hp, e_bonus_withoud_q),
        e_damage_component(XUN_JUE_BEI_LV, hp, e_bonus_withoud_q),
        e_damage_component(FU_REN_BEI_LV, hp, e_bonus_withoud_q),
        e_damage_component(FU_REN_BEI_LV, hp, e_bonus_withoud_q),
        e_damage_component(XUN_JUE_BEI_LV, hp, e_bonus_withoud_q),

        # 一轮循环(大约24秒)之外，某些配队才有这些
        # --------
        # 00:00:36.050				螃蟹
        e_damage_component(PANG_XIE_BEI_LV, hp,
                           e_bonus_withoud_q, is_extra=True),
        # 00:00:36.703				夫人
        e_damage_component(FU_REN_BEI_LV, hp,
                           e_bonus_withoud_q, is_extra=True),
        # 00:00:38.752				夫人
        e_damage_component(FU_REN_BEI_LV, hp,
                           e_bonus_withoud_q, is_extra=True),
        # 00:00:39.651				勋爵
        e_damage_component(XUN_JUE_BEI_LV, hp,
                           e_bonus_withoud_q, is_extra=True),
        # 00:00:40.711				夫人
        e_damage_component(FU_REN_BEI_LV, hp,
                           e_bonus_withoud_q, is_extra=True),
        # 00:00:42.791				螃蟹
        e_damage_component(PANG_XIE_BEI_LV, hp,
                           e_bonus_withoud_q, is_extra=True),
        # 00:00:42.916				夫人
        e_damage_component(FU_REN_BEI_LV, hp,
                           e_bonus_withoud_q, is_extra=True),
        # 00:00:44.175				勋爵
        e_damage_component(XUN_JUE_BEI_LV, hp,
                           e_bonus_withoud_q, is_extra=True),
        # 00:00:44.973				夫人，然后三小只消失
        e_damage_component(XUN_JUE_BEI_LV, hp,
                           e_bonus_withoud_q, is_extra=True),
    ]

    return e_damage_list_man_ming_bai_fu


def calc_score(hp, e_bonus, full_bonus, crit_rate, crit_damage):
    if only_e:
        e_damage_list = construct_e_damage_list_for_0_5_ming(hp, e_bonus)
    else:
        e_damage_list = construct_e_damage_list_for_bai_fu(hp, e_bonus)

    e_score_non_crit = 0

    for d in e_damage_list:
        if d.is_extra and not include_extra:
            break

        e_score_non_crit += d.score()

    e_score_crit = e_score_non_crit * crit_damage
    e_score_expect = e_score_non_crit * (1 + crit_rate * (crit_damage - 1))

    if not only_e:
        # 采用qea 万叶e, 夜兰qee，这种手法能更快速叠层
        class full_damage_component:
            def __init__(self, hp_bonus, bei_lv):
                self.__hp_bonus = hp_bonus
                self.bei_lv = bei_lv

            def score(self):
                return (hp + int(self.__hp_bonus * fu_ning_na_Max_Hp)) * self.bei_lv / 100 * full_bonus

        HEI_FU_BEI_LV = 18
        BAI_FU_BEI_LV = 18 + 25

        hp_bonus_list = [
            full_damage_component(0, HEI_FU_BEI_LV),
            full_damage_component(0.4, HEI_FU_BEI_LV),
            full_damage_component(0.48, HEI_FU_BEI_LV),
            full_damage_component(0.6, BAI_FU_BEI_LV),
            full_damage_component(0.9, BAI_FU_BEI_LV),
            full_damage_component(1.0, BAI_FU_BEI_LV)
        ]

        full_six_damage_non_crit = 0
        for d in hp_bonus_list:
            full_six_damage_non_crit += d.score()

        full_six_damage_crit = full_six_damage_non_crit * crit_damage
        full_six_damage_expect = full_six_damage_non_crit * \
            (1 + crit_rate * (crit_damage - 1))
    else:
        full_six_damage_crit = 0
        full_six_damage_expect = 0

    all_crit = e_score_crit + full_six_damage_crit
    all_expect = e_score_expect + full_six_damage_expect

    return (all_crit, all_expect, round(full_six_damage_crit / all_crit, 3), round(full_six_damage_expect / all_expect, 3))


def calculate_score_callback(combine: list[ShengYiWu]):
    extra_crit_damage = {
        "专武": 0.882
    }

    common_elem_bonus = {
        "万叶": 0.4,
        "夜兰平均增伤": 0.25,
        "芙芙Q增伤": shui_shen_q_bonus,
    }

    extra_e_bonus = {
        "固有天赋2": 0.28,  # 基本是能吃满的，操作得当，生命基本能保持在50%以上
        "专武": 0.08 * 3,

    }

    extra_hp_bonus = {
        "专武叠满两层": 0.28,
        "双水": 0.25,
        "夜兰四命保底两个e": 0.2,
    }

    crit_rate = 0.242  # 突破加成
    crit_damage = 1 + 0.5 + sum(extra_crit_damage.values())
    hp = 0
    hp_per = 0
    elem_bonus = 1 + sum(common_elem_bonus.values())
    energe_recharge = 1

    for p in combine:
        crit_rate += p.crit_rate
        crit_damage += p.crit_damage
        hp += p.hp
        hp_per += p.hp_percent
        elem_bonus += p.elem_bonus
        energe_recharge += p.energe_recharge

    crit_rate = round(crit_rate, 3)
    if crit_rate < 0.70:
        return None

    energe_recharge *= 100
    energe_recharge = round(energe_recharge, 1)
    if energe_recharge < 110:
        return None

    syw_e_bonus = 0

    syw_names = [p.name for p in combine]
    # print(syw_names)
    name_count = {i: syw_names.count(i) for i in syw_names}
    # print(name_count)
    for n in name_count:
        if name_count[n] < 2:  # 散件不计算套装效果
            continue

        # print(n)
        if n == ShengYiWu.HUA_HAI:
            hp_per += 0.2
        elif n == ShengYiWu.SHUI_XIAN:
            elem_bonus += 0.15
        elif n == ShengYiWu.QIAN_YAN:
            hp_per += 0.2
        elif n == ShengYiWu.CHEN_LUN:
            elem_bonus += 0.15
        elif n == ShengYiWu.JU_TUAN:
            syw_e_bonus += 0.2
            if name_count[n] >= 4:
                syw_e_bonus += 0.25 + 0.25

    all_hp = int(fu_ning_na_Max_Hp * (1
                                      + hp_per
                                      + sum(extra_hp_bonus.values())
                                      )) + hp + 4780
    e_bonus = elem_bonus + sum(extra_e_bonus.values()) + syw_e_bonus

    crit_score, expect_score, full_six_crit_zhan_bi, full_six_expect_zhan_bi = calc_score(
        all_hp, e_bonus, elem_bonus, crit_rate, crit_damage)

    max_hp = all_hp + int(fu_ning_na_Max_Hp * ming_2_hp_bonus_max)
    panel_hp = fu_ning_na_Max_Hp * (1 + hp_per) + 4780 + hp

    return [expect_score, crit_score, full_six_expect_zhan_bi, full_six_crit_zhan_bi, int(max_hp), int(panel_hp), round(e_bonus, 3), round(elem_bonus, 3), round(crit_rate, 3), round(crit_damage - 1, 3), round(energe_recharge, 1), combine]


result_description = ["总评分", "期望伤害评分", "暴击伤害评分", "满命六刀伤害期望占比", "满命六刀暴击伤害占比",
                      "实战最大生命值上限", "面板最大生命值", "战技元素伤害加成", "满命六刀元素伤害加成", "暴击率", "暴击伤害", "充能效率", "圣遗物组合"]


def find_syw_for_fu_ning_na():
    return calculate_score(find_combine_callback=find_combine_callback,
                           match_sha_callback=match_sha_callback,
                           match_bei_callback=match_bei_callback,
                           calculate_score_callbak=calculate_score_callback,
                           result_txt_file="fu_ning_na_syw.txt",
                           result_description=result_description)


# Main body
if __name__ == '__main__':
    find_syw_for_fu_ning_na()
