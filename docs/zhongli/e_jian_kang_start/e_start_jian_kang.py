import sys
import os
from collections import namedtuple
from typing import NamedTuple

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../..'))

from analysis_utils.ys_timestamps import Ys_Timestamp, print_timestamps_summary, range_print_func, null_timestamp

timestamp_dict = {
    "AGKU9134": ["00:00:06.318", "00:00:07.285", "00:00:07.535"],
    "DEVW3575": ["00:00:06.818", "00:00:07.852", "00:00:08.102"],
    "DYKS3694": ["00:00:06.735", "00:00:07.535", "00:00:07.785"],
    "FNFF7690": ["00:00:06.485", "00:00:07.485", "00:00:07.735"],
    "HGVD3199": ["00:00:07.135", "00:00:07.935", "00:00:08.185"],
    "HLSP4936": ["00:00:07.752", "00:00:08.718", "00:00:08.985"],
    "IDLB9713": ["00:00:07.202", "00:00:08.068", "00:00:08.318"],
    "JPKY7668": ["00:00:06.402", "00:00:07.168", "00:00:07.418"],
    "KTUS6857": ["00:00:07.735", "00:00:08.635", "00:00:08.885"],
    "KUWQ0550": ["00:00:06.102", "00:00:07.152", "00:00:07.402"],
    "LOYC2355": ["00:00:07.035", "00:00:07.885", "00:00:08.135"],
    "MWVW6180": ["00:00:07.243", "00:00:08.277", "00:00:08.527"],
    "MYCI1769": ["00:00:07.152", "00:00:07.985", "00:00:08.235"],
    "PIHE3953": ["00:00:06.868", "00:00:07.818", "00:00:08.068"],
    "PXTD9004": ["00:00:07.802", "00:00:08.785", "00:00:09.035"],
    "QZDP8581": ["00:00:07.002", "00:00:08.002", "00:00:08.252"],
    "RKSL7759": ["00:00:06.602", "00:00:07.635", "00:00:07.885"],
    "SONL5832": ["00:00:07.418", "00:00:08.385", "00:00:08.635"],
    "TCJC1482": ["00:00:04.668", "00:00:05.435", "00:00:05.702"],
    "TWCR1910": ["00:00:06.768", "00:00:07.768", "00:00:08.018"],
}

class Video_Timestamps(NamedTuple):
    e_start: Ys_Timestamp
    ling_hua_last_unbonused: Ys_Timestamp
    ling_hua_first_bonused: Ys_Timestamp


def get_intervals(ys_timestamp_dict: dict[str, Video_Timestamps]):
    intervals_dict = {}
    for filename, t in ys_timestamp_dict.items():
        intervals_dict[filename] = {
            "e减抗开始时间": (round(t.ling_hua_last_unbonused - t.e_start + 0.001, 3),
                              t.ling_hua_first_bonused - t.e_start),
        }
    
    return intervals_dict

sorted_intervals = print_timestamps_summary(Video_Timestamps, timestamp_dict, get_intervals, print_func=range_print_func)