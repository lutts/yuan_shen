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


def avg_min_max():
    l2 = [
5.168, 5.168, 5.17, 5.185, 5.2, 5.2, 5.2, 5.201, 5.217, 5.218, 5.218, 5.268
        ]
    l2.sort()

    l2_avg = round(sum(l2) / len(l2), 3)
    l2_max = max(l2)
    l2_min = min(l2)
    min_max_avg = round((l2_max + l2_min) / 2, 3)

    print("排序: ", l2)
    print("\t数量：" + str(len(l2)))
    print("\t最大：" + str(l2_max) + ", +" + str(round(l2_max - l2_avg, 3)))
    print("\t最小：" + str(l2_min) + ", " + str(round(l2_min - l2_avg, 3)))
    print("\t平均：" + str(l2_avg))
    print("\t最大-最小平均：" + str(min_max_avg))
    print("\t最大-最小-平均-差值: " + str(round(l2_max - min_max_avg, 3)))
    print("\t最小-最大范围：[" + str(l2_min) + ", " + str(l2_max) + "]")
    print("\tquantile range: ", valid_quantile_range(l2))
    print("\t2-sigma range: ", valid_sigma_range(l2))
    print("\t3-sigma range: ", valid_sigma_range(l2, num_deviation=3))

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

# Main body
if __name__ == '__main__':
    #avg_min_max()
    damage_sum()