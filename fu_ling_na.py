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


shui_shen_q_bonus_bei_lv = 0.0031
shui_shen_q_bonus = 400 * shui_shen_q_bonus_bei_lv
fu_ning_na_Max_Hp = 15307.0
ming_2_hp_bonus_max = 1.4  # 140%


def calc_score(hp, e_bonus, full_bonus, crit_rate, crit_damage):
    include_extra = False    # 带雷夜芙的时候，e技能持续时间能吃满
    only_e = False   # 芙芙没时间砍满命6刀时置为true
    e_extra_damage = 1.4  # 队友大于50%血量，e技能伤害为原来的1.4倍 （注：实测为1.542倍)

    class e_damage_component:
        def __init__(self, bei_lv, hp, bonus, is_extra=False):
            self.bei_lv = bei_lv
            self.hp = hp
            self.bonus = bonus
            self.is_extra = is_extra

        def score(self):
            return self.hp * self.bei_lv / 100 * e_extra_damage * self.bonus

    FU_REN_BEI_LV = 6.87
    XUN_JUE_BEI_LV = 12.67
    PANG_XIE_BEI_LV = 17.61

    full_hp = hp + int(fu_ning_na_Max_Hp * ming_2_hp_bonus_max)
    e_bonus_withoud_q = e_bonus - shui_shen_q_bonus

    e_damage_list = [
        # e结束：00:00:07.159
        # 前三次攻击的时候，就有6个头，表示叠了200层了
        # 夫人：00:00:08.559		（1.4）
        e_damage_component(FU_REN_BEI_LV, hp,
                           e_bonus_withoud_q + 200 * shui_shen_q_bonus_bei_lv),
        # 螃蟹：00:00:08.959			(1.8)
        e_damage_component(PANG_XIE_BEI_LV, hp,
                           e_bonus_withoud_q + 200 * shui_shen_q_bonus_bei_lv),
        # 勋爵：00:00:09.158			(1.999)
        e_damage_component(XUN_JUE_BEI_LV, hp,
                           e_bonus_withoud_q + 200 * shui_shen_q_bonus_bei_lv),

        # 夫人：00:00:10.198			(3.039)
        e_damage_component(FU_REN_BEI_LV, hp,
                           e_bonus_withoud_q + 300 * shui_shen_q_bonus_bei_lv),
        # 夫人：00:00:11.919			(4.76)
        e_damage_component(FU_REN_BEI_LV, hp,
                           e_bonus_withoud_q + 400 * shui_shen_q_bonus_bei_lv),

        # 增伤满层，但二命的生命还会继续叠层

        # 勋爵：00:00:12.518			(5.359)
        e_damage_component(XUN_JUE_BEI_LV, hp + \
                           int(0.184 * fu_ning_na_Max_Hp), e_bonus),
        # 夫人：00:00:13.479			(6.32)
        e_damage_component(FU_REN_BEI_LV, hp + \
                           int(0.438 * fu_ning_na_Max_Hp), e_bonus),
        # 螃蟹：00:00:14.360			(7.201)
        e_damage_component(PANG_XIE_BEI_LV, hp + \
                           int(0.438 * fu_ning_na_Max_Hp), e_bonus),
        # 夫人：00:00:15.161			(8.002)
        e_damage_component(FU_REN_BEI_LV, hp + \
                           int(0.517 * fu_ning_na_Max_Hp), e_bonus),
        # 勋爵：00:00:15.839			(8.68）
        e_damage_component(XUN_JUE_BEI_LV, hp + \
                           int(0.983 * fu_ning_na_Max_Hp), e_bonus),
        # 夫人：00:00:16.758			(9.599)
        e_damage_component(FU_REN_BEI_LV, hp + \
                           int(1.029 * fu_ning_na_Max_Hp), e_bonus),

        # 二命叠满生命
        # 夫人：00:00:18.359			(11.2)
        e_damage_component(FU_REN_BEI_LV, full_hp, e_bonus),
        # 勋爵：00:00:19.160			(12.001)
        e_damage_component(XUN_JUE_BEI_LV, full_hp, e_bonus),
        # 螃蟹：00:00:19.478			(12.319)
        e_damage_component(PANG_XIE_BEI_LV, full_hp, e_bonus),
        # 夫人：00:00:20.119			(12.96)
        e_damage_component(FU_REN_BEI_LV, full_hp, e_bonus),
        # 夫人：00:00:21.800			(14.641)
        e_damage_component(FU_REN_BEI_LV, full_hp, e_bonus),
        # 勋爵：00:00:22.639			(15.48)
        e_damage_component(XUN_JUE_BEI_LV, full_hp, e_bonus),
        # 夫人：00:00:23.439			(16.28)
        e_damage_component(FU_REN_BEI_LV, full_hp, e_bonus),
        # 螃蟹：00:00:24.639			(17.48)
        e_damage_component(PANG_XIE_BEI_LV, full_hp, e_bonus),
        # 夫人：00:00:25.080			(17.921)
        e_damage_component(FU_REN_BEI_LV, full_hp, e_bonus),

        # 大招结束
        # 勋爵：00:00:25.919			(18.76)
        e_damage_component(XUN_JUE_BEI_LV, hp, e_bonus_withoud_q),
        # 夫人：00:00:26.678			(19.519)
        e_damage_component(FU_REN_BEI_LV, hp, e_bonus_withoud_q),
        # 夫人：00:00:28.198			(21.039)
        e_damage_component(FU_REN_BEI_LV, hp, e_bonus_withoud_q),
        # 勋爵：00:00:29.398			(22.239)
        e_damage_component(XUN_JUE_BEI_LV, hp, e_bonus_withoud_q),
        # 夫人：00:00:29.718			(22.559)
        e_damage_component(FU_REN_BEI_LV, hp, e_bonus_withoud_q),
        # 螃蟹：00:00:29.759			(22.6)
        e_damage_component(PANG_XIE_BEI_LV, hp, e_bonus_withoud_q),
        # 夫人：00:00:31.199			(24.04)
        e_damage_component(FU_REN_BEI_LV, hp, e_bonus_withoud_q),

        # 一轮循环之外，某些配队才有这些
        # 勋爵：00:00:32.560			(25.401)
        e_damage_component(XUN_JUE_BEI_LV, hp,
                           e_bonus_withoud_q, is_extra=True),
        # 夫人：00:00:32.718			(25.559)
        e_damage_component(FU_REN_BEI_LV, hp,
                           e_bonus_withoud_q, is_extra=True),
        # 夫人：00:00:34.359			(27.2)
        e_damage_component(FU_REN_BEI_LV, hp,
                           e_bonus_withoud_q, is_extra=True),
        # 螃蟹：00:00:35.079			(27.92)
        e_damage_component(PANG_XIE_BEI_LV, hp,
                           e_bonus_withoud_q, is_extra=True),
        # 勋爵：00:00:35.799			(28.64)
        e_damage_component(XUN_JUE_BEI_LV, hp,
                           e_bonus_withoud_q, is_extra=True),
        # 夫人：00:00:35.878			(28.719)
        e_damage_component(FU_REN_BEI_LV, hp,
                           e_bonus_withoud_q, is_extra=True),
    ]

    fu_ren_damage_non_crit = 0
    xun_jue_damage_non_crit = 0
    pang_xie_damage_non_crit = 0

    for d in e_damage_list:
        if d.is_extra and not include_extra:
            break

        if d.bei_lv == FU_REN_BEI_LV:
            fu_ren_damage_non_crit += d.score()
        elif d.bei_lv == XUN_JUE_BEI_LV:
            xun_jue_damage_non_crit += d.score()
        elif d.bei_lv == PANG_XIE_BEI_LV:
            pang_xie_damage_non_crit += d.score()

    fu_ren_damage_crit = fu_ren_damage_non_crit * crit_damage
    fu_ren_damage_expect = fu_ren_damage_non_crit * \
        (1 + crit_rate * (crit_damage - 1))

    xun_jue_damage_crit = xun_jue_damage_non_crit * crit_damage
    xun_jue_damage_expect = xun_jue_damage_non_crit * \
        (1 + crit_rate * (crit_damage - 1))

    pang_xie_damage_crit = pang_xie_damage_non_crit * crit_damage
    pang_xie_damage_expect = pang_xie_damage_non_crit * \
        (1 + crit_rate * (crit_damage - 1))

    if not only_e:
        # 采用qea 万叶e, 夜兰qee，这种手法能更快速叠层
        # e技能结束：00:00:04.870
        # 满层：00:00:09.247                            0%						4.377
        # 芙芙出场：
        # 00:00:10.446			45433                   18.4%				5.576
        # 00:00:10.497			45628                   19.6%				5.627
        # 00:00:10.697			46628                   26.2%				5.827
        # 00:00:11.186			49328	第二刀           43.8%				6.316
        # 00:00:11.677			49328	第三刀           43.8%				6.807
        # 00:00:12.427			50528	第四刀（重击）    51.7%				7.557
        # 00:00:13.087			57673	第五刀           98.3%				8.217
        # 00:00:13.746			58378	第六刀          102.9%			8.876
        class full_damage_component:
            def __init__(self, hp_bonus, bei_lv):
                self.hp_bonus = hp_bonus
                self.bei_lv = bei_lv

            def score(self):
                return (hp + int(self.hp_bonus * fu_ning_na_Max_Hp)) * self.bei_lv / 100 * full_bonus

        HEI_FU_BEI_LV = 18
        BAI_FU_BEI_LV = 18 + 25

        hp_bonus_list = [
            full_damage_component(0, HEI_FU_BEI_LV),
            full_damage_component(0.438, HEI_FU_BEI_LV),
            full_damage_component(0.438, HEI_FU_BEI_LV),
            full_damage_component(0.517, BAI_FU_BEI_LV),
            full_damage_component(0.983, BAI_FU_BEI_LV),
            full_damage_component(1.029, BAI_FU_BEI_LV)
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

    all_crit = fu_ren_damage_crit + xun_jue_damage_crit + \
        pang_xie_damage_crit + full_six_damage_crit
    all_expect = fu_ren_damage_expect + xun_jue_damage_expect + \
        pang_xie_damage_expect + full_six_damage_expect

    return (all_crit, all_expect)


def calculate_score_callback(combine):
    base_crit_damage = 1 + 0.5 + 0.882
    gu_you_tian_fu_2_e_bonus = 0.28  # 基本是能吃满的
    wan_ye_bonus = 0.4
    zhuan_wu_e_bonus = 0.08 * 3
    ye_lan_bonus = 0.25  # 夜兰平均增伤
    base_e_bonus = 1 + wan_ye_bonus + shui_shen_q_bonus + \
        zhuan_wu_e_bonus + ye_lan_bonus + gu_you_tian_fu_2_e_bonus
    base_full_bonus = 1 + wan_ye_bonus + shui_shen_q_bonus + ye_lan_bonus

    crit_rate = sum([p.crit_rate for p in combine]) + 0.242
    if crit_rate < 0.70:
        return None

    hp = sum([p.hp for p in combine])
    hp_per = sum([p.hp_percent for p in combine])
    extra_crit_damage = sum([p.crit_damage for p in combine])
    extra_water_bonus = sum([p.elem_bonus for p in combine])
    total_energe_recharge = (
        sum([p.energe_recharge for p in combine]) + 1) * 100

    if total_energe_recharge < 110:
        return None

    extra_e_bonus = 0

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
            extra_water_bonus += 0.15
        elif n == ShengYiWu.QIAN_YAN:
            hp_per += 0.2
        elif n == ShengYiWu.CHEN_LUN:
            extra_water_bonus += 0.15
        elif n == ShengYiWu.JU_TUAN:
            if name_count[n] == 2:
                extra_e_bonus += 0.2
            elif name_count[n] >= 4:
                extra_e_bonus += 0.2 + 0.25 + 0.25

    all_hp = int(fu_ning_na_Max_Hp * (1
                                      + hp_per
                                      + 0.28  # 专武叠满两层
                                      + 0.25  # 双水
                                      + 0.2  # 夜兰四命保底两个e
                                      )) + hp + 4780
    all_crit_damage = base_crit_damage + extra_crit_damage
    e_bonus = base_e_bonus + extra_e_bonus + extra_water_bonus
    full_bonus = base_full_bonus + extra_water_bonus

    crit_score, expect_score = calc_score(
        all_hp, e_bonus, full_bonus, crit_rate, all_crit_damage)

    # print('all_hp:' + str(all_hp))
    # print("e_bonus:" + str(e_bonus))
    # print("full_bonus:" + str(full_bonus))
    # print('crit_rate:' + str(crit_rate))
    # print('crit_damage:' + str(all_crit_damage))
    # print("crit_score:" + str(crit_score))
    # print("expect_score:" + str(expect_score))
    # print('-----------------------------')

    max_hp = all_hp + int(fu_ning_na_Max_Hp * ming_2_hp_bonus_max)
    panel_hp = fu_ning_na_Max_Hp * (1 + hp_per) + 4780 + hp

    return [expect_score, crit_score, int(max_hp), int(panel_hp), round(e_bonus, 3), round(full_bonus, 3), round(crit_rate, 3), round(all_crit_damage - 1, 3), round(total_energe_recharge, 1), combine]


def find_syw_for_fu_ling_na():
    return calculate_score(find_combine_callback=find_combine_callback,
                           match_sha_callback=match_sha_callback,
                           match_bei_callback=match_bei_callback,
                           calculate_score_callbak=calculate_score_callback,
                           result_txt_file="fu_ling_na_syw.txt")


# Main body
if __name__ == '__main__':
    find_syw_for_fu_ling_na()
