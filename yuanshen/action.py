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
from .attribute_hub import ActionPlanAttributeSupplier, AttributeHub
from .monster import Monster
from .character import Character, Character_HP_Change_Data
from .events import Events


ActionPlan = typing.NewType("ActionPlan", None)


class ActionTimestampException(Exception):
    """ Action time already setted """


class Action:
    enable_debug = False
    enable_record = False

    def __init__(self, name):
        self.name = name
        # timestamp是动态计算出来的，这里只是放一个占位符
        self.__timestamp = 0

    def set_timestamp(self, t):
        # 时间戳只允许设置一次，这样做是为了防止将同一个action实例插入到 action_list 多次
        if self.__timestamp:
            raise ActionTimestampException(
                "Action timestamp already setted, can not change")

        self.__timestamp = t

    def get_timestamp(self):
        return self.__timestamp
    
    def __debug(self, fmt_str, *args, **kwargs):
        fmt_str = str(round(self.__timestamp, 3)) + ": " + fmt_str
        logging.debug(fmt_str, *args, **kwargs)
    
    def debug(self, fmt_str, *args, **kwargs):
        pass
        # self.__debug(fmt_str, *args, **kwargs)

    def do(self, plan: ActionPlan):
        return self.do_impl(plan)

    def do_impl(self, plan: ActionPlan):
        """
        * plan: 此Action所在的ActionPlan的实例
        """
        pass


class SwitchAction(Action):
    def __init__(self, ch: Character):
        super().__init__(f"切换到{ch.name}")
        self.ch = ch

    def do_impl(self, plan: ActionPlan):
        self.debug(self.name)
        plan.switch_ch_to_forground(self.ch)


class Q_Animation_Start_Action(Action):
    def __init__(self, ch: Character):
        super().__init__(f"{ch.name}大招动画开始")
        self.ch = ch

    def do_impl(self, plan: ActionPlan):
        self.debug(self.name)
        self.ch.get_hp().set_in_q_animation(True)


class Q_Animation_End_Action(Action):
    def __init__(self, ch: Character):
        super().__init__(f"{ch.name}大招动画结束")
        self.ch = ch

    def do_impl(self, plan: ActionPlan):
        self.debug(self.name)
        self.ch.get_hp().set_in_q_animation(False)


class AttributeAction(Action, ActionPlanAttributeSupplier):
    def do_impl(self, plan: ActionPlan):
        plan.add_extra_attr(self)


class ActionPlan:
    def __init__(self, characters: list[Character], monster: Monster):
        """
        注：会自动处理队伍元素共鸣，但双岩例外，因为有双岩不一定有盾，减了岩抗时，输出位不定是岩C，比如计算娜维娅队里的香菱或夜兰的输出

        如果需要添加双岩共鸣 buff, 需要手动调用 add_shuang_yan_buff
        """

        self.__characters = characters if characters else []
        self.__pre_process_characters()

        self.__forground_character: Character = None
        self.__monster = monster

        self.__current_index = 0
        self.__current_action_time = 0
        self.action_list: list[Action] = []

        self.__attribute_hub = AttributeHub(self)
        
        self.events = Events()

        self.__total_raw_damage = 0
        self.__total_expect_damage = 0
        self.__total_crit_damage = 0

    def __pre_process_characters(self):
        num_chs = len(self.__characters)
        if num_chs <= 1:
            return
        
        huo_num = 0
        shui_num = 0
        cao_num = 0
        bing_num = 0

        for i in range(0, num_chs):
            ch = self.__characters[i]
            if ch.elem_type is Ys_Elem_Type.HUO:
                huo_num += 1
            elif ch.elem_type is Ys_Elem_Type.SHUI:
                shui_num += 1
            elif ch.elem_type is Ys_Elem_Type.CAO:
                cao_num += 1
            elif ch.elem_type is Ys_Elem_Type.BING:
                bing_num += 1

            ch.set_teammates(self.__characters[:i] + self.__characters[i+1:])

        if huo_num >= 2:
            for t in self.__characters:
                t.add_atk_per(0.25)

        if shui_num >= 2:
            for t in self.__characters:
                t.get_hp().modify_max_hp_per(0.25)

        if cao_num >= 2:
            for t in self.__characters:
                t.add_elem_mastery(50 + 30 + 20)

        if bing_num >= 2:
            for t in self.__characters:
                t.add_crit_rate(0.15)

    def add_shuang_yan_buff(self):
        # 假设盾是常驻的
        for t in self.__characters:
            t.add_all_bonus(0.15)
        # 造成伤害使岩元素抗性下降20%，持续15秒，时间很长，加上可能的结晶盾，因此这里我们假设减抗是常驻的
        # 假设的前提：15秒内会攻击一次刷新时间、盾如果破碎的话，15秒内会重新开盾(主动开盾或捡结晶盾)
        self.__monster.add_jian_kang(0.2)

    def prepare(self):
        self.__set_attribute_hub()

    def finalize(self):
        self.__unset_attribute_hub()

    def __enter__(self):
        self.prepare()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.finalize()

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
            
    def get_foreground_character(self) -> Character:
        return self.__forground_character

    @property
    def monster(self):
        return self.__monster
    
    @staticmethod
    def get_effective_delay():
        """
        可能是由于网络通信原因, 原神中有些效果是有延迟的
        """
        return random.randint(66, 117) / 1000

    def get_current_action_time(self):
        return self.__current_action_time
    
    def __set_attribute_hub(self):
        self.__monster.set_attribute_hub(self.__attribute_hub)
        for t in self.__characters:
            t.set_attribute_hub(self.__attribute_hub)

    def __unset_attribute_hub(self):
        self.__monster.unset_attribute_hub()
        for t in self.__characters:
            t.unset_attribute_hub()

    def add_extra_attr(self, attr: ActionPlanAttributeSupplier):
        self.__attribute_hub.add_extra_attr(attr)

    def remove_extra_attr(self, attr: ActionPlanAttributeSupplier):
        self.__attribute_hub.remove_extra_attr(attr)
        if not self.__attribute_hub.has_extra_attr():
            self.__unset_attribute_hub()

    ##################################################

    def add_damage(self, damage, ch: Character):
        damage = self.monster.attacked(damage)
        cd = ch.get_crit_damage()
        expect_damage = ys_expect_damage(damage, ch.get_crit_rate(), cd)
        crit_damage = ys_crit_damage(damage, cd)
        damage = int(damage)

        self.__total_raw_damage += damage
        self.__total_expect_damage += expect_damage
        self.__total_crit_damage += crit_damage

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

    def switch_ch_to_forground(self, ch: Character):
        if self.__forground_character:
            if ch is self.__forground_character:
                return

        prev_fore = self.__forground_character
        ch.switch_to_foreground(self.__current_action_time)
        self.__forground_character = ch

        if prev_fore:
            prev_fore.switch_to_background(self.__current_action_time)

    def add_switch_action(self, ch: Character, t):
        action = SwitchAction(ch)
        action.set_timestamp(t)
        self.action_list.append(action)

    def switch_to_forground(self, character_name: str):
        if self.__forground_character:
            if self.__forground_character.name == character_name:
                return
            
        ch = self.get_character_by_name(character_name)
        self.switch_ch_to_forground(ch)

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

            # self.debug(str(change_data))
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
        fmt_str = str(round(self.get_current_action_time(), 3)) + ": " + fmt_str
        logging.debug(fmt_str, *args, **kwargs)

    def debug(self, fmt_str, *args, **kwargs):
        pass
        # self.__debug(fmt_str, *args, **kwargs)

    def q_animation_start(self, ch: Character, t):
        action = Q_Animation_Start_Action(ch)
        action.set_timestamp(t)
        self.action_list.append(action)

    def q_animation_end(self, ch: Character, t):
        action = Q_Animation_End_Action(ch)
        action.set_timestamp(t)
        self.action_list.append(action)

    def sort_action(self):
        self.action_list.sort(key=lambda a: a.get_timestamp())

    def append_action(self, action):
        self.action_list.append(action)

    def add_action(self, action:Action, min_t, max_t = None, base_action: Action = None, effective_delay=0) -> Action:
        base_time = 0 if base_action is None else base_action.get_timestamp()

        if not max_t:
            t = base_time + min_t
        else:
            t = base_time + random.randint(round(min_t * 1000), round(max_t * 1000)) / 1000
        action.set_timestamp(t + effective_delay)

        self.action_list.append(action)

        return action
            
    def insert_action(self, action, re_sort=False):
        self.action_list.append(action)
        if re_sort:
            self.sort_action()
            
    def insert_action_runtime(self, action):
        if action.get_timestamp() < self.__current_action_time:
            raise Exception("action timestamp small than current action time")
        
        idx = self.__current_index
        lst_len = len(self.action_list)
        
        while idx < lst_len:
            if self.action_list[idx].get_timestamp() > action.get_timestamp():
                self.action_list.insert(idx, action)
                return
            idx += 1
            
        self.action_list.append(action)

    def run(self):
        self.sort_action()

        self.__current_index = 0
        while self.__current_index < len(self.action_list):
            action = self.action_list[self.__current_index]
            self.__current_action_time = action.get_timestamp()
            action.do(self)

            self.__current_index += 1
