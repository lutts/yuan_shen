## 关于伤害数字

砍怪一刀，需要服务器端确认才会出伤害数字


# 生效延迟

哪些要加生效延迟：

* 扣血/回血：这两者是客户端立即显示，但如果他们会触发一些buff，那么是需要服务器端确认的，因此要加effective delay

哪些不需要加生效延迟：

* 芙芙的武器叠层：因为我们已经在扣血/回血加生效延迟了，这里不能重复添加
* 伤害数字出来的时间点：这已经是服务器端反馈的结果了，不需要加生效延迟