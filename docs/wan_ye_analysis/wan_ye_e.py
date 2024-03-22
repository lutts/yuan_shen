import sys
import os
from collections import namedtuple
from typing import NamedTuple

sys.path.append(os.path.abspath('..'))

from analysis_utils.ys_timestamps import Ys_Timestamp, print_timestamps_summary, print_avg_min_max, null_timestamp

timestamp_dict = {
    "AQFA2689": ["00:00:11.785", "00:00:11.968", "00:00:12.220", "00:00:12.853",  "00:00:13.053", "00:00:22.872", "00:00:23.105"],
    "DCJW4761": ["00:00:02.567", "00:00:02.783", "00:00:03.050", "00:00:03.633", "00:00:03.883", "00:00:13.787", "00:00:14.003"],
    "FEUJ1034": ["00:00:04.802", "00:00:05.002", "00:00:05.252", "00:00:05.868", "00:00:06.052", "00:00:16.020", "00:00:16.220"],
    "GKZS4374": ["00:00:01.967", "00:00:02.217", "00:00:02.500", "00:00:03.083", "00:00:03.333", "00:00:13.287", "00:00:13.470"],
    "GUQC8959": ["00:00:02.783", "00:00:02.983", "00:00:03.217", "00:00:03.867", "00:00:04.086", "00:00:13.787", "00:00:14.087"],
    "GZNM6206": ["00:00:06.252", "00:00:06.485", "00:00:06.785", "00:00:07.368", "00:00:07.585", "00:00:17.353", "00:00:17.653"],
    "ITDJ7855": ["00:00:05.168", "00:00:05.385", "00:00:05.635", "00:00:06.252", "00:00:06.518", "00:00:16.370", "00:00:16.687"],
    "LMSN5992": ["00:00:03.100", "00:00:03.317", "00:00:03.633", "00:00:04.185", "00:00:04.452", "00:00:14.253", "00:00:14.453"],
    "MVHI0270": ["00:00:02.325", "00:00:02.525", "00:00:02.775", "00:00:03.375", "00:00:03.575", "00:00:13.495", "00:00:13.795"],
    "OFVG1920": ["00:00:02.700", "00:00:02.900", "00:00:03.167", "00:00:03.783", "00:00:03.983", "00:00:13.770", "00:00:14.087"],
    "QZCJ8256": ["00:00:04.985", "00:00:05.252", "00:00:05.468", "00:00:06.235", "00:00:06.435", "00:00:16.337", "00:00:16.637"],
    "SWON9101": ["00:00:02.567", "00:00:02.800", "00:00:03.142", "00:00:03.692", "00:00:03.908", "00:00:13.595", "00:00:13.912"],
    "UNTS9121": ["00:00:01.967", "00:00:02.167", "00:00:02.450", "00:00:03.033", "00:00:03.233", "00:00:13.087", "00:00:13.287"],
    "WXYY8743": ["00:00:07.268", "00:00:07.485", "00:00:07.702", "00:00:08.352", "00:00:08.618", "00:00:18.453", "00:00:18.770"],
    "XCKC9059": ["00:00:05.818", "00:00:06.052", "00:00:06.285", "00:00:06.918", "00:00:07.185", "00:00:17.103", "00:00:17.320"],
}

class Video_Timestamps(NamedTuple):
    switch_to_wan_ye: Ys_Timestamp
    e_start: Ys_Timestamp
    up_kuo_san: Ys_Timestamp
    atk_button_again: Ys_Timestamp
    down_kuo_san: Ys_Timestamp
    ling_hua_last_bonused: Ys_Timestamp
    ling_hua_first_no_bonus: Ys_Timestamp

print(type(Video_Timestamps))

def get_intervals(ys_timestamp_dict: dict[str, Video_Timestamps]):
    intervals_dict = {}
    for name, t in ys_timestamp_dict.items():
        intervals_dict[name] = {
            "切万叶 - 开始e": t.e_start - t.switch_to_wan_ye,
            "开始e - 上升扩散出伤": t.up_kuo_san - t.e_start,
            "开始e - 重新变为攻击键": t.atk_button_again - t.e_start,
            "重新变为攻击键 - 下落扩散出伤": t.down_kuo_san - t.atk_button_again,
        }

    return intervals_dict

sorted_intervals = print_timestamps_summary(Video_Timestamps, timestamp_dict, get_intervals)

print_avg_min_max(sorted_intervals["重新变为攻击键 - 下落扩散出伤"])