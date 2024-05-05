import sys
import os
from collections import namedtuple
from typing import NamedTuple

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../..'))

from analysis_utils.ys_timestamps import Ys_Timestamp, print_timestamps_summary, print_avg_min_max, null_timestamp

timestamp_dict = {
    "DCZG1299": ["00:00:06.635", "00:00:16.920", "00:00:17.803", "Yes", null_timestamp, "None"],
    "DFHV5216": ["00:00:04.368", "00:00:14.670", "00:00:16.053", "No", null_timestamp, "None"],
    "FPKH9258": ["00:00:07.185", "00:00:17.503", "00:00:18.453", "Yes", null_timestamp, "None"],
    "HNPU5428": ["00:00:05.718", "00:00:16.137", "00:00:16.903", "Yes", "00:00:17.787", "No"],
    "ISCX6123": ["00:00:08.018", "00:00:18.470", "00:00:18.670", "Yes", null_timestamp, "None"],
    "JOGU9659": ["00:00:05.452", "00:00:15.770", "00:00:17.287", "No", null_timestamp, "None"],
    "MWDJ5095": ["00:00:07.535", "00:00:17.787", "00:00:18.737", "Yes", null_timestamp, "None"],
    "OGJQ2076": ["00:00:06.985", "00:00:17.287", "00:00:19.070", "No", null_timestamp, "None"],
    "PBTM5390": ["00:00:06.118", "00:00:16.453", "00:00:17.203", "Yes", null_timestamp, "None"],
    "QUZX2534": ["00:00:06.985", "00:00:17.353", "00:00:18.087", "Yes", null_timestamp, "None"],
    "RKEX0121": ["00:00:06.668", "00:00:17.037", "00:00:17.487", "Yes", "00:00:18.370", "Yes"],
    "TNUH1916": ["00:00:08.302", "00:00:18.687", "00:00:19.253", "Yes", "00:00:20.138", "Yes"],
    "TZYY6838": ["00:00:07.235", "00:00:17.570", "00:00:18.570", "Yes", null_timestamp, "None"]
}

class Video_Timestamps(NamedTuple):
    q_anim_start: Ys_Timestamp
    last_liu_feng_hit: Ys_Timestamp
    e_start: Ys_Timestamp
    up_ks_has_m2: str
    atk_btn: Ys_Timestamp
    down_ks_has_m2: str


def get_intervals(ys_timestamp_dict: dict[str, Video_Timestamps]):
    intervals_dict = {}
    for filename, t in ys_timestamp_dict.items():
        if t.down_ks_has_m2 == "Yes":
            last_m2 = t.atk_btn.to_float() + 0.083
        elif t.up_ks_has_m2 == "Yes":
            last_m2 = t.e_start.to_float() + 0.117
        else:
            last_m2 = 0

        if t.up_ks_has_m2 == "No":
            first_no_m2 = t.e_start.to_float() + 0.117
        elif t.down_ks_has_m2 == "No":
            fist_no_m2 = t.atk_btn.to_float() + 0.083
        else:
            first_no_m2 = 0

        intervals_dict[filename] = {
            "Q动画开始 - 最后吃到二命时间": round(last_m2 - t.q_anim_start.to_float(), 3),
            "Q动画开始 - 第一次没吃到二命时间": round(first_no_m2 - t.q_anim_start.to_float(), 3),
            "第五次流风 - 最后吃到二命时间": round(last_m2 - t.last_liu_feng_hit.to_float(), 3),
            "第五次流风 - 第一次没吃到二命时间": round(first_no_m2 - t.last_liu_feng_hit.to_float(), 3),
        }
    
    return intervals_dict

sorted_intervals = print_timestamps_summary(Video_Timestamps, timestamp_dict, get_intervals)