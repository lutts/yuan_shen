# 原神圣遗物工具

用于从所有圣遗物中寻找出对于某个角色来说最佳的圣遗物组合

目前支持以下角色：

* 芙宁娜
* 雷电将军
* 夜兰
* 纳西妲
* 神里绫华
* 香菱
* 胡桃
* 菲谢尔
* 艾尔海森

python版本要求：3.10及以上版本

## 使用方法

* base_syw.py里是所有圣遗物列表，按照花、羽毛、沙漏、杯子、头进行了分类，你需要花点时间将你的所有圣遗物录入到这个文件里替换掉我的圣遗物
* find_gou_liang.py: 这个用于寻找可以用于作为狗粮的圣遗物，输出结果在unused_syw_list.txt里，会列出一些狗粮备选，实际要吃哪个需要自行决定

目前还处于开发阶段，使用上不那么灵活，因为我只是用于自用开发的，无法做得非常全面，如果有clone我这些代码的朋友，需要根据你实际的角色池与配队对参数进行调整，因此要求你至少稍微懂一些python

以下面的芙宁娜部分代码片断为例

* 如果你不是满命的，q增伤倍率就不是0.0031了，十级最多为0.0025
* 如果没有二命，则需要将ming_2_hp_bonus_max设置为0
* 如果不是满命，那么only_e需要置为True
* 如果不是专武，和专武相关的参数也需要自行调整
* 等等等等，需要根据你的实际情况进行调整

```python
shui_shen_q_bonus_bei_lv = 0.0031
shui_shen_q_bonus = 400 * shui_shen_q_bonus_bei_lv
fu_ning_na_Max_Hp = 15307.0
ming_2_hp_bonus_max = 1.4  # 140%

def calc_score(hp, e_bonus, full_bonus, crit_rate, crit_damage):
    include_extra = False    # 带雷夜芙的时候，e技能持续时间能吃满
    only_e = False   # 芙芙没时间砍满命6刀时置为true
    e_extra_damage = 1.4  # 队友大于50%血量，e技能伤害为原来的1.4倍 （注：实测为1.542倍)

    ......
def calculate_score_callback(combine : list[ShengYiWu]):
    extra_crit_damage = {
        "专武": 0.882
    }

    common_elem_bonus = {
        "万叶": 0.4,
        "夜兰平均增伤": 0.25,
        "芙芙Q增伤": shui_shen_q_bonus,
    }

    extra_e_bonus = {
        "固有天赋2": 0.28,# 基本是能吃满的，操作得当，生命基本能保持在50%以上
        "专武": 0.08 * 3,

    }

    extra_hp_bonus = {
        "专武叠满两层": 0.28,
        "双水": 0.25,
        "夜兰四命保底两个e": 0.2,
    }
```

