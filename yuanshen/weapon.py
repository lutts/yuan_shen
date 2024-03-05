import weakref
from .attribute import Ys_Attribute_Supplier


class Ys_Weapon(Ys_Attribute_Supplier):
    def __init_subclass__(cls, name, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.name = name
    
    def __init__(self, base_atk, jing_lian_rank=1, **kwargs):
        """
        owner: 持有者
        base_atk: 基础攻击力
        jing_lian_rank: 精炼等阶

        kwargs: 副词条及被动提供的相关**静态**属性
        """
        if jing_lian_rank not in [1, 2, 3, 4, 5]:
            raise Exception("精炼等阶只能是1, 2, 3, 4, 5")
        
        self.__owner = None
        self.base_atk = base_atk
        self.jing_lian_rank = jing_lian_rank

        super().__init__(**kwargs)

    def set_owner(self, owner):
        self.__owner = weakref.ref(owner)

    def get_owner(self):
        return self.__owner()