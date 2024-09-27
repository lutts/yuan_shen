Vy = 159

def check_Vj(Vj):
    if 10000 / Vj >= 13000 / Vy:
        return False
    
    t = 10000 / Vj + 10000 / (Vj + 96 * 0.3)
    if t >= (6000 / Vy + 7000 / Vy + 10000 / Vy):
        return False
    
    t =  10000 / Vj + 10000 / (Vj + 96 * 0.3) + 9000 / (Vj + 96 * 0.3)
    if t >= (6000 / Vy + 7000 / Vy + 10000 / Vy + 10000 / Vy):
        return False
    
    return True

v = 96
while v < 136:
    if check_Vj(v):
        print(f"find v: {v}")
        break
    v += 1

