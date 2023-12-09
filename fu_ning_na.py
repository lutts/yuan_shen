#!/user/bin/env python3 -tt
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

import sys
import os
import logging
import itertools
from base_syw import ShengYiWu, calculate_score, find_syw, calc_expect_score
from ye_lan import YeLanQBonus


ming_zuo_num = 6
include_extra = False    # 某些配队，在芙芙大招结束后还继续输出，不切芙芙出来续大，此时将include_extra置为True
has_na_wei_lai_te = False
has_ye_lan = True

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
    fu_ning_na_q_bonus_bei_lv = 0.0031
else:
    fu_ning_na_q_bonus_bei_lv = 0.0025

fu_ning_na_q_max_bonus = 400 * fu_ning_na_q_bonus_bei_lv
fu_ning_na_Max_Hp = 15307.0

zhuan_wu_hp_bei_lv = 0.14
zhuan_wu_e_bonus_bei_lv = 0.08

extra_crit_damage = {
    "专武": 0.882
}

common_elem_bonus = {
    "万叶": 0.4,
}

extra_e_bonus = {
   #"固有天赋2": 0.28,  # 基本是能吃满的，操作得当，生命基本能保持在50%以上
}

variable_e_bonus = {
    "专武": zhuan_wu_e_bonus_bei_lv * 3
}

extra_hp_bonus = {
    "双水": 0.25,
}

variable_hp_bonus = {
    "专武叠满两层": zhuan_wu_hp_bei_lv * 2,
    "夜兰四命保底两个e": 0.2,
}


def match_sha_callback(syw: ShengYiWu):
    return syw.hp_percent == 0.466 or syw.energe_recharge == ShengYiWu.ENERGE_RECHARGE_MAX


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
    # [(qian_yan, h, cc:0.074, cd:0.078, hpp:0.134, re:0.162),
    #  (jue_dou_shi, y, cc:0.167, cd:0.062, hpp:0.111, re:0.045),
    # (qian_yan, s, cc:0.066, cd:0.21, hpp:0.466, atk:33, elem:40),
    # (hua_hai, b, cc:0.093, cd:0.21, hpp:0.466, defp:0.131, def:23),
    # (hua_hai, t, cc:0.07, cd:0.622, hpp:0.111, hp:687, defp:0.058)]]
    # 只计算双水fixed_hp = (1 + 0.134 + 0.111 + 0.466 + 0.466 + 0.111 + 0.4 + 0.25) * 15307 + 4780 + 687 = 50438
    # fixed_full_bonus = 1 + 万叶0.4 = 1.4
    # fixed_e_bonus = 1 + 万叶0.4 + 固有天赋0.28 = 1.68
    # return [
    #     (ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_HUA,
    #                crit_rate=0.074, crit_damage=0.078, hp_percent=0.134, energe_recharge=0.162),
    #      ShengYiWu(ShengYiWu.JUE_DOU_SHI, ShengYiWu.PART_YU,
    #                crit_rate=0.167, crit_damage=0.062, hp_percent=0.111, energe_recharge=0.045),
    #      ShengYiWu(ShengYiWu.QIAN_YAN, ShengYiWu.PART_SHA,
    #                crit_rate=0.066, crit_damage=0.21, hp_percent=0.466, atk=33, elem_mastery=40),
    #      ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_BEI,
    #                crit_rate=0.093, crit_damage=0.21, hp_percent=0.466, def_per=0.131, def_v=23)
    #      )
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

class E_Damage:
    def __init__(self, bei_lv, hp, bonus, has_feng_tao = True, is_extra=False):
        self.bei_lv = bei_lv
        self.__hp = hp
        self.bonus = bonus
        self.has_feng_tao = has_feng_tao
        self.is_extra = is_extra

    def score(self):
        gu_you_tian_fu_2_bonus = min(self.__hp / 1000 * 0.007, 0.28)
        d = self.__hp * self.bei_lv / 100 * e_extra_damage * (self.bonus + gu_you_tian_fu_2_bonus)
        if not self.has_feng_tao:
            d /= 1.2777 # 风套增伤27.77%
        return d


class Fu_Ren_E_Damage(E_Damage):
    def __init__(self, hp, bonus, has_feng_tao = True, is_extra=False):
        super().__init__(FU_REN_BEI_LV, hp, bonus, has_feng_tao, is_extra)


class Xun_Jue_E_Damage(E_Damage):
    def __init__(self, hp, bonus, has_feng_tao = True, is_extra=False):
        super().__init__(XUN_JUE_BEI_LV, hp, bonus, has_feng_tao, is_extra)


class Pang_Xie_E_Damage(E_Damage):
    def __init__(self, hp, bonus, has_feng_tao = True, is_extra=False):
        super().__init__(PANG_XIE_BEI_LV, hp, bonus, has_feng_tao, is_extra)


class ZhiLiao:
    # 芙芙满命的治疗时机比较复杂，似乎有时候不会同时治疗，暂时不在流程中引入芙芙治疗，等弄懂了具体机制再说
    def __init__(self):
        pass

    def start(self, start_time, interval, duration):
        pass

    def set_teammate_max_hp(self, p2_max_hp, p3_max_hp, p4_max_hp):
        self.p2_max_hp = p2_max_hp
        self.p3_max_hp = p3_max_hp
        self.p4_max_hp = p4_max_hp

    def cure_hp(self):
        return 0

    def cure_hp_percent(self):
        return 0

    def stop(self):
        pass


class Qi:
    FU_RE_QI_FEN_ZHI = 1.6
    XUN_JUE_QI_FEN_ZHI = 2.4
    PANG_XIE_QI_FEN_ZHI = 3.6

    MING_2_HP_BEI_LV = 0.0035

    def __init__(self, hp, e_bonus):
        self.q_stopped = False
        if ming_zuo_num > 0:
            self.initial_qi = 150
        else:
            self.initial_qi = 0

        self.__qi = self.initial_qi
        # print("inital qi: " + str(self.__qi))

        self.__hp = hp
        self.__extra_qi = 0
        self.e_bonus_withoud_q = e_bonus

        self.ye_lan_bonus = YeLanQBonus()
        if not has_ye_lan:
            self.ye_lan_bonus.invalidate()

    def append(self, new_qi, bei_lv=0):
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

    def append_fu_ren(self, timestamp, is_extra=False):
        ed = Fu_Ren_E_Damage(self.hp(), self.e_bonus(timestamp), is_extra)
        self.append(4 * Qi.FU_RE_QI_FEN_ZHI)
        return ed

    def append_xun_jue(self, timestamp, is_extra=False):
        ed = Xun_Jue_E_Damage(self.hp(), self.e_bonus(timestamp), is_extra)
        self.append(4 * Qi.XUN_JUE_QI_FEN_ZHI)
        return ed

    def append_pang_xie(self, timestamp, is_extra=False):
        ed = Pang_Xie_E_Damage(self.hp(), self.e_bonus(timestamp), is_extra)
        self.append(4 * Qi.PANG_XIE_QI_FEN_ZHI)
        return ed

    def stop(self):
        self.q_stopped = True

    def qi(self):
        return self.__qi

    def extra_qi(self):
        return self.__extra_qi

    def e_bonus(self, timestamp):
        if self.q_stopped:
            return self.e_bonus_withoud_q
        else:
            return self.e_bonus_withoud_q + self.ye_lan_bonus.bonus(timestamp) + self.__qi * fu_ning_na_q_bonus_bei_lv
        
    def add_hp(self, extra_hp):
        self.__hp += extra_hp

    def hp(self):
        if self.q_stopped:
            return self.__hp
        else:
            return int(self.__hp + self.__extra_qi * Qi.MING_2_HP_BEI_LV * fu_ning_na_Max_Hp)

    def __str__(self):
        return str(self.qi()) + "(" + str(self.extra_qi()) + ")" + ", " + str(self.e_bonus(0)) + ", " + str(self.hp())

    def __repr__(self) -> str:
        return self.__str__()


def construct_e_damage_list_for_0_5_ming(fixed_hp, fixed_e_bonus):
    e_damage_patter_0_5_ming = []

     # 三小只发动攻击前会扣血，专武叠一层（虽然是三次攻击，但0.2秒内只叠一层)
    qi = Qi(fixed_hp + int(zhuan_wu_hp_bei_lv * fu_ning_na_Max_Hp), 
            fixed_e_bonus + zhuan_wu_e_bonus_bei_lv)

    # 夫人：00:00:08.564			(1.8s)
    e_damage_patter_0_5_ming.append(qi.append_fu_ren(8.564))
    # 螃蟹：00:00:08.964			(2.2s)
    e_damage_patter_0_5_ming.append(qi.append_pang_xie(8.964))
    # 勋爵：00:00:09.164			(2.4s)
    e_damage_patter_0_5_ming.append(qi.append_xun_jue(9.164))

    # 下次攻击发动前扣血，专武又叠一层
    # 夜兰e
    qi.e_bonus_withoud_q += zhuan_wu_e_bonus_bei_lv
    if has_ye_lan:
        qi.add_hp(int((zhuan_wu_hp_bei_lv + 0.1) * fu_ning_na_Max_Hp))
    else:
        qi.add_hp(int(zhuan_wu_hp_bei_lv * fu_ning_na_Max_Hp))

    # 夫人：00:00:10.204			(3.44s)
    e_damage_patter_0_5_ming.append(qi.append_fu_ren(10.204))

    # 下次攻击发动前扣血，专武战技增伤再叠一层（满了)
    qi.e_bonus_withoud_q += zhuan_wu_e_bonus_bei_lv

    qi.ye_lan_bonus.start(11.709)

    # 夫人：00:00:11.923			(5.159s)
    e_damage_patter_0_5_ming.append(qi.append_fu_ren(11.923))

    # 全队奶，假设能奶满
    exhausted_hp_per = qi.qi() - qi.initial_qi
    # print("checkpoint1: " + str(qi) + ", exhausted_hp_per:" + str(exhausted_hp_per))
    qi.append(exhausted_hp_per, 1)

    # 夜eqe结束
    if has_ye_lan:
        qi.add_hp(int(0.1 * fu_ning_na_Max_Hp))

    # print("checkpoint2: " + str(qi))

    # 勋爵：00:00:12.524			(5.76s)
    e_damage_patter_0_5_ming.append(qi.append_xun_jue(12.524))
    # 夫人：00:00:13.484			(6.72s)
    e_damage_patter_0_5_ming.append(qi.append_fu_ren(13.484))
    # 螃蟹：00:00:13.484			(7.6s)
    e_damage_patter_0_5_ming.append(qi.append_pang_xie(13.484))
    # 夫人：00:00:13.484			(8.4s)
    e_damage_patter_0_5_ming.append(qi.append_fu_ren(13.484))

    # 此时那维莱特满血，所以没有回血的48加成
    if has_na_wei_lai_te:
        qi.append(16)

    # 勋爵：00:00:15.844			(9.08s)
    e_damage_patter_0_5_ming.append(qi.append_xun_jue(15.844))
    # 夫人：00:00:15.844			(10s)
    if has_na_wei_lai_te:
        qi.append(16)
    e_damage_patter_0_5_ming.append(qi.append_fu_ren(15.844))
    # 夫人：00:00:18.364			(11.6s)
    if has_na_wei_lai_te:
        qi.append(16)
    e_damage_patter_0_5_ming.append(qi.append_fu_ren(18.364))
    # 勋爵：00:00:19.164			(12.4s)
    e_damage_patter_0_5_ming.append(qi.append_xun_jue(19.164))
    # 螃蟹：00:00:19.484			(12.72)
    e_damage_patter_0_5_ming.append(qi.append_pang_xie(19.484))
    # 夫人：00:00:20.124			(13.36)
    e_damage_patter_0_5_ming.append(qi.append_fu_ren(20.124))

    # 有那维莱特时，以下3次各多加48点， 再多加16/32/48点
    if has_na_wei_lai_te:
        qi.append(48 + 16)

    # 夫人：00:00:21.804			(15.04)
    e_damage_patter_0_5_ming.append(qi.append_fu_ren(21.804))
    # 勋爵：00:00:22.644			(15.88)
    if has_na_wei_lai_te:
        qi.append(16)
    e_damage_patter_0_5_ming.append(qi.append_xun_jue(22.644))
    # 夫人：00:00:23.444			(16.68)
    if has_na_wei_lai_te:
        qi.append(16)
    e_damage_patter_0_5_ming.append(qi.append_fu_ren(23.444))
    # 0~1命时叠满3/4，有水龙王时，此时叠满
    # 螃蟹：00:00:24.684			(17.92)
    e_damage_patter_0_5_ming.append(qi.append_pang_xie(24.684))
    # 夫人：00:00:25.084			(18.32)
    e_damage_patter_0_5_ming.append(qi.append_fu_ren(25.084))
    # 勋爵：00:00:25.923			(19.159)
    e_damage_patter_0_5_ming.append(qi.append_xun_jue(25.923))
    # 夫人：00:00:26.684			(19.92)
    e_damage_patter_0_5_ming.append(qi.append_fu_ren(26.684))

    # 大招消失
    # print("before q stop: " + str(qi))
    qi.stop()
    # print("after q stop: " + str(qi))

    # 夫人：00:00:28.204			(21.44)
    e_damage_patter_0_5_ming.append(qi.append_fu_ren(28.204))
    # 勋爵：00:00:29.404			(22.64)
    e_damage_patter_0_5_ming.append(qi.append_xun_jue(29.404))
    # 夫人：00:00:29.724			(22.96)
    e_damage_patter_0_5_ming.append(qi.append_fu_ren(29.724))
    # 螃蟹：00:00:29.764			(23)
    e_damage_patter_0_5_ming.append(qi.append_pang_xie(29.764))

    # 一轮循环按24秒算，以下的输出为一些特殊配队才有
    # 夫人：00:00:31.204			(24.44)
    e_damage_patter_0_5_ming.append(qi.append_fu_ren(31.204, is_extra=True))
    # 勋爵：00:00:32.564			(25.8)
    e_damage_patter_0_5_ming.append(qi.append_xun_jue(32.564, is_extra=True))
    # 夫人：00:00:32.724			(25.96)
    e_damage_patter_0_5_ming.append(qi.append_fu_ren(32.724, is_extra=True))
    # 夫人：00:00:34.364			(27.6)
    e_damage_patter_0_5_ming.append(qi.append_fu_ren(34.364, is_extra=True))
    # 螃蟹：00:00:35.084			(28.32)
    e_damage_patter_0_5_ming.append(qi.append_pang_xie(35.084, is_extra=True))
    # 勋爵：00:00:35.804			(29.04)
    e_damage_patter_0_5_ming.append(qi.append_xun_jue(35.804, is_extra=True))
    # 夫人：00:00:35.884			(29.12)
    e_damage_patter_0_5_ming.append(qi.append_fu_ren(35.884, is_extra=True))

    return e_damage_patter_0_5_ming


def construct_e_damage_list_for_bai_fu(fixed_hp, fixed_e_bonus):
    # 满命，切白芙砍三刀，再切回黑芙时，三小只的行动模式
    # 测试手法：钟离e，夜兰e 芙芙qeaa，万夜e，夜兰eq，芙芙zaaaz
    damage_list = []

    ye_lan_bonus = YeLanQBonus()

    if not has_ye_lan:
        ye_lan_bonus.invalidate()

    variable_hp_per = 0

    # 夜兰e起手
    if has_ye_lan:
        variable_hp_per += 0.1

    # 三小只先扣血，然后才造成伤害，因此第一次的攻击就能吃到专武一层hp和战技增伤，同时能吃到256层左右的芙芙大招增伤
    variable_hp_per += zhuan_wu_hp_bei_lv
    # print("checkpoint1: variable_hp_per = " + str(variable_hp_per))
    cur_hp = fixed_hp + int(variable_hp_per * fu_ning_na_Max_Hp)
    cur_bonus = fixed_e_bonus + zhuan_wu_e_bonus_bei_lv + 256 * fu_ning_na_q_bonus_bei_lv

    # 前三次吃不到万叶加成
    cur_bonus -= common_elem_bonus["万叶"]

    damage_list.append(Fu_Ren_E_Damage(cur_hp, cur_bonus, has_feng_tao=False))
    damage_list.append(Pang_Xie_E_Damage(cur_hp, cur_bonus, has_feng_tao=False))
    damage_list.append(Xun_Jue_E_Damage(cur_hp, cur_bonus, has_feng_tao=False))

    # 夫人发动攻击再次扣血，叠一层专武，hp叠满2层，战技2层
    # 芙芙奶刀这期间会加一次血，战技3层
    # 此时叠层大约会有350层
    variable_hp_per += zhuan_wu_hp_bei_lv
    # print("checkpoint2: variable_hp_per = " + str(variable_hp_per))
    cur_hp = fixed_hp + int(variable_hp_per * fu_ning_na_Max_Hp)
    cur_bonus = fixed_e_bonus + zhuan_wu_e_bonus_bei_lv * 3 + 350 * fu_ning_na_q_bonus_bei_lv

    damage_list.append(Fu_Ren_E_Damage(cur_hp, cur_bonus))

    # 夜兰e再叠一层生命
    # q增伤叠满层，大约441层，41 * 0.35% = 14.35，按11%算
    variable_hp_per += 0.1
    # print("checkpoint3: variable_hp_per = " + str(variable_hp_per))
    cur_hp = fixed_hp + int((variable_hp_per + 0.11) * fu_ning_na_Max_Hp)
    cur_bonus = fixed_e_bonus + 0.08 * 3 + 400 * fu_ning_na_q_bonus_bei_lv
    full_fixed_e_bonus = cur_bonus
    # print("full_fixed_e_bonus = " + str(full_fixed_e_bonus))

    damage_list.append(Fu_Ren_E_Damage(cur_hp, cur_bonus))

    # 夜兰q增伤开始生效
    ye_lan_bonus.start(10.655)

    # 勋爵的下一次攻击叠层大约来到507层，107 * 0.35% = 37.45%, 按34%计算
    cur_hp = fixed_hp + int((variable_hp_per + 0.34) * fu_ning_na_Max_Hp)
    cur_bonus = full_fixed_e_bonus + ye_lan_bonus.bonus(11.135)

    # print("checkpoint4: cur_hp = " + str(cur_hp) + ", cur_bonus = " + str(cur_bonus))

    damage_list.append(Xun_Jue_E_Damage(cur_hp, cur_bonus))

    # 夫人的下次攻击二命hp加成为41.9%
    cur_hp = fixed_hp + int((variable_hp_per + 0.419) * fu_ning_na_Max_Hp)
    cur_bonus = full_fixed_e_bonus + ye_lan_bonus.bonus(12.052)

    # 切为白芙，三刀后再切黑芙，三小只行动重置
    cur_hp = fixed_hp + int((variable_hp_per + 1.2) * fu_ning_na_Max_Hp)
    cur_bonus = full_fixed_e_bonus + ye_lan_bonus.bonus(16.204)

    damage_list.append(Fu_Ren_E_Damage(cur_hp, cur_bonus))

    # 二命hp也叠满了
    cur_hp = fixed_hp + int((variable_hp_per + 1.4) * fu_ning_na_Max_Hp)

    cur_bonus = full_fixed_e_bonus + ye_lan_bonus.bonus(16.754)
    # print("checkpoint5: cur_hp = " + str(cur_hp) + ", cur_bonus = " + str(cur_bonus))
    damage_list.append(Pang_Xie_E_Damage(cur_hp, cur_bonus))

    cur_bonus = full_fixed_e_bonus + ye_lan_bonus.bonus(16.804)
    damage_list.append(Xun_Jue_E_Damage(cur_hp, cur_bonus))

    cur_bonus = full_fixed_e_bonus + ye_lan_bonus.bonus(17.754)
    damage_list.append(Fu_Ren_E_Damage(cur_hp, cur_bonus))

    cur_bonus = full_fixed_e_bonus + ye_lan_bonus.bonus(19.621)
    damage_list.append(Fu_Ren_E_Damage(cur_hp, cur_bonus))

    cur_bonus = full_fixed_e_bonus + ye_lan_bonus.bonus(20.239)
    damage_list.append(Xun_Jue_E_Damage(cur_hp, cur_bonus))

    cur_bonus = full_fixed_e_bonus + ye_lan_bonus.bonus(21.039)
    damage_list.append(Fu_Ren_E_Damage(cur_hp, cur_bonus))

    cur_bonus = full_fixed_e_bonus + ye_lan_bonus.bonus(22.072)
    damage_list.append(Pang_Xie_E_Damage(cur_hp, cur_bonus))

    cur_bonus = full_fixed_e_bonus + ye_lan_bonus.bonus(22.589)
    damage_list.append(Fu_Ren_E_Damage(cur_hp, cur_bonus))

    # 大招动画消失，但大招效果还在
    cur_bonus = full_fixed_e_bonus + ye_lan_bonus.bonus(23.406)
    damage_list.append(Xun_Jue_E_Damage(cur_hp, cur_bonus))

    # 大招效果消失
    cur_bonus = fixed_e_bonus + zhuan_wu_e_bonus_bei_lv * 3 + ye_lan_bonus.bonus(24.339)
    cur_hp = fixed_hp + int(variable_hp_per * fu_ning_na_Max_Hp)
    # print("checkpoint5: cur_hp = " + str(cur_hp) + ", cur_bonus = " + str(cur_bonus))
    damage_list.append(Fu_Ren_E_Damage(cur_hp, cur_bonus))

    # 一轮输出结束，夜兰的大招也恰好结束
    ye_lan_bonus.stop()

    # 以下为特殊配队才会有的伤害，增伤只剩下专武的了
    cur_bonus = fixed_e_bonus + zhuan_wu_e_bonus_bei_lv * 3 - common_elem_bonus["万叶"]

    #     夫人：00:00:25.906	伤害871
    damage_list.append(Fu_Ren_E_Damage(cur_hp, cur_bonus, has_feng_tao=False,))
    # 勋爵：00:00:26.639  伤害1606
    damage_list.append(Xun_Jue_E_Damage(cur_hp, cur_bonus, has_feng_tao=False))
    # 螃蟹：00:00:27.256
    damage_list.append(Pang_Xie_E_Damage(cur_hp, cur_bonus, has_feng_tao=False))
    # 夫人：00:00:27.472		伤害871
    damage_list.append(Fu_Ren_E_Damage(cur_hp, cur_bonus, has_feng_tao=False))
    # 夫人：00:00:29.174
    damage_list.append(Fu_Ren_E_Damage(cur_hp, cur_bonus, has_feng_tao=False))


    # 勋爵：00:00:29.875	伤害1606
    damage_list.append(Xun_Jue_E_Damage(cur_hp, cur_bonus, is_extra=True))
    # 夫人：00:00:30.774
    damage_list.append(Fu_Ren_E_Damage(cur_hp, cur_bonus, is_extra=True))
    # 夫人：00:00:32.257
    damage_list.append(Fu_Ren_E_Damage(cur_hp, cur_bonus, is_extra=True))
    # 螃蟹：00:00:32.357
    damage_list.append(Pang_Xie_E_Damage(cur_hp, cur_bonus, is_extra=True))
    # 勋爵：00:00:33.124
    damage_list.append(Xun_Jue_E_Damage(cur_hp, cur_bonus, is_extra=True))
    # 夫人：00:00:33.875
    damage_list.append(Fu_Ren_E_Damage(cur_hp, cur_bonus, is_extra=True))
    # 夫人：00:00:35.391
    damage_list.append(Fu_Ren_E_Damage(cur_hp, cur_bonus, is_extra=True))

    return damage_list


def calc_score(fixed_hp, fixed_e_bonus, fixed_full_bonus, crit_rate, crit_damage):
    # print("fixed_hp:" + str(fixed_hp))
    # print("fixed_e_bonus:" + str(fixed_e_bonus))
    # print("fixed_full_bonus:" + str(fixed_full_bonus))
    if only_e:
        e_damage_list = construct_e_damage_list_for_0_5_ming(
            fixed_hp, fixed_e_bonus)
    else:
        e_damage_list = construct_e_damage_list_for_bai_fu(
            fixed_hp, fixed_e_bonus)

    e_score_non_crit = 0

    for d in e_damage_list:
        if d.is_extra and not include_extra:
            break

        e_score_non_crit += d.score()

    e_score_crit = e_score_non_crit * crit_damage
    e_score_expect = calc_expect_score(e_score_non_crit, crit_rate, crit_damage)

    if not only_e:
        class full_damage_component:
            def __init__(self, hp_bonus, elem_bonus, bei_lv, has_feng_tao = True):
                self.__hp_bonus = hp_bonus
                self.__elem_bonus = elem_bonus
                self.__bei_lv = bei_lv
                self.__has_feng_tao = has_feng_tao

            def score(self):
                d = (fixed_hp + int(self.__hp_bonus * fu_ning_na_Max_Hp)) * self.__bei_lv / 100 * self.__elem_bonus
                if not self.__has_feng_tao:
                    d /= 1.2777
                return d

        HEI_FU_BEI_LV = 18
        BAI_FU_BEI_LV = 18 + 25

        full_damage_list = []

        ye_lan_bonus = YeLanQBonus()

        if not has_ye_lan:
            ye_lan_bonus.invalidate()

        cur_hp_bonus = 0
        if has_ye_lan:
            cur_hp_bonus = 0.1

        # 第一刀: 只有夜兰一命的hp加成，且没有万叶加成
        cur_elem_bonus = fixed_full_bonus + 150 * fu_ning_na_q_bonus_bei_lv - common_elem_bonus["万叶"]
        # print("第一刀：" + str(round(cur_hp_bonus,  3)) + ", " + str(round(cur_elem_bonus, 3)))
        fd = full_damage_component(cur_hp_bonus, cur_elem_bonus, HEI_FU_BEI_LV, has_feng_tao=False)
        full_damage_list.append(fd)

        cur_hp_bonus += 0.14  # 专武叠一层
        # 第二刀也没有万叶加成
        cur_elem_bonus = fixed_full_bonus - common_elem_bonus["万叶"] + 256 * \
            fu_ning_na_q_bonus_bei_lv  # 三小只扣血，叠层到256
        
        # print("第二刀：" + str(round(cur_hp_bonus,  3)) + ", " + str(round(cur_elem_bonus, 4)))
        fd = full_damage_component(cur_hp_bonus, cur_elem_bonus, HEI_FU_BEI_LV, has_feng_tao=False)
        full_damage_list.append(fd)

        # 夜兰e
        if has_ye_lan:
            cur_hp_bonus += 0.1
        # 专武肯定叠满
        cur_hp_bonus += 0.14

        # 夜兰q增伤开始生效
        ye_lan_bonus.start(10.655)

        cur_elem_bonus = fixed_full_bonus + \
            fu_ning_na_q_max_bonus + ye_lan_bonus.bonus(12.102)
        
        # print("第三刀：" + str(round(cur_hp_bonus,  3)) + ", " + str(round(cur_elem_bonus, 3)))
        fd = full_damage_component(
            cur_hp_bonus + 0.408, cur_elem_bonus, HEI_FU_BEI_LV)
        full_damage_list.append(fd)

        cur_elem_bonus = fixed_full_bonus + \
            fu_ning_na_q_max_bonus + ye_lan_bonus.bonus(13.038)
        
        # print("第四刀：" + str(round(cur_hp_bonus,  3)) + ", " + str(round(cur_elem_bonus, 3)))
        fd = full_damage_component(
            cur_hp_bonus + 0.7855, cur_elem_bonus, BAI_FU_BEI_LV)
        full_damage_list.append(fd)

        cur_elem_bonus = fixed_full_bonus + \
            fu_ning_na_q_max_bonus + ye_lan_bonus.bonus(13.471)
        
        # print("第五刀：" + str(round(cur_hp_bonus,  3)) + ", " + str(round(cur_elem_bonus, 3)))
        fd = full_damage_component(
            cur_hp_bonus + 0.8535, cur_elem_bonus, BAI_FU_BEI_LV)
        full_damage_list.append(fd)

        cur_elem_bonus = fixed_full_bonus + \
            fu_ning_na_q_max_bonus + ye_lan_bonus.bonus(14.071)
        
        # print("第六刀：" + str(round(cur_hp_bonus,  3)) + ", " + str(round(cur_elem_bonus, 3)))
        fd = full_damage_component(
            cur_hp_bonus + 0.994, cur_elem_bonus, BAI_FU_BEI_LV)
        full_damage_list.append(fd)

        full_six_damage_non_crit = 0
        for d in full_damage_list:
            full_six_damage_non_crit += d.score()

        full_six_damage_crit = full_six_damage_non_crit * crit_damage
        full_six_damage_expect = full_six_damage_non_crit * \
            (1 + crit_rate * (crit_damage - 1))
    else:
        full_six_damage_crit = 0
        full_six_damage_expect = 0

    all_crit = e_score_crit + full_six_damage_crit
    all_expect = e_score_expect + full_six_damage_expect

    return (all_crit, all_expect, round(full_six_damage_crit / all_crit, 3))


def calculate_score_callback(combine: list[ShengYiWu]):
    crit_rate = 0.242  # 突破加成
    crit_damage = 1 + 0.5 + sum(extra_crit_damage.values())
    hp = 4780
    hp_per = 0
    six_bonus = 1 + sum(common_elem_bonus.values())
    energe_recharge = 1

    for p in combine:
        crit_rate += p.crit_rate
        crit_damage += p.crit_damage
        hp += p.hp
        hp_per += p.hp_percent
        six_bonus += p.elem_bonus
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
            six_bonus += 0.15
        elif n == ShengYiWu.QIAN_YAN:
            hp_per += 0.2
        elif n == ShengYiWu.CHEN_LUN:
            six_bonus += 0.15
        elif n == ShengYiWu.JU_TUAN:
            syw_e_bonus += 0.2
            if name_count[n] >= 4:
                syw_e_bonus += 0.25 + 0.25

    all_hp = int(fu_ning_na_Max_Hp * (1
                                      + hp_per
                                      + sum(extra_hp_bonus.values())
                                      )) + hp
    e_bonus = six_bonus + sum(extra_e_bonus.values()) + syw_e_bonus

    crit_score, expect_score, full_six_zhan_bi = calc_score(
        all_hp, e_bonus, six_bonus, crit_rate, crit_damage)

    max_hp_per = hp_per + sum(extra_hp_bonus.values()) + sum(
        variable_hp_bonus.values()) + ming_2_hp_bonus_max
    max_hp = int(fu_ning_na_Max_Hp * (1 + max_hp_per)) + hp
    panel_hp = fu_ning_na_Max_Hp * (1 + hp_per) + hp

    max_e_bonus = e_bonus + \
        sum(variable_e_bonus.values()) + fu_ning_na_q_max_bonus + 0.28  # 固有天赋2吃满
    max_six_bonus = six_bonus + fu_ning_na_q_max_bonus

    return [expect_score, crit_score, full_six_zhan_bi, int(max_hp), int(panel_hp), round(max_e_bonus, 3), round(max_six_bonus, 3), round(crit_rate, 3), round(crit_damage - 1, 3), round(energe_recharge, 1), combine]


result_description = ["总评分", "期望伤害评分", "暴击伤害评分", "满命六刀伤害占比", "实战最大生命值上限",
                      "面板最大生命值", "战技最高元素伤害加成(不包含夜兰的)", "满命六刀最高元素伤害加成（不包含夜兰的）", "暴击率", "暴击伤害", "充能效率", "圣遗物组合"]


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
