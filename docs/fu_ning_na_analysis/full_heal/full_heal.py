# 使用模板：复制下面的代码
import sys
import os
from collections import namedtuple
from typing import NamedTuple

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../..'))

from analysis_utils.ys_timestamps import Ys_Timestamp, print_timestamps_summary, print_avg_min_max, null_timestamp

dao_6_dict = {
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
}

zhong_li_in_front_dict = {
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
    # "00:00:06.952"切钟离站前台
    "WFYJ6253": ["00:00:03.517", "00:00:03.683",
                 ["00:00:04.785", "00:00:05.735", "00:00:06.818", "00:00:07.735", "00:00:08.702",
                  "00:00:09.702", "00:00:10.685", "00:00:11.685", "00:00:12.653", "00:00:13.703",
                  "00:00:14.670", "00:00:15.620", "00:00:16.603", "00:00:17.620", "00:00:18.653",
                  "00:00:19.570", "00:00:20.572"],
                 ["00:00:04.985", "00:00:06.018", "00:00:07.135", "00:00:08.202", "00:00:09.185",
                  "00:00:10.152", "00:00:11.102", "00:00:12.170", "00:00:13.153", "00:00:14.070",
                  "00:00:15.120", "00:00:16.120", "00:00:17.037", "00:00:18.087", "00:00:19.020",
                  "00:00:20.003", "00:00:20.938"],
                 ["00:00:04.785", "00:00:05.735", "00:00:06.818", "00:00:07.718", "00:00:08.702",
                  "00:00:10.052", "00:00:11.102", "00:00:12.087", "00:00:13.320", "00:00:14.387",
                  "00:00:15.720", "00:00:16.703", "00:00:17.620", "00:00:18.653", "00:00:19.903",
                  "00:00:20.938", "00:00:21.972"]],
}

# 上面数据不正常，第二天又录了几个视频
next_day_dao_6_dict = {
    "IPUD9000": ["00:00:05.068", "00:00:05.185",
                 ["00:00:06.285", "00:00:07.335", "00:00:08.335", "00:00:09.252", "00:00:10.218",
                  "00:00:11.218", "00:00:12.187", "00:00:13.237", "00:00:14.187", "00:00:15.337",
                  "00:00:16.253", "00:00:17.203", "00:00:18.170", "00:00:19.187", "00:00:20.222",
                  "00:00:21.222", "00:00:22.172"],
                 ["00:00:06.385", "00:00:07.552", "00:00:08.868", "00:00:09.835", "00:00:10.802",
                  "00:00:11.885", "00:00:12.820", "00:00:13.787", "00:00:14.987", "00:00:15.903",
                  "00:00:16.870", "00:00:17.870", "00:00:18.870", "00:00:19.787", "00:00:20.822",
                  "00:00:21.872", "00:00:22.805"],
                 []],
    # 关了meta fx
    "GLOG7473": ["00:00:06.235", "00:00:06.402",
                 ["00:00:07.452", "00:00:08.535", "00:00:09.502", "00:00:10.468", "00:00:11.535", 
                  "00:00:12.453", "00:00:13.537", "00:00:14.420", "00:00:15.453", "00:00:16.453",
                  "00:00:17.503", "00:00:18.470", "00:00:19.453", "00:00:20.472", "00:00:21.438",
                  "00:00:22.472", "00:00:23.488"],
                 ["00:00:07.602", "00:00:08.835", "00:00:10.052", "00:00:11.035", "00:00:12.087",
                  "00:00:13.020", "00:00:14.070", "00:00:15.053", "00:00:16.053", "00:00:17.020",
                  "00:00:17.970", "00:00:18.970", "00:00:20.003", "00:00:21.038", "00:00:22.005",
                  "00:00:22.988", "00:00:23.955"],
                 []],
    # 关了 meta fx
    "WFFP6191": ["00:00:04.918", "00:00:04.985",
                 ["00:00:06.235", "00:00:07.202", "00:00:08.185", "00:00:09.168", "00:00:10.102",
                  "00:00:11.085", "00:00:12.137", "00:00:13.103", "00:00:14.137", "00:00:15.070",
                  "00:00:16.037", "00:00:17.037", "00:00:18.070", "00:00:19.070", "00:00:20.038",
                  "00:00:21.055", "00:00:22.005"],
                 ["00:00:06.402", "00:00:07.485", "00:00:08.602", "00:00:09.585", "00:00:10.668",
                  "00:00:11.602", "00:00:12.587", "00:00:13.637", "00:00:14.653", "00:00:15.637",
                  "00:00:16.637", "00:00:17.603", "00:00:18.553", "00:00:19.537", "00:00:20.538",
                  "00:00:21.538", "00:00:22.505"],
                 []],
    
}

dao_1_dict = {
    "ETSM7770": ["00:00:04.702", "00:00:04.802",
                 ["00:00:05.952", "00:00:06.968", "00:00:07.902"],
                 ["00:00:05.952", "00:00:06.968"],
                 []],
    "JSNC7908": ["00:00:05.235", "00:00:05.352",
                 ["00:00:06.518", "00:00:07.518", "00:00:08.452"],
                 ["00:00:06.518", "00:00:07.518", "00:00:08.452"],
                 []],
    "OYFC8520": ["00:00:05.427", "00:00:05.510",
                 ["00:00:06.677", "00:00:07.643", "00:00:08.660"],
                 ["00:00:06.660", "00:00:07.643"],
                 []],
    "QKGL4705": ["00:00:04.685", "00:00:04.802",
                 ["00:00:05.952", "00:00:06.902", "00:00:07.868"], # 第三次夜兰、万叶没治疗到
                 ["00:00:05.952", "00:00:06.902", "00:00:07.868"],
                 []],
    "XUKA7158": ["00:00:06.052", "00:00:06.185",
                 ["00:00:07.285", "00:00:08.335", "00:00:09.318"], # 第三次只治疗了钟离
                 ["00:00:07.285", "00:00:08.352"],
                 []],
    "YJRA6237": ["00:00:03.983", "00:00:04.152",
                 ["00:00:05.268", "00:00:06.252", "00:00:07.252"], # 第三次都治疗到了
                 ["00:00:05.268", "00:00:06.252"],
                 []],
}

dao_2_dict = {
    "FFEC3443": ["00:00:05.635", "00:00:05.802",
                 ["00:00:06.918", "00:00:07.885", "00:00:08.835", "00:00:09.835", "00:00:10.818", "00:00:11.768"],
                 ["00:00:07.018", "00:00:07.985", "00:00:08.935", "00:00:09.935", "00:00:10.902"],
                 []],
    "FKNK1558": ["00:00:05.285", "00:00:05.452",
                 ["00:00:06.585", "00:00:07.518", "00:00:08.468", "00:00:09.468", "00:00:10.468", "00:00:11.468"],
                 ["00:00:06.668", "00:00:07.618", "00:00:08.568", "00:00:09.568", "00:00:10.568"],
                 []],
    "QRBJ3595": ["00:00:05.252", "00:00:05.352",
                 ["00:00:06.568", "00:00:07.468", "00:00:08.468", "00:00:09.518", "00:00:10.452", "00:00:11.435"],
                 ["00:00:06.585", "00:00:07.568", "00:00:08.535", "00:00:09.518", "00:00:10.518"],
                 []],
    "SIBV5220": ["00:00:04.785", "00:00:04.952",
                 ["00:00:06.052", "00:00:07.052", "00:00:08.002", "00:00:08.952", "00:00:10.002", "00:00:10.985"],
                 ["00:00:06.152", "00:00:07.052", "00:00:08.102", "00:00:09.052", "00:00:10.002"],
                 []],
    "WHJR0304": ["00:00:05.518", "00:00:05.668",
                 ["00:00:06.802", "00:00:07.752", "00:00:08.768", "00:00:09.768", "00:00:10.818", "00:00:11.785"],
                 ["00:00:06.885", "00:00:07.852", "00:00:08.852", "00:00:09.868", "00:00:10.818"],
                 []],
    "YDTK7381": ["00:00:05.202", "00:00:05.285",
                 ["00:00:06.452", "00:00:07.518", "00:00:08.502", "00:00:09.435", "00:00:10.402", "00:00:11.452"],
                 ["00:00:06.535", "00:00:07.585", "00:00:08.535", "00:00:09.535", "00:00:10.518"],
                 []],
}

dao_3_dict = {
    "ALCN4464": ["00:00:05.385", "00:00:05.485",
                 ["00:00:06.618", "00:00:07.668", "00:00:08.652", "00:00:09.618", "00:00:10.552", 
                  "00:00:11.618", "00:00:12.553", "00:00:13.537"],
                 ["00:00:06.718", "00:00:07.868", "00:00:08.818", "00:00:09.835", "00:00:10.752",
                  "00:00:11.718", "00:00:12.753", "00:00:13.720"],
                 []],
    "DQWX0065": ["00:00:04.552", "00:00:04.635",
                 ["00:00:05.835", "00:00:06.802", "00:00:07.818", "00:00:08.785", "00:00:10.018", 
                  "00:00:10.785", "00:00:11.752", "00:00:12.770"],
                 ["00:00:05.935", "00:00:07.002", "00:00:08.035", "00:00:08.985", "00:00:10.102",
                  "00:00:11.035", "00:00:11.952", "00:00:12.987"],
                 []],
    "HUAV8771": ["00:00:05.518", "00:00:05.635",
                 ["00:00:06.785", "00:00:07.768", "00:00:08.752", "00:00:09.718", "00:00:10.685",
                  "00:00:11.685", "00:00:12.670", "00:00:13.620"],
                 ["00:00:06.868", "00:00:07.935", "00:00:08.952", "00:00:09.918", "00:00:10.885",
                  "00:00:11.868", "00:00:12.903", "00:00:13.820"],
                 []],
    "KDBE9362": ["00:00:05.652", "00:00:05.818",
                 ["00:00:06.918", "00:00:07.868", "00:00:08.868", "00:00:09.852", "00:00:10.868",
                  "00:00:11.818", "00:00:12.837", "00:00:13.820"],
                 ["00:00:07.018", "00:00:08.068", "00:00:09.068", "00:00:10.068", "00:00:11.068",
                  "00:00:12.018", "00:00:13.037", "00:00:13.987"],
                 []],
    "OZEI8699": ["00:00:04.485", "00:00:04.652",
                 ["00:00:05.702", "00:00:06.785", "00:00:07.685", "00:00:08.685", "00:00:09.885",
                  "00:00:10.702", "00:00:11.702", "00:00:12.687"],
                 ["00:00:05.918", "00:00:06.885", "00:00:07.868", "00:00:08.885", "00:00:10.052",
                  "00:00:10.885", "00:00:11.903", "00:00:12.887"],
                 []],
    "SYBO6060": ["00:00:05.118", "00:00:05.285",
                 ["00:00:06.385", "00:00:07.418", "00:00:08.385", "00:00:09.335", "00:00:10.335",
                  "00:00:11.385", "00:00:12.353", "00:00:13.320"],
                 ["00:00:06.502", "00:00:07.618", "00:00:08.585", "00:00:09.535", "00:00:10.518",
                  "00:00:11.552", "00:00:12.570", "00:00:13.603"],
                 []],
}

dao_4_dict = {
    "ISMG9555": ["00:00:05.168", "00:00:05.285",
                 ["00:00:06.485", "00:00:07.402", "00:00:08.385", "00:00:09.402", "00:00:10.385", 
                  "00:00:11.368", "00:00:12.303", "00:00:13.337", "00:00:14.287", "00:00:15.287",
                  "00:00:16.270"],
                 ["00:00:06.652", "00:00:07.668", "00:00:08.685", "00:00:09.752", "00:00:10.602", 
                  "00:00:11.668", "00:00:12.637", "00:00:13.587", "00:00:14.587", "00:00:15.587",
                  "00:00:16.537"],
                 []],
    "KEJE7834": ["00:00:05.568", "00:00:05.702",
                 ["00:00:06.835", "00:00:07.818", "00:00:08.768", "00:00:09.818", "00:00:10.785",
                  "00:00:11.802", "00:00:12.770", "00:00:13.737", "00:00:14.720", "00:00:15.703",
                  "00:00:16.720"],
                 ["00:00:06.968", "00:00:08.135", "00:00:09.052", "00:00:10.118", "00:00:11.035",
                  "00:00:12.085", "00:00:12.987", "00:00:14.020", "00:00:14.987", "00:00:16.003",
                  "00:00:17.070"],
                 []],
    "KWDH0441": ["00:00:05.802", "00:00:05.935",
                 ["00:00:07.035", "00:00:08.068", "00:00:09.068", "00:00:10.052", "00:00:10.985",
                  "00:00:12.053", "00:00:12.970", "00:00:13.970", "00:00:14.953", "00:00:15.987",
                  "00:00:16.953"],
                 ["00:00:07.152", "00:00:08.352", "00:00:09.352", "00:00:10.368", "00:00:11.302",
                  "00:00:12.237", "00:00:13.320", "00:00:14.237", "00:00:15.203", "00:00:16.203",
                  "00:00:17.170"],
                 []],
    "PIJG1895": ["00:00:05.352", "00:00:05.452",
                 ["00:00:06.602", "00:00:07.652", "00:00:08.552", "00:00:09.552", "00:00:10.535", 
                  "00:00:11.585", "00:00:12.553", "00:00:13.537", "00:00:14.537", "00:00:15.537",
                  "00:00:16.553"],
                 ["00:00:06.702", "00:00:07.852", "00:00:08.852", "00:00:09.852", "00:00:10.835",
                  "00:00:11.885", "00:00:12.820", "00:00:13.837", "00:00:14.853", "00:00:15.820",
                  "00:00:16.853"],
                 []],
    "TWIN3185": ["00:00:05.502", "00:00:05.602",
                 ["00:00:06.752", "00:00:07.802", "00:00:08.702", "00:00:09.685", "00:00:10.668",
                  "00:00:11.735", "00:00:12.720", "00:00:13.653", "00:00:14.637", "00:00:15.620",
                  "00:00:16.637"],
                 ["00:00:06.802", "00:00:08.002", "00:00:09.002", "00:00:09.985", "00:00:10.952",
                  "00:00:12.035", "00:00:12.937", "00:00:13.903", "00:00:14.937", "00:00:15.887",
                  "00:00:16.937"],
                 []],
    "XXCA8966": ["00:00:05.152", "00:00:05.235",
                 ["00:00:06.402", "00:00:07.468", "00:00:08.368", "00:00:09.368", "00:00:10.402",
                  "00:00:11.385", "00:00:12.453", "00:00:13.470", "00:00:14.403", "00:00:15.437",
                  "00:00:16.437"],
                 ["00:00:06.502", "00:00:07.702", "00:00:08.685", "00:00:09.668", "00:00:10.702",
                  "00:00:11.685", "00:00:12.653", "00:00:13.703", "00:00:14.687", "00:00:15.720",
                  "00:00:16.637"],
                 []],
}

dao_5_dict = {
    "FQGC5171": ["00:00:05.168", "00:00:05.252",
                 ["00:00:06.452", "00:00:07.385", "00:00:08.418", "00:00:09.352", "00:00:10.418",
                  "00:00:11.368", "00:00:12.337", "00:00:13.337", "00:00:14.353", "00:00:15.270",
                  "00:00:16.270", "00:00:17.270", "00:00:18.253", "00:00:19.170"],
                 ["00:00:06.502", "00:00:07.752", "00:00:08.785", "00:00:09.702", "00:00:10.752",
                  "00:00:11.668", "00:00:12.653", "00:00:13.653", "00:00:14.653", "00:00:15.670",
                  "00:00:16.637", "00:00:17.653", "00:00:18.553", "00:00:19.587"],
                 []],
    "IGWA5827": ["00:00:05.402", "00:00:05.485",
                 ["00:00:06.685", "00:00:07.652", "00:00:08.752", "00:00:09.652", "00:00:10.702",
                  "00:00:11.652", "00:00:12.670", "00:00:13.637", "00:00:14.637", "00:00:15.670",
                  "00:00:16.637", "00:00:17.670", "00:00:18.620", "00:00:19.653"],
                 ["00:00:06.785", "00:00:08.052", "00:00:09.068", "00:00:10.035", "00:00:11.068",
                  "00:00:12.053", "00:00:13.103", "00:00:14.037", "00:00:15.053", "00:00:16.070",
                  "00:00:17.070", "00:00:18.070", "00:00:19.020", "00:00:20.055"],
                 []],
    "KYHR9770": ["00:00:05.735", "00:00:05.835",
                 ["00:00:07.102", "00:00:08.018", "00:00:09.002", "00:00:10.052", "00:00:10.968",
                  "00:00:12.037", "00:00:12.970", "00:00:13.970", "00:00:15.053", "00:00:15.987",
                  "00:00:17.037", "00:00:18.037", "00:00:18.970", "00:00:20.020"],
                 ["00:00:07.302", "00:00:08.302", "00:00:09.418", "00:00:10.452", "00:00:11.435",
                  "00:00:12.370", "00:00:13.437", "00:00:14.370", "00:00:15.453", "00:00:16.370",
                  "00:00:17.437", "00:00:18.470", "00:00:19.370", "00:00:20.355"],
                 []],
    "OQTF9636": ["00:00:04.160", "00:00:04.243",
                 ["00:00:05.393", "00:00:06.393", "00:00:07.393", "00:00:08.377", "00:00:09.460",
                  "00:00:10.410", "00:00:11.377", "00:00:12.445", "00:00:13.345", "00:00:14.362",
                  "00:00:15.395", "00:00:16.328", "00:00:17.412", "00:00:18.412"],
                 ["00:00:05.577", "00:00:06.693", "00:00:07.777", "00:00:08.777", "00:00:09.777",
                  "00:00:10.810", "00:00:11.743", "00:00:12.745", "00:00:13.762", "00:00:14.662",
                  "00:00:15.778", "00:00:16.728", "00:00:17.728", "00:00:18.695"],
                 []],
    "SZXH9377": ["00:00:05.635", "00:00:05.818",
                 ["00:00:06.885", "00:00:07.935", "00:00:08.902", "00:00:09.902", "00:00:10.935",
                  "00:00:12.053", "00:00:12.903", "00:00:13.903", "00:00:14.887", "00:00:15.853",
                  "00:00:16.903", "00:00:17.870", "00:00:18.870", "00:00:19.837"],
                 ["00:00:06.985", "00:00:08.235", "00:00:09.218", "00:00:10.218", "00:00:11.352",
                  "00:00:12.320", "00:00:13.203", "00:00:14.287", "00:00:15.287", "00:00:16.237",
                  "00:00:17.220", "00:00:18.187", "00:00:19.253", "00:00:20.222"],
                 []],
    "TIGO7625": ["00:00:05.918", "00:00:06.035",
                 ["00:00:07.152", "00:00:08.185", "00:00:09.135", "00:00:10.152", "00:00:11.202",
                  "00:00:12.170", "00:00:13.203", "00:00:14.120", "00:00:15.120", "00:00:16.120",
                  "00:00:17.153", "00:00:18.170", "00:00:19.070", "00:00:20.105"],
                 ["00:00:07.252", "00:00:08.468", "00:00:09.368", "00:00:10.552", "00:00:11.535",
                  "00:00:12.537", "00:00:13.553", "00:00:14.520", "00:00:15.520", "00:00:16.503",
                  "00:00:17.587", "00:00:18.520", "00:00:19.520", "00:00:20.522"],
                 []],
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
        first_times = [t.bg_heal_times[0], t.fufu_heal_times[0]]
        last_times = [t.bg_heal_times[-1], t.fufu_heal_times[-1]]

        fg_heal_times = t.fg_heal_times
        if not fg_heal_times:
            fg_heal_times = t.fufu_heal_times
        else:
            first_times.append(fg_heal_times[0])
            last_times.append(fg_heal_times[-1])
        
        min_time = min(first_times)
        max_time = max(last_times)

        intervals_dict[filename] = {
            "第一刀 - 队友首次回血": t.bg_heal_times[0] - t.first_a_hit,
            "后台回血间隔": [t.bg_heal_times[i] - t.bg_heal_times[i-1] for i in range(1, len(t.bg_heal_times))],
            "第一刀 - 芙芙首次回血": t.fufu_heal_times[0] - t.first_a_hit,
            "芙芙回血间隔": [t.fufu_heal_times[i] - t.fufu_heal_times[i - 1] for i in range(1, len(t.fufu_heal_times))],
            "前台回血间隔": [fg_heal_times[i] - fg_heal_times[i-1] for i in range(1, len(fg_heal_times))],
            "芙芙首次回血落后队友": t.fufu_heal_times[0] - t.bg_heal_times[0],
            "芙芙首次-第二次回血": t.fufu_heal_times[1] - t.fufu_heal_times[0] if len(t.fufu_heal_times) > 1 else None,
            "芙芙第二次-第三次回血":  t.fufu_heal_times[2] - t.fufu_heal_times[1] if len(t.fufu_heal_times) > 2 else None,
            "芙芙第三次-第四次回血": t.fufu_heal_times[3] - t.fufu_heal_times[2] if len(t.fufu_heal_times) > 3 else None,
            "最早-最晚回血时间间隔": max_time - min_time
        }
    
    return intervals_dict

all_td = {}
all_td.update(dao_1_dict)
all_td.update(dao_2_dict)
all_td.update(dao_3_dict)
all_td.update(dao_4_dict)
all_td.update(dao_5_dict)
all_td.update(next_day_dao_6_dict)

print("=========只砍一刀=========")
print_timestamps_summary(Video_Timestamps,
                         dao_1_dict,
                         get_intervals)

print("=========砍二刀=========")
print_timestamps_summary(Video_Timestamps,
                         dao_2_dict,
                         get_intervals)

print("=========砍三刀=========")
print_timestamps_summary(Video_Timestamps,
                         dao_3_dict,
                         get_intervals)

print("=========砍四刀=========")
print_timestamps_summary(Video_Timestamps,
                         dao_4_dict,
                         get_intervals)

print("=========砍五刀=========")
print_timestamps_summary(Video_Timestamps,
                         dao_5_dict,
                         get_intervals)

print("=========砍六刀=========")
print_timestamps_summary(Video_Timestamps,
                         next_day_dao_6_dict,
                         get_intervals)

print("=========所有数据汇总=========")
print_timestamps_summary(Video_Timestamps,
                         all_td,
                         get_intervals)