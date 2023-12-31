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
18.737, 18.354, 18.253, 18.52
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
