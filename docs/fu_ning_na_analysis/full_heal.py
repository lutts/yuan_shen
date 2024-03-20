# 使用模板：复制下面的代码
import sys
import os
from collections import namedtuple
from typing import NamedTuple

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../..'))

from analysis_utils.ys_timestamps import Ys_Timestamp, print_timestamps_summary, print_avg_min_max, null_timestamp

timestamp_dict = {
    "BAAT7160": ["00:00:04.885", ]
}

class Video_Timestamps(NamedTuple):
    first_a_hit: Ys_Timestamp
    first_a_damage: Ys_Timestamp
    teammate_heal_times: list[Ys_Timestamp]
    fufu_heal_times: list[Ys_Timestamp]
    heal_while_fufu_full: Ys_Timestamp


def get_intervals(ys_timestamp_dict: dict[str, Video_Timestamps]):
    intervals_dict = {}
    for filename, t in ys_timestamp_dict.items():
        intervals_dict[filename] = {
            "第一刀 - 首次回血": 0,
            "回血间隔": 0,
            "芙芙回血延迟": 0,
        }
    
    return intervals_dict

sorted_intervals = print_timestamps_summary(Video_Timestamps, timestamp_dict, get_intervals)