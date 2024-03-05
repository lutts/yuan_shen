from ..weapon import Ys_Weapon
from ..character import Character, Character_HP_Change_Data
from ..action import Action, ActionPlan


class Jing_Shui_Liu_Yong_Zhi_Hui(Ys_Weapon, name="静水流涌之辉"):
    E_BONUS_MULTIPLIER = [8/100, 10/100, 12/100, 14/100, 16/100]
    HP_BONUS_MULTIPLIER = [14/100, 17.5/100, 21/100, 24.5/100, 28/100]

    def __init__(self, base_atk, jing_lian_rank=1, **kwargs):
        super().__init__(base_atk, jing_lian_rank=jing_lian_rank, **kwargs)

        self.__e_bonus_level = 0
        self.__e_bonus_last_change_time = 0

        self.__hp_bonus_level = 0
        self.__hp_bonus_last_change_time = 0

    @property
    def e_bonus_level(self):
        return self.__e_bonus_level
    
    @property
    def hp_bonus_level(self):
        return self.__hp_bonus_level
    
    def apply_static_attributes(self, character: Character):
        character.add_crit_damage(0.882)
    
    def apply_passive(self, character: Character, action_plan: ActionPlan=None):
        if not action_plan:
            character.add_e_bonus(Jing_Shui_Liu_Yong_Zhi_Hui.E_BONUS_MULTIPLIER[self.jing_lian_rank - 1])
            character.get_hp().modify_max_hp_per(Jing_Shui_Liu_Yong_Zhi_Hui.HP_BONUS_MULTIPLIER[self.jing_lian_rank - 1])
        else:
            action_plan.add_consume_hp_callback(self.on_hp_changed)
            action_plan.add_regenerate_hp_callback(self.on_hp_changed)

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
            plan.remove_consume_hp_callback(self.on_hp_changed)
            plan.remove_regenerate_hp_callback(self.on_hp_changed)
                      
    def increase_e_bonus_level(self, plan: ActionPlan):
        if self.__e_bonus_level >= 3:
            return
        
        cur_time = plan.get_current_action_time()

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
        
        cur_time = plan.get_current_action_time()

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
        multiplier = Jing_Shui_Liu_Yong_Zhi_Hui.HP_BONUS_MULTIPLIER[self.supervisor.jing_lian_rank - 1]
        owner.get_hp().modify_max_hp_per(multiplier)
        self.debug("静水流涌之辉生命叠一层，目前层数: %d",  self.supervisor.hp_bonus_level)
        if Action.enable_record:
            plan.damage_record_hp()


class Increase_JingShui_E_Bonus_Level_Action(Action):
    def __init__(self, supervisor: Jing_Shui_Liu_Yong_Zhi_Hui):
        super().__init__("静水流涌之辉战技增伤叠层")
        self.supervisor = supervisor

    def do_impl(self, plan: ActionPlan):
        owner: Character = self.supervisor.owner
        multiplier = Jing_Shui_Liu_Yong_Zhi_Hui.E_BONUS_MULTIPLIER[self.supervisor.jing_lian_rank - 1]
        owner.add_e_bonus(multiplier)
        self.debug("静水流涌之辉战技叠一层，目前层数: %d", self.supervisor.e_bonus_level)
        # FIXME:
        # plan.damage_record_bonus()