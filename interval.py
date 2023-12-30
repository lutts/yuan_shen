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


l2 = [
0, 0.133,  0.15,  0.082,  0.167,  0.117,  0.1,  0.1,  0.017
]

l2_avg = round(sum(l2) / len(l2), 3)
l2_max = max(l2)
l2_min = min(l2)
min_max_avg = round((l2_max + l2_min) / 2, 3)

print("\t数量：" + str(len(l2)))
print("\t最大：" + str(l2_max) + "， +" + str(round(l2_max - l2_avg, 3)))
print("\t最小：" + str(l2_min) + "， " + str(round(l2_min - l2_avg, 3)))
print("\t平均：" + str(l2_avg))
print("\t最大-最小平均：" + str(min_max_avg))
print("\t最大-最小-平均-差值: " + str(round(l2_max - min_max_avg, 3)))