import sys
import os
from collections import namedtuple
from typing import NamedTuple

sys.path.append(os.path.abspath('../..'))

from analysis_utils.ys_timestamps import Ys_Timestamp, print_timestamps_summary, print_avg_min_max
    
timestamp_dict = {
    "AAXH4358": ["00:00:03.083", "00:00:04.885", "00:00:04.952", "00:00:06.852",
                 "00:00:07.235", "00:00:07.318", "00:00:08.802", "00:00:08.868", "00:00:09.168",
                 "00:00:11.068", "00:00:11.735", "00:00:11.818", "00:00:11.987", "00:00:13.487", "00:00:14.220", "00:00:14.370",
                 "00:00:17.553", "00:00:17.753", "00:00:00.000", "00:00:18.603", "00:00:00.000", "00:00:19.003",
                 "00:00:23.538"
                 ],
    "ABCN2638": ["00:00:02.200", "00:00:03.933", "00:00:04.000", "00:00:05.902",
                 "00:00:06.218", "00:00:06.285", "00:00:07.752", "00:00:07.852", "00:00:08.102",
                 "00:00:10.252", "00:00:10.968", "00:00:11.018", "00:00:11.135", "00:00:12.637", "00:00:13.370", "00:00:13.653",
                 "00:00:17.537", "00:00:17.753", "00:00:18.020", "00:00:18.637", "00:00:18.887", "00:00:19.270",
                 "00:00:23.822" 
                 ],
    "AREY8421": ["00:00:03.042", "00:00:04.827", "00:00:04.893", "00:00:06.793",
                 "00:00:06.993", "00:00:07.060", "00:00:08.527", "00:00:08.610", "00:00:08.877",
                 "00:00:10.993", "00:00:11.677", "00:00:11.727", "00:00:11.943", "00:00:13.462", "00:00:14.128", "00:00:14.395",
                 "00:00:17.678", "00:00:17.878", "00:00:00.000", "00:00:18.778", "00:00:19.012", "00:00:19.212",
                 "00:00:24.063"
                 ],
    "AZVW1609": ["00:00:02.183", "00:00:03.950", "00:00:04.018", "00:00:05.918",
                 "00:00:06.218", "00:00:06.285", "00:00:07.752", "00:00:07.852", "00:00:08.118",
                 "00:00:10.035", "00:00:10.735", "00:00:10.785", "00:00:10.968", "00:00:12.470", "00:00:13.137", "00:00:13.337",
                 "00:00:16.487", "00:00:16.903", "00:00:00.000", "00:00:17.770", "00:00:17.970", "00:00:18.120",
                 "00:00:23.155"
                 ],
    "BWTQ6665": ["00:00:01.817", "00:00:03.650", "00:00:03.717", "00:00:05.618",
                 "00:00:05.968", "00:00:06.035", "00:00:07.502", "00:00:07.585", "00:00:07.902",
                 "00:00:09.918", "00:00:10.602", "00:00:10.652", "00:00:10.752", "00:00:12.270", "00:00:13.053", "00:00:13.187",
                 "00:00:16.470", "00:00:16.687", "00:00:00.000", "00:00:17.553", "00:00:17.770", "00:00:18.053",
                 "00:00:22.972"
                 ],
    "CDNL1631": ["00:00:01.233", "00:00:03.000", "00:00:03.067", "00:00:04.968",
                 "00:00:05.152", "00:00:05.218", "00:00:06.685", "00:00:06.768", "00:00:07.052",
                 "00:00:09.085", "00:00:09.818", "00:00:09.868", "00:00:10.052", "00:00:11.552", "00:00:12.203", "00:00:12.353",
                 "00:00:15.437", "00:00:15.637", "00:00:00.000", "00:00:16.537", "00:00:00.000", "00:00:16.987",
                 "00:00:22.138"],
}


class Video_Timestamps(NamedTuple):
    zhong_li_e_start_1: Ys_Timestamp
    switch_to_fufu_1: Ys_Timestamp
    fufu_q_anim_start: Ys_Timestamp
    fufu_q_anim_end: Ys_Timestamp

    switch_to_wan_ye_1: Ys_Timestamp
    wan_ye_q_anim_start: Ys_Timestamp
    wan_ye_q_kuo_san: Ys_Timestamp
    wan_ye_q_anim_end: Ys_Timestamp
    switch_to_fufu_2: Ys_Timestamp

    switch_to_ye_lan_1: Ys_Timestamp
    ye_lan_1st_e_end: Ys_Timestamp
    ye_lan_4_ming_1: Ys_Timestamp
    ye_lan_q_anim_start: Ys_Timestamp
    ye_lan_q_anim_end: Ys_Timestamp
    ye_lan_4_ming_2: Ys_Timestamp
    switch_to_fufu_3: Ys_Timestamp

    switch_to_wan_ye_2: Ys_Timestamp
    wan_ye_e_start: Ys_Timestamp
    wan_ye_e_up_kuo_san: Ys_Timestamp
    wan_ye_e_atk_btn: Ys_Timestamp
    wan_ye_e_down_kuo_san: Ys_Timestamp
    switch_to_ye_lan_2: Ys_Timestamp

    switch_to_zhong_li: Ys_Timestamp


def get_intervals(ys_timestamp_dict: dict[str, Video_Timestamps]):
    intervals_dict = {}
    for filename, t in ys_timestamp_dict.items():
        intervals_dict[filename] = {
            "钟离e - 切芙芙": t.switch_to_fufu_1 - t.zhong_li_e_start_1,
            "切芙芙 - 芙芙Q动画开始": t.fufu_q_anim_start - t.switch_to_fufu_1,
            "芙芙Q动画时长": t.fufu_q_anim_end - t.fufu_q_anim_start,
            "芙芙Q动画开始 - 切万叶": t.switch_to_wan_ye_1 - t.fufu_q_anim_start,
            "切万叶 - 万叶Q动画开始": t.wan_ye_q_anim_start - t.switch_to_wan_ye_1,
            "万叶动画开始 - Q扩散出伤": t.wan_ye_q_kuo_san - t.wan_ye_q_anim_start,
            "万叶Q动画时长": t.wan_ye_q_anim_end - t.wan_ye_q_anim_start,
            "万叶Q动画开始 - 切芙芙": t.switch_to_fufu_2 -  t.wan_ye_q_anim_start,
            "切夜兰 - 第一个e结束": t.ye_lan_1st_e_end - t.switch_to_ye_lan_1,
            "夜兰第一个e结束 - 4命生效": t.ye_lan_4_ming_1 - t.ye_lan_1st_e_end,
            "夜兰第一个e结束 - Q动画开始": t.ye_lan_q_anim_start - t.ye_lan_1st_e_end,
            "夜兰动画时长": t.ye_lan_q_anim_end - t.ye_lan_q_anim_start,
            "夜兰Q动画结束 - 第二个e结束": t.ye_lan_4_ming_2 - t.ye_lan_q_anim_end,
            "夜兰第二个e结束 - 切芙芙": t.switch_to_fufu_3 - t.ye_lan_4_ming_2,
            "切万叶 - 万叶e开始":  t.wan_ye_e_start - t.switch_to_wan_ye_2,
            "万叶e开始 - e上升扩散出伤": t.wan_ye_e_up_kuo_san - t.wan_ye_e_start,
            "万叶e开始 - 变回攻击键": t.wan_ye_e_atk_btn - t.wan_ye_e_start,
            "变回攻击键 - e下落扩散出伤": t.wan_ye_e_down_kuo_san - t.wan_ye_e_atk_btn,
            "变回攻击键 - 切夜兰": t.switch_to_ye_lan_2 - t.wan_ye_e_atk_btn,
            "夜兰e CD还差秒数": round(10 - (t.switch_to_ye_lan_2 - t.ye_lan_1st_e_end), 3),
            "一轮输出时间": t.switch_to_zhong_li - t.zhong_li_e_start_1
        }

    return intervals_dict

sorted_intervals = print_timestamps_summary(Video_Timestamps, timestamp_dict, get_intervals)