import sys
import os
from collections import namedtuple
from typing import NamedTuple

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../..'))

from analysis_utils.ys_timestamps import Ys_Timestamp, print_timestamps_summary, print_avg_min_max, null_timestamp

huang_dao_dict = {
    "AUJC7755": ["00:00:09.152", "00:00:09.752", "00:00:09.818"],
    "EHVM9234": ["00:00:09.552", "00:00:10.118", "00:00:10.185"],
    "GYMN0944": ["00:00:10.302", "00:00:10.885", "00:00:10.952"],
    "JDZH0808": ["00:00:09.285", "00:00:09.868", "00:00:09.985"],
    "JVYQ6185": ["00:00:09.618", "00:00:10.185", "00:00:10.252"],
    "MXVI5341": ["00:00:10.618", "00:00:11.268", "00:00:11.335"],
    "NJPN3439": ["00:00:08.502", "00:00:09.085", "00:00:09.202"],
    "QPYG1965": ["00:00:10.302", "00:00:10.952", "00:00:11.035"],
}

mang_dao_dict = {
    
}

class Video_Timestamps(NamedTuple):
    gen: Ys_Timestamp
    hit: Ys_Timestamp
    damage: Ys_Timestamp


def get_intervals(ys_timestamp_dict: dict[str, Video_Timestamps]):
    intervals_dict = {}
    for filename, t in ys_timestamp_dict.items():
        intervals_dict[filename] = {
            "生成 - 命中": t.hit - t.gen,
            "命中 - 出伤": t.damage - t.hit,
        }
    
    return intervals_dict

sorted_intervals = print_timestamps_summary(Video_Timestamps, huang_dao_dict, get_intervals)