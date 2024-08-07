from enum import Enum


class Ys_Elem_Type(Enum):
    HUO = "Pyro"
    SHUI = "Hydro"
    LEI = "Electro"
    BING = "Cryo"

    CAO = "Dendro"

    FENG = "Anemo"

    YAN = "Geo"
    WU_LI = "wu li"


class TeamElemGongMing:
    def __init__(self, team_elem_types: list[Ys_Elem_Type]):
        self.team_elem_types = team_elem_types

        self.huo_num = 0
        self.shui_num = 0
        self.bing_num = 0

        self.cao_num = 0
        self.yan_num = 0
        
        for et in team_elem_types:
            if et is Ys_Elem_Type.HUO:
                self.huo_num += 1
            elif et is Ys_Elem_Type.SHUI:
                self.shui_num += 1
            elif et is Ys_Elem_Type.BING:
                self.bing_num += 1
            elif et is Ys_Elem_Type.CAO:
                self.cao_num += 1
            elif et is Ys_Elem_Type.YAN:
                self.yan_num += 1

        if self.huo_num >= 2:
            self.atk_per = 0.25
        else:
            self.atk_per = 0

        if self.shui_num >= 2:
            self.hp_per = 0.25
        else:
            self.hp_per = 0

        if self.bing_num >= 2:
            self.crit_rate = 0.15
        else:
            self.crit_rate = 0

        if self.cao_num >= 2:
            self.elem_mastery = 50 + 30 + 20
        else:
            self.elem_mastery = 0

        if self.yan_num >= 2:
            # NOTE: 双岩共鸣的 buff 是有限制的：1) 前台有护盾时才有 15% 的增伤，2) 只减岩抗
            # 造成伤害使岩元素抗性下降20%，持续15秒，时间很长，加上可能的结晶盾，因此这里我们假设减抗是常驻的
            # 假设的前提：15秒内会攻击一次刷新时间、盾如果破碎的话，15秒内会重新开盾(主动开盾或捡结晶盾)
            self.elem_bonus = 0.15
            self.jian_kang = 0.2