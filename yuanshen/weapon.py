from .item import Ys_Item


# 武器的特点(圣遗物套装有同样的特点)
# 1. 能给 characters 提供一些 fixed_attrs
# 2. 有些武器被动需要在实战运行中触发(监听事件)，相当于是一个 Buff


class Ys_Weapon(Ys_Item):
    def __init_subclass__(cls, name, **kwargs):
        """
        base_atk: 基础攻击力(武器主词条)
        """
        
        super().__init_subclass__(**kwargs)
        cls.name = name

    def __init__(self, base_atk):
        self.base_atk = base_atk