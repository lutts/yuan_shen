"""
Module documentation.
"""

import uuid
from .basic import Ys_Attribute_Supplier, Ys_Elem_Type

class ShengYiWu(Ys_Attribute_Supplier):
    ALL_PARTS = ['h', 'y', 's', 'b', 't']
    PART_HUA = 'h'
    PART_YU = 'y'
    PART_SHA = 's'
    PART_BEI = 'b'
    PART_TOU = 't'

    PART_TO_POSITION = {
        PART_HUA: 0,
        PART_YU: 1,
        PART_SHA: 2,
        PART_BEI: 3,
        PART_TOU: 4
    }

    ENERGY_RECHARGE_MAX = 0.518
    BONUS_MAX = 0.466
    CRIT_RATE_MAIN = 0.311
    CRIT_DAMAGE_MAIN = 0.622
    ELEM_MASTERY_MAIN = 187

    JU_TUAN = 'ju_tuan'
    LIE_REN = 'lie_ren'
    HUA_HAI = 'hua_hai'
    SHUI_XIAN = 'shui_xian'
    LE_YUAN = 'le_yuan'
    SHI_JIN = 'shi_jin'
    SHEN_LIN = 'shen_lin'
    JUE_YUAN = 'jue_yuan'
    ZHUI_YI = 'zhui_yi'
    QIAN_YAN = 'qian_yan'
    CHEN_LUN = 'chen_lun'
    BING_TAO = 'bing_tao'
    RU_LEI = 'ru_lei'
    FENG_TAO = 'feng_tao'
    ZONG_SHI = 'zong_shi'
    YUE_TUAN = 'yue_tuan'
    JUE_DOU_SHI = 'jue_dou_shi'
    SHA_SHANG = 'sha_shang'
    QI_SHI_DAO = 'qi_shi_dao'
    HUI_SHENG = "hui_sheng"
    XI_SHI_ZHI_GE = "xi shi zhi ge"

    def __init__(self, name, part, crit_rate=0.0, crit_damage=0.0, hp_percent=0.0, hp=0, energy_recharge=0.0,
                 atk_per=0.0, atk=0, def_per=0.0, def_v=0, elem_mastery=0, elem_bonus=0.0, elem_type: Ys_Elem_Type=None):
        self.id = str(uuid.uuid4())
        self.name = name
        self.part = part
        self.position = ShengYiWu.PART_TO_POSITION[part]
        # TODO: 圣遗物属性有隐藏小数点，有空的时候可以研究一下，不过影响不大，不急

        super().__init__(crit_rate=crit_rate, crit_damage=crit_damage, hp_percent=hp_percent, hp=hp,
                         atk_per=atk_per, atk=atk, def_per=def_per, def_v=def_v,
                         elem_mastery=elem_mastery, elem_bonus=elem_bonus,
                         energy_recharge=energy_recharge)
        self.elem_type: Ys_Elem_Type = elem_type

    @classmethod
    def from_string(cls, syw_str: str):
        # (jue_yuan, h, cc:0.066, cd:0.117, atkp:0.111, atk:33)
        syw_str = syw_str.strip('() ')
        attrs = syw_str.split(", ")
        if len(attrs) < 6:
            return None
        
        name = attrs[0]
        part = attrs[1]
        syw = ShengYiWu(name, part)
        for i in range(2, len(attrs)):
            attr = attrs[i]
            key, value = attr.split(':')

            try:
                fvalue = float(value)
            except:
                pass

            if key == "cc":
                syw.crit_rate = fvalue
            elif key == "cd":
                syw.crit_damage = fvalue
            elif key == "hpp":
                syw.hp_percent = fvalue
            elif key == "hp":
                syw.hp = int(value)
            elif key == "re":
                syw.energy_recharge = fvalue
            elif key == "atkp":
                syw.atk_per = fvalue
            elif key == "atk":
                syw.atk = int(value)
            elif key == "defp":
                syw.def_per = fvalue
            elif key == "def":
                syw.def_v = int(value)
            elif key == "elem":
                syw.elem_mastery = int(value)
            elif key == "bonus":
                syw.elem_bonus = fvalue
            elif key == "et":
                syw.elem_type = Ys_Elem_Type(value)

        return syw
    
    @classmethod
    def string_to_syw_combine(cls, syw_combine_str: str | list[str]):
        if isinstance(syw_combine_str, list):
            syw_str_lst = syw_combine_str
        else:
            syw_str_lst = syw_combine_str.split("), (")
        syw_combine = []
        for syw_str in syw_str_lst:
            syw = ShengYiWu.from_string(syw_str)
            if syw:
                syw_combine.append(syw)
            else:
                raise Exception("parse syw combine string failed on " + syw_str)
            
        return syw_combine

    def __str__(self):
        s = '(' + self.name + ', ' + self.part + ", "
        s += super().__str__()
        if self.elem_type:
            s += ", et:" + self.elem_type.value
        s += ')'
        return s

    def __repr__(self) -> str:
        return self.__str__()