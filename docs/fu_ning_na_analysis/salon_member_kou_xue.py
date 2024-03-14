import copy

# 所有可能的扣血组合

kou_xue_percent = [1.6 / 100, 2.4 / 100, 3.6/100, 
                   (1.6 + 2.4) / 100,
                   (1.6 + 3.6) / 100,
                   (2.4 + 3.6) / 100,
                   (1.6 + 2.4 + 3.6) / 100]
kou_xue_per_str = ["f", "x", "p", "f/x", "f/p", "x/p", "f/x/p"]

history = [(None, None, None)]

def print_history():
    h = [(h[0], h[1], None if h[2] is None else round(h[2], 3)) for h in history]
    print(h)

print("press p to print histories")
print("press b to back to previous state")
print("press u to back to un-initialized state")
print("输入 z 表示专武叠层生效一层")

while True:
    if len(history) > 1:
        cur_hp = history[-1][0]
        max_hp = history[-1][1]
        next_possible = []
        prompt_str = "maybe cur_hps: "
        for i in range(0, len(kou_xue_percent)):
            per = kou_xue_percent[i]
            next_cur_hp = int(cur_hp - per * max_hp)
            next_percent = next_cur_hp / max_hp
            next_possible.append((next_cur_hp, max_hp, next_percent))
            prompt_str += "{}: {}({}), ".format(i, next_cur_hp, kou_xue_per_str[i])

        print(prompt_str)
        hps = input("input cur_hp/max_hp: ")
    else:
        next_possible = None
        hps = input("input initial cur_hp/max_hp: ")

    if hps == "b":
        if len(history) < 2:
            print("无可回退了")
        else:
            history.pop()
        if history[-1][-1]:
            prev_cur_hp = history[-1][0]
            prev_max_hp = history[-1][1]
            print(f"回退到前一个状态:{prev_cur_hp}/{prev_max_hp}")
        else:
            print("回退到了未初始化状态")

        continue
    elif hps == 'u':
        history = [(None, None, None)]
        print("回退到了未初始化状态")
        continue
    elif hps == 'p':
        print_history()
        continue
    elif hps == "z":
        if len(history) > 1:
            cur_hp = history[-1][0]
            max_hp = history[-1][1]
            cur_percent = history[-1][2]

            max_hp += 0.14 * 15307
            max_hp = int(max_hp)
            cur_hp = int(max_hp * cur_percent)
            history.append((cur_hp, max_hp, cur_percent))
            print("专武叠层完毕")
            print_history()
        else:
            print("请先初始化")

        continue
    elif next_possible and hps in ["0", "1", "2", "3", "4", "5", "6"]:
        cur_hp, max_hp, cur_percent = next_possible[int(hps)]
    else:
        try:
            cur_hp, max_hp = hps.split('/')
        except Exception as e:
            cur_hp = hps
            max_hp = None

        try:
            cur_hp = int(cur_hp)
            if max_hp:
                max_hp = int(max_hp)
            else:
                prev_max_hp = history[-1][1]
                if not prev_max_hp:
                    print("max hp unknown.")
                    continue
                else:
                    max_hp = prev_max_hp
        except:
            continue
        
        cur_percent = cur_hp / max_hp

    prev_percent = history[-1][-1]

    history.append((cur_hp, max_hp, cur_percent))

    if not prev_percent:
        print("intialize done.")
    else:
        print("changed percent: ", round(prev_percent - cur_percent, 3))