import weakref

class Ys_Attribute_Supplier:
    def __init__(self,
                 crit_rate=0.0, crit_damage=0.0,
                 hp_percent=0.0, hp=0,
                 atk_per=0.0, atk=0,
                 def_per=0.0, def_v=0,
                 elem_mastery=0,
                 energy_recharge=0.0,

                 normal_a_bonus = 0.0,
                 charged_a_bonus = 0.0,
                 plunging_bonus = 0.0,
                 e_bonus = 0.0,
                 q_bonus = 0.0,
                 elem_bonus=0.0):
        """
        这里的参数理应只包括静态属性，所谓静态属性是指：无需释放技能就可以拥有属性

        例如：

        * 圣遗物提供的属性
        * 武器的主副词条
        * 武器中一些只需要出战，但不需要进入战斗就能获得的属性，比如螭骨剑的叠层等等
        """
        self.crit_rate = crit_rate
        self.crit_damage = crit_damage
        self.hp_percent = hp_percent
        self.hp = hp
        self.atk_per = atk_per
        self.atk = atk
        self.def_per = def_per
        self.def_v = def_v
        self.elem_mastery = elem_mastery
        self.energy_recharge = energy_recharge

        self.normal_a_bonus = normal_a_bonus
        self.charged_a_bonus = charged_a_bonus
        self.plunging_bonus = plunging_bonus
        self.e_bonus = e_bonus
        self.q_bonus = q_bonus
        self.elem_bonus = elem_bonus

        self.__owner = None

    def set_owner(self, owner):
        self.__owner = weakref.ref(owner)

    def get_owner(self):
        return self.__owner()

    def apply_passive(self, plan):
        """
        重载这个函数完成两件事

        1. 为触发被动做准备，比如向 plan 监听某个事件
        2. 有些武器或圣遗物特效能影响队友，重载这个函数进行设置
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