import sys
import os
from collections import namedtuple
from typing import NamedTuple

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../..'))

from analysis_utils.ys_timestamps import Ys_Timestamp, print_timestamps_summary, range_print_func, null_timestamp

timestamp_dict = {
    "ELVM7974": ["00:00:02.900", "00:00:23.905", "00:00:24.605", "00:00:24.855"],
    "KTAH2329": ["00:00:02.583", "00:00:23.655", "00:00:24.038", "00:00:24.288"],
    "LLDP4440": ["00:00:02.150", "00:00:23.172", "00:00:23.638", "00:00:23.888"],
    "LTYA1412": ["00:00:02.883", "00:00:23.972", "00:00:24.638", "00:00:24.888"],
    "MPCC8481": ["00:00:02.533", "00:00:23.605", "00:00:24.155", "00:00:24.405"],
    "OEFD1863": ["00:00:03.883", "00:00:24.922", "00:00:25.605", "00:00:25.855"],
    "OJWE2293": ["00:00:01.967", "00:00:23.022", "00:00:23.855", "00:00:24.105"],
    "TWIV1719": ["00:00:02.350", "00:00:23.438", "00:00:24.155", "00:00:24.405"],
    "UCWV0245": ["00:00:02.433", "00:00:23.472", "00:00:24.355", "00:00:24.605"],
    "VMII8354": ["00:00:02.467", "00:00:23.522", "00:00:24.122", "00:00:24.372"],
    "VYEX0299": ["00:00:04.402", "00:00:25.505", "00:00:26.055", "00:00:26.305"],
    "YDRS8978": ["00:00:03.583", "00:00:24.622", "00:00:25.122", "00:00:25.372"],
}

class Video_Timestamps(NamedTuple):
    e_start: Ys_Timestamp
    shield_start_disappear: Ys_Timestamp
    ling_hua_last_bonused: Ys_Timestamp
    ling_hua_first_unbonused: Ys_Timestamp


def get_intervals(ys_timestamp_dict: dict[str, Video_Timestamps]):
    intervals_dict = {}
    for filename, t in ys_timestamp_dict.items():
        intervals_dict[filename] = {
            "e开始 - 盾开始消失": t.shield_start_disappear - t.e_start,
            "盾开始消失 - 减抗消失": (round(t.ling_hua_last_bonused - t.shield_start_disappear + 0.001, 3), 
                             t.ling_hua_first_unbonused - t.shield_start_disappear),
            "减抗持续时间": (round(t.ling_hua_last_bonused - t.e_start + 0.001, 3), t.ling_hua_first_unbonused - t.e_start),
        }
    
    return intervals_dict

sorted_intervals = print_timestamps_summary(Video_Timestamps, timestamp_dict, get_intervals,
                                            description_print_func={"减抗持续时间": range_print_func,
                                                                    "盾开始消失 - 减抗消失": range_print_func})