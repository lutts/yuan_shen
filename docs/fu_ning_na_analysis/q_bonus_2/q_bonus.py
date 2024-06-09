import sys
import os
import random
from collections import namedtuple
from typing import NamedTuple

sys.path.append(os.path.abspath('../..'))

from analysis_utils.ys_timestamps import Ys_Timestamp, print_timestamps_summary, print_avg_min_max, null_timestamp

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