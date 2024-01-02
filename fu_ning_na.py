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

if has_ye_lan or has_na_wei_lai_te:
    has_shuang_shui = True
else:
    has_shuang_shui = False


class Teammate_HP:
    def __init__(self, base_hp, max_hp):
        self.base_hp = base_hp
        self.max_hp = max_hp


teammate_hp = {
    Teammate_HP(14450, 46461),  # 夜兰
    Teammate_HP(14695, 58661),  # 钟离
    Teammate_HP(13348, 23505),  # 万叶
}

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

q_bei_lv = 24.2
e_bei_lv = 16.7

HEI_FU_BEI_LV = 18
BAI_FU_BEI_LV = 18 + 25

if ming_zuo_num >= 5:
    fu_ning_na_qi_bonus_bei_lv = 0.0031
else:
    fu_ning_na_qi_bonus_bei_lv = 0.0025

fu_ning_na_q_max_bonus = 400 * fu_ning_na_qi_bonus_bei_lv
fu_ning_na_Max_Hp = 15307.0

zhuan_wu_hp_bei_lv = 0.14
zhuan_wu_e_bonus_bei_lv = 0.08

extra_crit_damage = {
    "专武": 0.882
}

extra_hp_bonus = {
}

if has_shuang_shui:
    extra_hp_bonus["双水"] = 0.25

extra_common_elem_bonus = {
    "万叶": 0.4,
}

extra_e_bonus = {
}

other_hp_bonus = {
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
    # [(zhui_yi, h, cc:0.152, cd:0.132, re:0.097, defp:0.073),
    # (shui_xian, y, cc:0.117, cd:0.194, def:23, elem:23),
    # (shui_xian, s, cc:0.074, cd:0.218, hpp:0.466, re:0.091, atk:18),
    # (hua_hai, b, cc:0.093, cd:0.21, hpp:0.466, defp:0.131, def:23),
    # (hua_hai, t, cc:0.07, cd:0.622, hpp:0.111, hp:687, defp:0.058)]]
    # 只计算双水fixed_hp = (1 + 0.466 + 0.466 + 0.111 + 0.2 + 0.25) * 15307 + 4780 + 687 = 43627(实际为43625)
    # fixed_full_bonus = 1 + 万叶0.4 + 2水仙 = 1.55
    # fixed_e_bonus = 1 + 万叶0.4 + 固有天赋0.28 + 2水仙 = 1.83
    return [
        (ShengYiWu(ShengYiWu.ZHUI_YI, ShengYiWu.PART_HUA,
                   crit_rate=0.152, crit_damage=0.132, energe_recharge=0.097, def_per=0.073),
         ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_YU,
                   crit_rate=0.117, crit_damage=0.194, def_v=23, elem_mastery=23),
         ShengYiWu(ShengYiWu.SHUI_XIAN, ShengYiWu.PART_SHA,
                   crit_rate=0.074, crit_damage=0.218, energe_recharge=0.091, atk=18, hp_percent=0.466),
         ShengYiWu(ShengYiWu.HUA_HAI, ShengYiWu.PART_BEI,
                   crit_rate=0.093, crit_damage=0.21, def_per=0.131, def_v=23, hp_percent=0.466)
         )
    ]

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


def gu_you_tian_fu_2_bonus(hp):
    return min(hp / 1000 * 0.007, 0.28)


class Qi_HP_Bonus:
    def __init__(self, fixed_hp, fixed_e_bonus, fixed_common_bonus,
                 qi_fen_level, zhuan_wu_hp_level, zhuan_wu_e_bonus_level,
                 ye_lan_e_num=0, ye_lan_q_bonus=0):
        self.fixed_hp = fixed_hp
        self.fixed_e_bonus = fixed_e_bonus
        self.fixed_common_bonus = fixed_common_bonus

        self.qi_fen_level = qi_fen_level
        self.zhuan_wu_hp_level = zhuan_wu_hp_level
        self.zhuan_wu_e_bonus_level = zhuan_wu_e_bonus_level
        self.ye_lan_e_num = ye_lan_e_num
        self.ye_lan_q_bonus = ye_lan_q_bonus

        self.__hp = None
        self.__common_bonus = None
        self.__e_bonus = None

    def hp(self):
        if not self.__hp:
            extra_hp_percent = self.ye_lan_e_num * 0.1
            extra_hp_percent += self.zhuan_wu_hp_level * zhuan_wu_hp_bei_lv
            if ming_zuo_num >= 2 and self.qi_fen_level > 400:
                extra_hp_percent += min((self.qi_fen_level - 400)
                                        * 0.0035, 1.4)

            self.__hp = self.fixed_hp + \
                int(fu_ning_na_Max_Hp * extra_hp_percent)

        return self.__hp

    def common_elem_bonus(self, has_extra_bonus=True, in_front=False):
        if not self.__common_bonus:
            bonus = self.fixed_common_bonus
            bonus += min(400, self.qi_fen_level) * fu_ning_na_qi_bonus_bei_lv
            if in_front:
                bonus += self.ye_lan_q_bonus
            if not has_extra_bonus:
                bonus -= sum(extra_common_elem_bonus.values())

            self.__common_bonus = bonus

        return self.__common_bonus

    def e_bonus(self, has_extra_bonus=True, in_front=False):
        if not self.__e_bonus:
            bonus = self.fixed_e_bonus
            bonus += self.zhuan_wu_e_bonus_level * zhuan_wu_e_bonus_bei_lv
            bonus += gu_you_tian_fu_2_bonus(self.hp())
            bonus += min(400, self.qi_fen_level) * fu_ning_na_qi_bonus_bei_lv
            if in_front:
                bonus += self.ye_lan_q_bonus
            if not has_extra_bonus:
                bonus -= sum(extra_e_bonus.values())

            self.__e_bonus = bonus

        return self.__e_bonus


class Damage:
    def __init__(self, bei_lv, has_feng_tao=True, is_extra=False, has_extra_bonus=True, in_front=False):
        self.bei_lv = bei_lv
        self.has_feng_tao = has_feng_tao
        self.is_extra = is_extra
        self.has_extra_bonus = has_extra_bonus
        self.in_front = in_front

    def set_qi_hp_bonus(self, qi_hp_bonus: Qi_HP_Bonus):
        self.qi_hp_bonus = qi_hp_bonus

    def damage(self):
        return 0


class E_Damage(Damage):
    def damage(self):
        elem_bonus = self.qi_hp_bonus.e_bonus(
            self.has_extra_bonus, self.in_front)
        d = self.qi_hp_bonus.hp() * self.bei_lv / 100 * e_extra_damage * elem_bonus
        if not self.has_feng_tao:
            d /= 1.2777  # 风套增伤27.77%
        return d


class Fu_Ren_E_Damage(E_Damage):
    def __init__(self, has_feng_tao=True, is_extra=False, has_extra_bonus=True, in_front=False):
        super().__init__(FU_REN_BEI_LV, has_feng_tao, is_extra, has_extra_bonus, in_front)


class Xun_Jue_E_Damage(E_Damage):
    def __init__(self, has_feng_tao=True, is_extra=False, has_extra_bonus=True, in_front=False):
        super().__init__(XUN_JUE_BEI_LV,  has_feng_tao, is_extra, has_extra_bonus, in_front)


class Pang_Xie_E_Damage(E_Damage):
    def __init__(self, has_feng_tao=True, is_extra=False, has_extra_bonus=True, in_front=False):
        super().__init__(PANG_XIE_BEI_LV, has_feng_tao, is_extra, has_extra_bonus, in_front)


class Ming_6_Damage(Damage):
    def __init__(self, bei_lv):
        super().__init__(bei_lv, has_feng_tao=True,
                         is_extra=False, has_extra_bonus=True, in_front=True)

    def damage(self):
        elem_bonus = self.qi_hp_bonus.common_elem_bonus(
            self.has_extra_bonus, in_front=True)
        d = self.qi_hp_bonus.hp() * self.bei_lv / 100 * elem_bonus
        if not self.has_feng_tao:
            d /= 1.2777
        return d


class Bai_Fu_Damage(Ming_6_Damage):
    def __init__(self):
        super().__init__(BAI_FU_BEI_LV)


class Hei_Fu_Damage(Ming_6_Damage):
    def __init__(self):
        super().__init__(HEI_FU_BEI_LV)


def calc_score(fixed_hp, fixed_e_bonus, fixed_common_bonus, crit_rate, crit_damage):
    print("fixed_hp:" + str(fixed_hp))
    print("fixed_e_bonus:" + str(fixed_e_bonus))
    print("fixed_full_bonus:" + str(fixed_common_bonus))

    # 注：这个列表里不需要包含三个宠物的第一次攻击以及满命六刀，因为：
    # 
    # * 三个宠物的第一次攻击是默认包含的
    # * 满命六刀会自动添加
    damage_list = [
        Fu_Ren_E_Damage(),
        Fu_Ren_E_Damage(),
        Xun_Jue_E_Damage(),
        Fu_Ren_E_Damage(),
        Pang_Xie_E_Damage(),

        Fu_Ren_E_Damage(),
        Xun_Jue_E_Damage(),
        Fu_Ren_E_Damage(),
        Fu_Ren_E_Damage(),
        Xun_Jue_E_Damage(),
        Pang_Xie_E_Damage(),

        Fu_Ren_E_Damage(),
        Fu_Ren_E_Damage(),
        Xun_Jue_E_Damage(),
    ]


def calculate_score_callback(combine: list[ShengYiWu]):
    crit_rate = 0.242  # 突破加成
    crit_damage = 1 + 0.5 + sum(extra_crit_damage.values())
    hp = 4780
    hp_per = 0
    common_bonus = 1 + sum(extra_common_elem_bonus.values())
    energe_recharge = 1

    for p in combine:
        crit_rate += p.crit_rate
        crit_damage += p.crit_damage
        hp += p.hp
        hp_per += p.hp_percent
        common_bonus += p.elem_bonus
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
            common_bonus += 0.15
        elif n == ShengYiWu.QIAN_YAN:
            hp_per += 0.2
        elif n == ShengYiWu.CHEN_LUN:
            common_bonus += 0.15
        elif n == ShengYiWu.JU_TUAN:
            syw_e_bonus += 0.2
            if name_count[n] >= 4:
                syw_e_bonus += 0.25 + 0.25

    all_hp = int(fu_ning_na_Max_Hp * (1
                                      + hp_per
                                      + sum(extra_hp_bonus.values())
                                      )) + hp
    e_bonus = common_bonus + sum(extra_e_bonus.values()) + syw_e_bonus

    crit_score, expect_score, full_six_zhan_bi = calc_score(
        all_hp, e_bonus, common_bonus, crit_rate, crit_damage)

    max_hp_per = hp_per + sum(extra_hp_bonus.values()) + sum(
        other_hp_bonus.values()) + ming_2_hp_bonus_max
    max_hp = int(fu_ning_na_Max_Hp * (1 + max_hp_per)) + hp
    panel_hp = fu_ning_na_Max_Hp * (1 + hp_per) + hp

    max_e_bonus = e_bonus + zhuan_wu_e_bonus_bei_lv * \
        3 + fu_ning_na_q_max_bonus + 0.28  # 固有天赋2吃满
    max_common_bonus = common_bonus + fu_ning_na_q_max_bonus

    return [expect_score, crit_score, full_six_zhan_bi, int(max_hp), int(panel_hp), round(max_e_bonus, 3), round(max_common_bonus, 3), round(crit_rate, 3), round(crit_damage - 1, 3), round(energe_recharge, 1), combine]


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
