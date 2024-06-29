from ..weapon import Ys_Weapon
from ..character import Character, Character_HP_Change_Data
from ..action import Action, ActionPlan


class Jing_Shui_Liu_Yong_Zhi_Hui(Ys_Weapon, name="静水流涌之辉"):
    E_BONUS_MULTIPLIER = [8/100, 10/100, 12/100, 14/100, 16/100]
    HP_BONUS_MULTIPLIER = [14/100, 17.5/100, 21/100, 24.5/100, 28/100]

    def __init__(self, base_atk=542, crit_damage=0.882, refinement_rank=1):
        """
        默认为 90 级精一
        """
        self.base_atk = base_atk
        self.crit_damage = crit_damage
        self.e_bonus_multiplier = Jing_Shui_Liu_Yong_Zhi_Hui.E_BONUS_MULTIPLIER[refinement_rank - 1]
        self.hp_bonus_multiplier = Jing_Shui_Liu_Yong_Zhi_Hui.HP_BONUS_MULTIPLIER[refinement_rank - 1]

        self.reset()

    def reset(self, plan):
        self.remove_callback(plan)
        self.__e_bonus_level = 0
        self.__e_bonus_last_change_time = 0

        self.__hp_bonus_level = 0
        self.__hp_bonus_last_change_time = 0

    def apply_fixed_attr(self, owner: Character):
        owner.fixed_attrs.crit_damage += self.crit_damage
    
    def apply_dynamic_attr(self, owner: Character, plan: ActionPlan):
        if plan is None:
            owner.buff_attrs.e_bonus += self.e_bonus_multiplier * 3
            owner.get_hp().buff_attrs.hp_per += self.hp_bonus_multiplier * 2
            owner.get_hp().on_max_hp_changed()
        else:
            plan.add_consume_hp_callback(self.on_hp_changed)
            plan.add_regenerate_hp_callback(self.on_hp_changed)

    def remove_callback(self, plan: ActionPlan):
        plan.remove_consume_hp_callback(self.on_hp_changed)
        plan.remove_regenerate_hp_callback(self.on_hp_changed)
    
    def on_hp_changed(self, plan: ActionPlan, source: Character, targets_with_data: list[Character_HP_Change_Data]):
        teammate_processed = False
        owner = self.get_owner()
        for tdata in targets_with_data:
            if tdata.character is owner:
                self.increase_e_bonus_level(plan)
            elif not teammate_processed:
                self.increase_hp_bonus_level(plan)
                teammate_processed = True

        if self.__hp_bonus_level >= 2 and self.__e_bonus_level >= 3:
            self.remove_callback(plan)
                      
    def increase_e_bonus_level(self, plan: ActionPlan):
        if self.__e_bonus_level >= 3:
            return
        
        cur_time = plan.current_action_time

        if self.__e_bonus_last_change_time and (cur_time - self.__e_bonus_last_change_time < 0.2):
            return

        self.__e_bonus_last_change_time = cur_time
        self.__e_bonus_level += 1

        action = Increase_JingShui_E_Bonus_Level_Action(self)
        action.set_timestamp(cur_time + plan.get_effective_delay())
        plan.insert_action_runtime(action)

    def increase_hp_bonus_level(self, plan: ActionPlan):
        if self.__hp_bonus_level >= 2:
            return
        
        cur_time = plan.current_action_time

        if self.__hp_bonus_last_change_time and (cur_time - self.__hp_bonus_last_change_time < 0.2):
            # 有0.2秒的CD
            return

        self.__hp_bonus_last_change_time = cur_time
        self.__hp_bonus_level += 1

        action = Increase_JingShui_Hp_Level_Action(self)
        action.set_timestamp(cur_time + plan.get_effective_delay())
        plan.insert_action_runtime(action)
    
class Increase_JingShui_Hp_Level_Action(Action):
    def __init__(self, supervisor: Jing_Shui_Liu_Yong_Zhi_Hui):
        super().__init__("静水流涌之辉生命值叠层")
        self.supervisor = supervisor

    def do_impl(self, plan: ActionPlan):
        owner: Character = self.supervisor.owner
        multiplier = Jing_Shui_Liu_Yong_Zhi_Hui.HP_BONUS_MULTIPLIER[self.supervisor.refinement_rank - 1]
        owner.get_hp().modify_max_hp_per(multiplier)
        self.debug("静水流涌之辉生命叠一层，目前层数: %d",  self.supervisor.hp_bonus_level)


class Increase_JingShui_E_Bonus_Level_Action(Action):
    def __init__(self, supervisor: Jing_Shui_Liu_Yong_Zhi_Hui):
        super().__init__("静水流涌之辉战技增伤叠层")
        self.supervisor = supervisor

    def do_impl(self, plan: ActionPlan):
        owner: Character = self.supervisor.owner
        multiplier = Jing_Shui_Liu_Yong_Zhi_Hui.E_BONUS_MULTIPLIER[self.supervisor.refinement_rank - 1]
        owner.add_e_bonus(multiplier)
        self.debug("静水流涌之辉战技叠一层，目前层数: %d", self.supervisor.e_bonus_level)