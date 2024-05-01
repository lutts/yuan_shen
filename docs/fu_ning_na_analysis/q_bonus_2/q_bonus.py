import sys
import os
import random
from collections import namedtuple
from typing import NamedTuple

sys.path.append(os.path.abspath('../..'))
sys.path.append(os.path.abspath('../../..'))

from analysis_utils.ys_timestamps import Ys_Timestamp, print_timestamps_summary, print_avg_min_max, null_timestamp
from yuanshen.utils import ys_crit_damage
from yuanshen.monster import Monster

timestamp_dict = {
    "BIQM0831": ["00:00:02.817", "00:00:04.510", "00:00:21.213", "00:00:22.530", "00:00:22.630", 
                 "00:00:22.397", "00:00:22.547", "00:00:22.647", "00:00:22.730"],
    "COOE9058": ["00:00:01.900", "00:00:03.583", "00:00:20.305", "00:00:21.572", "00:00:21.638", 
                 "00:00:21.405", "00:00:21.472", "00:00:21.655", "00:00:21.738"],
    "CQGZ6621": ["00:00:02.717", "00:00:04.485", "00:00:21.255", "00:00:22.388", "00:00:22.438", 
                 "00:00:22.205", "00:00:22.305", "00:00:22.455", "00:00:22.522"],
    "DFXN8271": ["00:00:03.567", "00:00:05.252", "00:00:21.988", "00:00:23.272", "00:00:23.388", 
                 "00:00:23.188", "00:00:23.322", "00:00:23.438", "00:00:23.588"],
    "EAOG1399": ["00:00:01.183", "00:00:02.833", "00:00:19.603", "00:00:20.855", "00:00:20.905", 
                 "00:00:20.705", "00:00:20.822", "00:00:20.955", "00:00:21.022"],
    "IDHI1234": ["00:00:02.883", "00:00:04.552", "00:00:21.272", "00:00:22.555", "00:00:22.672", 
                 "00:00:22.488", "00:00:22.572", "00:00:22.738", "00:00:22.872"],
    "ITQE8747": ["00:00:00.900", "00:00:02.583", "00:00:19.287", "00:00:20.588", "00:00:20.705", 
                 "00:00:20.588", "00:00:20.672", "00:00:20.838", "00:00:20.905"],
    "KIJQ2393": ["00:00:00.950", "00:00:02.617", "00:00:19.353", "00:00:20.655", "00:00:20.772", 
                 "00:00:20.505", "00:00:20.638", "00:00:20.755", "00:00:20.872"],
    "LBOZ6415": ["00:00:03.333", "00:00:05.102", "00:00:21.722", "00:00:23.022", "00:00:23.088", 
                 "00:00:22.855", "00:00:22.988", "00:00:23.105", "00:00:23.188"],
    "NAWF3466": ["00:00:02.850", "00:00:04.502", "00:00:21.255", "00:00:22.555", "00:00:22.672", 
                 "00:00:22.588", "00:00:22.672", "00:00:22.822", "00:00:22.972"],
    "NXDB0573": ["00:00:02.950", "00:00:04.635", "00:00:21.338", "00:00:22.655", "00:00:22.772", 
                 "00:00:22.538", "00:00:22.638", "00:00:22.788", "00:00:22.872"],
    "PYNQ0427": ["00:00:02.933", "00:00:04.618", "00:00:21.338", "00:00:22.605", "00:00:22.655", 
                 "00:00:22.605", "00:00:22.655", "00:00:22.855", "00:00:22.955"],
    "QIBR6807": ["00:00:03.700", "00:00:05.368", "00:00:22.272", "00:00:23.422", "00:00:23.472", 
                 "00:00:23.288", "00:00:23.438", "00:00:23.538", "00:00:23.672"],
    "SJZW3632": ["00:00:01.167", "00:00:02.850", "00:00:19.553", "00:00:20.938", "00:00:21.005", 
                 "00:00:20.788", "00:00:20.938", "00:00:21.022", "00:00:21.105"],
    "UQAW5464": ["00:00:01.650", "00:00:03.333", "00:00:20.238", "00:00:21.322", "00:00:21.422", 
                 "00:00:21.305", "00:00:21.422", "00:00:21.555", "00:00:21.638"],
    "XTIQ5433": ["00:00:02.650", "00:00:04.318", "00:00:21.055", "00:00:22.355", "00:00:22.472", 
                 "00:00:22.288", "00:00:22.438", "00:00:22.538", "00:00:22.672"],
    "XZOS4291": ["00:00:02.867", "00:00:04.618", "00:00:21.455", "00:00:22.538", "00:00:22.638", 
                 "00:00:22.422", "00:00:22.505", "00:00:22.672", "00:00:22.738"]
}

class Video_Timestamps(NamedTuple):
    q_anim_start: Ys_Timestamp
    q_damage: Ys_Timestamp
    bian_kuang_te_xiao_dismiss: Ys_Timestamp
    pao_pao_disappear: Ys_Timestamp
    hp_restore: Ys_Timestamp

    ling_hua_last_bonused_hit: Ys_Timestamp
    ling_hua_last_bonused_damage:  Ys_Timestamp

    ling_hua_first_unbonused_hit: Ys_Timestamp
    ling_hua_first_unbonused_damage: Ys_Timestamp


def get_intervals(ys_timestamp_dict: dict[str, Video_Timestamps]):
    intervals_dict = {}
    for filename, t in ys_timestamp_dict.items():
        ling_hua_bonused_hit_delay = (t.ling_hua_last_bonused_damage - t.ling_hua_last_bonused_hit) / 2
        ling_hua_unbonused_hit_delay = (t.ling_hua_first_unbonused_damage - t.ling_hua_first_unbonused_hit) / 2

        intervals_dict[filename] = {
            "Q动画开始 - Q出伤": t.q_damage - t.q_anim_start,
            "Q动画开始 - 边框特效消失": t.bian_kuang_te_xiao_dismiss - t.q_anim_start,
            "边框特效消失 - 泡泡消失": t.pao_pao_disappear - t.bian_kuang_te_xiao_dismiss,
            "泡泡消失 - 最后一次增伤命中": round(t.ling_hua_last_bonused_hit - t.pao_pao_disappear, 3),
            "泡泡消失 - 最长可能增伤命中": round(t.ling_hua_first_unbonused_hit - t.pao_pao_disappear, 3),
            "泡泡消失 - 生命值上限重置": t.hp_restore - t.pao_pao_disappear,
            "Q动画开始 - 泡泡消失": t.pao_pao_disappear - t.q_anim_start,
            "Q动画开始 - 生命值上限重置": t.hp_restore - t.q_anim_start,
            "允许的最大Q动画开始-生命值上限重置": t.ling_hua_first_unbonused_damage - t.q_anim_start,
            "Q动画开始 - 最后一次增伤命中": round(t.ling_hua_last_bonused_hit - t.q_anim_start, 3),
            "Q动画开始 - 最长可能增伤命中": round(t.ling_hua_first_unbonused_hit - t.q_anim_start, 3),
            "绫华命中 - 出伤": [t.ling_hua_last_bonused_damage - t.ling_hua_last_bonused_hit,
                          t.ling_hua_first_unbonused_damage - t.ling_hua_first_unbonused_hit],
            "绫华吃增伤命中 - 出伤/泡泡消失 - 生命值上限重置": (t.ling_hua_last_bonused_damage - t.ling_hua_last_bonused_hit,
                                         t.hp_restore - t.pao_pao_disappear),
        }
    
    return intervals_dict


sorted_intervals = print_timestamps_summary(Video_Timestamps, timestamp_dict, get_intervals)

a_multiplier = [70.3/100, 63.6/100, 80.1/100, 106.5/100, 107.9/100, 13.8/100]
# max_hp = [44764, 46817, 48960, 48960]

init_max_hp = 19759
# init_max_hp = 26267
base_e_bonus = 0
max_hp = [init_max_hp, 
          int(init_max_hp + 0.14 * 15307), 
          int(init_max_hp + 0.28 * 15307)]

salom_member_multiplier = [6.87/100, 12.67/100, 17.61/100]
# cd = 2.369
cd = 1.517
#cd = 1.46

wan_ye_em = 0


def  get_hp_and_bonus(zw_hp_level, zw_e_level, qi, is_e, is_salon_member=True):
    hp = max_hp[zw_hp_level]
    bonus = base_e_bonus

    hp += 15307 * 0.3 # 夜兰 3 个e

    global wan_ye_em
    bonus += wan_ye_em * 0.04 / 100  # 万叶 e

    if qi > 400:
        hp += 15307 * (qi - 400) * 0.0035

    if qi < 0: # 用于测试，数据表明，芙芙的增伤是先消失的，然后才重置生命值上限，这期间可能会插入出伤
        hp += 15307 * 400 * 0.0035
    
    if qi > 0:
        bonus += min(400, qi) * 0.0031

    if is_e:
        if is_salon_member:
            bonus += min(hp / 1000 * 0.7 / 100, 0.28)   # 固有天赋
        bonus += 0.08 * zw_e_level

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
    hp, bonus = get_hp_and_bonus(zw_hp_level, zw_e_level, qi, is_e=True, is_salon_member=False)
    bonus -= 0.28
    damage = hp * 16.71 / 100 * (1 + bonus)
    damage = monster.attacked(damage)
    return (int(damage), ys_crit_damage(damage, cd))


def get_salon_member_damage(multiplier, zw_hp_level, zw_e_level, monster, qi=0):
    hp, bonus = get_hp_and_bonus(zw_hp_level, zw_e_level, qi, is_e=True)
    #print("hp:", round(hp))
    #print("bonus:", round(bonus, 3))
    #print("bonus: ", bonus)
    if qi == 0:
        bonus += 0.08
    damage = hp * multiplier * (1 + bonus) * 1.4
    damage = monster.attacked(damage)
    return (int(damage), ys_crit_damage(damage, cd))

def get_fu_ren_damage(zw_hp_level, zw_e_level, monster, qi=0):
    return get_salon_member_damage(salom_member_multiplier[0], zw_hp_level, zw_e_level, monster, qi)

def get_xun_jue_damage(zw_hp_level, zw_e_level, monster, qi=0):
    return get_salon_member_damage(salom_member_multiplier[1], zw_hp_level, zw_e_level, monster, qi)

def get_pang_xie_damage(zw_hp_level, zw_e_level, monster, qi=0):
    return get_salon_member_damage(salom_member_multiplier[2], zw_hp_level, zw_e_level, monster, qi)


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
#monster.add_jian_kang(0.2)

wan_ye_em = 994 #+ 200
monster.add_jian_kang(0.4)

qi = 0


print("e: ", get_e_damage(0, 0, monster))

print("夫人出伤: ", get_fu_ren_damage(zw_hp_level=2, zw_e_level=3, monster=monster, qi=qi))
print("勋爵出伤: ", get_xun_jue_damage(zw_hp_level=2, zw_e_level=3, monster=monster, qi=qi))
print("螃蟹出伤: ", get_pang_xie_damage(zw_hp_level=2, zw_e_level=3, monster=monster, qi=qi))

print("Q出伤: ", get_q_damage(zw_hp_level=1, zw_e_level=0, monster=monster, qi=150))

print("第一刀: ", get_a_damage(zw_hp_level=2, zw_e_level=1, monster=monster, qi=172.4, phrase=1, hei_dao=True))

rd = 272 / (monster.get_kang_xin_cheng_shang() * monster.get_fang_yu_xi_shu())
rd /= (35146 * 6.87/100)
rd /= 1.4
rd -= 1
print("rd = ", rd)
print("rdiff = ", (rd - 0.883622))

rd = 272 / (35146 * 6.87/100)
rd /= 1.4
rd /= 1.883622
rd /= monster.get_fang_yu_xi_shu()
rd = (1/rd - 1) / 4
print("rd = ", rd)
print("kx: ", monster.get_kang_xin_cheng_shang())


#print(get_qi_from_damage(929, monster, zw_hp_level=1, zw_e_level=0, damage_func=get_q_damage, is_crit=False))
#print(get_qi_from_damage(2739, monster, zw_hp_level=2, zw_e_level=1, damage_func=get_a_damage, is_crit=True, phrase=1, hei_dao=True))

def salon_member_damages():
    global wan_ye_em

    wan_ye_buff_lst = [(994 + 200, 0.4), (994, 0.4), (994 + 200, 0), (994, 0), (0, 0)]
    wan_ye_desc = [
        "          万叶二命",
        "        万叶无二命",
        "  万叶二命(无减抗)",
        "万叶无二命(无减抗)",
        "            无万叶"
    ]
    qi_lst = [800, -1, 0]

    for idx in range(0, len(wan_ye_buff_lst)):
        wan_ye_buff = wan_ye_buff_lst[idx]
        wan_ye_em = wan_ye_buff[0]
        
        monster = Monster(level=93, kang_xin=3.1)
        monster.add_jian_kang(wan_ye_buff[1])

        f_no_zl = []
        x_no_zl = []
        p_no_zl = []
        for qi in qi_lst:
            f_no_zl.append(get_fu_ren_damage(zw_hp_level=2, zw_e_level=3, monster=monster, qi=qi))
            x_no_zl.append(get_xun_jue_damage(zw_hp_level=2, zw_e_level=3, monster=monster, qi=qi))
            p_no_zl.append(get_pang_xie_damage(zw_hp_level=2, zw_e_level=3, monster=monster, qi=qi))

        monster.add_jian_kang(0.2) # 钟离

        f_zl = []
        x_zl = []
        p_zl = []
        for qi in qi_lst:
            f_zl.append(get_fu_ren_damage(zw_hp_level=2, zw_e_level=3, monster=monster, qi=qi))
            x_zl.append(get_xun_jue_damage(zw_hp_level=2, zw_e_level=3, monster=monster, qi=qi))
            p_zl.append(get_pang_xie_damage(zw_hp_level=2, zw_e_level=3, monster=monster, qi=qi))

        print(f"{wan_ye_desc[idx]}:\t夫人出伤: {f_zl[0]}/{f_no_zl[0]}\t{f_zl[1]}/{f_no_zl[1]}\t{f_zl[2]}/{f_no_zl[2]}")
        print(f"\t\t\t勋爵出伤: {x_zl[0]}/{x_no_zl[0]}\t{x_zl[1]}/{x_no_zl[1]}\t{x_zl[2]}/{x_no_zl[2]}")
        print(f"\t\t\t螃蟹出伤: {p_zl[0]}/{p_no_zl[0]}\t{p_zl[1]}/{p_no_zl[1]}\t{p_zl[2]}/{p_no_zl[2]}")
        print("\n")


salon_member_damages()

m1 = Monster(level=93, kang_xin=3.1)
m2 = Monster(level=93, kang_xin=3.1)
m2.add_jian_fang(0.3)

mul = m2.get_fang_yu_xi_shu() / m1.get_fang_yu_xi_shu()

print(1653 * mul)
print(1628 * mul)
print(291 * mul)
print(1459 * mul)
print(1630 * mul)
print(1655 * mul)
print(286 * mul)


def ye_lan_q_damage():
    d = 40166 * 15.53 / 100
    d *= (1 + 0.616 + 0.2 + 0.01)
    d *= 3.4
    m = Monster(level=93, kang_xin=3.1)
    d = m.attacked(d)
    print(round(d))

ye_lan_q_damage()