#!/user/bin/env python3 -c
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

import sys
import os
import logging
import itertools
import copy
import uuid
import concurrent.futures
import traceback
from math import ceil
from collections.abc import Callable

from .elem_type import Ys_Elem_Type
from .utils import ys_expect_damage, ys_crit_damage
from .syw import ShengYiWu
from .syw_collection import all_syw


all_syw_by_position = [all_syw[ShengYiWu.PART_HUA],
                       all_syw[ShengYiWu.PART_YU],
                       all_syw[ShengYiWu.PART_SHA],
                       all_syw[ShengYiWu.PART_BEI],
                       all_syw[ShengYiWu.PART_TOU]
                       ]


def debug_set_syw(part, syw_lst):
    all_syw[part] = syw_lst


def debug_add_syw(syw: ShengYiWu):
    all_syw[syw.part].append(syw)

def debug_find_by_id(id):
    for syw_lst in all_syw.values():
        for syw in syw_lst:
            if syw.id == id:
                return syw

def find_syw(match_syw_callback):
    matched_syw = []
    for sl in all_syw.values():
        for s in sl:
            if match_syw_callback(s):
                matched_syw.append(s)
    return matched_syw

qualifier_threshold = 1.5
score_threshold = 1.8


def set_score_threshold(new_threashold):
    global score_threshold
    score_threshold = new_threashold


def set_qualifier_threshold(new_threashold):
    global qualifier_threshold
    qualifier_threshold = new_threashold


class ShengYiWu_Score:
    def __init__(self, syw_combine: list[ShengYiWu]):
        self.__expect_score = 0
        self.__crit_score = 0

        self.__overall_score = 0

        self.__extra_score = 0
        self.__custom_data = None
        self.__syw_combine: list[ShengYiWu] = syw_combine

    def damage_to_score(self, damage, crit_rate, crit_damage):
        self.__expect_score = ys_expect_damage(damage, crit_rate, crit_damage)
        self.__crit_score = ys_crit_damage(damage, crit_damage)

    @property
    def expect_score(self):
        return self.__expect_score

    @expect_score.setter
    def expect_score(self, score):
        self.__expect_score = score

    @property
    def crit_score(self):
        return self.__crit_score

    @crit_score.setter
    def crit_score(self, score):
        self.__crit_score = score

    @property
    def overall_score(self):
        return self.__overall_score

    @overall_score.setter
    def overall_score(self, score):
        self.__overall_score = score

    @property
    def extra_score(self):
        return self.__extra_score
    
    @extra_score.setter
    def extra_score(self, score):
        self.__extra_score = score

    @property
    def custom_data(self):
        return self.__custom_data

    @custom_data.setter
    def custom_data(self, data):
        self.__custom_data = data

    @property
    def syw_combine(self):
        return self.__syw_combine

    @syw_combine.setter
    def syw_combine(self, c):
        self.__syw_combine = c


class Score_List:
    def __init__(self):
        self.__max_expect_score = 0
        self.__max_crit_score = 0
        self.__max_extra_score = 0
        self.__score_list: list[ShengYiWu_Score] = []

    @property
    def max_expect_score(self):
        return self.__max_expect_score

    @max_expect_score.setter
    def max_expect_score(self, score):
        self.__max_expect_score = score

    @property
    def max_crit_score(self):
        return self.__max_crit_score

    @max_crit_score.setter
    def max_crit_score(self, score):
        self.__max_crit_score = score

    @property
    def max_extra_score(self):
        return self.__max_extra_score
    
    @max_extra_score.setter
    def max_extra_score(self, score):
        self.__max_extra_score = score

    @property
    def score_list(self):
        return self.__score_list

    def merge(self, another_lst):
        if another_lst.max_expect_score != self.max_expect_score or another_lst.max_crit_score != self.max_crit_score:
            raise Exception(
                "Score_List merge: max_expect_score or max_crit_score not match!")
        
        self.__score_list.extend(another_lst.score_list)

    def add_score(self, score: ShengYiWu_Score):
        self.__score_list.append(score)

        if score.expect_score > self.__max_expect_score:
            self.__max_expect_score = score.expect_score

        if score.crit_score > self.__max_crit_score:
            self.__max_crit_score = score.crit_score

        if score.extra_score > self.__max_extra_score:
            self.__max_extra_score = score.extra_score

    def discard_below_threshold(self, threshold, min_remain=30):
        above_list: list[ShengYiWu_Score] = []
        below_list: list[ShengYiWu_Score] = []
        for score in self.__score_list:
            overall_score = score.expect_score / self.__max_expect_score
            overall_score += score.crit_score / self.__max_crit_score
            score.overall_score = overall_score

            if overall_score >= threshold:
                above_list.append(score)
            else:
                below_list.append(score)

        num_above = len(above_list)
        if num_above < min_remain:
            below_list.sort(key=lambda x: x.overall_score)
            extra_num = 30 - num_above
            above_list.extend(below_list[-extra_num:])

        self.__score_list = above_list

    def write_to_file(self, result_txt_file, result_description):
        if not self.__score_list:
            return
        
        self.__score_list.sort(key=lambda x: x.overall_score)
        print("write num:", len(self.__score_list))

        desc = "总评分, 期望伤害评分, 暴击伤害评分, " + str(result_description) + ", 圣遗物组合" 

        with open(result_txt_file, 'w', encoding='utf-8') as f:
            for score in self.__score_list:
                expect_score_str = str(score.expect_score) + '(' + str(round(score.expect_score / self.__max_expect_score, 4)) + ')'
                crit_score_str = str(score.crit_score) + '(' + str(round(score.crit_score / self.__max_crit_score, 4)) + ')'
                write_lst = [str(round(score.overall_score, 4)), expect_score_str, crit_score_str, 
                             str(score.custom_data), 
                             str(score.syw_combine)]
                # print((i, c))
                # f.write(str((round(score, 4), c, )))
                f.write(", ".join(write_lst))
                f.write('\n\n')

            f.write(str(desc))
            f.write('\n\n')
            f.write("最大期望伤害: " + str(self.__max_expect_score))
            f.write('\n')
            f.write("最大暴击伤害: " + str(self.__max_crit_score))
            f.write('\n')
            f.write("max_extra_score: " + str(self.__max_extra_score))
            f.write('\n')

# 各种套装组合的模式，分别有四件套，2+2，2件套+3散件
# 
# 前面四个表示 set1 应该出现的位置，后一个表示散件应该出现的位置
SET4_PATTERN = [[[0, 1, 2, 3], [4]], [[0, 1, 2, 4], [3]], [[0, 1, 3, 4], [2]], [[0, 2, 3, 4], [1]], [[1, 2, 3, 4], [0]]]
# 前面两个为 set1 应该出现的位置，中间两个表示 set2 应该出现的位置，最后一个表示散件应该出现的位置
SET2P2_PATTERN = [[[0, 1], [3, 4], [2]], [[1, 4], [0, 3], [2]], [[2, 4], [0, 3], [1]], 
                    [[2, 3], [1, 4], [0]], [[1, 2], [3, 4], [0]], [[3, 4], [0, 1], [2]], 
                    [[0, 2], [1, 4], [3]], [[0, 4], [1, 2], [3]], [[1, 4], [2, 3], [0]], 
                    [[2, 4], [1, 3], [0]], [[1, 3], [0, 2], [4]], [[0, 1], [2, 4], [3]], 
                    [[0, 2], [3, 4], [1]], [[1, 4], [0, 2], [3]], [[0, 3], [2, 4], [1]], 
                    [[3, 4], [1, 2], [0]], [[0, 2], [1, 3], [4]], [[2, 3], [0, 1], [4]], 
                    [[1, 2], [0, 4], [3]], [[0, 4], [2, 3], [1]], [[2, 3], [0, 4], [1]], 
                    [[0, 3], [1, 2], [4]], [[2, 4], [0, 1], [3]], [[0, 1], [2, 3], [4]], 
                    [[1, 3], [0, 4], [2]], [[3, 4], [0, 2], [1]], [[1, 3], [2, 4], [0]], 
                    [[0, 4], [1, 3], [2]], [[0, 3], [1, 4], [2]], [[1, 2], [0, 3], [4]]
                    ]
# 前面两件表示 set1 应该出现的位置，后面三个表示散件应该出现的位置
SET2_PATTERN = [[[0, 1], [2, 3, 4]], [[0, 2], [1, 3, 4]], [[0, 3], [1, 2, 4]], 
                [[0, 4], [1, 2, 3]], [[1, 2], [0, 3, 4]], [[1, 3], [0, 2, 4]], 
                [[1, 4], [0, 2, 3]], [[2, 3], [0, 1, 4]], [[2, 4], [0, 1, 3]], 
                [[3, 4], [0, 1, 2]]]

SAN_JIAN_SET_NAME = "散件"
SAN_JIAN_SET_PATTERNS = [[SAN_JIAN_SET_NAME, SAN_JIAN_SET_NAME, SAN_JIAN_SET_NAME, SAN_JIAN_SET_NAME, SAN_JIAN_SET_NAME]]

class Syw_Combine_Desc:
    def __init__(self, set1_name=None, set1_num=0, set2_name=None, set2_num=0):
        """
        set1_num 和 set2_num 允许的组合模式为: 0+0, 2+2, 4+0, 0+4, 2+0, 0+2
        
        其中 0+0 比较特殊：
        
        * 如果同时指定了 set1_name 和 set2_name，则等价于 2+2
        * 如果 set1_name 和 set2_name 都没指定，则表示全散件
        """
        if set1_num + set2_num > 4:
            raise Exception("set1_num + set2_num > 4")
        elif set1_num == 0 and set2_num == 0:   # 0+0
            if set1_name and set2_name:
                set1_num = 2
                set2_num = 2
            elif set1_name or set2_name:
                raise Exception("set1_num and set2_num is 0, but set1_name and set2_name not both specified or un-specified")
        elif set1_num == 2 and set2_num == 2:   # 2+2
            if not set1_name or not set2_name:
                raise Exception("2+2, but set1_name or set2_name not specified")
        elif set1_num == 4: # 4+0
            if set2_name:
                raise Exception("set1_num is 4, but set2_name is not None")
            elif not set1_name:
                raise Exception("set1_num is 4, but set1_name is not specified")
            else:
                single_set_name = set1_name
        elif set2_num == 4 and set1_name: # 0+4
            if set1_name:
                raise Exception("set2_num is 4, but set1_name is not None")
            elif not set2_name:
                raise Exception("set2_num is 4, but set2_name is not specified")
            else:
                single_set_name = set2_name
        elif set1_num == 2 and set2_num == 0:   # 2+0
            if set2_name:
                raise Exception("2+0, but set2_name is specified")
            elif not set1_name:
                raise Exception("2+0, but set1_name is not specified")
            else:
                single_set_name = set1_name
        elif set1_num == 0 and set2_num == 2:   # 0+2
            if set1_name:
                raise Exception("0+2, but set1_name is specified")
            elif not set2_name:
                raise Exception("0+2, but set2_name is not specified")
            else:
                single_set_name = set2_name
        elif set1_name == set2_name:
            raise Exception("set1_name == set2_name")
        
        self.set1_name = set1_name
        self.set1_num = set1_num

        self.set2_name = set2_name
        self.set2_num = set2_num

        self.set_patterns = []
        if self.set1_num == 4 or set2_num == 4:
            for pos_pattern in SET4_PATTERN:
                # eg: pos_pattern = [[0, 1, 2, 3], [4]]
                pattern = [None, None, None, None, None]
                for pos in pos_pattern[0]:
                    pattern[pos] = single_set_name

                for pos in pos_pattern[1]:
                    pattern[pos] = SAN_JIAN_SET_NAME

                self.set_patterns.append(pattern)
        elif self.set1_num == 2 and self.set2_num == 2:
            for pos_pattern in SET2P2_PATTERN:
                # eg: pos_pattern = [[0, 1], [3, 4], [2]]
                pattern = [None, None, None, None, None]
                for pos in pos_pattern[0]:
                    pattern[pos] = set1_name

                for pos in pos_pattern[1]:
                    pattern[pos] = set2_name

                for pos in pos_pattern[2]:
                    pattern[pos] = SAN_JIAN_SET_NAME

                self.set_patterns.append(pattern)
        elif self.set1_num == 2 or self.set2_num == 2:
            for pos_pattern in SET2_PATTERN:
                # eg: pos_pattern = [[0, 1], [2, 3, 4]]
                pattern = [None, None, None, None, None]
                for pos in pos_pattern[0]:
                    pattern[pos] = single_set_name

                for pos in pos_pattern[1]:
                    pattern[pos] = SAN_JIAN_SET_NAME

                self.set_patterns.append(pattern)
        else:
            self.set_patterns = SAN_JIAN_SET_PATTERNS

    @staticmethod
    def any_2p2(set_names: list[str]):
        set_names = set(set_names)
        all_2p2 = list(itertools.combinations(set_names, 2))
        descs = []
        for set1_name, set2_name in all_2p2:
            # print(set1_name, set2_name)
            descs.append(Syw_Combine_Desc(set1_name=set1_name, set2_name=set2_name))

        return descs

def match_syw(s: ShengYiWu, expect_name, matcher=None) -> bool:
    if s.name != expect_name:
        return False
    
    if matcher:
        return matcher(s)
    else:
        return True
        

# 花和羽毛没有 match callback，因为正常来说，没有双暴的花和羽毛不会列入 all_syw 集合中的
def find_syw_combine(combine_desc_lst: list[Syw_Combine_Desc],
                     match_sha_callback=None, match_bei_callback=None, match_tou_callback=None):
    sha_list: list[ShengYiWu] = []
    bei_list: list[ShengYiWu] = []
    tou_list: list[ShengYiWu] = []

    if match_sha_callback:
        for syw in all_syw[ShengYiWu.PART_SHA]:
            if match_sha_callback(syw):
                sha_list.append(syw)
    else:
        sha_list = all_syw[ShengYiWu.PART_SHA]

    if match_bei_callback:
        for syw in all_syw[ShengYiWu.PART_BEI]:
            if match_bei_callback(syw):
                bei_list.append(syw)
    else:
        bei_list = all_syw[ShengYiWu.PART_BEI]

    if match_tou_callback:
        for syw in all_syw[ShengYiWu.PART_TOU]:
            if match_tou_callback(syw):
                tou_list.append(syw)
    else:
        tou_list = all_syw[ShengYiWu.PART_TOU]

    # 散件集合
    syw_set_dict: dict[str, list[list[ShengYiWu]]] = {
        SAN_JIAN_SET_NAME: [all_syw[ShengYiWu.PART_HUA], all_syw[ShengYiWu.PART_YU], sha_list, bei_list, tou_list]
    }

    # 接下来扫描套装
    for combine_desc in combine_desc_lst:
        set_names = []
        if combine_desc.set1_name:
            set_names.append(combine_desc.set1_name)
        if combine_desc.set2_name:
            set_names.append(combine_desc.set2_name)

        for name in set_names:
            if name not in syw_set_dict:
                syw_set_dict[name] = [
                    [syw for syw in all_syw_by_position[0] if match_syw(syw, name)],
                    [syw for syw in all_syw_by_position[1] if match_syw(syw, name)],
                    [syw for syw in all_syw_by_position[2] if match_syw(syw, name, match_sha_callback)],
                    [syw for syw in all_syw_by_position[3] if match_syw(syw, name, match_bei_callback)],
                    [syw for syw in all_syw_by_position[4] if match_syw(syw, name, match_tou_callback)],
                ]

    # 接下来按照 set pattern组合圣遗物
    
    all_combins_5 = {}
    raw_score_list: list[ShengYiWu_Score] = []

    for combine_desc in combine_desc_lst:
        for pattern in combine_desc.set_patterns:
            syw_lst_lst = [syw_set_dict[pattern[0]][0],
                           syw_set_dict[pattern[1]][1],
                           syw_set_dict[pattern[2]][2],
                           syw_set_dict[pattern[3]][3],
                           syw_set_dict[pattern[4]][4]]
            for c0 in syw_lst_lst[0]:
                for c1 in syw_lst_lst[1]:
                    for c2 in syw_lst_lst[2]:
                        for c3 in syw_lst_lst[3]:
                            for c4 in syw_lst_lst[4]:
                                combine = [c0, c1, c2, c3, c4]
                                # TODO: 有更好的去重复算法么？总感觉这样用字符串 dict 很费时
                                scid = c0.id + c1.id + c2.id + c3.id + c4.id
                                if scid not in all_combins_5:
                                    all_combins_5[scid] = True
                                    raw_score_list.append(ShengYiWu_Score(combine))
    
    return raw_score_list

def calc_score_1st_phrase(raw_score_list: list[ShengYiWu_Score], 
                          calculate_score_callbak: Callable[[ShengYiWu_Score], bool]) -> Score_List:
    score_list = Score_List()

    for score in raw_score_list:
        if not calculate_score_callbak(score):
            continue

        score_list.add_score(score)

    return score_list


def calc_score_2nd_phrase(score_list: Score_List, threshold) -> Score_List:
    score_list.discard_below_threshold(threshold)
    return score_list


def chunk_into_n(lst, n):
    size = ceil(len(lst) / n)
    return list(
        map(lambda x: lst[x * size:x * size + size],
            list(range(n)))
    )


def calc_score_multi_proc(raw_score_list, calculate_score_callbak, threshold) -> Score_List:
    all_combines_chunks = chunk_into_n(raw_score_list, 5)

    final_score_list = Score_List()

    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [executor.submit(
            calc_score_1st_phrase, lst, calculate_score_callbak) for lst in all_combines_chunks]

        score_list_lst: list[Score_List] = []
        for future in concurrent.futures.as_completed(futures):
            try:
                score_list = future.result()
                if score_list.max_expect_score > final_score_list.max_expect_score:
                    final_score_list.max_expect_score = score_list.max_expect_score

                if score_list.max_crit_score > final_score_list.max_crit_score:
                    final_score_list.max_crit_score = score_list.max_crit_score

                if score_list.max_extra_score > final_score_list.max_extra_score:
                    final_score_list.max_extra_score = score_list.max_extra_score

                score_list_lst.append(score_list)
            except Exception as exc:
                print('1st generated an exception: %s' % (exc))
                traceback.print_exc()

        for score_list in score_list_lst:
            score_list.max_expect_score = final_score_list.max_expect_score
            score_list.max_crit_score = final_score_list.max_crit_score
            score_list.max_extra_score = final_score_list.max_extra_score

        futures = [executor.submit(calc_score_2nd_phrase, lst, threshold) for lst in score_list_lst]
        for future in concurrent.futures.as_completed(futures):
            try:
                final_score_list.merge(future.result())
            except Exception as exc:
                print('1st generated an exception: %s' % (exc))
                traceback.print_exc()

    return final_score_list


def calc_score_inline(raw_score_list, calculate_score_callbak, threshold) -> Score_List:
    score_list = calc_score_1st_phrase(raw_score_list, calculate_score_callbak)
    return calc_score_2nd_phrase(score_list, threshold)


def calculate_score(raw_score_list: list[ShengYiWu_Score],
                    calculate_score_callbak,
                    result_txt_file, result_description,
                    calculate_score_qualifier=None):
    lst_len = len(raw_score_list)

    if calculate_score_qualifier:
        if lst_len > 10000:
            score_list = calc_score_multi_proc(
                raw_score_list, calculate_score_qualifier, qualifier_threshold)
        else:
            score_list = calc_score_inline(
                raw_score_list, calculate_score_qualifier, qualifier_threshold)


        raw_score_list = score_list.score_list
        lst_len = len(raw_score_list)
        print("qualified remain: ", lst_len)

    if lst_len > 10000:
        score_list = calc_score_multi_proc(raw_score_list, calculate_score_callbak, score_threshold)
    else:
        score_list = calc_score_inline(raw_score_list, calculate_score_callbak, score_threshold)

    score_list.write_to_file(result_txt_file, result_description)

    return score_list


def test_find_syw_combines():
    combine_desc_lst = Syw_Combine_Desc.any_2p2([ShengYiWu.JU_TUAN, 
                                                 ShengYiWu.HUA_HAI,
                                                 ShengYiWu.QIAN_YAN,
                                                 ShengYiWu.CHEN_LUN,
                                                 ShengYiWu.SHUI_XIAN])
    
    def match_sha_callback(syw: ShengYiWu): return syw.hp_percent == 0.466 or syw.energy_recharge == ShengYiWu.ENERGY_RECHARGE_MAX
    def match_bei_callback(syw: ShengYiWu): return syw.hp_percent == 0.466 or syw.elem_type == Ys_Elem_Type.SHUI

    combine_desc_lst.append(Syw_Combine_Desc(set1_name=ShengYiWu.JU_TUAN, set1_num=4))
    raw_score_list = find_syw_combine(combine_desc_lst, 
                                      match_sha_callback=match_sha_callback,
                                      match_bei_callback=match_bei_callback)
    print(len(raw_score_list))
    return raw_score_list

# Main body
if __name__ == '__main__':
    test_find_syw_combines()