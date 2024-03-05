def ys_crit_damage(non_crit_damage, crit_damage):
    return int(non_crit_damage * (1 + crit_damage))

def ys_crit_damage_no_round(non_crit_damage, crit_damage):
    return non_crit_damage * (1 + crit_damage)

def ys_expect_damage(non_crit_damage, crit_rate, crit_damage):
    c = min(crit_rate, 1)
    return int(non_crit_damage * (1 + c * crit_damage))

def ys_expect_damage_no_round(non_crit_damage, crit_rate, crit_damage):
    c = min(crit_rate, 1)
    return non_crit_damage * (1 + c * crit_damage)
