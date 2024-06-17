#!/user/bin/env python3 -c
# -*- coding: utf-8 -*-
"""
Module documentation.
"""

from enum import Flag, auto


class BuffAttrs(Flag):
    CRIT_RATE = auto()
    CRIT_DAMAGE = auto()
    ATK_PER = auto()
    ATK = auto()
    DEF_PER = auto()
    DEF_V = auto()
    ELEM_MASTERY = auto()
    HEALING_BONUS = auto()
    INCOMING_HEALING_BONUS = auto()
    ENERGY_RECHARGE = auto()

    ELEM_BONUS = auto()
    NORMAL_A_BONUS = auto()
    CHARGED_A_BONUS = auto()
    PLUNGING_BONUS = auto()
    E_BONUS = auto()
    Q_BONUS = auto()

    HP_PER = auto()
    HP = auto()

    JIAN_KANG = auto()
    JIAN_FANG = auto()
    IGNORE_FANG = auto()


class Buff:
    def __init_subclass__(cls, max_layer=0, co_exist=False, re_convertable=True, 
                          attrs: BuffAttrs = None, depend_attrs: BuffAttrs = None) -> None:
        """
        * max_layer: 最大允许叠层, 0 表示不允许重复存在(即: 后来的 buff_type 相同的会覆盖旧的), 默认不可重复存在(0)

            * 注：如果 creator 不同，则还需要根据 co_exist 来判断是否允许重复存在

        * co_exist: 不同 creator 的相同 buff_type 是否允许同时存在（即：效果是否可叠加）, True 表示可叠加, False 表示不可叠加，
        仅在 creator 不为 None 时有效。默认不可叠加(False)

        * re_convertable: buff 提供的属性是否可以被二次转化，默认为可被二次转化(True), 不能二次转化的 buff 只能用于技能结算，不能被其他 buff 二次利用
        * attrs: buff 所提供的属性
        * depend_attrs:  buff 依赖的属性
        """
        super().__init_subclass__()

        cls.max_layer = max_layer
        cls.co_exist = co_exist
        cls.attrs_reusable = re_convertable
        if not attrs:
            raise Exception("Buff attrs must be specified")
        cls.attrs = attrs
        cls.depend_attrs = depend_attrs
        

    def __init__(self, start_time: float, end_time: float = None, creator=None):
        """
        start_time: buff 开始时间

        end_time: None表示永久

        creator: buff 施加者，可能是某个 Character, 也可能是某件武器，也可能是圣遗物效果
        """

        self.start_time = start_time
        self.end_time = end_time
        self.cur_layer = 1
        self.creator = creator

    def inc_layer(self, new_buff):
        if self.cur_layer < self.max_layer:
            self.cur_layer += 1

    def update(self, buff_manager):
        pass


class BuffManager:
    def __init__(self):
        self.plan = None
        self.__buff_lst: list[Buff] = None

    def init(self, plan):
        self.plan = plan
        self.__buff_lst: list[Buff] = []

    def reset(self):
        self.plan = None
        self.__buff_lst = None

    def update(self, cur_time):
        for ch in self.plan.characters:
            ch.reset_buff_attrs()
        self.plan.monster.buff_attrs.reset()

        in_effect_buff = []

        for buff in self.__buff_lst:
            if buff.end_time is not None and buff.end_time > cur_time:
                buff.on_finish(self)
            else:
                in_effect_buff.append(buff)
                if cur_time >= buff.start_time:
                    buff.update(self)

        self.__buff_lst = in_effect_buff

    def __add_buff(self, new_buff: Buff):
        if not new_buff.attrs_reusable:
            # 不可二次转化的直接放在后面
            self.__buff_lst.append(new_buff)
        else:
            #（注：即便时用旧的方案，从 Character 拿属性的时候，也要考虑是否 re_convertable）
            # 设 new_buff 为 A，现有 buff_lst 为 B <- C，D，E，其中：C 依赖 B，D 和 B毫无关系，E是不可转化的
            # 假设 B 依赖 A，则 A 应该插入到 B 前面，即 A <- B <- C, D, E
            # 如果 A 依赖 C，就形成依赖循环，这时应该如何处理？(TODO)
            # 如果 A 依赖 D，则 D 应该在 B 前面，这相当于 B 通过 A “间接”依赖了 D
            # 这涉及到一个问题，B 和 D 毫无关系，D应该放在哪？
            #  如果 D 放在 B 后面，就会出现上面所说的情形，某个时候可能要将 D 挪到 B 前面
            #  如果 D 放在 B 前面，如果某个时候插入了一个 ”依赖 B，被 D依赖的”，我们又得将 D 挪到 B 的后面，这相当于 D 通过 A ”间接“依赖了 B 
            # 所以，一开始两个互不依赖的，以后可能能过新 buff 间接地产生依赖关系
            # 我们是否将 buff_lst 拆成两个或三个：1) 彼此有依赖关系的(coupling_lst)，2) 不依赖别人也不被别人依赖的(independent_lst); 3) 不可二次转化的(un_reusable_lst)
            # 或者用 树形结构？其实有可能会是网状结构
            #   * 根节点放置 1)不依赖别的 buff；2) 和其他 buff 毫无关系的；3) 不可二次转化的
            #   * 如果依赖别的 buff，则挂到那个 buff 的 child 下，并且从根节点的 child 移除
            # 接下来就涉及 update 时的遍历顺序问题了，如果广度优先，则： A <- C, D <- B <- C, ，如果是按 A-> D -> C -> B 执行的话，顺序就错了，如何解决？
            # 也许我们还需要记录 level 值，C 的 level 值是 3，所以不会在遍历完 level_1 的 A 和 D 后被遍历，最终结果：A -> D -> B -> C
            # C 在加入 B的 childs 时，因为 B 的 level 为 2，所以 C 的 level 为 3
            # 接下来是解决删除的问题了：删除一个 buff，将使得依赖他的所有 buff (childs)都会被重新评估---以便挂载到合适的 buff 或 root 下
            # 还要解决一个问题: A <- C，此时插入 B, 依赖 A, 且被 C 依赖, 理论上会形成 A <- B <- C，但 A <- C 的“链路”还在，如何解除？
            #   -》不需要解除，因为 C 的 level 为 2 了，肯定在 B 之后才会执行
            # 还有其他问题：纳西妲开大的时候，要从队友中找出精通值最大的来决定转化多少精通，即 attrs = 精通，depend_attrs = 精通
            #   -》 这其实涉及到另一个问题：re_convertable 的 buff 何时将他们的值加到角色身上？ 如果有另一个 re_convertable 的 buff 提供了精通属性，如何确保它在纳西妲大招 Buff 结算完才结算呢？
            #       -》处理 re_convertable 为 True 的 buff 时，属性值会直接写入到 Character
            #       -》处理 re_convertable 为 False 的 Buff 时，属性值不会直接写入到 Character，而是缓存在 BuffManager 里，所有 un-re_convertable 的都处理完后，才统一写入到 Character
            # 算法：1) 一层(level)一层处理，如果遇到了 un-re_convertable 的，先按遇到的顺序缓存起来，2) 处理 un-re_convertable 的，先写入 BuffManager 缓存，最后统一写入 Character 
            # 在这种树形结构中，如何将一个 buff 替换成另一个 buff ?
            # class BuffNode:
            #   level: int
            #   childs: list[BuffNode]
            #   buff: Buff
            for idx in range(0, len(self.__buff_lst)):
                buff = self.__buff_lst[idx]
                if new_buff.depend_attrs & buff.attrs:
                    pass # 需要往后加
                elif new_buff and (new_buff.attrs & buff.depend_attrs):
                    break 


    def add_buff(self, new_buff: Buff):
        same_type_buff_lst: list[Buff] = []
        for b in self.__buff_lst:
            if type(b) is type(new_buff):
                same_type_buff_lst.append(b)

        if same_type_buff_lst:
            if new_buff.max_layer == 0:  # 不允许叠层
                if new_buff.co_exist:
                    # 不可重复，但不同 creator 允许同时存在
                    # 那么只需要替换掉 creator 相同的那个 old buff 即可
                    for old_buff in same_type_buff_lst:
                        if old_buff.creator is new_buff.creator:
                            self.__buff_lst.remove(old_buff)
                            self.__buff_lst.append(new_buff)
                            return

                    # 没有 creator 相同的，作为新 buff 添加到列表
                    self.__buff_lst.append(new_buff)
                else:
                    # 不可重复，而且不论 creator 是否相同都不可重复
                    assert len(same_type_buff_lst) == 1
                    old_buff = same_type_buff_lst[0]
                    self.__buff_lst.remove(old_buff)
                    self.__buff_lst.append(new_buff)
            else:   # 允许叠层
                if new_buff.co_exist:
                    # 允许叠层，并且不同 creator 是分别叠层的
                    # 找出 creator 相同的 old_buff，叠层加一
                    for old_buff in same_type_buff_lst:
                        if old_buff.creator is new_buff.creator:
                            old_buff.inc_layer(new_buff)
                            return

                    # 没有 creator 相同的，作为新 buff 添加到列表
                    self.__buff_lst.append(new_buff)
                else:
                    # 允许叠层，但不同 creator 不允许共存
                    # 这意味着，只在 creator 相同时叠层，否则如果 creator 不同，new_buff 将替换掉 old_buff
                    assert len(same_type_buff_lst) == 1
                    old_buff = same_type_buff_lst[0]
                    if old_buff.creator is new_buff.creator:
                        old_buff.inc_layer(new_buff)
                    else:
                        self.__buff_lst.remove(old_buff)
                        self.__buff_lst.append(new_buff)
        else:
            self.__buff_lst.append(new_buff)

    def remove_buff(self, buff: Buff):
        self.__buff_lst.remove(buff)

    @property
    def buff_lst(self):
        """
        for test only!
        """
        return self.__buff_lst

    def get_crit_rate(self, ch, include_un_reusable=True):
        return sum([buff.get_crit_rate(self.plan, ch) for buff in self.__buff_lst])

    def get_crit_damage(self, ch, include_un_reusable=True):
        return sum([buff.get_crit_damage(self.plan, ch) for buff in self.__buff_lst])

    def get_max_hp(self, ch, include_un_reusable=True):
        extra_hp_per = sum([buff.get_hp_percent(self.plan, ch)
                           for buff in self.__buff_lst])
        extra_hp = sum([buff.get_hp(self.plan, ch)
                       for buff in self.__buff_lst])

        return extra_hp + ch.get_hp().get_base_hp() * extra_hp_per

    def get_atk(self, ch, include_un_reusable=True):
        extra_atk_per = sum([buff.get_atk_per(self.plan, ch)
                            for buff in self.__buff_lst])
        extra_atk = sum([buff.get_atk(self.plan, ch)
                        for buff in self.__buff_lst])

        return extra_atk + ch.get_base_atk() * extra_atk_per

    def get_defence(self, ch, include_un_reusable=True):
        extra_def_per = sum([buff.get_def_per(self.plan, ch)
                            for buff in self.__buff_lst])
        extra_def = sum([buff.get_def(self.plan, ch)
                        for buff in self.__buff_lst])

        return extra_def + ch.get_base_defence() * extra_def_per

    def get_elem_mastery(self, ch, include_un_reusable=True):
        return sum([buff.get_elem_mastery(self.plan, ch) for buff in self.__buff_lst])

    def get_healing_bonus(self, ch, include_un_reusable=True):
        return sum([buff.get_healing_bonus(self.plan, ch) for buff in self.__buff_lst])

    def get_incoming_healing_bonus(self, ch, include_un_reusable=True):
        return sum([buff.get_incoming_healing_bonus(self, ch) for buff in self.__buff_lst])

    def get_energy_recharge(self, ch, include_un_reusable=True):
        return sum([buff.get_energy_recharge(self.plan, ch) * 100 for buff in self.__buff_lst])

    def get_normal_a_bonus(self, ch, include_un_reusable=True):
        return sum([buff.get_elem_bonus(self.plan, ch) + buff.get_normal_a_bonus(self.plan, ch) for buff in self.__buff_lst])

    def get_charged_a_bonus(self, ch, include_un_reusable=True):
        return sum([buff.get_elem_bonus(self.plan, ch) + buff.get_charged_a_bonus(self.plan, ch) for buff in self.__buff_lst])

    def get_plunging_bonus(self, ch, include_un_reusable=True):
        return sum([buff.get_elem_bonus(self.plan, ch) + buff.get_plunging_bonus(self.plan, ch) for buff in self.__buff_lst])

    def get_e_bonus(self, ch, include_un_reusable=True):
        return sum([buff.get_elem_bonus(self.plan, ch) + buff.get_e_bonus(self.plan, ch) for buff in self.__buff_lst])

    def get_q_bonus(self, ch, include_un_reusable=True):
        return sum([buff.get_elem_bonus(self.plan, ch) + buff.get_q_bonus(self.plan, ch) for buff in self.__buff_lst])

    def get_jian_kang(self, include_un_reusable=True):
        return sum([buff.get_jian_kang(self.plan) for buff in self.__buff_lst])

    def get_jian_fang(self, include_un_reusable=True):
        return sum([buff.get_jian_fang(self.plan) for buff in self.__buff_lst])

    def get_ignore_fang(self, include_un_reusable=True):
        return sum([buff.get_ignore_fang(self.plan) for buff in self.__buff_lst])


def _do_test():
    class Creator1:
        pass

    class Creator2:
        pass

    class Buff_Lay_0_Co_f(Buff, attrs="test"):
        pass

    class Buff_Lay_0_Co_t(Buff, co_exist=True, attrs="test"):
        pass

    class Buff_Lay_2_Co_f(Buff, max_layer=2, attrs="test"):
        pass

    class Buff_Lay_2_Co_t(Buff, max_layer=2, co_exist=True, attrs="test"):
        pass

    def is_same_lst(l1, l2):
        if len(l1) != len(l2):
            return False

        for b in l1:
            if b not in l2:
                return False

        return True

    creator1 = Creator1()
    creator2 = Creator2()

    buff_manager = BuffManager()
    buff_manager.init(None)
    buff_manager.add_buff(Buff_Lay_0_Co_f(0, creator=creator1))
    new_buff = Buff_Lay_0_Co_f(0, creator2)
    buff_manager.add_buff(new_buff)
    assert is_same_lst(buff_manager.buff_lst, [new_buff])

    buff_manager = BuffManager()
    buff_manager.init(None)
    buff_manager.add_buff(Buff_Lay_0_Co_f(0, creator=creator1))
    new_buff = Buff_Lay_0_Co_f(0, creator1)
    buff_manager.add_buff(new_buff)
    assert is_same_lst(buff_manager.buff_lst, [new_buff])

    buff_manager = BuffManager()
    buff_manager.init(None)
    buff1 = Buff_Lay_0_Co_t(0, creator=creator1)
    buff2 = Buff_Lay_0_Co_t(0, creator=creator2)
    buff_manager.add_buff(buff1)
    buff_manager.add_buff(buff2)
    assert is_same_lst(buff_manager.buff_lst, [buff1, buff2])

    buff_manager = BuffManager()
    buff_manager.init(None)
    buff1 = Buff_Lay_0_Co_t(0, creator=creator1)
    buff2 = Buff_Lay_0_Co_t(0, creator=creator1)
    buff_manager.add_buff(buff1)
    buff_manager.add_buff(buff2)
    assert is_same_lst(buff_manager.buff_lst, [buff2])

    buff_manager = BuffManager()
    buff_manager.init(None)
    buff1 = Buff_Lay_2_Co_f(0, creator=creator1)
    buff2 = Buff_Lay_2_Co_f(0, creator=creator1)
    buff_manager.add_buff(buff1)
    buff_manager.add_buff(buff2)
    assert is_same_lst(buff_manager.buff_lst, [buff1])
    assert buff1.cur_layer == 2

    buff_manager = BuffManager()
    buff_manager.init(None)
    buff1 = Buff_Lay_2_Co_f(0, creator=creator1)
    buff2 = Buff_Lay_2_Co_f(0, creator=creator2)
    buff_manager.add_buff(buff1)
    buff_manager.add_buff(buff2)
    assert is_same_lst(buff_manager.buff_lst, [buff2])
    assert buff2.cur_layer == 1

    buff_manager = BuffManager()
    buff_manager.init(None)
    buff1 = Buff_Lay_2_Co_t(0, creator=creator1)
    buff2 = Buff_Lay_2_Co_t(0, creator=creator1)
    buff_manager.add_buff(buff1)
    buff_manager.add_buff(buff2)
    assert is_same_lst(buff_manager.buff_lst, [buff1])
    assert buff1.cur_layer == 2

    buff_manager = BuffManager()
    buff_manager.init(None)
    buff1 = Buff_Lay_2_Co_t(0, creator=creator1)
    buff2 = Buff_Lay_2_Co_t(0, creator=creator2)
    buff_manager.add_buff(buff1)
    buff_manager.add_buff(buff2)
    assert is_same_lst(buff_manager.buff_lst, [buff1, buff2])
    assert buff1.cur_layer == 1
    assert buff2.cur_layer == 1

    buff_manager = BuffManager()
    buff_manager.init(None)
    buff1 = Buff_Lay_2_Co_t(0, creator=creator1)
    buff2 = Buff_Lay_2_Co_t(0, creator=creator2)
    buff3 = Buff_Lay_2_Co_t(0, creator=creator1)
    buff_manager.add_buff(buff1)
    buff_manager.add_buff(buff2)
    buff_manager.add_buff(buff3)
    assert is_same_lst(buff_manager.buff_lst, [buff1, buff2])
    assert buff1.cur_layer == 2
    assert buff2.cur_layer == 1


# Main body
if __name__ == '__main__':
    _do_test()
