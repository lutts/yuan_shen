import itertools

elem_ch_num = d = {"火":6, "水":5, "雷":7, "冰":4, "风":6, "岩":5, "草":7}

elem_combination = list(itertools.combinations(elem_ch_num, 3))

result = {}
for c in elem_combination:
    s = str(c)
    total = 0
    for n in c:
        total += d[n]
    result[s] = total + 1 # 加上爷

sorted_result = sorted(result.items(), key=lambda x: x[1])
for k, v in sorted_result:
    print(f"{k}:{v}")