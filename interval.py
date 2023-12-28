l = [
08.986, 
09.669, 
16.654, 
17.454, 
21.906, 
22.722, 
27.072, 
27.939, 
32.157, 
33.107, 
]
print("扣血-出伤间隔：" + str([round(l[i+1] - l[i], 3) for i in range(0, len(l), 2)]))
print("扣血间隔：" + str([round(l[i+2] - l[i], 3) for i in range(0, len(l) - 2, 2)]))
print("出伤间隔：" + str([round(l[i + 3] - l[i+1], 3) for i in range(0, len(l) - 2, 2)]))