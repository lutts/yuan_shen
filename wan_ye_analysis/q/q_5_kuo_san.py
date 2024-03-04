import sys
import os

sys.path.append(os.path.abspath('../..'))

from analysis_utils.ys_timestamps import Ys_Timestamp, print_timestamps_summary

timestamp_names = [
    "switch_to_wan_ye", "q_start", "q_damage", "q_end",
    "liu_feng_first",
    "liu_feng_2nd",
    "liu_feng_3rd",
    "liu_feng_4th",
    "liu_feng_5th"
]


timestamp_dict = {
    "SCVE3726":
    ["00:00:02.333", "00:00:02.417", "00:00:03.900", "00:00:03.967",
     ["00:00:04.752", "00:00:04.902", "00:00:00.000"],
        ["00:00:06.735", "00:00:06.818", "00:00:06.935"],
        ["00:00:08.702", "00:00:08.818", "00:00:08.918"],
        ["00:00:10.702", "00:00:10.802", "00:00:10.918"],
        ["00:00:12.687", "00:00:12.770", "00:00:12.870"]
     ],

    "IDNC5218":
    ["00:00:01.567", "00:00:01.967", "00:00:03.467", "00:00:03.517",
     ["00:00:04.318", "00:00:04.418"],
        ["00:00:06.285", "00:00:06.385", "00:00:06.502"],
        ["00:00:08.252", "00:00:08.335", "00:00:08.435"],
        ["00:00:10.218", "00:00:10.318", "00:00:10.418"],
        ["00:00:12.187", "00:00:12.287", "00:00:12.387"]
     ],

    "AKFD9318":
    ["00:00:03.650", "00:00:03.717", "00:00:05.418", "00:00:05.268",
     ["00:00:06.035", "00:00:06.185"],
        ["00:00:08.018", "00:00:08.118", "00:00:08.218"],
        ["00:00:09.985", "00:00:10.068", "00:00:10.185"],
        ["00:00:11.952", "00:00:12.037", "00:00:12.137"],
        ["00:00:13.920", "00:00:14.053", "00:00:14.053"]
     ],

    "KHKP7001":
    ["00:00:03.450", "00:00:03.517", "00:00:04.985", "00:00:05.085",
     ["00:00:05.818", "00:00:05.985"],
        ["00:00:07.802", "00:00:07.985", "00:00:07.985"],
        ["00:00:09.768", "00:00:09.868", "00:00:09.968"],
        ["00:00:11.735", "00:00:11.818", "00:00:11.953"],
        ["00:00:13.703", "00:00:13.803", "00:00:13.903"]
     ],

    "JVFM9028":
    ["00:00:03.350", "00:00:03.417", "00:00:04.902", "00:00:04.985",
     ["00:00:05.802", "00:00:05.885"],
        ["00:00:07.785", "00:00:07.885", "00:00:07.985"],
        ["00:00:09.785", "00:00:09.885", "00:00:09.985"],
        ["00:00:11.785", "00:00:11.885", "00:00:11.985"],
        ["00:00:13.787", "00:00:13.887", "00:00:13.987"],
     ]
}

def get_intervals(ys_timestamp_dict: dict[str, list[Ys_Timestamp|list[Ys_Timestamp]]]):
    intervals_dict = {}
    for name, ys_timestamps in ys_timestamp_dict.items():
        switch_to_wan_ye = ys_timestamps["switch_to_wan_ye"]
        q_start = ys_timestamps["q_start"]
        q_damage = ys_timestamps["q_damage"]
        q_end = ys_timestamps["q_end"]

        liu_feng_first: list[Ys_Timestamp] = ys_timestamps["liu_feng_first"]
        if len(liu_feng_first):
            liu_feng_first.append(Ys_Timestamp("00:00:00.000"))

        liu_feng_2nd: list[Ys_Timestamp] = ys_timestamps["liu_feng_2nd"]
        liu_feng_3rd: list[Ys_Timestamp] = ys_timestamps["liu_feng_3rd"]
        liu_feng_4th: list[Ys_Timestamp] = ys_timestamps["liu_feng_4th"]
        liu_feng_5th: list[Ys_Timestamp] = ys_timestamps["liu_feng_5th"]

        intervals_dict[name] = {
            "切万叶 - Q动画开始": q_start - switch_to_wan_ye,
            "Q动画开始 - Q扩散出冰伤": q_damage - q_start,
            "Q动画开始 - Q动画结束": q_end - q_start,

            "Q动画结束 - 第一次流风开始": liu_feng_first[0] - q_end,
            "流风间隔": [
                liu_feng_2nd[0] - liu_feng_first[0],
                liu_feng_3rd[0] - liu_feng_2nd[0],
                liu_feng_4th[0] - liu_feng_3rd[0],
                liu_feng_5th[0] - liu_feng_4th[0]
            ],
            "流风开始 - 扩散出伤": [
                liu_feng_2nd[-1] - liu_feng_2nd[0],
                liu_feng_3rd[-1] - liu_feng_3rd[0],
                liu_feng_4th[-1] - liu_feng_4th[0],
                liu_feng_5th[-1] - liu_feng_5th[0],
            ],
            "第一次流风 - 最后一次流风": liu_feng_5th[0] - liu_feng_first[0],
            "Q动画结束 - 最后一次流风": liu_feng_5th[0] - q_end,
        }

    return intervals_dict


print_timestamps_summary(timestamp_names, timestamp_dict, get_intervals)

timestamp_names2 = [
    "q_anim_start", "kuo_san_damage", "q_anim_end", "ling_hua_first_damage", "ling_hua_last_jian_kang_damage", "ling_hua_first_non_jian_kang_damage"
]
timestamps_dict2 = {
"ALUG6642": ["00:00:02.533",  "00:00:04.018", "00:00:04.085", "00:00:10.068", "00:00:13.870", "00:00:14.070"],
"ANJH0223": ["00:00:04.385", "00:00:05.852", "00:00:05.952", "00:00:13.537", "00:00:15.820", "00:00:16.120"],
"AOFY0306": ["00:00:02.967", "00:00:04.435", "00:00:04.518", "00:00:11.685", "00:00:14.453", "00:00:14.653"],
"CTQH8628": ["00:00:04.685", "00:00:06.152", "00:00:06.235", "00:00:13.387", "00:00:15.937", "00:00:16.237"],
"DOAR0004": ["00:00:02.567", "00:00:04.035", "00:00:04.118", "00:00:12.053", "00:00:13.803", "00:00:14.103"],
"DZUW3580": ["00:00:06.843", "00:00:08.327", "00:00:08.393", "00:00:15.745", "00:00:18.312", "00:00:18.495"],
"FCAU1727": ["00:00:02.967", "00:00:04.435", "00:00:04.535", "00:00:12.237", "00:00:14.253", "00:00:14.553"],
"PYEM5482": ["00:00:05.252", "00:00:06.718", "00:00:06.802", "00:00:13.970", "00:00:16.687", "00:00:17.003"],
"QFMS1729": ["00:00:06.718", "00:00:08.218", "00:00:08.268", "00:00:15.970", "00:00:18.003", "00:00:18.203"],
"RDXF8588": ["00:00:09.102", "00:00:10.568", "00:00:10.652", "00:00:19.037", "00:00:20.572", "00:00:20.872"],
"RODA2772": ["00:00:05.818", "00:00:07.285", "00:00:07.385", "00:00:14.787", "00:00:17.120", "00:00:17.320"],
"UYYO0728": ["00:00:04.685", "00:00:06.168", "00:00:06.235", "00:00:13.537", "00:00:16.087", "00:00:16.370"],
"VFZI2953": ["00:00:05.618", "00:00:07.085", "00:00:07.168", "00:00:14.120", "00:00:17.103", "00:00:17.403"],
"XKQA5526": ["00:00:05.335", "00:00:06.818", "00:00:06.902", "00:00:14.437", "00:00:16.670", "00:00:16.987"]
}

def get_intervals2(ys_timestamp_dict: dict[str, list[Ys_Timestamp|list[Ys_Timestamp]]]):
    intervals_dict = {}
    for name, ys_timestamps in ys_timestamp_dict.items():
        q_anim_start = ys_timestamps["q_anim_start"]
        kuo_san_damage = ys_timestamps["kuo_san_damage"]
        q_anim_end = ys_timestamps["q_anim_end"]

        intervals_dict[name] = {
            "Q动画开始 - 扩散出伤": kuo_san_damage - q_anim_start,
        }

    return intervals_dict

print_timestamps_summary(timestamp_names2, timestamps_dict2, get_intervals2)








    
