#!/user/bin/env python3 -tt
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

import sys
import os
import logging

from base_syw import find_syw, set_score_threshold, ShengYiWu_Score, Score_List
from ye_lan import find_syw_for_ye_lan_with_fu_fu, find_syw_for_ye_lan_with_lei_shen
from fu_ning_na import find_syw_for_fu_ning_na
from lei_shen import find_syw_for_lei_shen
from ling_hua import find_syw_for_ling_hua
from xiang_ling import find_syw_for_xiang_ling
from na_xi_da import find_syw_for_na_xi_da, find_syw_for_na_xi_da_all
from fei_xie_er import find_syw_for_fei_xie_er
from hu_tao import find_syw_for_hu_tao, find_syw_for_hu_tao_lie_ren
from ai_er_hai_seng import find_syw_for_ai_er_hai_seng

def syw_list_to_id_list(score_list: Score_List):
    id_list = []
    for score in score_list.score_list:
        for s in score.syw_combine:
            #print(s)
            id_list.append(s.id)

    return id_list


# Main body
if __name__ == '__main__':
    all_syw = find_syw(lambda s: True)
    all_id_list = [s.id for s in all_syw]

    used_syw_funcs = [
        find_syw_for_ye_lan_with_lei_shen,
        find_syw_for_ye_lan_with_fu_fu,
        find_syw_for_fu_ning_na,
        find_syw_for_lei_shen,
        find_syw_for_ling_hua,
        find_syw_for_xiang_ling,
        find_syw_for_na_xi_da_all,
        find_syw_for_na_xi_da,
        find_syw_for_fei_xie_er,
        find_syw_for_hu_tao_lie_ren,
        # find_syw_for_hu_tao,
        find_syw_for_ai_er_hai_seng
    ]

    used_syw_id_list = []

    set_score_threshold(1.9)
    for func in used_syw_funcs:
        used_syw_id_list += syw_list_to_id_list(func())

    unused_syw_id_list = list(set(all_id_list) - set(used_syw_id_list))

    with open("unused_syw_list.txt", 'w', encoding='utf-8') as f:
        for s in all_syw:
            if s.id in unused_syw_id_list:
                f.write(str(s))
                f.write('\n\n')