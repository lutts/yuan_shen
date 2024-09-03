from ..character import Character
from ..weapon import Ys_Weapon
from ..elem_type import Ys_Elem_Type
from ..monster import Monster
from ..buff_manager import BuffAttrs, Buff, MultiLayerBuff
from ..action import Action, ActionPlan


class Ye_Lan_Ch(Character, name="夜兰", elem_type=Ys_Elem_Type.SHUI, ming_zuo_num=6,
                ch_level=90, a_level=10, e_level=13, q_level=13, q_energy=70):
    PO_JU_SHI_MULTIPLIER = [18.52/100, 19.68/100, 20.84/100]
    E_MULTIPLIER = [36.2/100, 38.4/100, 40.7/100, 43.0/100, 45.2/100, 48.1/100]
    Q_MULTIPLIER = [11.69/100, 12.42/100, 13.15/100, 13.89/100, 14.62/100, 15.53/100]
    QXT_MULTIPLIER = [7.80/100, 8.28/100, 8.77/100, 9.26/100, 9.74/100, 10.35/100]

    NUM_ELEM_TYPE_TO_HP_PER = [6/100, 12/100, 18/100, 30/100]

    @staticmethod
    def create_instance(weapon=None):
        return Ye_Lan_Ch(base_hp=14450, weapon=weapon, crit_rate=0.242)
    
    def init_for_plan(self, plan: ActionPlan):
        super().init_for_plan(plan)

        # 固有天赋 1
        elem_types_set = set(plan.gong_ming.team_elem_types)
        self.tf1_hp_per = Ye_Lan_Ch.NUM_ELEM_TYPE_TO_HP_PER[len(elem_types_set)]
        self.get_hp().fixed_hp_per += self.tf1_hp_per

    
    def finish_plan(self, plan):
        super().finish_plan(plan)

        self.get_hp().fixed_hp_per -= self.tf1_hp_per
        
    
    def __get_damage(self, multiplier, bonus, monster:Monster):
        damage = self.get_hp().get_max_hp() * multiplier * (1 + bonus)
        if monster:
            return monster.attacked(damage)
        else:
            return damage
    
    def get_po_ju_shi_damage(self, ming_6=True, monster: Monster = None):
        if ming_6 and self.ming_zuo_num < 6:
            return 0
        
        multiplier = Ye_Lan_Ch.PO_JU_SHI_MULTIPLIER[self.a_idx()]
        damage = self.__get_damage(multiplier, self.get_a_bonus(), monster)
        if ming_6:
            damage *= 156/100
        
        return damage
    
    def get_e_damage(self, monster: Monster=None):
        multiplier = Ye_Lan_Ch.E_MULTIPLIER[self.e_idx()]
        return self.__get_damage(multiplier, self.get_e_bonus(), monster)
    
    def get_q_damage(self, monster: Monster=None):
        multiplier = Ye_Lan_Ch.Q_MULTIPLIER[self.q_idx()]
        return self.__get_damage(multiplier, self.get_q_bonus(), monster)
    
    def get_qxt_damage(self, monster: Monster=None):
        multiplier = Ye_Lan_Ch.QXT_MULTIPLIER[self.q_idx()]
        return self.__get_damage(multiplier, self.get_q_bonus(), monster)
    
    def get_extra_qxt_damage(self, monster: Monster=None):
        if self.ming_zuo_num < 2:
            return 0
        
        return self.__get_damage(14/100, self.get_q_bonus(), monster)
    
    def do_e(self, plan: ActionPlan, t):
        """
        t: E技能引爆的时间
        """
        plan.add_action(YeLan_E_Action(t, self))

    def do_q(self, plan: ActionPlan, q_anim_start_time, do_damage = False):
        pass


class YeLan_Ming_4_Action(Action, Buff):
    def __init__(self):
        super().__init__("夜兰四命生效一层")

    def do_impl(self, plan: ActionPlan):
        plan.add_extra_attr(self)

    def get_hp_percent(self, plan, target_character):
        # FIXME: 生效时长是否要加？持续25秒是否能覆盖整个输出轴？
        return 0.1
    

class YeLan_E_Action(Action):
    def __init__(self, start_time, ye_lan: Ye_Lan_Ch):
        super().__init__("夜兰E", start_time)
        self.ye_lan = ye_lan

    def do(self, plan: ActionPlan):
        if self.ye_lan.calc_damage:
            plan.add_damage(self.ye_lan.get_e_damage(), self.ye_lan)



class YeLan_Q_Bonus_Action(AttributeAction):
    def __init__(self):
        super().__init__("夜兰Q增伤开始")

    def do_impl(self, plan: ActionPlan):
        plan.add_extra_attr(self)

    def get_elem_bonus(self, plan: ActionPlan, target_character: Character):
        if not target_character.is_in_foreground():
            return 0
        
        cur_time = plan.current_action_time
        dur = cur_time - self.get_timestamp()
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