# 原神圣遗物工具

用于从所有圣遗物中寻找出对于某个角色来说最佳的圣遗物组合

也可用于”预强化“圣遗物，即：在真正强化圣遗物前，可以在强化前按假设的数据录入程序中，运行程序看是否会对现有圣遗物有提升，比如：如果刷到一个水杯，强化前，你可以先假设这个水杯能强化出6.6暴击，21暴伤，按这个假设录入到程序中，看是否有提升，如果没有，就可以先不强化了，免得浪费狗粮

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
* 那维莱特
* 行秋
* 九条裟罗

python版本要求：3.10及以上版本

## 开发思路

我是按以下方法开发这个工具的

* 首先，录制视频：用角色配上想要的配队找大boss或是深渊实际打几遍
* 然后，分析视频：选取较为理想的一遍，逐帧分析视频，记录下角色打出了哪些伤害，打出伤害时的状态(比如二命芙芙的血量变化，夜兰大招增伤量等等)
* 此分析的结果为基准编写程序，原神的不同的伤害计算有不同的乘区，一般我们只需要关注攻击力乘区、伤害加成乘区、夜兰胡桃芙芙的生命乘区，芙芙固有天赋的独立乘区等等，至于抗性乘区之类的都是固定的，不影响圣遗物不同组合之间的比较

## 圣遗物比较方法

程序会分别计算暴击伤害、期望伤害，然后综合这两者进行综合评分

之所以采用这种评分方式，而不是只以期望伤害为依据，是因为有时还是想稍微降点期望伤害来赌一赌大数字的

## 使用方法

* base_syw.py里是所有圣遗物列表，按照花、羽毛、沙漏、杯子、头进行了分类，你需要花点时间将你的所有圣遗物录入到这个文件里替换掉我的圣遗物
* find_gou_liang.py: 这个用于寻找可以用于作为狗粮的圣遗物，输出结果在unused_syw_list.txt里，会列出一些狗粮备选，实际要吃哪个需要自行决定
* 各个角色的输出结果在各自的txt文件里，例如ye_lan_syw.txt是夜兰圣遗物组合的输出结果，从最差到最好排序，因此需要打开这个txt后拉到文件最后面，从最好的里面选取你觉得合适的

目前还处于开发阶段，使用上不那么灵活，因为我只是用于自用开发的，无法做得非常全面，如果有clone我这些代码的朋友，需要根据你实际的角色池与配队对参数进行调整，因此要求你至少稍微懂一些python

以下面的芙宁娜部分代码片断为例

* 将ming_zuo_num修改为你的芙宁娜命座数
* 根据你的常用配队将include_extra置为True或False
* 如果和那维莱特组队，将has_na_wei_lai_te置为True
* 如果我用的不是专武，和专武相关的参数也需要删除，并添加你自已的武器的相关参数
* 如果你的夜兰不是四命，或者不和夜兰组队， 和夜兰相关的参数也需要删除

```python
ming_zuo_num = 6
include_extra = False    # 某些配队，在芙芙大招结束后还继续输出，不切芙芙出来续大，此时将include_extra置为True
has_na_wei_lai_te = False

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
