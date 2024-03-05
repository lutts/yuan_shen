#!/user/bin/env python3 -tt
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

import random
from action import Action, ActionPlan
from character import Character

# 要注意的几个点：
# 1. 治疗对象：全队 or 仅前台 or 某个特定角色
# 2. 是否阻塞：掉血就触发治疗，还是只按固定的间隔治疗，目前只有满命芙芙的奶刀治疗芙芙自已的时候是阻塞的
# 3. 事件触发的治疗，例如白术的大招在盾破碎时就会治疗，七七开e后普攻或重击打怪就会治疗，芭芭拉开e后普攻，心海开q后普攻，等等
# 4. 治疗阈值：高于70%班尼特就不会治疗，角色满血是否会治疗

class Qin_Heal_Field_Action(Action):
    q_level_to_ratio =[
        (0, 0),
        (0.2512, 154), # 1
        (0.2700, 169), # 2
        (0.2889, 186), # 3
        (0.3140, 204), # 4
        (0.3328, 223), # 5
        (0.3517, 244), # 6
        (0.3768, 266), # 7
        (0.4019, 289), # 8
        (0.4270, 313), # 9
        (0.4522, 339), # 10
        (0.4773, 366), # 11
        (0.5024, 394), # 12
        (0.5338, 424), # 13
    ]

    def __init__(self, qin: Character):
        super().__init__("琴大招持续治疗")
        self.qin = qin

    def do_impl(self, plan: ActionPlan):
        q_ratio = Qin_Heal_Field_Action.q_level_to_ratio[self.qin.q_level]
        cure_num = round(self.qin.get_atk() * q_ratio[0] + q_ratio[1])
        self.debug("琴大招持续治疗")
        plan.regenerate_hp(targets=plan.characters, hp=cure_num, source=self.qin)


class Qin_Heal_Action(Action):
    q_level_to_ratio =[
        (0, 0),
        (2.51, 1540), # 1
        (2.70, 1694), # 2
        (2.89, 1861), # 3
        (3.14, 2041), # 4
        (3.33, 2234), # 5
        (3.52, 2439), # 6
        (3.77, 2657), # 7
        (4.02, 2888), # 8
        (4.27, 3132), # 9
        (4.52, 3389), # 10
        (4.77, 3659), # 11
        (5.02, 3941), # 12
        (5.34, 4236), # 13
    ]
    def __init__(self, name, qin:Character):
        super().__init__(name)

        self.qin = qin

    def get_cure_interval(self):
        return random.randint(int(0.971 * 1000), int(1.035 * 1000)) / 1000

    def do_impl(self, plan: ActionPlan):
        q_ratio = Qin_Heal_Action.q_level_to_ratio[self.qin.q_level]
        cure_num = round(self.qin.get_atk() * q_ratio[0] + q_ratio[1])

        self.debug("琴治疗全队")
        plan.regenerate_hp(targets=plan.characters, hp=cure_num, source=self.qin)

        cur_time = plan.get_current_action_time()
        end_time = cur_time + 10
        next_cure_time = cur_time + self.get_cure_interval()
        for _ in range(0, 10):
            action = Qin_Heal_Field_Action(self.qin)
            action.set_timestamp(next_cure_time)
            plan.insert_action_runtime(action)

            next_cure_time += self.get_cure_interval()
            if next_cure_time > end_time:
                next_cure_time = end_time
