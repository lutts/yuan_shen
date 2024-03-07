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
            "泡泡消失 - 生命值上限重置": t.hp_restore - t.pao_pao_dismiss,
            "Q动画开始 - 生命值上限重置": t.hp_restore - t.q_anim_start,
            "允许的最大Q动画开始-生命值上限重置": t.ling_hua_first_unbonused - t.q_anim_start
        }
    
    return intervals_dict


sorted_intervals = print_timestamps_summary(Video_Timestamps, timestamp_dict, get_intervals)

a_multiplier = [70.3/100, 63.6/100, 80.1/100, 106.5/100, 107.9/100, 13.8/100]
max_hp = [44764, 46817, 48960, 48960]
e_bonus = [0.616, 0.616 + 0.08, 0.616 + 2 * 0.08, 0.616 + 3 * 0.08]
salom_member_multiplier = [6.87/100, 12.67/100, 17.61/100]

def get_a_damage(phrase, zw_level, monster, hei_dao=True):
    multiplier = a_multiplier[phrase - 1]
    if hei_dao:
        full_multiplier = 18/100
    else:
        full_multiplier = (18 + 25) / 100
    damage = (1124 * multiplier + max_hp[zw_level] * full_multiplier) * (1 + 0.616)
    return monster.attacked(damage)


def get_salon_member_damage(multiplier, zw_level, monster):
    damage = max_hp[zw_level] * multiplier * (1 + 0.28 + e_bonus[zw_level]) * 1.4
    return monster.attacked(damage)

def get_e_damages():
    cd = 2.369

    monster = Monster(level=93, kang_xin=3.1)
    monster.add_jian_kang(0.2)

    print(monster)

    for phrase in range(1, 7):
        hei_str = f"普攻第{phrase}段: "
        bai_str = "        : "
        for zw_level in range(0, 3):
            hei_damage = get_a_damage(phrase, zw_level, monster)
            hei_crit = ys_crit_damage(hei_damage, cd)
            hei_damage = round(hei_damage)

            bai_damage = get_a_damage(phrase, zw_level, monster, hei_dao=False)
            bai_crit = ys_crit_damage(bai_damage, cd)
            bai_damage = round(bai_damage)

            hei_str += f"黑: {hei_damage}/{hei_crit}\t\t"
            bai_str += f"白: {bai_damage}/{bai_crit}\t\t"

        print(hei_str)
        print(bai_str)

    e_str = "e伤害:"
    for zw_level in range(0, 4):
        e_damage = max_hp[zw_level] * 16.7/100 * (1 + e_bonus[zw_level])
        e_damage = monster.attacked(e_damage)
        e_crit = ys_crit_damage(e_damage, cd)
        e_damage = round(e_damage)

        e_str += f"{e_damage}/{e_crit}\t\t"

    print(e_str)


    for multiplier in salom_member_multiplier:
        sl_str = ""
        for zw_level in range(0, 4):
            sl_damage = get_salon_member_damage(multiplier, zw_level, monster)
            sl_crit = ys_crit_damage(sl_damage, cd)
            sl_damage = round(sl_damage)

            sl_str += f"{sl_damage}/{sl_crit}\t\t"
        print(sl_str)

get_e_damages()