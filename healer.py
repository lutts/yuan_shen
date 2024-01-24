#!/user/bin/env python3 -tt
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

from action import Action, ActionPlan

# 奶妈的几个要点：
# 1. 奶的时候，是奶全队，还是只奶前台
# 2. 是掉血就触发奶，还是只按固定的间隔奶
# 3. 掉血就触发奶也分两种：
#   a. 有固定的治疗间隔，治疗后，在这段间隔内不会再次治疗
#   b. 只要掉血，就会奶
# 4. 事件触发的奶，和是否掉血无关，例如白术的大招在盾破碎时就会治疗，七七开e后普攻或重击打怪就会治疗，芭芭拉开e后普攻，心海开q后普攻，等等

class Healer_Action(Action):
    def do_impl(self, plan: ActionPlan):
        return super().do_impl(plan)