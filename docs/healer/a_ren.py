import sys
import os
from collections import namedtuple
from typing import NamedTuple

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))

from analysis_utils.ys_timestamps import Ys_Timestamp, print_timestamps_summary, print_avg_min_max, null_timestamp

timestamp_dict = {
    "UKHD8048": ["00:00:00.933", 
                 ["00:00:03.092", "00:00:03.392", 
                  "00:00:04.593", "00:00:04.810",
                  "00:00:06.093", "00:00:06.327",
                  "00:00:07.593", "00:00:07.810",
                  "00:00:09.093", "00:00:09.310",
                  "00:00:10.593", "00:00:10.827",
                  "00:00:12.093", "00:00:12.345",
                  "00:00:13.595", "00:00:13.812",
                  "00:00:15.095", "00:00:15.328",
                  "00:00:16.595", "00:00:16.845"]],
    "OQSK7873": [null_timestamp,
                 ["00:00:01.950", "00:00:02.200",
                  "00:00:03.450", "00:00:03.700",
                  "00:00:04.952", "00:00:05.218",
                  "00:00:06.452", "00:00:06.735",
                  "00:00:07.952", "00:00:08.202",
                  "00:00:09.452", "00:00:09.718",
                  "00:00:10.952", "00:00:11.235",
                  "00:00:12.453", "00:00:12.687",
                  "00:00:13.953", "00:00:14.203",
                  "00:00:15.453", "00:00:15.720"]],
    "QSUT9028": ["00:00:01.517",
                 ["00:00:03.650", "00:00:03.900",
                  "00:00:05.152", "00:00:05.402",
                  "00:00:06.652", "00:00:06.918",
                  "00:00:08.152", "00:00:08.385",
                  "00:00:09.652", "00:00:09.902",
                  "00:00:11.152", "00:00:11.402",
                  "00:00:12.653", "00:00:12.887",
                  "00:00:14.153", "00:00:14.437",
                  "00:00:15.653", "00:00:15.937",
                  "00:00:17.153", "00:00:17.437"]],
    "CEWX7250": ["00:00:03.267",
                 ["00:00:05.418", "00:00:05.668",
                  "00:00:06.918", "00:00:07.352",
                  "00:00:08.418", "00:00:08.668",
                  "00:00:09.918", "00:00:10.152",
                  "00:00:11.418", "00:00:11.668",
                  "00:00:12.920", "00:00:13.137",
                  "00:00:14.420", "00:00:14.637",
                  "00:00:15.920", "00:00:16.153",
                  "00:00:17.420", "00:00:17.637",
                  "00:00:18.920", "00:00:19.137"]]
}

class Video_Timestamps(NamedTuple):
    e_start: Ys_Timestamp
    heal_times: list[Ys_Timestamp]


def get_intervals(ys_timestamp_dict: dict[str, Video_Timestamps]):
    intervals_dict = {}
    for filename, t in ys_timestamp_dict.items():
        intervals_dict[filename] = {
            "开e - 首次治疗动画开始": t.heal_times[0] - t.e_start,
            "动画开始间隔": [t.heal_times[i] - t.heal_times[i-2] for i in range(2, len(t.heal_times), 2)],
            "动画开始 - 血条变化": [t.heal_times[i+1] -  t.heal_times[i] for i in range(0, len(t.heal_times), 2)]
        }
    
    return intervals_dict

sorted_intervals = print_timestamps_summary(Video_Timestamps, timestamp_dict, get_intervals)