import sys
import os
sys.path.append(os.path.abspath('../..'))

from yuanshen.utils import ys_crit_damage
from yuanshen.monster import Monster

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

monster = Monster(level=93, kang_xin=-0.2)
monster.add_jian_kang(0.2)
print(monster.attacked(1124 * 0.703 * 1.465))

print("===============")

monster = Monster()
monster.add_jian_kang(0.4)
print(monster.attacked(1))
print(monster.attacked(41988 * 14.47 / 100 * (1 + 1.4764 + 0.3)))