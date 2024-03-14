import sys
import os
from collections import namedtuple
from typing import NamedTuple

sys.path.append(os.path.abspath('../../..'))

from analysis_utils.ys_timestamps import Ys_Timestamp, print_timestamps_summary, print_avg_min_max, null_timestamp


timestamp_dict = {
    "BCMZ8065": ["00:00:05.168", "00:00:06.835", "00:00:06.935"],
    "BFAX7141": ["00:00:05.268", "00:00:06.935", "00:00:07.152"],
    "CNVK0887": ["00:00:05.593", "00:00:07.310", "00:00:07.310"],
    "GFJO4738": ["00:00:05.802", "00:00:07.468", "00:00:07.735"],
    "GFXP7325": ["00:00:06.643", "00:00:08.393", "00:00:08.493"],
    "HPBV5506": ["00:00:05.968", "00:00:07.652", "00:00:07.752"],
    "IQVI9769": ["00:00:05.668", "00:00:07.335", "00:00:07.518"],
    "JPEK6183": ["00:00:05.102", "00:00:06.768", "00:00:06.968"],
    "JTFQ5234": ["00:00:04.152", "00:00:05.818", "00:00:05.918"],
    "KPQL6389": ["00:00:05.302", "00:00:06.968", "00:00:07.052"],
    "KUJQ5423": ["00:00:05.935", "00:00:07.602", "00:00:07.802"],
    "MFOC8547": ["00:00:05.785", "00:00:07.435", "00:00:07.535"],
    "MLOM6867": ["00:00:03.767", "00:00:05.435", "00:00:05.635"],
    "PLMG0838": ["00:00:06.635", "00:00:08.368", "00:00:08.468"],
    "PLYT3458": ["00:00:05.152", "00:00:06.818", "00:00:07.002"],
    "PMZV0987": ["00:00:05.218", "00:00:06.902", "00:00:07.185"],
    "SFAN9441": ["00:00:04.302", "00:00:05.952", "00:00:06.068"],
    "TRQP7720": ["00:00:05.868", "00:00:07.535", "00:00:07.735"],
    "VPAX2223": ["00:00:05.318", "00:00:07.002", "00:00:07.185"],
    "YHQK4927": ["00:00:04.918", "00:00:06.568", "00:00:06.785"],

}


class Video_Timestamps(NamedTuple):
    q_anim_start: Ys_Timestamp
    q_damage: Ys_Timestamp
    ling_hua_first_bonused: Ys_Timestamp


def get_intervals(ys_timestamp_dict: dict[str, Video_Timestamps]):
    intervals_dict = {}
    for filename, t in ys_timestamp_dict.items():
        intervals_dict[filename] = {
            "Q动画开始 - Q出伤": t.q_damage - t.q_anim_start,
            "Q出伤 - 绫华吃到增伤": t.ling_hua_first_bonused - t.q_damage,
            "Q动画开始 - 绫华吃到增伤": t.ling_hua_first_bonused - t.q_anim_start,
        }

    return intervals_dict


sorted_intervals = print_timestamps_summary(
    Video_Timestamps, timestamp_dict, get_intervals)
