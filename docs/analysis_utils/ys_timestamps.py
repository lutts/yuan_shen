from datetime import datetime
import math
import numpy


def quantile_exc(data, n):
    """
    n: 第几个四分位数
    """
    if n < 1 or n > 3:
        return False
    
    data.sort()
    position = (len(data) + 1) * n / 4
    pos_int = int(math.modf(position)[1])
    pos_decimal = position - pos_int
    quartile = data[pos_int - 1] + (data[pos_int] - data[pos_int - 1]) * pos_decimal
    return quartile


def np_quantile(data_list, n):
    if n < 1 or n > 3:
        return None
    
    q = numpy.quantile(data_list, n / 4)
    
    if n == 1: # round down
        q = int(q * 1000) / 1000

    return round(q, 3)

def valid_quantile_range(data_list):
    q1 = np_quantile(data_list, 1)
    q3 = np_quantile(data_list, 3)

    q_min = q1 - 1.5 * (q3 - q1)
    q_min = round(q_min, 3)

    q_max = q3 + 1.5 * (q3 - q1)
    q_max = round(q_max, 3)

    return (q_min, q_max)


def valid_sigma_range(data_list, num_deviation = 2):
    data_array = numpy.asarray(data_list)
    mean = numpy.mean(data_array, axis=0)
    std = numpy.std(data_array, axis=0)

    return (round(mean - num_deviation * std,  3), round(mean + num_deviation * std, 3))

def print_avg_min_max(times):
    times.sort()

    times_avg = round(sum(times) / len(times), 3)
    times_max = max(times)
    times_min = min(times)
    min_max_avg = round((times_max + times_min) / 2, 3)

    print("排序: ", times)
    print("\t数量：" + str(len(times)))
    print("\t最大：" + str(times_max) + ", +" + str(round(times_max - times_avg, 3)))
    print("\t最小：" + str(times_min) + ", " + str(round(times_min - times_avg, 3)))
    print("\t平均：" + str(times_avg))
    print("\t最大-最小平均：" + str(min_max_avg))
    print("\t最大-最小-平均-差值: " + str(round(times_max - min_max_avg, 3)))
    print("\t最小-最大范围：[" + str(times_min) + ", " + str(times_max) + "]")
    print("\tquantile range: ", valid_quantile_range(times))
    print("\t2-sigma range: ", valid_sigma_range(times))
    print("\t3-sigma range: ", valid_sigma_range(times, num_deviation=3))


class Ys_Timestamp:
    FORMAT = "%H:%M:%S.%f"

    def __init__(self, timestamp_str):
        try:
            self.t = datetime.strptime(timestamp_str, Ys_Timestamp.FORMAT)
        except:
            self.t = None

    def __sub__(self, other):
        if self.t is None:
            return None
        
        if isinstance(other, datetime):
            other_t = other
        else:
            if other.t is None:
                return None
            other_t = other.t

        minus = False
        if self.t > other_t:
            diff = self.t - other_t
        else:
            diff = other_t - self.t
            minus = True

        seconds = diff.seconds
        ms = diff.microseconds / 1000000
        # print(diff)
        # print("seconds: ", seconds)
        # print("ms:", ms)
        diff = seconds + ms
        if minus:
            diff = 0 - diff

        return round(diff, 3)
    
    def to_float(self):
        zero = datetime.strptime("00:00:00.000", Ys_Timestamp.FORMAT)

        return self - zero
    
    def __str__(self) -> str:
        return str(self.t)
    
    def __repr__(self) -> str:
        return repr(self.t)
    
null_timestamp = Ys_Timestamp("0")


def generic_field_parser(t_lst):
    parse_result = []
    all_times = []
    for t in t_lst:
        if isinstance(t, str):
            ys_t = Ys_Timestamp(t)
            if ys_t.t:
                parse_result.append(ys_t)
                all_times.append(t)
            else:
                parse_result.append(t)
        elif t is null_timestamp:
            parse_result.append(t)
        elif isinstance(t, list) or isinstance(t, tuple):
            sub_result, sub_times = generic_field_parser(t)
            parse_result.append(sub_result)
            all_times.extend(sub_times)

    if isinstance(t_lst, tuple):
        parse_result = tuple(parse_result)

    return parse_result, all_times


def generic_print_func(description, raw_intervals, soreted_valid_intervals):
    s = description + ": "

    for filename, raw_interval in raw_intervals:
        s += "[" + filename + ":"
        if isinstance(raw_interval, list):
            # 加上编号，避免太多时数数浪费时间
            s += ", ".join([str(i+1) +":" + str(raw_interval[i]) for i in range(0, len(raw_interval))]) + "]"
        else:
            s += str(raw_interval)
        s += '], '

    s += "\n"
    s += "排序: " + str(soreted_valid_intervals)
    s += "\n"
    print(s)

def print_timestamps_summary(Video_Timestamps_cls, timestamp_dict: dict[str, list], 
                             get_intervals_func, print_func=None):
    ys_timestamp_dict = {}
    for filename, times in timestamp_dict.items():
        num_fields = len(Video_Timestamps_cls._fields)
        num_times = len(times)
        if num_fields != num_times:
            raise Exception(f"Video_Timestamps_cls field number({num_fields}) not match with {filename} time number({num_times})")
        
        parse_result, all_times = generic_field_parser(times)

        times_set = set(all_times)
        if len(all_times) != len(times_set):
            print("{} has duplicate timestamps: {}".format(
                filename, [t for t in all_times if all_times.count(t) > 1]))
            
        ys_timestamp_dict[filename] = Video_Timestamps_cls(*parse_result)

    intervals_dict = get_intervals_func(ys_timestamp_dict)

    summary = {}
    for filename, interval_dict in intervals_dict.items():
        for description, interval in interval_dict.items():
            if description in summary:
                summary[description].append([filename, interval])
            else:
                summary[description] = [[filename, interval]]

    valid_intervals_dict = {}
    for description, raw_intervals in summary.items():
        soreted_valid_intervals = []
        for interval in raw_intervals:
            it = interval[1]
            if isinstance(it, list):
                soreted_valid_intervals.extend([i for i in it if i is not None])
            elif it is not None:
                soreted_valid_intervals.append(it)

        def key_func(t):
            if isinstance(t, tuple):
                return t[0]
            else:
                return t
            
        soreted_valid_intervals.sort(key=key_func)

        if not print_func:
            generic_print_func(description, raw_intervals, soreted_valid_intervals)
        else:
            print_func(description, raw_intervals, soreted_valid_intervals)

        valid_intervals_dict[description] = soreted_valid_intervals

    return valid_intervals_dict

# 使用模板：复制下面的代码
# import sys
# import os
# from collections import namedtuple
# from typing import NamedTuple

# sys.path.append(os.path.abspath('../..'))

# from analysis_utils.ys_timestamps import Ys_Timestamp, print_timestamps_summary, print_avg_min_max, null_timestamp

# timestamp_dict = {
# }

# class Video_Timestamps(NamedTuple):
#     q_anim_start: Ys_Timestamp
#     q_anim_end: Ys_Timestamp

#     pao_pao_disappear: Ys_Timestamp

#     ling_hua_last_bonused:  Ys_Timestamp
#     ling_hua_first_unbonused: Ys_Timestamp


# def get_intervals(ys_timestamp_dict: dict[str, Video_Timestamps]):
#     intervals_dict = {}
#     for filename, t in ys_timestamp_dict.items():
#         intervals_dict[filename] = {
#         }
    
#     return intervals_dict

# sorted_intervals = print_timestamps_summary(Video_Timestamps, timestamp_dict, get_intervals)