#!/user/bin/env python3 -tt
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

import logging
import typing
import random
import weakref

from monster import Monster
from character import Character, Character_HP_Change_Data
from events import Events

ActionPlan = typing.NewType("ActionPlan", None)

class ActionTimestampException(Exception):
    """ Action time already setted """


class Action:
    enable_debug = False

    def __init__(self, name, owner:Character = None):
        self.name = name
        self.owner: Character = owner
        self.done = False
        # timestamp是动态计算出来的，这里只是放一个占位符
        self.__timestamp = 0

    def set_done(self):
        self.done = True

    def set_timestamp(self, t):
        # 时间戳只允许设置一次，这样做是为了防止将同一个action实例插入到 action_list
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
        if self.done:
            return None

        return self.do_impl(plan)

    def do_impl(self, plan: ActionPlan):
        """
        * plan: 此Action所在的ActionPlan的实例
        """
        pass

class ActionPlanAttributes:
    def get_crit_rate(self, plan, target_character):
        return 0
        
    def get_crit_damage(self, plan, target_character):
        return 0
        
    def get_hp_percent(self, plan, target_character):
        return 0
        
    def get_hp(self, plan, target_character):
        return 0
        
    def get_atk_per(self, plan, target_character):
        return 0
    
    def get_atk(self, plan, target_character):
        return 0
        
    def get_def_per(self, plan, target_character):
        return 0
        
    def get_def(self, plan, target_character):
        return 0
        
    def get_elem_mastery(self, plan, target_character):
        return 0
    
    def get_elem_bonus(self, plan, target_character):
        return 0
    
    def get_energy_recharge(self, plan, target_character):
        return 0
    
    def get_normal_a_bonus(self, plan, target_character):
        return 0

    def get_charged_a_bonus(self, plan, target_character):
        return 0
    
    def get_plunging_bonus(self, plan, target_character):
        return 0
    
    def get_e_bonus(self, plan, target_character):
        return 0
    
    def get_q_bonus(self, plan, target_character):
        return 0
    
    def get_jian_kang(self, plan):
        return 0
    
    def get_jian_fang(self, plan):
        return 0
    
    def get_ignore_fang(self, plan):
        return 0
        

class ActionPlan:
    def __init__(self, characters: list[Character], monster: Monster):
        self.__characters = characters
        self.__forground_character: Character = None
        self.__monster = monster

        self.__current_index = 0
        self.__current_action_time = 0
        self.action_list: list[Action] = []

        self.__extra_attrs: list[ActionPlanAttributes] = []

        self.events = Events()
        # self.__has_on_consume_hp_callback = False
        # self.__has_on_regenerate_hp_callback = False
        # self.__has_on_over_healed_callback = False

        self.__total_damage = 0

    @property
    def characters(self):
        return self.__characters

    def get_character(self, name) -> Character:
        for t in self.__characters:
            if t.name == name:
                return  t
            
    def get_foreground_character(self) -> Character:
        return self.__forground_character

    @property
    def monster(self):
        return self.__monster
    
    @property
    def total_damage(self):
        return self.__total_damage

    def get_current_action_time(self):
        return self.__current_action_time
    
    def add_extra_attr(self, attr: ActionPlanAttributes):
        if attr not in self.__extra_attrs:
            self.__extra_attrs.append(attr)

    def remove_extra_attr(self, attr: ActionPlanAttributes):
        self.__extra_attrs.remove(attr)

    def get_crit_rate(self, ch: Character):
        extra_crit_rate = sum([attr.get_crit_rate(self, ch) for attr in self.__extra_attrs])
        return ch.get_crit_rate() + extra_crit_rate
    
    def get_crit_damage(self, ch: Character):
        extra_crit_damage = sum([attr.get_crit_damage(self, ch) for attr in self.__extra_attrs])
        return ch.get_crit_damage() + extra_crit_damage
    
    def get_max_hp(self, ch: Character):
        extra_hp_per = sum([attr.get_hp_percent(self, ch) for attr in self.__extra_attrs])
        extra_hp = sum([attr.get_hp(self, ch) for attr in self.__extra_attrs])

        return ch.get_max_hp() + extra_hp + round(ch.get_hp().get_base_hp() * extra_hp_per)
    
    def get_atk(self, ch: Character):
        extra_atk_per = sum([attr.get_atk_per(self, ch) for attr in self.__extra_attrs])
        extra_atk = sum([attr.get_atk(self, ch) for attr in self.__extra_attrs])

        return ch.get_atk() + extra_atk + round(ch.get_base_atk() * extra_atk_per)
    
    def get_defence(self, ch: Character):
        extra_def_per = sum([attr.get_def_per(self, ch) for attr in self.__extra_attrs])
        extra_def = sum([attr.get_def(self, ch) for attr in self.__extra_attrs])

        return ch.get_defence() + extra_def + round(ch.get_base_defence() * extra_def_per)
    
    def get_elem_mastery(self, ch: Character):
        return ch.get_elem_mastery() + sum([attr.get_elem_mastery(self, ch) for attr in self.__extra_attrs])
    
    def get_energy_recharge(self, ch: Character):
        extra = sum([attr.get_energy_recharge(self, ch) for attr in self.__extra_attrs])
        return ch.get_energy_recharge() + extra
    
    def get_normal_a_bonus(self, ch: Character):
        extra = sum([attr.get_elem_bonus(self, ch) + attr.get_normal_a_bonus(self, ch) for attr in self.__extra_attrs])
        return ch.get_normal_a_bonus() + extra
    
    def get_charged_a_bonus(self, ch: Character):
        extra = sum([attr.get_elem_bonus(self, ch) + attr.get_charged_a_bonus(self, ch) for attr in self.__extra_attrs])
        return ch.get_charged_a_bonus() + extra
    
    def get_plunging_bonus(self, ch: Character):
        extra = sum([attr.get_elem_bonus(self, ch) + attr.get_plunging_bonus(self, ch) for attr in self.__extra_attrs])
        return ch.get_plunging_bonus() + extra
    
    def get_e_bonus(self, ch: Character):
        extra = sum([attr.get_elem_bonus(self, ch) + attr.get_e_bonus(self, ch) for attr in self.__extra_attrs])
        return ch.get_e_bonus() + extra
    
    def get_q_bonus(self, ch: Character):
        extra = sum([attr.get_elem_bonus(self, ch) + attr.get_q_bonus(self, ch) for attr in self.__extra_attrs])
        return ch.get_q_bonus() + extra
    
    def get_kang_xin_multiplier(self):
        extra_jian_kang = sum([attr.get_jian_kang(self) for attr in self.__extra_attrs])
        return self.monster.get_jian_kang_bonus(extra_jian_kang)
    
    def get_fang_yu_multiplier(self):
        extra_jian_fang = sum([attr.get_jian_fang(self) for attr in self.__extra_attrs])
        extra_ignore_def = sum([attr.get_ignore_fang(self) for attr in self.__extra_attrs])
        return self.monster.get_fang_yu_xi_shu(extra_jian_fang=extra_jian_fang, 
                                                extra_ignore_defence_ratio=extra_ignore_def)


    ##################################################

    def add_damage(self, damage):
        if self.__extra_attrs:
            real_damage = damage * self.get_kang_xin_multiplier() * self.get_fang_yu_multiplier()
        else:
            real_damage = self.monster.attacked(damage)
        #print("add damage:", round(real_damage, 3))
        self.__total_damage += real_damage
        return real_damage

    def switch_to_forground(self, character_name):
        if self.__forground_character:
            if self.__forground_character.name == character_name:
                return

        prev_fore = self.__forground_character
        ch = self.get_character(character_name)
        ch.switch_to_foreground()
        self.__forground_character = ch
        
        if prev_fore:
            prev_fore.switch_to_background()

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
                source_ch = self.get_character(source)
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

    def sort_action(self):
        self.action_list.sort(key=lambda a: a.get_timestamp())

    def add_action_obj(self, action:Action, min_t, max_t, base_action: Action = None, negative=False, effective_delay=0):
        base_time = 0 if base_action is None else base_action.get_timestamp()

        t = random.randint(round(min_t * 1000), round(max_t * 1000)) / 1000
        if negative:
            timestamp = base_time - t
        else:
            timestamp = base_time + t
        action.set_timestamp(timestamp + effective_delay)

        self.action_list.append(action)

        return action

    def add_action(self, name, cls, min_t, max_t, base_action=None, negative=False, effective_delay=0, **kwargs):
        action = cls(name, **kwargs)

        ba = None
        if base_action:
            ba = self.find_action(base_action)
            if not ba:
                raise Exception("base action " + base_action + " not found!")
            
        return self.add_action_obj(action, min_t, max_t, base_action=ba, negative=negative, effective_delay=effective_delay)

    def find_action(self, action_name) -> Action:
        for a in reversed(self.action_list):
            if a.name == action_name:
                return a
            
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

    def check_duplicate_action(self):
        action_names = [a.name for a in self.action_list]
        action_name_set = set(action_names)
        if len(action_names) != len(action_name_set):
            raise Exception("action name duplicated!")

    def run(self):
        self.sort_action()

        self.__current_index = 0
        while self.__current_index < len(self.action_list):
            action = self.action_list[self.__current_index]
            self.__current_action_time = action.get_timestamp()
            action.do(self)

            self.__current_index += 1