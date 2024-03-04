#!/user/bin/env python3 -tt
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

import random

from attribute_hub import ActionPlanAttributeSupplier
from ys_basic import Ys_Elem_Type, Ys_Weapon, ys_crit_damage, ys_expect_damage
from character import Character
from monster import Monster
from action import Action, ActionPlan, AttributeAction
from ys_syw import ShengYiWu

import ys_weapon

class Ye_Lan_Ch(Character, name="夜兰", elem_type=Ys_Elem_Type.SHUI, ming_zuo_num=6,
                ch_level=90, a_level=10, e_level=13, q_level=13, q_energy=70):
    # 技能最少点到 8 级
    MIN_SKILL_LEVEL = 8
    PO_JU_SHI_MULTIPLIER = [18.52/100, 19.68/100, 20.84/100]
    E_MULTIPLIER = [36.2/100, 38.4/100, 40.7/100, 43.0/100, 45.2/100, 48.1/100]
    Q_MULTIPLIER = [11.69/100, 12.42/100, 13.15/100, 13.89/100, 14.62/100, 15.53/100]
    QXT_MULTIPLIER = [7.80/100, 8.28/100, 8.77/100, 9.26/100, 9.74/100, 10.35/100]

    NUM_ELEM_TYPE_TO_HP_PER = {
            1: 6/100, 2: 12/100, 3: 18/100, 4: 30/100
        }

    def __init__(self, weapon: Ys_Weapon=None):
        super().__init__(base_hp=14450, weapon=weapon, crit_rate=0.242)

    def set_teammates(self, teammates: list[Character]):
        super().set_teammates(teammates)

        # 固有天赋 1
        elem_types_set = set([Ys_Elem_Type.SHUI] + [t.elem_type for t in teammates])
        tf1_hp_per = Ye_Lan_Ch.NUM_ELEM_TYPE_TO_HP_PER[len(elem_types_set)]
        self.get_hp().modify_max_hp_per(tf1_hp_per)
    
    def __get_damage(self, multiplier, bonus, monster:Monster):
        damage = self.get_hp().get_max_hp() * multiplier * (1 + bonus)
        if monster:
            return monster.attacked(damage)
        else:
            return damage
    
    def get_po_ju_shi_damage(self, ming_6=True, monster: Monster = None):
        if ming_6 and self.ming_zuo_num < 6:
            return 0
        
        multiplier = Ye_Lan_Ch.PO_JU_SHI_MULTIPLIER[self.a_level - Ye_Lan_Ch.MIN_SKILL_LEVEL]
        damage = self.__get_damage(multiplier, self.get_a_bonus(), monster)
        if ming_6:
            damage *= 156/100
        
        return damage
    
    def get_e_damage(self, monster: Monster=None):
        multiplier = Ye_Lan_Ch.E_MULTIPLIER[self.e_level - Ye_Lan_Ch.MIN_SKILL_LEVEL]
        return self.__get_damage(multiplier, self.get_e_bonus(), monster)
    
    def get_q_damage(self, monster: Monster=None):
        multiplier = Ye_Lan_Ch.Q_MULTIPLIER[self.q_level - Ye_Lan_Ch.MIN_SKILL_LEVEL]
        return self.__get_damage(multiplier, self.get_q_bonus(), monster)
    
    def get_qxt_damage(self, monster: Monster=None):
        multiplier = Ye_Lan_Ch.QXT_MULTIPLIER[self.q_level - Ye_Lan_Ch.MIN_SKILL_LEVEL]
        return self.__get_damage(multiplier, self.get_q_bonus(), monster)
    
    def get_extra_qxt_damage(self, monster: Monster=None):
        if self.ming_zuo_num < 2:
            return 0
        
        return self.__get_damage(14/100, self.get_q_bonus(), monster)


class YeLan_Ming_4_Action(Action, ActionPlanAttributeSupplier):
    def __init__(self):
        super().__init__("夜兰四命生效一层")

    def do_impl(self, plan: ActionPlan):
        plan.add_extra_attr(self)

    def get_hp_percent(self, plan, target_character):
        # FIXME: 生效时长是否要加？持续25秒是否能覆盖整个输出轴？
        return 0.1

class YeLan_Q_Bonus_Action(AttributeAction):
    """
    注：plan.add_action 时，这个 Action 的 min_t 和 max_t 填写夜兰大招动画开始的时间，实际的增伤开始时间会自动计算
    """
    def __init__(self):
        super().__init__("夜兰Q增伤开始")

    def set_timestamp(self, t):
        super().set_timestamp(t)
        # 参见 ye_lan_readme.md
        self.bonus_start_time = t + random.randint(1235, 1270) / 1000

    def do_impl(self, plan: ActionPlan):
        plan.add_extra_attr(self)

    def get_elem_bonus(self, plan: ActionPlan, target_character: Character):
        if not target_character.is_in_foreground():
            return 0
        
        cur_time = plan.get_current_action_time()
        dur = cur_time - self.bonus_start_time
        if dur <= 0:
            return 0
        
        if dur >= 15:
            return 0
        
        return (1 + int(dur) * 3.5) / 100

class YeLanQBonus:
    def __init__(self):
        self.__invalid = False
        self.__stopped = True
        self.__start_time = 0

    def invalidate(self):
        self.__invalid = True

    def start(self, start_time):
        self.__stopped = False
        self.__start_time = start_time

    def bonus(self, checkpoint_time):
        #logging.debug("YeLanQBonus.bonus, checkpoint_time: %s, stopped:%s, invalid:%s, start_time:%s",
        #              round(checkpoint_time, 3), self.__stopped, self.__invalid, round(self.__start_time, 3))
        if self.__stopped or self.__invalid:
            return 0

        dur = checkpoint_time - self.__start_time
        if dur <= 0:
            return 0

        if dur >= 15:
            return 0

        return (1 + int(dur) * 3.5) / 100

    def stop(self):
        self.__stopped = True

class Ying_Bao_Ch(Character, name="影宝", elem_type=Ys_Elem_Type.LEI, ming_zuo_num=4, 
                  ch_level=90, a_level=4, e_level=9, q_level=13, q_energy=90):
    e_bonus_multiplier = [
        0.22/100, # 1
        0.23/100, # 2
        0.24/100, # 3
        0.25/100, # 4
        0.26/100, # 5
        0.27/100, # 6
        0.28/100, # 7
        0.29/100, # 8
        0.30/100, # 9
        0.30/100, # 10
        0.30/100, # 11
        0.30/100, # 12
        0.30/100, # 13
    ]
    # 梦想一刀倍率
    meng_dao_multiplier = [
        401/100, # 1
        431/100, # 2
        461/100, # 3
        501/100, # 4
        531/100, # 5
        561/100, # 6
        601/100, # 7
        641/100, # 8
        681/100, # 9
        721/100, # 10
        762/100, # 11
        802/100, # 12
        852/100, # 13
    ]

    meng_dao_yuan_li_bonus = [
        3.89/100, # 1
        4.18/100, # 2
        4.47/100, # 3
        4.86/100, # 4
        5.15/100, # 5
        5.44/100, # 6
        5.83/100, # 7
        6.22/100, # 8
        6.61/100, # 9
        7.00/100, # 10
        7.39/100, # 11
        7.78/100, # 12
        8.26/100, # 13
    ]

    # 梦想一心下普攻倍率：一段，二段，三段，四段，五段，重击
    meng_a_multiplier = [
        [44.7/100, 44.0/100, 53.8/100, (30.9/100, 31.0/100), 73.9/100, (61.6/100, 74.4/100)], # 1
        [47.8/100, 47.0/100, 57.5/100, (33.0/100, 33.1/100), 79.0/100, (65.8/100, 79.4/100)], # 2
        [50.8/100, 50.0/100, 61.2/100, (35.1/100, 35.2/100), 84.0/100, (70.0/100, 84.5/100)], # 3
        [54.9/100, 53.9/100, 66.1/100, (37.9/100, 38.0/100), 90.7/100, (75.6/100, 91.3/100)], # 4
        [58.0/100, 56.9/100, 69.7/100, (40.0/100, 40.1/100), 95.8/100, (79.8/100, 96.3/100)], # 5
        [61.5/100, 60.4/100, 74.0/100, (42.5/100, 42.6/100), 101.7/100, (84.7/100, 102.2/100)], # 6
        [66.1/100, 64.9/100, 79.5/100, (45.6/100, 45.8/100), 109.2/100, (91.0/100, 109.9/100)], # 7
        [70.7/100, 69.4/100, 85.0/100, (48.8/100, 48.9/100), 115.8/100, (97.3/100, 117.5/100)], # 8
        [75.2/100, 73.9/100, 90.5/100, (51.9/100, 52.1/100), 124.4/100, (103.6/100, 125.1/100)], # 9
        [79.8/100, 78.4/100, 96.0/100, (55.1/100, 55.3/100), 131.9/100, (109.9/100, 132.7/100)], # 10
        [84.4/100, 82.9/100, 101.5/100, (58.279/100, 58.43/100), 139.5/100, (116.2/100, 140.3/100)], # 11
        [89.0/100, 87.4/100, 107.0/100, (61.43/100, 61.6/100), 147.1/100, (122.5/100, 147.9/100)], # 12
        [93.5/100, 91.9/100, 112.5/100, (64.6/100, 64.8/100), 154.6/100, (128.8/100, 155.5/100)], # 13
    ]

    meng_a_yuan_li_bonus = [
        0.73/100, # 1
        0.78/100, # 2
        0.84/100, # 3
        0.91/100, # 4
        0.96/100, # 5
        1.02/100, # 6
        1.09/100, # 7
        1.16/100, # 8
        1.23/100, # 9
        1.31/100, # 10
        1.38/100, # 11
        1.45/100, # 12
        1.54/100, # 13
    ]

    def __init__(self, weapon: Ys_Weapon):
        super().__init__(base_atk=337, weapon=weapon, 
                         energy_recharge=132+20 # 绝缘二套效果默认算进来
                         )
        self.meng_xiang_yi_dao_damage = 0
        
    def do_post_set_syw_combine(self):
        self.panel_energy_recharge = self.get_energy_recharge()
        self.panel_bonus = (self.panel_energy_recharge - 100) * 0.004 + self.get_q_bonus()
        self.panel_crit_damage = self.get_crit_damage()

        self.get_weapon().apply_combat_attributes(self)
        self.panel_atk = self.get_atk()

        self.get_weapon().apply_passive(self)        

        energy_recharge = self.get_energy_recharge()

        extra_elem_bonus = (energy_recharge - 100) * 0.004  # 固有天赋2
        extra_elem_bonus += min(energy_recharge / 4 / 100, 0.75) # 四绝缘
        extra_elem_bonus += Ying_Bao_Ch.get_bonus_to_q(self.q_energy, ying_bao_e_level=self.e_level)

        self.add_all_bonus(extra_elem_bonus)


    @classmethod
    def get_bonus_to_q(cls, q_energy, ying_bao_e_level=0):
        if not ying_bao_e_level:
            ying_bao_e_level = cls.e_level

        return cls.e_bonus_multiplier[ying_bao_e_level -  1] * q_energy

    def get_yuan_li(self):
        # 注：目前都按最大愿力层数来计算
        return 60

    def get_meng_xiang_yi_dao_multiplier(self):
        """
        extra_bonus: 主要是随时间而变化的增伤，例如：夜兰、芙芙
        """
        multiplier = Ying_Bao_Ch.meng_dao_multiplier[self.q_level - 1]
        multiplier += self.get_yuan_li() * Ying_Bao_Ch.meng_dao_yuan_li_bonus[self.q_level - 1]

        return multiplier
    
    def get_meng_a_multiplier(self, phrase, sub_phrase=1):
        """
        extra_bonus: 主要是随时间而变化的增伤，例如：夜兰、芙芙
        """
        multiplier = Ying_Bao_Ch.meng_a_multiplier[self.q_level - 1][phrase - 1]
        if phrase == 4:
            multiplier = multiplier[sub_phrase - 1]
        
        multiplier += self.get_yuan_li() * Ying_Bao_Ch.meng_a_yuan_li_bonus[self.q_level - 1]
        
        return multiplier
    
    def get_charged_a_multiplier(self, sub_phrase):
        multiplier = Ying_Bao_Ch.meng_a_multiplier[self.q_level - 1][-1][sub_phrase -1]
        multiplier += self.get_yuan_li() * Ying_Bao_Ch.meng_a_yuan_li_bonus[self.q_level - 1]

        return multiplier
    
    def get_q_action(self):
        return YingBao_Q_Action(self)
    
    def get_a_action(self, phrase, sub_phrase=1):
        return YingBao_A_Action(self, phrase=phrase, sub_phrase=sub_phrase)
    
    def get_charged_a_action(self, sub_phrase):
        return YingBao_Charged_A_Action(self, sub_phrase=sub_phrase)


# 影宝的 e 是全轴覆盖的，因此不需要单独的 action


class YingBao_Q_Action(Action):
    def __init__(self, ying_bao: Ying_Bao_Ch):
        super().__init__("影宝Q")
        self.ying_bao = ying_bao

    def do_impl(self, plan: ActionPlan):
        ying_bao = self.ying_bao

        all_atk = ying_bao.get_atk()
        multiplier = ying_bao.get_meng_xiang_yi_dao_multiplier()
        bonus = 1 + ying_bao.get_q_bonus()

        q_damage = all_atk * multiplier * bonus
        # print("q_bonus=", ying_bao.get_q_bonus())
        q_damage, crit_damage, _ = plan.add_damage(q_damage, ying_bao)
        ying_bao.meng_xiang_yi_dao_damage = crit_damage

        if Action.enable_debug:
            print(plan.monster)
            print("q_damage:{}, q_crit:{}, all_atk:{}, elem_bonus:{}, multiplier:{}".format(
                round(q_damage), crit_damage, round(all_atk), 
                round(bonus, 3), round(multiplier, 3)))

class YingBao_A_Action(Action):
    def __init__(self, ying_bao: Ying_Bao_Ch, phrase, sub_phrase=1):
        super().__init__(f"影宝普攻{phrase}-{sub_phrase}")
        self.phrase = phrase
        self.sub_phrase = sub_phrase
        self.ying_bao = ying_bao

    def do_impl(self, plan: ActionPlan):
        ying_bao = self.ying_bao
        
        all_atk = ying_bao.get_atk()
        multiplier = ying_bao.get_meng_a_multiplier(phrase=self.phrase, sub_phrase=self.sub_phrase)
        bonus = 1 + ying_bao.get_q_bonus()
        # print("add damage2: ", round(all_atk * multiplier * bonus, 3))
        a_damage, crit_damage, _ = plan.add_damage(all_atk * multiplier * bonus, ying_bao)

        if Action.enable_debug:
            print(plan.monster)
            print("a_damage:{}, q_crit:{}, all_atk:{}, elem_bonus:{}, multiplier:{}".format(
                round(a_damage), crit_damage, round(all_atk), 
                round(bonus, 3), round(multiplier, 3)))


class YingBao_Charged_A_Action(Action):
    def __init__(self, ying_bao: Ying_Bao_Ch, sub_phrase):
        super().__init__(f"影宝重击{sub_phrase}段")
        self.sub_phrase = sub_phrase
        self.ying_bao = ying_bao

    def do_impl(self, plan: ActionPlan):
        ying_bao = self.ying_bao
        
        all_atk = ying_bao.get_atk()
        multiplier = ying_bao.get_charged_a_multiplier(sub_phrase=self.sub_phrase)
        bonus = 1 + ying_bao.get_q_bonus()

        z_damage, crit_damage, _ = plan.add_damage(all_atk * multiplier * bonus, ying_bao)

        if Action.enable_debug:
            print(plan.monster)
            print("a_damage:{}, q_crit:{}, all_atk:{}, elem_bonus:{}, multiplier:{}".format(
                round(z_damage), round(z_damage * (1 + ying_bao.get_crit_damage())), round(all_atk), 
                round(bonus, 3), round(multiplier, 3)))


class BanNiTe_Q_Action(Action, ActionPlanAttributeSupplier):
    q_atk_multiplier = [
        56/100, # 1
        60/100, # 2
        64/100, # 3
        70/100, # 4
        74/100, # 5
        78/100, # 6
        84/100, # 7
        90/100, # 8
        95/100, # 9
        101/100, # 10
        106/100, # 11
        112/100, # 12
        119/100, # 13
    ]
        
    def __init__(self, base_atk, q_level, ming_zuo_num, is_4_zong_shi=True):
        multiplier =BanNiTe_Q_Action.q_atk_multiplier[q_level - 1]
        if ming_zuo_num >= 1:
            multiplier += 20/100
        
        self.atk_bonus = int(base_atk * multiplier)
        self.atk_per_bonus = 0
        if is_4_zong_shi:
            self.atk_per_bonus = 0.2

        super().__init__("班尼特Q")

    def do_impl(self, plan: ActionPlan):
        plan.add_extra_attr(self)

    def get_atk_per(self, plan: ActionPlan, target_character):
        cur_time = plan.get_current_action_time()
        if cur_time - self.get_timestamp() > 12:
            return 0
        
        return self.atk_per_bonus
    
    def get_atk(self, plan: ActionPlan, target_character):
        cur_time = plan.get_current_action_time()
        if cur_time - self.get_timestamp() > 12:
            return 0
        
        return self.atk_bonus
    
    @classmethod
    def create_instance(cls):
        return BanNiTe_Q_Action(base_atk=756, q_level=13, ming_zuo_num=5)
    

class Jiu_Tiao_Sha_Luo_Ch(Character, name="九条裟罗", elem_type=Ys_Elem_Type.LEI, ming_zuo_num=6,
                         ch_level=81, a_level=1, e_level=12, q_level=11, q_energy=80):
    charged_a_multiplier = [124/100, 133/100, 143/100, 155/100, 164/100, 174/100, 
                            186/100, 198/100, 211/100, 223/100, 235.6/100]
    e_damage_multiplier = [
        125.8/100, # 1
        135.2/100, # 2
        144.6/100, # 3
        157.2/100, # 4
        166.6/100, # 5
        176.1/100, # 6
        188.6/100, # 7
        201.2/100, # 8
        213.8/100, # 9
        226.4/100, # 10
        238.9/100, # 11
        251.5/100, # 12
        267.2/100, # 13
    ]

    e_atk_multiplier = [
        43/100, # 1
        46/100, # 2
        49/100, # 3
        54/100, # 4
        57/100, # 5
        60/100, # 6
        64/100, # 7
        69/100, # 8
        73/100, # 9
        77/100, # 10
        82/100, # 11
        86/100, # 12
        91/100, # 13
    ]

    jin_gang_huai_multiplier = [
        409.6/100, # 1
        440.3/100, # 2
        471.0/100, # 3
        512/100, # 4
        542.7/100, # 5
        573.4/100, # 6
        614.4/100, # 7
        655.4/100, # 8
        696.3/100, # 9
        737.3/100, # 10
        778.2/100, # 11
        819.2/100, # 12
        870.4/100, # 13
    ]

    lei_shuo_multiplier = [
        34.1/100, # 1
        36.7/100, # 2
        39.2/100, # 3
        42.7/100, # 4
        45.2/100, # 5
        47.8/100, # 6
        51.2/100, # 7
        54.6/100, # 8
        58.0/100, # 9
        61.4/100, # 10
        64.8/100, # 11
        68.2/100, # 12
        72.5/100, # 13
    ]

    def __init__(self, weapon: Ys_Weapon, syw_combine: list[ShengYiWu]):
        super().__init__(base_atk=184, weapon=weapon)
        self.add_atk_per(0.24) # 81级

        self.set_syw_combine(syw_combine)
        self.add_energy_recharge(0.2) # 绝缘两件套效果

        weapon.apply_combat_attributes(self)

        self.panel_atk = self.get_atk()

        weapon.apply_passive(self)

    def get_charged_a_damage(self):
        multiplier = Jiu_Tiao_Sha_Luo_Ch.charged_a_multiplier[self.a_level - 1]
        return self.get_atk() * multiplier * (1 + self.get_a_bonus())

    def get_wu_yu_damage(self):
        multiplier = Jiu_Tiao_Sha_Luo_Ch.e_damage_multiplier[self.e_level - 1]
        return self.get_atk() * multiplier * (1 + self.get_e_bonus())

    def get_e_damage(self):
        if self.ming_zuo_num < 2:
            return 0
        else:
            return 0.3 * self.get_wu_yu_damage()

    def get_q_damage(self):
        num = 4
        if self.ming_zuo_num >= 4:
            num = 6

        jin_gang_huai_multiplier = Jiu_Tiao_Sha_Luo_Ch.jin_gang_huai_multiplier[self.q_level - 1]
        lei_shuo_multiplier = Jiu_Tiao_Sha_Luo_Ch.lei_shuo_multiplier[self.q_level - 1]

        multiplier = jin_gang_huai_multiplier + lei_shuo_multiplier * num

        return self.get_atk() * multiplier * (1 + self.get_q_bonus())

    def get_atk_bonus(self):
        multiplier = Jiu_Tiao_Sha_Luo_Ch.e_atk_multiplier[self.e_level - 1]
        return self.get_base_atk() * multiplier

    def get_crit_damage_bonus(self):
        if self.ming_zuo_num >= 6:
            return 0.6
        else:
            return 0
    
    @classmethod
    def create_instance(cls, syw_combine: list[ShengYiWu]):
        weapon = ys_weapon.Tian_Kong_Zhi_Yi(base_atk=674, crit_rate=0.221)
        return Jiu_Tiao_Sha_Luo_Ch(weapon, syw_combine)
