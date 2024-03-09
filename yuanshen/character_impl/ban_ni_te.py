from ..action import Action, ActionPlan
from ..attribute_hub import ActionPlanAttributeSupplier


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