import math
import numpy
import itertools
from datetime import datetime
from base_syw import all_syw

time_format_data = "%H:%M:%S.%f"
def time_diff(t1_str, t2_str):
    t1 = datetime.strptime(t1_str, time_format_data)
    t2 = datetime.strptime(t2_str, time_format_data)
    minus = False
    if t1 > t2:
        diff = t1 - t2
        minus = True
    else:
        diff = t2 - t1
    seconds = diff.seconds
    ms = diff.microseconds / 1000000
    # print(diff)
    # print("seconds: ", seconds)
    # print("ms:", ms)
    diff = seconds + ms
    if minus:
        diff = 0 - diff
    
    return round(diff, 3)

#print(time_diff("00:00:05.586", "00:00:04.519"))

def all_syw_combines():
    print(len(all_syw['h']))
    print(len(all_syw['y']))
    print(len(all_syw['s']))
    print(len(all_syw['b']))
    print(len(all_syw['t']))

    all_parts_name = ['h', 'y', 's', 'b', 't']
    all_parts = set([0, 1, 2, 3, 4])
    l4 = list(itertools.combinations(all_parts, 4))
    l4_with_san = []
    for l in  l4:
        s = all_parts - set(l)
        l4_with_san.append([list(l), list(s)])
    print("四件套：", len(l4_with_san))

    print(l4_with_san)

    l2 = list(itertools.combinations(all_parts,  2))
    l2_with_san = []
    for l in l2:
        s = all_parts - set(l)
        l2_with_san.append([list(l), list(s)])
    print("两件套: ", len(l2_with_san))
    print(l2_with_san)

    l2p2 = []
    for c in l2:
        missed = all_parts - set(c)
        missed_c = list(itertools.combinations(missed, 2))
        
        for m in missed_c:
            l2p2.append(c + m)

    l2p2 = list(set(l2p2))
    l2p2_with_san = []
    for l in l2p2:
        c = [l[0], l[1]]
        m = [l[2], l[3]]
        s = list(all_parts - set(l))
        l2p2_with_san.append([c, m, s])
    print("2+2: ", len(l2p2_with_san))
    print(l2p2_with_san)



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


def kou_xue_chu_shang():
    l = [
    09.769, 
    10.552, 
    17.804, 
    18.721, 
    23.106, 
    23.906, 
    28.122, 
    29.107, 
    33.274, 
    34.157, 
    ]
    print("扣血-出伤间隔：" + str([round(l[i+1] - l[i], 3) for i in range(0, len(l), 2)]))
    print("扣血间隔：" + str([round(l[i+2] - l[i], 3) for i in range(0, len(l) - 2, 2)]))
    print("出伤间隔：" + str([round(l[i + 3] - l[i+1], 3) for i in range(0, len(l) - 2, 2)]))


def avg_min_max(times):
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

def action_timestamps():
    l3 = [
    07.486, 
    08.636, 
    08.886, 
    09.036, 
    09.186, 
    09.369, 
    10.069, 
    10.085, 
    10.219, 
    11.569, 
    12.437, 
    12.737, 
    13.504, 
    13.537, 
    14.304, 
    14.687, 
    14.921, 
    15.421, 
    16.337, 
    22.689, 
    26.472,  
    ]

    print(round(l3[1] - l3[0], 3))
    print(round(l3[2] - l3[0], 3))
    print(round(l3[3] - l3[1], 3))
    print(round(l3[4] - l3[1], 3))
    print(round(l3[5] - l3[3], 3))
    print(round(l3[6] - l3[5], 3))
    print(round(l3[7] - l3[6], 3))
    print(round(l3[8] - l3[7], 3))
    print(round(l3[9] - l3[8], 3))
    print(round(l3[10] - l3[9], 3))
    print(round(l3[11] - l3[10], 3))
    print(round(l3[12] - l3[11], 3))
    print(round(l3[13] - l3[11], 3))
    print(round(l3[14] - l3[13], 3))
    print(round(l3[15] - l3[14], 3))
    print(round(l3[16] - l3[14], 3))
    print(round(l3[17] - l3[15], 3))
    print(round(l3[18] - l3[17], 3))

def test():
    data = [1.665, 1.670, 1.716, 1.717, 1.666, 1.784, 1.699, 1.835, 1.766, 1.619, 1.716, 1.767, 1.715, 1.818, 1.650, 1.718, 1.667, 1.717, 1.716, 1.667, 1.817, 1.668, 1.617, 1.732, 1.668, 2.000, 1.683, 1.700, 1.704, 1.783, 1.617, 1.700, 1.700, 1.718, 1.667, 1.767, 1.666, 1.667, 1.733, 1.700, 1.633, 1.752, 1.683, 1.700, 1.717, 1.733, 1.617, 1.718, 1.684, 1.617, 1.752, 1.666, 1.683, 1.800, 1.617, 1.716, 1.769, 1.650, 1.717, 1.733, 1.618, 1.717, 1.750, 1.717, 1.700, 1.682, 1.653, 1.700, 1.684, 1.716, 1.700, 1.700, 1.683, 1.719, 1.850, 1.533, 1.717, 1.716, 1.669,]
    
    q1 = quantile_exc(data, 1)
    q2 = quantile_exc(data, 2)
    q3 = quantile_exc(data, 3)
    print(data)
    print("第一四分位数: ", q1)
    print("第二四分位数: ", q2)
    print("第三四分位数: ", q3)
    print("第一四分位数n: ", np_quantile(data, 1))
    print("第二四分位数n: ", np_quantile(data, 2))
    print("第三四分位数n: ", np_quantile(data, 3))
    print("quantile range: ", valid_quantile_range(data))
    print("2-sigma range: ", valid_sigma_range(data))

    valid_min, valid_max = valid_sigma_range(data)
    for d in data:
        if d < valid_min:
            print(d)
        elif d > valid_max:
            print(d)

def damage_sum():
    damages  = [
8722,
8930,
9625,
10881,
7245,
11752,
13361,
18570,
9224,
10384,
19698,
17817,
43088,
44327,
18555,
45325,
13093,
25870,
35956,
14027,
14027,
26417,
14324,
36716,
6359,
11727,
6359,
5136,
9472,
11059,
4314
    ]

    for i in range(0, len(damages)):
        print(str(damages[i]) + ", " + str(sum(damages[0:i+1])))


class Haha:
    i = 0

    def __init__(self):
        self.a = 0
        self.b = Haha.i
        Haha.i += 1

h1 = Haha()
h2 = Haha()

def ying_ye_fu_qing():
    intervals = [["影宝e"],
              ["切芙芙出来"], 
              ["芙芙点按e"],
              ["芙芙大招动画开始"], 
              ["芙芙大招动画结束"],
              ["切夜兰出来"],
              ["夜兰e生效一层"],
              ["夜兰大招动画开始"],
              ["夜兰大招动画结束"],
              ["夜兰e生效一层"],
              ["切琴出来"],
              ["琴大招动画开始"], 
              ["琴奶全队时间"],
              ["琴大招动画结束"],
              ["切影宝出来"],
              ["影宝大招动画开始"], 
              ["影宝大招动画结束"],
    ]
    times = [
       ["00:00:02.684", "00:00:03.834", "00:00:04.036", "00:00:04.919", "00:00:06.819", "00:00:07.286", "00:00:08.036", "00:00:08.169", "00:00:09.686", "00:00:10.486", "00:00:10.972", "00:00:12.371", "00:00:13.071", "00:00:13.821", "00:00:15.154", "00:00:15.254", "00:00:17.087"],
       ["00:00:01.301", "00:00:02.167", "00:00:02.384", "00:00:03.284", "00:00:05.186", "00:00:05.586", "00:00:06.336", "00:00:06.586", "00:00:08.086", "00:00:08.786", "00:00:09.069", "00:00:10.702", "00:00:11.436", "00:00:12.137", "00:00:13.371", "00:00:13.454", "00:00:15.454"],
       ["00:00:01.384", "00:00:02.351", "00:00:02.634", "00:00:03.534", "00:00:05.436", "00:00:05.836", "00:00:06.619", "00:00:06.819", "00:00:08.319", "00:00:09.052", "00:00:09.386", "00:00:10.919", "00:00:11.686", "00:00:12.354", "00:00:12.804", "00:00:12.887", "00:00:14.871"]
       ]
    
    for tl in times:
        intervals[0].append(time_diff(tl[0], tl[1]))
        intervals[1].append(time_diff(tl[1], tl[2]))
        for i in range(3, len(intervals)):
            if i >= len(tl):
                break
            if i == 13:
                intervals[i].append(time_diff(tl[i-2], tl[i]))
            else:
                intervals[i].append(time_diff(tl[i-1], tl[i]))

    for i in intervals:
        print(i)

# Main body
if __name__ == '__main__':
    #avg_min_max()

    d = [
        0,
8718.896,
17646.904,
27269.907,
37713.777,
48157.647,
54702.888,
68060.926,
86627.229,
96059.8,
105830.943,
125951.946,
143298.011,
184735.834,
226721.346,
244296.676,
287514.177,
299964.515,
325397.753,
360747.345,
374770.727,
388794.109,
414656.736,
428976.587,
465682.931,
472040.271,
483764.797,
490122.137,
495255.966,
504724.032,
515778.129,
520090.545,
    ]

    for i in range(1, len(d)):
        print(round(d[i] - d[i-1], 3))