# 使用模板：复制下面的代码
import sys
import os
from collections import namedtuple
from typing import NamedTuple

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../..'))

from analysis_utils.ys_timestamps import Ys_Timestamp, print_timestamps_summary, print_avg_min_max, null_timestamp

timestamp_dict = {
    "AJTL1094": ["00:00:04.768", "00:00:04.885",
                 ["00:00:06.002", "00:00:07.035", "00:00:08.002", "00:00:09.002", "00:00:10.068", 
                  "00:00:11.035", "00:00:12.103", "00:00:12.970", "00:00:13.987", "00:00:15.003", 
                  "00:00:15.987", "00:00:16.987", "00:00:18.003", "00:00:18.987", "00:00:19.970", 
                  "00:00:20.988", "00:00:21.972"],
                 ["00:00:06.202", "00:00:07.352", "00:00:08.502", "00:00:09.585", "00:00:10.718",
                  "00:00:11.768", "00:00:12.703", "00:00:13.787", "00:00:14.770", "00:00:15.720",
                  "00:00:16.687", "00:00:17.920", "00:00:19.137", "00:00:20.272", "00:00:21.455", 
                  "00:00:22.672", "00:00:23.722"],
                  []],
    "AXLN1616": ["00:00:05.102", "00:00:05.185",
                 ["00:00:06.335", "00:00:07.385", "00:00:08.418", "00:00:09.385", "00:00:10.352",
                  "00:00:11.352", "00:00:12.320", "00:00:13.337", "00:00:14.320", "00:00:15.387",
                  "00:00:16.337", "00:00:17.287", "00:00:18.337", "00:00:19.237", "00:00:20.255",
                  "00:00:21.288", "00:00:22.222"],
                 ["00:00:06.502", "00:00:07.685", "00:00:08.952", "00:00:10.068", "00:00:11.152",
                  "00:00:12.320", "00:00:13.270", "00:00:14.537", "00:00:15.637", "00:00:16.737",
                  "00:00:17.837", "00:00:18.870", "00:00:19.970", "00:00:21.172", "00:00:22.222",
                  "00:00:23.422", "00:00:24.638"
                  ],
                  []],
    "BCQS7892": ["00:00:04.785", "00:00:04.952",
                 ["00:00:06.018", "00:00:07.052", "00:00:08.052", "00:00:09.052", "00:00:10.068",
                  "00:00:11.002", "00:00:12.070", "00:00:13.053", "00:00:13.987", "00:00:15.070",
                  "00:00:16.020", "00:00:17.020", "00:00:17.970", "00:00:19.020", "00:00:20.038",
                  "00:00:21.005", "00:00:22.022"],
                 ["00:00:06.252", "00:00:07.368", "00:00:08.552", "00:00:09.585", "00:00:10.652",
                  "00:00:11.902", "00:00:12.803", "00:00:13.987", "00:00:15.070", "00:00:16.120",
                  "00:00:17.320", "00:00:18.337", "00:00:19.320", "00:00:20.338", "00:00:21.338",
                  "00:00:22.388", "00:00:23.388"],
                  []],
    # "00:00:09.260"切钟离站前台
    "CUEN0663": ["00:00:05.193", "00:00:05.360",
                 ["00:00:06.427", "00:00:07.477", "00:00:08.443", "00:00:09.393", "00:00:10.493",
                  "00:00:11.427", "00:00:12.445", "00:00:13.428", "00:00:14.462", "00:00:15.395",
                  "00:00:16.412", "00:00:17.478", "00:00:18.378", "00:00:19.428", "00:00:20.447",
                  "00:00:21.397", "00:00:22.363"],
                 ["00:00:06.577", "00:00:07.677", "00:00:08.993", "00:00:09.993", "00:00:10.993",
                  "00:00:11.927", "00:00:13.012", "00:00:13.945", "00:00:14.978", "00:00:15.978",
                  "00:00:17.012", "00:00:17.978", "00:00:18.995", "00:00:19.928", "00:00:20.963",
                  "00:00:21.947", "00:00:22.897"],
                 ["00:00:06.427", "00:00:07.477", "00:00:08.443", "00:00:09.393", "00:00:10.493",
                  "00:00:11.577", "00:00:12.612", "00:00:13.745", "00:00:14.978", "00:00:16.078",
                  "00:00:17.062", "00:00:18.178", "00:00:19.328", "00:00:20.547", "00:00:21.547",
                  "00:00:22.647", "00:00:23.963"]],
    # "00:00:07.868"切钟离站前台
    "ARCV9080": ["00:00:03.683", "00:00:03.850",
                 ["00:00:05.018", "00:00:05.968", "00:00:06.902", "00:00:07.952", "00:00:08.852",
                  "00:00:09.935", "00:00:10.852", "00:00:11.902", "00:00:12.820", "00:00:13.787",
                  "00:00:14.820", "00:00:15.770", "00:00:16.787", "00:00:17.770", "00:00:18.803",
                  "00:00:19.753", "00:00:20.822"],
                 ["00:00:05.168", "00:00:06.168", "00:00:07.468", "00:00:08.452", "00:00:09.452", 
                  "00:00:10.402", "00:00:11.402", "00:00:12.437", "00:00:13.420", "00:00:14.403",
                  "00:00:15.387", "00:00:16.370", "00:00:17.320", "00:00:18.337", "00:00:19.287",
                  "00:00:20.422", "00:00:21.322"],
                 ["00:00:05.018", "00:00:05.968", "00:00:06.902", "00:00:07.968", "00:00:08.852", 
                  "00:00:10.035", "00:00:11.235", "00:00:12.237", "00:00:13.503", "00:00:14.620",
                  "00:00:15.703", "00:00:16.637", "00:00:17.620", "00:00:18.887", "00:00:20.072",
                  "00:00:21.238", "00:00:22.405"]],
}

class Video_Timestamps(NamedTuple):
    first_a_hit: Ys_Timestamp
    first_a_damage: Ys_Timestamp
    bg_heal_times: list[Ys_Timestamp]
    fufu_heal_times: list[Ys_Timestamp]
    fg_heal_times: list[Ys_Timestamp]


def get_intervals(ys_timestamp_dict: dict[str, Video_Timestamps]):
    intervals_dict = {}
    for filename, t in ys_timestamp_dict.items():
        fg_heal_times = t.fg_heal_times
        if not fg_heal_times:
            fg_heal_times = t.fufu_heal_times

        intervals_dict[filename] = {
            "第一刀 - 队友首次回血": t.bg_heal_times[0] - t.first_a_hit,
            "后台回血间隔": [t.bg_heal_times[i] - t.bg_heal_times[i-1] for i in range(1, len(t.bg_heal_times))],
            "第一刀 - 芙芙首次回血": t.fufu_heal_times[0] - t.first_a_hit,
            "芙芙回血间隔": [t.fufu_heal_times[i] - t.fufu_heal_times[i - 1] for i in range(1, len(t.fufu_heal_times))],
            "前台回血间隔": [fg_heal_times[i] - fg_heal_times[i-1] for i in range(1, len(fg_heal_times))]
        }
    
    return intervals_dict

sorted_intervals = print_timestamps_summary(Video_Timestamps, timestamp_dict, get_intervals)