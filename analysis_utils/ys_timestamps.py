from datetime import datetime


class Ys_Timestamp:
    FORMAT = "%H:%M:%S.%f"

    def __init__(self, timestamp_str):
        try:
            self.t = datetime.strptime(timestamp_str, Ys_Timestamp.FORMAT)
        except:
            self.t = None

    def __sub__(self, other):
        if self.t is None:
            return "None"

        if other.t is None:
            return "None"

        minus = False
        if self.t > other.t:
            diff = self.t - other.t
        else:
            diff = other.t - self.t
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

def print_timestamps_summary(timestamp_names: list[str], timestamp_dict: dict[str, list[str|list[str]]], get_intervals_func):
    ys_timestamp_dict = {}
    for name, times in timestamp_dict.items():
        if len(timestamp_names) != len(times):
            raise Exception("timestamp_names need update!")

        ys_timestamps = {}
        all_times = []
        for idx in range(0, len(times)):
            t = times[idx]
            if isinstance(t, list):
                all_times.extend(t)

                sub_lst = []
                for sub_t in t:
                    sub_lst.append(Ys_Timestamp(sub_t))
                ys_timestamps[timestamp_names[idx]] = sub_lst
            else:
                all_times.append(t)

                ys_timestamps[timestamp_names[idx]] = Ys_Timestamp(t)

        times_set = set(all_times)
        if len(all_times) != len(times_set):
            print("{} has duplicate timestamps: {}".format(
                name, [t for t in all_times if all_times.count(t) > 1]))
            
        ys_timestamp_dict[name] = ys_timestamps

    intervals_dict = get_intervals_func(ys_timestamp_dict)

    summary = {}
    for name, intervals in intervals_dict.items():
        for desc, interval in intervals.items():
            if desc in summary:
                summary[desc].append([name, interval])
            else:
                summary[desc] = [[name, interval]]

    for desc, intervals in summary.items():
        valid_intervals = []
        for interval in intervals:
            it = interval[1]
            if isinstance(it, list):
                valid_intervals.extend([i for i in it if i != "None"])
            else:
                valid_intervals.append(it)
        valid_intervals.sort()

        print("{}: {}\n排序：{}\n".format(desc, intervals, valid_intervals))