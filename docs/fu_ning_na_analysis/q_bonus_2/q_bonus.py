import sys
import os
import random
from collections import namedtuple
from typing import NamedTuple

sys.path.append(os.path.abspath('../..'))
sys.path.append(os.path.abspath('../../..'))

print(sys.path)

from analysis_utils.ys_timestamps import Ys_Timestamp, print_timestamps_summary, print_avg_min_max
from yuanshen.utils import ys_crit_damage
from yuanshen.monster import Monster

timestamp_dict = {
    "BIQM0831": ["00:00:02.817", "00:00:04.510", "00:00:22.530", "00:00:22.630", "00:00:22.730"],
    "COOE9058": ["00:00:01.900", "00:00:03.583", "00:00:21.572", "00:00:21.638", "00:00:21.738"],
    "CQGZ6621": ["00:00:02.717", "00:00:04.485", "00:00:22.388", "00:00:22.438", "00:00:22.522"],
    "DFXN8271": ["00:00:03.567", "00:00:05.252", "00:00:23.272", "00:00:23.388", "00:00:23.588"],
    "DTUH0332": ["00:00:01.167", "00:00:02.800", "00:00:20.855", "00:00:20.972", "00:00:21.072"],
    "EAOG1399": ["00:00:01.183", "00:00:02.833", "00:00:20.855", "00:00:20.905", "00:00:21.022"],
    "FFXO3278": ["00:00:02.917", "00:00:04.585", "00:00:22.605", "00:00:22.722", "00:00:23.022"],
    "IDHI1234": ["00:00:02.883", "00:00:04.552", "00:00:22.555", "00:00:22.672", "00:00:22.872"],
    "ITQE8747": ["00:00:00.900", "00:00:02.583", "00:00:20.588", "00:00:20.705", "00:00:20.905"],
    "KIJQ2393": ["00:00:00.950", "00:00:02.617", "00:00:20.655", "00:00:20.772", "00:00:20.872"],
    "LBOZ6415": ["00:00:03.333", "00:00:05.102", "00:00:23.022", "00:00:23.088", "00:00:23.188"],
    "NAWF3466": ["00:00:02.850", "00:00:04.502", "00:00:22.555", "00:00:22.672", "00:00:22.972"],
    "NXDB0573": ["00:00:02.950", "00:00:04.635", "00:00:22.655", "00:00:22.772", "00:00:22.872"],
    "PYNQ0427": ["00:00:02.933", "00:00:04.618", "00:00:22.605", "00:00:22.655", "00:00:22.955"],
    "QIBR6807": ["00:00:03.700", "00:00:05.368", "00:00:23.422", "00:00:23.472", "00:00:23.672"],
    "QJDQ3936": ["00:00:03.017", "00:00:04.685", "00:00:22.672", "00:00:22.788", "00:00:23.088"],
    "SJZW3632": ["00:00:01.167", "00:00:02.850", "00:00:20.938", "00:00:21.005", "00:00:21.105"],
    "UQAW5464": ["00:00:01.650", "00:00:03.333", "00:00:21.322", "00:00:21.422", "00:00:21.638"],
    "XTIQ5433": ["00:00:02.650", "00:00:04.318", "00:00:22.355", "00:00:22.472", "00:00:22.672"],
    "XZOS4291": ["00:00:02.867", "00:00:04.618", "00:00:22.538", "00:00:22.638", "00:00:22.738"]
}

class Video_Timestamps(NamedTuple):
    q_anim_start: Ys_Timestamp
    q_damage: Ys_Timestamp
    pao_pao_dismiss: Ys_Timestamp
    hp_restore: Ys_Timestamp
    ling_hua_first_unbonused: Ys_Timestamp


def get_intervals(ys_timestamp_dict: dict[str, Video_Timestamps]):
    intervals_dict = {}
    for filename, t in ys_timestamp_dict.items():
        intervals_dict[filename] = {
            "Q动画开始 - Q出伤": t.q_damage - t.q_anim_start,
            "Q动画开始 - 泡泡消失": t.pao_pao_dismiss - t.q_anim_start,
            "Q动画开始 - 泡泡消失 - 减18": round(t.pao_pao_dismiss - t.q_anim_start - 18, 3),
            "Q出伤 - 泡泡消失 - 减18 ": round(t.pao_pao_dismiss - t.q_damage - 18, 3),
            "泡泡消失 - 生命值上限重置": t.hp_restore - t.pao_pao_dismiss,
            "Q动画开始 - 生命值上限重置": t.hp_restore - t.q_anim_start,
            "Q动画开始 - 生命值上限重置 - 减18": round(t.hp_restore - t.q_anim_start - 18, 3),
            "允许的最大Q动画开始-生命值上限重置": t.ling_hua_first_unbonused - t.q_anim_start
        }
    
    return intervals_dict


sorted_intervals = print_timestamps_summary(Video_Timestamps, timestamp_dict, get_intervals)

a_multiplier = [70.3/100, 63.6/100, 80.1/100, 106.5/100, 107.9/100, 13.8/100]
max_hp = [44764, 46817, 48960, 48960]
e_bonus = [0.616, 0.616 + 0.08, 0.616 + 2 * 0.08, 0.616 + 3 * 0.08]
salom_member_multiplier = [6.87/100, 12.67/100, 17.61/100]
cd = 2.369


def  get_hp_and_bonus(zw_hp_level, zw_e_level, qi, is_e):
    hp = max_hp[zw_hp_level]
    bonus = 0.466 + 0.15

    if is_e:
        bonus += 0.28   # 固有天赋
        bonus += 0.08 * zw_e_level

    if qi > 400:
        hp += 15307 * (qi - 400) * 0.0035
    
    if qi > 0:
        bonus += min(400, qi) * 0.0031

    return (hp, bonus)


def get_a_damage(zw_hp_level, zw_e_level, monster, qi=0, phrase=1, hei_dao=True):
    multiplier = a_multiplier[phrase - 1]
    if hei_dao:
        full_multiplier = 18/100
    else:
        full_multiplier = (18 + 25) / 100

    hp, bonus = get_hp_and_bonus(zw_hp_level, 0, qi, is_e=False)
    damage = (1124 * multiplier + hp * full_multiplier) * (1 + bonus)
    damage = monster.attacked(damage)
    return (int(damage), ys_crit_damage(damage, cd))


def get_e_damage(zw_hp_level, zw_e_level, monster, qi=0):
    hp, bonus = get_hp_and_bonus(zw_hp_level, zw_e_level, qi, is_e=True)
    bonus -= 0.28
    damage = hp * 16.71 / 100 * (1 + bonus)
    damage = monster.attacked(damage)
    return (int(damage), ys_crit_damage(damage, cd))


def get_salon_member_damage(multiplier, zw_hp_level, zw_e_level, monster, qi=0):
    hp, bonus = get_hp_and_bonus(zw_hp_level, zw_e_level, qi, is_e=True)
    damage = hp * multiplier * (1 + bonus) * 1.4
    damage = monster.attacked(damage)
    return (int(damage), ys_crit_damage(damage, cd))

def get_fu_ren_damage(zw_hp_level, zw_e_level, monster, qi=0):
    return get_salon_member_damage(6.87/100, zw_hp_level, zw_e_level, monster, qi)

def get_xun_jue_damage(zw_hp_level, zw_e_level, monster, qi=0):
    return get_salon_member_damage(12.67/100, zw_hp_level, zw_e_level, monster, qi)

def get_pang_xie_damage(zw_hp_level, zw_e_level, monster, qi=0):
    return get_salon_member_damage(17.61/100, zw_hp_level, zw_e_level, monster, qi)


def get_q_damage(zw_hp_level, zw_e_level, monster, qi=0):
    hp, bonus = get_hp_and_bonus(zw_hp_level=zw_hp_level, zw_e_level=0, qi=qi,  is_e=False)
    damage = hp * 24.24 / 100 * (1 + bonus)
    damage = monster.attacked(damage)
    return (int(damage), ys_crit_damage(damage, cd))


from enum import Enum
class D_Compare_Result(Enum):
    EQUAL = "equal"
    LESS = "less"
    GREATER = "greater"

def damage_compare(damage, base_damage):
    low =  base_damage - 3
    high = base_damage + 3
    if low <= damage and damage <= high:
        return D_Compare_Result.EQUAL
    elif damage < low:
        return D_Compare_Result.LESS
    else:
        return D_Compare_Result.GREATER
    

def get_qi_from_damage(damage, monster: Monster, zw_hp_level, zw_e_level, damage_func, is_crit, **kwargs):
    if is_crit:
        damage /= (1 + cd)

    d, _  = damage_func(zw_hp_level, zw_e_level, monster, qi=0, **kwargs)
    if damage_compare(d, damage) is D_Compare_Result.EQUAL:
        return 0
    
    d, _ = damage_func(zw_hp_level, zw_e_level, monster, qi=800, **kwargs)
    if damage_compare(d, damage) is D_Compare_Result.EQUAL:
        return 800

    qi_low = 0
    qi_high = 800
    
    while qi_low < qi_high:
        qi = round((qi_low + qi_high) / 2, 3)

        d, _ = damage_func(zw_hp_level, zw_e_level, monster, qi=qi, **kwargs)
        if damage == d:
            return qi
        elif damage < d:
            qi_high = qi - 0.001
        else:
            qi_low = qi + 0.001
        # cr = damage_compare(damage, d)
        # if cr is D_Compare_Result.EQUAL:
        #     return qi
        # elif cr is D_Compare_Result.LESS:
        #     qi_high = qi - 0.001
        # else:
        #     qi_low = qi + 0.001

    return qi_high


monster = Monster(level=93, kang_xin=3.1)
monster.add_jian_kang(0.2)  # 钟离


print("e: ", get_e_damage(0, 0, monster))

print("夫人出伤: ", get_fu_ren_damage(zw_hp_level=1, zw_e_level=0, monster=monster))
print("勋爵出伤: ", get_xun_jue_damage(zw_hp_level=1, zw_e_level=0, monster=monster))
print("螃蟹出伤: ", get_pang_xie_damage(zw_hp_level=1, zw_e_level=0, monster=monster))

print("Q出伤: ", get_q_damage(zw_hp_level=1, zw_e_level=0, monster=monster, qi=150))

print("第一刀: ", get_a_damage(zw_hp_level=2, zw_e_level=1, monster=monster, qi=172.4, phrase=1, hei_dao=True))


print(get_qi_from_damage(929, monster, zw_hp_level=1, zw_e_level=0, damage_func=get_q_damage, is_crit=False))
print(get_qi_from_damage(2739, monster, zw_hp_level=2, zw_e_level=1, damage_func=get_a_damage, is_crit=True, phrase=1, hei_dao=True))