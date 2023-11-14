#!/user/bin/env python3 -tt
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

import sys
import os
import logging

from base_syw import find_syw
from ye_lan import find_syw_for_ye_lan
from fu_ling_na import find_syw_for_fu_ling_na
from lei_shen import find_syw_for_lei_shen
from ling_hua import find_syw_for_ling_hua
from xiang_ling import find_syw_for_xiang_ling
from na_xi_da import find_syw_for_na_xi_da

def syw_dict_to_id_list(syw_dict):
    id_list = []
    for sl in syw_dict.values():
        for sc in sl:
            for s in sc[-1]:
                #print(s)
                id_list.append(s.id)

    return id_list


# Main body
if __name__ == '__main__':
    all_syw = find_syw(lambda s: True)
    all_id_list = [s.id for s in all_syw]

    used_syw_funcs = [
        find_syw_for_ye_lan,
        find_syw_for_fu_ling_na,
        find_syw_for_lei_shen,
        find_syw_for_ling_hua,
        find_syw_for_xiang_ling,
        find_syw_for_na_xi_da,
    ]

    used_syw_id_list = []

    for func in used_syw_funcs:
        used_syw_id_list += syw_dict_to_id_list(func())

    unused_syw_id_list = list(set(all_id_list) - set(used_syw_id_list))

    with open("unused_syw_list.txt", 'w', encoding='utf-8') as f:
        for s in all_syw:
            if s.id in unused_syw_id_list:
                f.write(str(s))
                f.write('\n\n')


    # ye_lan_syw = syw_dict_to_id_list(find_syw_for_ye_lan())
    # fu_ling_na_syw = syw_dict_to_id_list(find_syw_for_fu_ling_na())
    # lei_shen_syw = syw_dict_to_id_list(find_syw_for_lei_shen())
    # ling_hua_syw = syw_dict_to_id_list(find_syw_for_ling_hua())
    # xiang_ling_syw = syw_dict_to_id_list(find_syw_for_xiang_ling())
    # na_xi_da_syw = syw_dict_to_id_list(find_syw_for_na_xi_da())

    # used_syw_list = ye_lan_syw + fu_ling_na_syw