#!/user/bin/env python3 -tt
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

import logging
import typing
import random

from .elem_type import Ys_Elem_Type
from .utils import ys_crit_damage, ys_expect_damage
from .buff_manager import Buff, BuffManager
from .monster import Monster
from .character import Character, Character_HP_Change_Data
from .events import Events


ActionPlan = typing.NewType("ActionPlan", None)

class Action:
    enable_debug = False
    enable_record = False

    def __init__(self, name, start_time):
        self.name = name
        self.start_time = start_time
        self.idx = None

    def set_idx(self, idx):
        self.idx = idx

    def __debug(self, fmt_str, *args, **kwargs):
        fmt_str = str(round(self.start_time, 3)) + ": " + fmt_str
        logging.debug(fmt_str, *args, **kwargs)
    
    def debug(self, fmt_str, *args, **kwargs):
        pass
        # self.__debug(fmt_str, *args, **kwargs)

    def get_timeline_nodes(self):
        return [(self.start_time, self.idx)]
    
    def need_update_buff(self):
        return True

    def do(self, plan: ActionPlan):
        """
        * return value: True if finished, False if not finished, aka, repeatable
        """
        return True

class SwitchAction(Action):
    def __init__(self, ch: Character, t):
        super().__init__(f"切换到{ch.name}", t)
        self.ch = ch

    def need_update_buff(self):
        return False

    def do(self, plan: ActionPlan):
        plan.switch_character(self.ch)

class Q_Animation_Start_Action(Action):
    def __init__(self, ch: Character, t):
        super().__init__(f"{ch.name}大招动画开始")
        self.ch = ch

    def need_update_buff(self):
        return False

    def do(self, plan: ActionPlan):
        self.ch.get_hp().set_in_q_animation(True)


class Q_Animation_End_Action(Action):
    def __init__(self, ch: Character, t):
        super().__init__(f"{ch.name}大招动画结束")
        self.ch = ch

    def need_update_buff(self):
        return False

    def do(self, plan: ActionPlan):
        self.ch.get_hp().set_in_q_animation(False)


class ActionPlan:
    def __init__(self, characters: list[Character], monster: Monster):
        """
        * characters: 队伍角色列表
        
        注：会自动处理队伍元素共鸣，但双岩例外，因为有双岩不一定有盾，减了岩抗时，输出位不定是岩C，比如计算娜维娅队里的香菱或夜兰的输出

        如果需要添加双岩共鸣 buff, 需要手动调用 add_shuang_yan_buff
        """

        self.__characters = characters if characters else []
        self.__forground_character: Character = None
        self.__monster = monster if monster else Monster()
        self.__buff_manager = BuffManager()
        self.events = Events()

        self.__total_raw_damage = 0
        self.__total_expect_damage = 0
        self.__total_crit_damage = 0

        self.__current_index = 0
        self.__current_action_time = 0
        self.__action_array: list[Action] = []
        self.__time_line = []

    def __process_characters(self, reset=False):
        huo_num = 0
        shui_num = 0
        cao_num = 0
        bing_num = 0

        for ch in self.__characters:
            if ch.elem_type is Ys_Elem_Type.HUO:
                huo_num += 1
            elif ch.elem_type is Ys_Elem_Type.SHUI:
                shui_num += 1
            elif ch.elem_type is Ys_Elem_Type.CAO:
                cao_num += 1
            elif ch.elem_type is Ys_Elem_Type.BING:
                bing_num += 1

            weapon = ch.get_weapon()
            if reset:
                ch.reset_attrs()
                if weapon:
                    weapon.reset(self)
            else:
                if weapon:
                    weapon.apply_dynamic_attr(ch, self)


        if huo_num >= 2:
            for t in self.__characters:
                if reset:
                    t.sub_atk_per(0.25)
                else:
                    t.add_atk_per(0.25)

        if shui_num >= 2:
            for t in self.__characters:
                if reset:
                    t.get_hp().modify_max_hp_per(-0.25)
                else:
                    t.get_hp().modify_max_hp_per(0.25)

        if cao_num >= 2:
            em = 50 + 30 + 20
            for t in self.__characters:
                if reset:
                    t.sub_elem_mastery(em)
                else:
                    t.add_elem_mastery()

        if bing_num >= 2:
            for t in self.__characters:
                if reset:
                    t.sub_crit_rate(0.15)
                else:
                    t.add_crit_rate(0.15)

    def __init_characters(self):
        self.__process_characters()

    def __reset_characters(self):
        self.__process_characters(reset=True)

    def add_shuang_yan_buff(self):
        # 假设盾是常驻的
        for t in self.__characters:
            t.add_all_bonus(0.15)
        # 造成伤害使岩元素抗性下降20%，持续15秒，时间很长，加上可能的结晶盾，因此这里我们假设减抗是常驻的
        # 假设的前提：15秒内会攻击一次刷新时间、盾如果破碎的话，15秒内会重新开盾(主动开盾或捡结晶盾)
        self.__monster.add_jian_kang(0.2)

    def prepare(self):
        self.__buff_manager.init(self)
        self.__init_characters()
        
    def finish(self):
        self.__monster.buff_attrs.reset()
        self.__reset_characters()
        self.__buff_manager.reset()

    def __enter__(self):
        self.prepare()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.finish()

    @property
    def characters(self):
        return self.__characters

    def get_character_by_name(self, name) -> Character:
        for t in self.__characters:
            if t.name == name:
                return  t
            
    def get_character_by_position(self, pos) -> Character:
        if pos > len(self.__characters):
            return None
        
        return self.__characters[pos]
            
    def get_p1(self):
        return self.get_character_by_position(0)
    
    def get_p2(self):
        return self.get_character_by_position(1)
    
    def get_p3(self):
        return self.get_character_by_position(2)
    
    def get_p4(self):
        return self.get_character_by_position(3)
    
    def get_teammates(self, ch):
        return [c for c in self.__characters if c is not ch]
            
    @property
    def forground_character(self):
        return self.__forground_character

    @property
    def backgroud_characters(self):
        return [c for c in self.__characters if c is not self.__forground_character]

    @property
    def monster(self):
        return self.__monster

    @property
    def current_action_time(self):
        return self.__current_action_time

    ##################################################

    def add_buff(self, buff: Buff, update=False):
        self.__buff_manager.add_buff(buff, self.__current_action_time)
        if update:
            self.__buff_manager.update(self, self.__current_action_time)

    def update_buff(self):
        self.__buff_manager.update(self, self.__current_action_time)

    def get_effective_delay(self):
        # 生效延迟
        # return random.uniform(0.05, 0.15)
        return 0.05 + random.random() / 10
    
    def get_small_delay(self):
        """
        time range: [0, 0.05]
        """
        return random.random() / 20

    def random_choice_2(self, n1, n2):
        r = random.random()
        if r < 0.5:
            return n1
        else:
            return n2

    def random_choice_3(self, n1, n2, n3):
        r = random.random()
        if r < 0.33:
            return n1
        elif r < 0.66:
            return n2
        else:
            return n3

    def add_damage(self, damage, ch: Character, raw_damage_only=False):
        damage = self.monster.attacked(damage)

        expect_damage = 0
        crit_damage = 0
        if not raw_damage_only:
            cd = ch.get_crit_damage()
            expect_damage = ys_expect_damage(damage, ch.get_crit_rate(), cd)
            crit_damage = ys_crit_damage(damage, cd)
            damage = int(damage)

            self.__total_expect_damage += expect_damage
            self.__total_crit_damage += crit_damage
            
        self.__total_raw_damage += damage
        
        return (damage, crit_damage, expect_damage)
    
    @property
    def total_raw_damage(self):
        return self.__total_raw_damage
    
    @property
    def total_expect_damage(self):
        return self.__total_expect_damage
    
    @property
    def total_crit_damage(self):
        return self.__total_crit_damage

    def switch_character(self, ch: Character):
        if self.__forground_character:
            if ch is self.__forground_character:
                return

        prev_fore = self.__forground_character
        ch.switch_to_foreground(self.__current_action_time)
        self.__forground_character = ch

        if prev_fore:
            prev_fore.switch_to_background(self.__current_action_time)

    def add_switch_action(self, ch: Character, t):
        action = SwitchAction(ch, t)
        self.add_action(action)

    def add_consume_hp_callback(self, callback):
        self.events.on_consume_hp += callback

    def remove_consume_hp_callback(self, callback):
        self.events.on_consume_hp -= callback

    def call_consume_hp_callback(self, source: Character, targets_with_data: list[Character_HP_Change_Data]):
        if hasattr(self.events, "on_consume_hp"):
            self.events.on_consume_hp(self, source, targets_with_data)

    def add_regenerate_hp_callback(self, callback):
        self.events.on_regenerate_hp += callback

    def remove_regenerate_hp_callback(self, callback):
        self.events.on_regenerate_hp -= callback

    def call_regenerate_hp_callback(self, source: Character, targets_with_data: list[Character_HP_Change_Data]):
        if hasattr(self.events, "on_regenerate_hp"):
            self.events.on_regenerate_hp(self, source, targets_with_data)

    def add_over_healed_callback(self, callback):
        self.events.on_over_healed += callback

    def remove_over_healed_callback(self, callback):
        self.events.on_over_healed -= callback

    def call_over_healed_callback(self, source: Character, targets_with_data: list[Character_HP_Change_Data]):
        if hasattr(self.events, "on_over_healed"):
            self.events.on_over_healed(self, source, targets_with_data)

    def modify_cur_hp(self, targets: list[Character]=None, hp=0, hp_per=0, source=None):
        if not targets:
            targets = self.__characters

        hp_changed_targets: list[Character_HP_Change_Data] = []
        over_healed_targets: list[Character_HP_Change_Data] = []

        healing_bonus = 0
        source_ch = source
        if source:
            if isinstance(source, Character):
                healing_bonus = source.get_healing_bonus()
            else:
                source_ch = self.get_character_by_name(source)
                healing_bonus = source_ch.get_healing_bonus()

        for c in targets:
            if hp > 0:
                change_data = c.regenerate_hp(hp, healing_bonus)
            elif hp < 0:
                change_data = c.consume_hp(hp)

            if hp_per > 0:
                change_data = c.regenerate_hp_per(hp_per, healing_bonus)
            elif hp_per < 0:
                change_data = c.consume_hp_per(hp_per)

            if change_data.has_changed():
                hp_changed_targets.append(change_data)

            if change_data.is_over_healed():
                over_healed_targets.append(change_data)

        if hp_changed_targets:
            self.debug("当前生命值变化的角色: %s", ",".join(
                [c.character.name for c in hp_changed_targets]))
            
            if hp < 0 or hp_per < 0:
                self.call_consume_hp_callback(source=source_ch, targets_with_data=hp_changed_targets)
            else:
                self.call_regenerate_hp_callback(source=source_ch, targets_with_data=hp_changed_targets)

        if over_healed_targets:
            self.debug("治疗溢出的角色: %s", ",".join(
                [c.character.name for c in over_healed_targets]))
            self.call_over_healed_callback(source_ch, over_healed_targets)

        return (source_ch, hp_changed_targets, over_healed_targets)

    regenerate_hp = modify_cur_hp

    def __debug(self, fmt_str, *args, **kwargs):
        fmt_str = str(round(self.current_action_time, 3)) + ": " + fmt_str
        logging.debug(fmt_str, *args, **kwargs)

    def debug(self, fmt_str, *args, **kwargs):
        pass
        # self.__debug(fmt_str, *args, **kwargs)

    def q_animation_start(self, ch: Character, t):
        self.add_actioin(Q_Animation_Start_Action(ch, t))

    def q_animation_end(self, ch: Character, t):
        self.add_action(Q_Animation_End_Action(ch, t))

    def __add_action_to_array(self, action):
        action_idx = len(self.__action_array)
        action.set_idx(action_idx)
        self.__action_array.append(action)

    def add_action(self, action: Action):
        self.__add_action_to_array(action)
        self.__time_line.extend(action.get_timeline_nodes())

    def insert_timeline_node_runtime(self, insert_position, node):
        timeline_len = len(self.__time_line)
        
        while insert_position < timeline_len:
            if self.__time_line[insert_position][0] > node[0]:
                self.__time_line.insert(insert_position, node)
                return insert_position + 1
            insert_position += 1

        # 此时 timelineidx == timeline_len
        self.__time_line.append(node)

        return insert_position + 1
    
    def insert_timeline_node_after_cur_idx(self, node):
        return self.insert_timeline_node_runtime(self.__current_index + 1, node)

    def insert_action_runtime(self, action: Action):
        if action.start_time < self.__current_action_time:
            raise Exception(f"Error: insert action {action.name} @{action.start_time} before current time {self.__current_action_time}")
        self.__add_action_to_array(action)

        timeline_nodes = action.get_timeline_nodes()
        insert_position =  self.__current_index + 1
        for node in timeline_nodes:
            insert_position = self.insert_timeline_node_runtime(insert_position, node)

    def run(self):
        self.__time_line.sort(key=lambda a: a[0])

        self.__current_index = 0
        while self.__current_index < len(self.__time_line):
            action_idx = self.__time_line[self.__current_index][1]
            action = self.__action_array[action_idx]
            if action is not None:
                cur_time = self.__time_line[self.__current_index][0]
                self.__current_action_time = cur_time
                if action.need_update_buff():
                    self.__buff_manager.update(self, cur_time)
                print(f"do action {action.name}")
                finished = action.do(self)
                if finished:
                    self.__action_array[action_idx] = None
            
            self.__current_index += 1
