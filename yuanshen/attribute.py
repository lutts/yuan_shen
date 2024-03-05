
class Ys_Attribute_Supplier:
    def __init__(self,
                 crit_rate=0.0, crit_damage=0.0,
                 hp_percent=0.0, hp=0,
                 atk_per=0.0, atk=0,
                 def_per=0.0, def_v=0,
                 elem_mastery=0, elem_bonus=0.0,
                 energy_recharge=0.0,

                 normal_a_bonus = 0.0,
                 charged_a_bonus = 0.0,
                 plunging_bonus = 0.0,
                 e_bonus = 0.0,
                 q_bonus = 0.0):
        self.crit_rate = crit_rate
        self.crit_damage = crit_damage
        self.hp_percent = hp_percent
        self.hp = hp
        self.atk_per = atk_per
        self.atk = atk
        self.def_per = def_per
        self.def_v = def_v
        self.elem_mastery = elem_mastery
        self.elem_bonus = elem_bonus
        self.energy_recharge = energy_recharge

        self.normal_a_bonus = normal_a_bonus
        self.charged_a_bonus = charged_a_bonus
        self.plunging_bonus = plunging_bonus
        self.e_bonus = e_bonus
        self.q_bonus = q_bonus

    def apply_static_attributes(self, character):
        """
        设置没有和怪物进入战斗时的属性
        """
        pass

    def apply_combat_attributes(self, character):
        """
        设置和怪物进入战斗时的属性
        """
        pass

    def apply_passive(self, character, action_plan=None):
        """
        有些属性是有条件触发的, 例如芙芙专武需要扣血叠层

        action_plan 如果为 None，需要假设条件达成，对 character 直接进行属性设置
        """
        pass

    def __str__(self):
        attrs = []
        if self.crit_rate:
            attrs.append('cc:' + str(self.crit_rate))

        if self.crit_damage:
            attrs.append('cd:' + str(self.crit_damage))

        if self.hp_percent:
            attrs.append('hpp:' + str(self.hp_percent))

        if self.hp:
            attrs.append('hp:' + str(self.hp))

        if self.energy_recharge:
            attrs.append('re:' + str(self.energy_recharge))

        if self.atk_per:
            attrs.append('atkp:' + str(self.atk_per))

        if self.atk:
            attrs.append('atk:' + str(self.atk))

        if self.def_per:
            attrs.append('defp:' + str(self.def_per))

        if self.def_v:
            attrs.append('def:' + str(self.def_v))

        if self.elem_mastery:
            attrs.append('elem:' + str(self.elem_mastery))

        if self.elem_bonus:
            attrs.append('bonus:' + str(self.elem_bonus))

        return ", ".join(attrs)
    
    def __repr__(self) -> str:
        return self.__str__()