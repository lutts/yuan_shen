import sys
import os
import random
from collections import namedtuple
from typing import NamedTuple

sys.path.append(os.path.abspath('../..'))

from analysis_utils.ys_timestamps import Ys_Timestamp, print_timestamps_summary, print_avg_min_max, null_timestamp
    
timestamp_dict = {
    "AAXH4358": ["00:00:03.083", "00:00:04.885", "00:00:04.952", "00:00:06.635", "00:00:06.852",
                 "00:00:07.235", "00:00:07.318", "00:00:08.802", "00:00:08.868", "00:00:09.168",
                 "00:00:11.068", "00:00:11.735", "00:00:11.818", "00:00:11.987", "00:00:13.487", "00:00:14.220", "00:00:14.370",
                 "00:00:17.553", "00:00:17.753", "00:00:17.987", "00:00:18.603", "00:00:18.803", "00:00:19.003",
                 "00:00:23.538", "00:00:24.705"
                 ],
    "ABCN2638": ["00:00:02.200", "00:00:03.933", "00:00:04.000", "00:00:05.685", "00:00:05.902",
                 "00:00:06.218", "00:00:06.285", "00:00:07.752", "00:00:07.852", "00:00:08.102",
                 "00:00:10.252", "00:00:10.968", "00:00:11.018", "00:00:11.135", "00:00:12.637", "00:00:13.370", "00:00:13.653",
                 "00:00:17.537", "00:00:17.753", "00:00:18.020", "00:00:18.637", "00:00:18.887", "00:00:19.270",
                 "00:00:23.822", "00:00:23.672"
                 ],
    "AREY8421": ["00:00:03.042", "00:00:04.827", "00:00:04.893", "00:00:06.560", "00:00:06.793",
                 "00:00:06.993", "00:00:07.060", "00:00:08.527", "00:00:08.610", "00:00:08.877",
                 "00:00:10.993", "00:00:11.677", "00:00:11.727", "00:00:11.943", "00:00:13.462", "00:00:14.128", "00:00:14.395",
                 "00:00:17.678", "00:00:17.878", "00:00:18.112", "00:00:18.778", "00:00:19.012", "00:00:19.212",
                 "00:00:24.063", "00:00:24.647"
                 ],
    "AZVW1609": ["00:00:02.183", "00:00:03.950", "00:00:04.018", "00:00:05.718", "00:00:05.918",
                 "00:00:06.218", "00:00:06.285", "00:00:07.752", "00:00:07.852", "00:00:08.118",
                 "00:00:10.035", "00:00:10.735", "00:00:10.785", "00:00:10.968", "00:00:12.470", "00:00:13.137", "00:00:13.337",
                 "00:00:16.487", "00:00:16.903", "00:00:17.153", "00:00:17.770", "00:00:17.970", "00:00:18.120",
                 "00:00:23.155", "00:00:23.722"
                 ],
    "BWTQ6665": ["00:00:01.817", "00:00:03.650", "00:00:03.717", "00:00:05.402", "00:00:05.618",
                 "00:00:05.968", "00:00:06.035", "00:00:07.502", "00:00:07.585", "00:00:07.902",
                 "00:00:09.918", "00:00:10.602", "00:00:10.652", "00:00:10.752", "00:00:12.270", "00:00:13.053", "00:00:13.187",
                 "00:00:16.470", "00:00:16.687", "00:00:17.003", "00:00:17.553", "00:00:17.770", "00:00:18.053",
                 "00:00:22.972", "00:00:23.388"
                 ],
    "CDNL1631": ["00:00:01.233", "00:00:03.000", "00:00:03.067", "00:00:04.735", "00:00:04.968",
                 "00:00:05.152", "00:00:05.218", "00:00:06.685", "00:00:06.768", "00:00:07.052",
                 "00:00:09.085", "00:00:09.818", "00:00:09.868", "00:00:10.052", "00:00:11.552", "00:00:12.203", "00:00:12.353",
                 "00:00:15.437", "00:00:15.637", "00:00:15.870", "00:00:16.537", "00:00:16.770", "00:00:16.987",
                 "00:00:22.138", "00:00:22.838"],
    "CXQW6779": ["00:00:01.700", "00:00:03.517", "00:00:03.583", "00:00:05.252", "00:00:05.485",
                 "00:00:05.685", "00:00:05.752", "00:00:07.218", "00:00:07.318", "00:00:07.552",
                 "00:00:09.452", "00:00:10.135", "00:00:10.185", "00:00:10.318", "00:00:11.818", "00:00:12.470", "00:00:12.637",
                 "00:00:15.737", "00:00:15.903", "00:00:16.137", "00:00:16.787", "00:00:17.020", "00:00:17.153",
                 "00:00:22.022", "00:00:23.322"],
    "EIXZ2855": ["00:00:01.850", "00:00:03.633", "00:00:03.700", "00:00:05.385", "00:00:05.602", 
                 "00:00:05.935", "00:00:06.002", "00:00:07.518", "00:00:07.552", "00:00:07.835",
                 "00:00:09.818", "00:00:10.502", "00:00:10.568", "00:00:10.735", "00:00:12.237", "00:00:13.037", "00:00:13.470",
                 "00:00:16.603", "00:00:16.820", "00:00:17.087", "00:00:17.670", "00:00:17.870", "00:00:18.553",
                 "00:00:22.955", "00:00:23.438"],
    "EMLK4661": ["00:00:02.533", "00:00:04.318", "00:00:04.385", "00:00:06.052", "00:00:06.285", 
                 "00:00:06.535", "00:00:06.602", "00:00:08.052", "00:00:08.152", "00:00:08.535",
                 "00:00:10.552", "00:00:11.252", "00:00:11.302", "00:00:11.385", "00:00:12.887", "00:00:13.537", "00:00:13.920",
                 "00:00:17.303", "00:00:17.520", "00:00:17.753", "00:00:18.403", "00:00:18.603", "00:00:18.787",
                 "00:00:24.105", "00:00:24.072"],
    "GZCR6234": ["00:00:01.867", "00:00:03.700", "00:00:03.767", "00:00:05.452", "00:00:05.668",
                 "00:00:05.968", "00:00:06.035", "00:00:07.502", "00:00:07.585", "00:00:07.918",
                 "00:00:10.352", "00:00:11.018", "00:00:11.068", "00:00:11.218", "00:00:12.720", "00:00:13.437", "00:00:13.720",
                 "00:00:16.953", "00:00:17.170", "00:00:17.470", "00:00:18.137", "00:00:18.337", "00:00:18.603",
                 "00:00:22.738", "00:00:23.455"],
    "ICKB3381": ["00:00:02.017", "00:00:03.783", "00:00:03.850", "00:00:05.552", "00:00:05.752",
                 "00:00:06.052", "00:00:06.118", "00:00:07.602", "00:00:07.685", "00:00:07.968",
                 "00:00:10.102", "00:00:10.802", "00:00:10.852", "00:00:11.018", "00:00:12.520", "00:00:13.170", "00:00:13.903",
                 "00:00:16.937", "00:00:17.137", "00:00:17.387", "00:00:18.003", "00:00:18.220", "00:00:18.587",
                 "00:00:24.555", "00:00:23.605"],
    "IKQB9796": ["00:00:02.183", "00:00:03.892", "00:00:03.958", "00:00:05.627", "00:00:05.860",
                 "00:00:06.293", "00:00:06.360", "00:00:07.827", "00:00:07.910", "00:00:08.193", 
                 "00:00:10.477", "00:00:11.127", "00:00:11.177", "00:00:11.260", "00:00:12.762", "00:00:13.462", "00:00:13.712",
                 "00:00:16.828", "00:00:17.028", "00:00:17.245", "00:00:17.895", "00:00:18.095", "00:00:18.328",
                 null_timestamp, "00:00:23.630"],
    "IRBN1676": ["00:00:02.300", "00:00:04.202", "00:00:04.268", "00:00:05.935", "00:00:06.168", 
                 "00:00:06.785", "00:00:06.852", "00:00:08.318", "00:00:08.402", "00:00:08.702",
                 "00:00:11.002", "00:00:11.685", "00:00:11.735", "00:00:12.003", "00:00:13.503", "00:00:14.153", "00:00:14.670",
                 "00:00:18.520", "00:00:18.720", null_timestamp, "00:00:19.587", "00:00:19.870", "00:00:20.422",
                 "00:00:25.888", "00:00:23.955"],
    "JWGO2927": ["00:00:03.800", "00:00:05.552", "00:00:05.652", "00:00:07.302", "00:00:07.518",
                 "00:00:07.952", "00:00:08.035", "00:00:09.485", "00:00:09.568", "00:00:09.818",
                 "00:00:11.818", "00:00:12.520", "00:00:12.587", "00:00:12.803", "00:00:14.303", "00:00:14.987", "00:00:15.170",
                 "00:00:18.270", "00:00:18.437", "00:00:18.737", "00:00:19.303", "00:00:19.520", "00:00:19.670",
                 "00:00:24.422", "00:00:25.288"],
    "KVJG4578": ["00:00:02.150", "00:00:03.917", "00:00:03.983", "00:00:05.635", "00:00:05.885", 
                 "00:00:06.435", "00:00:06.502", "00:00:07.968", "00:00:08.068", "00:00:08.352",
                 "00:00:10.335", "00:00:11.035", "00:00:11.085", "00:00:11.285", "00:00:12.787", "00:00:13.537", "00:00:13.653",
                 "00:00:16.970", "00:00:17.203", "00:00:17.437", "00:00:18.103", "00:00:18.337", "00:00:18.737",
                 "00:00:23.488", "00:00:23.722"],
    "LITS1766": ["00:00:03.183", "00:00:05.002", "00:00:05.068", "00:00:06.735", "00:00:06.968",
                 "00:00:07.152", "00:00:07.235", "00:00:08.702", "00:00:08.785", "00:00:09.068",
                 "00:00:11.102", "00:00:11.802", "00:00:11.868", "00:00:11.985", "00:00:13.487", "00:00:14.170", "00:00:14.353",
                 "00:00:17.820", "00:00:18.087", "00:00:18.370", "00:00:18.970", "00:00:19.153", "00:00:19.437",
                 "00:00:24.238", "00:00:24.805"],
    "NEPO1639": ["00:00:02.000", "00:00:03.817", "00:00:03.883", "00:00:05.552", "00:00:05.785",
                 "00:00:06.118", "00:00:06.185", "00:00:07.652", "00:00:07.752", "00:00:08.068",
                 "00:00:09.968", "00:00:10.652", "00:00:10.718", "00:00:10.835", "00:00:12.337", "00:00:13.170", "00:00:13.320",
                 "00:00:16.503", "00:00:16.670", "00:00:16.903", "00:00:17.537", "00:00:17.720", "00:00:18.087",
                 "00:00:22.655", "00:00:23.622"],
    "PCLG8482": ["00:00:02.250", "00:00:03.950", "00:00:04.018", "00:00:05.835", "00:00:05.918", 
                 "00:00:06.202", "00:00:06.268", "00:00:07.718", "00:00:07.818", "00:00:08.102",
                 "00:00:10.018", "00:00:10.685", "00:00:10.735", "00:00:10.885", "00:00:12.387", "00:00:13.037", "00:00:13.303",
                 "00:00:16.453", "00:00:16.687", "00:00:16.987", "00:00:17.537", "00:00:17.720", "00:00:18.170",
                 "00:00:23.155", "00:00:23.705"],
    "PVIC2605": ["00:00:02.833", "00:00:04.518", "00:00:04.585", "00:00:06.252", "00:00:06.485",
                 "00:00:06.652", "00:00:06.718", "00:00:08.168", "00:00:08.285", "00:00:08.552",
                 "00:00:10.502", "00:00:11.152", "00:00:11.218", "00:00:11.402", "00:00:12.903", "00:00:13.603", "00:00:13.787",
                 "00:00:17.087", "00:00:17.320", "00:00:17.570", "00:00:18.187", "00:00:18.370", "00:00:18.620",
                 "00:00:23.172", "00:00:24.288"],
    "QASK9303": ["00:00:01.800", "00:00:03.550", "00:00:03.617", "00:00:05.302", "00:00:05.535",
                 "00:00:05.885", "00:00:05.968", "00:00:07.418", "00:00:07.518", "00:00:07.735",
                 "00:00:09.718", "00:00:10.385", "00:00:10.452", "00:00:10.635", "00:00:12.153", "00:00:12.903", "00:00:13.037",
                 "00:00:16.737", "00:00:16.970", "00:00:17.187", "00:00:17.837", "00:00:18.070", "00:00:18.337",
                 "00:00:22.488", "00:00:23.372"],
    "QHXX4110": ["00:00:01.333", "00:00:03.000", "00:00:03.067", "00:00:04.752", "00:00:04.968", 
                 "00:00:05.252", "00:00:05.318", "00:00:06.818", "00:00:06.885", "00:00:07.052",
                 "00:00:09.135", "00:00:09.802", "00:00:09.852", "00:00:09.968", "00:00:11.485", "00:00:12.337","00:00:12.570",
                 "00:00:16.387", "00:00:16.603", "00:00:16.837", "00:00:17.487", "00:00:17.670", "00:00:18.003",
                 "00:00:22.455", "00:00:22.755"],
    "RJZS4611": ["00:00:00.733", "00:00:02.433", "00:00:02.500", "00:00:04.185", "00:00:04.402", 
                 "00:00:04.735", "00:00:04.802", "00:00:06.268", "00:00:06.352", "00:00:06.668",
                 "00:00:08.618", "00:00:09.302", "00:00:09.352", "00:00:09.468", "00:00:10.968", "00:00:11.602", "00:00:11.835",
                 "00:00:14.770", "00:00:14.953", "00:00:15.187", "00:00:15.820", "00:00:16.037", "00:00:16.287",
                 "00:00:21.788", "00:00:22.238"],
    "RLGH9027": ["00:00:02.917", "00:00:04.668", "00:00:04.752", "00:00:06.418", "00:00:06.652", 
                 "00:00:07.018", "00:00:07.085", "00:00:08.552", "00:00:08.652", "00:00:08.852",
                 "00:00:10.685", "00:00:11.335", "00:00:11.385", "00:00:11.518", "00:00:13.020", "00:00:13.770", "00:00:14.020",
                 "00:00:18.070", "00:00:18.303", "00:00:18.520", "00:00:19.153", "00:00:19.370", "00:00:19.670",
                 "00:00:23.588", "00:00:24.455"],
    "TLJU0085": ["00:00:03.150", "00:00:04.835", "00:00:04.902", "00:00:06.568", "00:00:06.802",
                 "00:00:07.202", "00:00:07.285", "00:00:08.752", "00:00:08.818", "00:00:09.168",
                 "00:00:11.252", "00:00:11.985", "00:00:12.037", "00:00:12.287", "00:00:13.787", "00:00:14.520", "00:00:14.687",
                 "00:00:18.053", "00:00:18.253", "00:00:18.470", "00:00:19.137", "00:00:19.337", "00:00:19.670",
                 "00:00:24.888", "00:00:24.622"],
    "TQDD2462": ["00:00:00.633", "00:00:02.617", "00:00:02.683", "00:00:04.368", "00:00:04.585", 
                 "00:00:04.852", "00:00:04.918", "00:00:06.435", "00:00:06.485", "00:00:06.735",
                 "00:00:08.818", "00:00:09.518", "00:00:09.568", "00:00:09.735", "00:00:11.252", "00:00:11.902", "00:00:12.052",
                 "00:00:15.070", "00:00:15.237", null_timestamp, "00:00:16.103", "00:00:16.370", "00:00:16.553",
                 "00:00:21.672", "00:00:22.355"],
    "ULUO1558": ["00:00:02.100", "00:00:03.783", "00:00:03.850", "00:00:05.535", "00:00:05.752", 
                 "00:00:05.985", "00:00:06.052", "00:00:07.518", "00:00:07.618", "00:00:07.885",
                 "00:00:09.918", "00:00:10.585", "00:00:10.652", "00:00:10.852", "00:00:12.353", "00:00:13.070", "00:00:13.287",
                 "00:00:17.570", "00:00:17.770", "00:00:18.020", "00:00:18.653", "00:00:18.853", "00:00:19.120",
                 "00:00:22.672", "00:00:23.505"],
    "VIYZ9499": ["00:00:02.000", "00:00:03.733", "00:00:03.783", "00:00:05.452", "00:00:05.685",
                 "00:00:06.035", "00:00:06.102", "00:00:07.602", "00:00:07.668", "00:00:07.985",
                 "00:00:09.985", "00:00:10.668", "00:00:10.735", "00:00:10.918", "00:00:12.420", "00:00:13.087", "00:00:13.437",
                 "00:00:16.953", "00:00:17.237", "00:00:17.470", "00:00:18.187", "00:00:18.453", "00:00:18.653",
                 "00:00:23.422", "00:00:23.472"],
    "VSEO2414": ["00:00:01.767", "00:00:03.533", "00:00:03.600", "00:00:05.268", "00:00:05.502",
                 "00:00:05.918", "00:00:05.985", "00:00:07.452", "00:00:07.535", "00:00:08.085", 
                 "00:00:10.235", "00:00:10.985", "00:00:11.035", "00:00:11.152", "00:00:12.653", "00:00:13.387", "00:00:14.053",
                 "00:00:17.303", "00:00:17.537", "00:00:17.787", "00:00:18.403", "00:00:18.653", "00:00:19.103",
                 "00:00:23.755", "00:00:23.288"],
    "WOKA8029": ["00:00:01.667", "00:00:03.400", "00:00:03.467", "00:00:05.118", "00:00:05.368",
                 "00:00:05.718", "00:00:05.785", "00:00:07.235", "00:00:07.335", "00:00:07.602",
                 "00:00:09.618", "00:00:10.335", "00:00:10.402", "00:00:10.468", "00:00:11.970", "00:00:12.720", "00:00:12.870",
                 "00:00:16.103", "00:00:16.353", "00:00:16.603", "00:00:17.237", "00:00:17.453", "00:00:17.687",
                 "00:00:22.672", "00:00:23.222"],
    "XYUJ5817": ["00:00:01.900", "00:00:03.650", "00:00:03.733", "00:00:05.418", "00:00:05.635",
                 "00:00:05.835", "00:00:05.902", "00:00:07.385", "00:00:07.452", "00:00:07.702",
                 "00:00:09.685", "00:00:10.352", "00:00:10.385", "00:00:10.485", "00:00:11.985", "00:00:12.703", "00:00:12.853",
                 "00:00:15.903", "00:00:16.103", "00:00:16.337", "00:00:16.970", "00:00:17.153", "00:00:17.670",
                 "00:00:22.372", "00:00:23.472"],
    "YGDJ5533": ["00:00:02.583", "00:00:04.268", "00:00:04.335", "00:00:06.002", "00:00:06.235",
                 "00:00:06.568", "00:00:06.635", "00:00:08.102", "00:00:08.202", "00:00:08.418",
                 "00:00:10.468", "00:00:11.102", "00:00:11.152", "00:00:11.452", "00:00:12.953", "00:00:13.670", "00:00:13.803",
                 "00:00:17.687", "00:00:17.920", "00:00:18.187", "00:00:18.837", "00:00:19.053", "00:00:19.220",
                 "00:00:23.222", "00:00:24.072"],
}


class Video_Timestamps(NamedTuple):
    zhong_li_e_start_1: Ys_Timestamp
    switch_to_fufu_1: Ys_Timestamp
    fufu_q_anim_start: Ys_Timestamp
    fufu_q_damage: Ys_Timestamp
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
    pao_pao_actual_disappear: Ys_Timestamp


def get_intervals(ys_timestamp_dict: dict[str, Video_Timestamps]):
    intervals_dict = {}
    for filename, t in ys_timestamp_dict.items():
        ye_lan_q_bonus_end =  round(t.ye_lan_q_anim_start.to_float() + random.uniform(1.235, 1.27) + 15, 3)
        ye_lan_3rd_e_cd_ok_time = round(10 + t.ye_lan_1st_e_end.to_float(), 3)

        intervals_dict[filename] = {
            "钟离e - 切芙芙": t.switch_to_fufu_1 - t.zhong_li_e_start_1,
            "切芙芙 - 芙芙Q动画开始": t.fufu_q_anim_start - t.switch_to_fufu_1,
            "Q动画开始 - Q出伤":  t.fufu_q_damage - t.fufu_q_anim_start,
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
            "一轮输出时间": t.switch_to_zhong_li - t.zhong_li_e_start_1,
            "夜兰第三个e CD转好": ye_lan_3rd_e_cd_ok_time,
            "切到夜兰时, e CD还差秒数": round(10 - (t.switch_to_ye_lan_2 - t.ye_lan_1st_e_end), 3),
            "芙芙Q动画开始 - 泡泡消失": t.pao_pao_actual_disappear - t.fufu_q_anim_start,
            "Q出伤 - 泡泡消失 - 18": round(t.pao_pao_actual_disappear - t.fufu_q_damage - 18, 3),
            "夜兰大招结束时间": ye_lan_q_bonus_end,
            "芙芙泡泡消失 - 夜兰大招结束": round(ye_lan_q_bonus_end - t.pao_pao_actual_disappear.to_float(), 3),
            "芙芙泡泡消失 - 夜兰第三个e cd转好": round(ye_lan_3rd_e_cd_ok_time - t.pao_pao_actual_disappear.to_float(), 3),
            
        }

    return intervals_dict

sorted_intervals = print_timestamps_summary(Video_Timestamps, timestamp_dict, get_intervals)