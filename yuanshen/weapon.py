from .attribute import Ys_Attribute_Supplier


class Ys_Weapon(Ys_Attribute_Supplier):
    def __init_subclass__(cls, name, base_atk, refinement_rank=1, **kwargs):
        """
        base_atk: 基础攻击力(武器主词条)
        refinement_rank: 精炼等阶
        """
        if refinement_rank not in [1, 2, 3, 4, 5]:
            raise Exception("精炼等阶只能是1, 2, 3, 4, 5")
        
        super().__init_subclass__(**kwargs)
        cls.name = name
        cls.base_atk = base_atk
        cls.refinement_rank = refinement_rank