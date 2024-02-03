#!/user/bin/env python3 -tt
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

from action import Action, ActionPlan

# 要注意的几个点：
# 1. 治疗对象：全队 or 仅前台 or 某个特定角色
# 2. 是否阻塞：掉血就触发治疗，还是只按固定的间隔治疗，目前只有满命芙芙的奶刀治疗芙芙自已的时候是阻塞的
# 3. 事件触发的治疗，例如白术的大招在盾破碎时就会治疗，七七开e后普攻或重击打怪就会治疗，芭芭拉开e后普攻，心海开q后普攻，等等
# 4. 治疗阈值：高于70%班尼特就不会治疗，角色满血是否会治疗

class Healer_Qin:
    def __init__(self, atk, healing_bonus, ):
        pass

