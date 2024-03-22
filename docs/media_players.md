目前使用过两个播放器来逐帧分析

* mpv（建议使用，逐帧定位精准）
* potplayer（缺点：因为D和F定位不准，需要配合G，操作繁琐很多）

分析文件中，早期用的是potplayer，在这个文件的时间点之后，都会使用 mpv

## mpv

* 按 . 逐帧向前的话，停下来的时间就是当前画面的真实时间
* 按 , 逐帧后退也同理
* seek命令按指定时间absolute定位时，如果是一帧开始，时间就是用户指定的时间，如果不是，则会自动圆整：+-0.005，圆整到当前帧开始，否则圆整到下一帧开始
	* 例如：00:00.083是新一帧的开始，如果 seek-to 的时候指定 00:00.083，那就是00:00.083，但如果指定的是 00:00.084，则会跳到 00:00:083
	* 如果指定的是00:00.089，则会跳到 00:00.100
	
分析mpv得到的帧时间时要注意：实际生效的点可能在 帧时间 - 0.016，只是因为视频按帧显示而推后了

### 时间间隔的计算问题

* 3.717：切芙芙，但也有可能在3.701就切出来了，只不过画面显示不出来
* 3.950：点按e，但也可能3.934就点按了，只不过画面显示不出来
* 最大的可能性是：3.950 - 3.701 = 0.249
* 最小的可能性是：3.934 - 3.717  = 0.217
* 0.249 - 0.217 - 0.032 = 2 * 0.016
* 两个原始时间点相减得到的是平均值：3.950 - 3.717 = 0.233

应该以哪个为准呢？

* 如果取最大值，很有可能把最终可能值拉大了，误差：0.032
* 如果取最小值，很有可能把最终可能值拉小了，误差：0.032
* 取平均：误差0.016

取平均值？？？两边不“得罪”？

## potplayer

* 按 F 逐帧向前的话，停下来的时间并不是当前画面的真实时间，具体是什么时间至今没有弄清楚！！！
* 按 D 逐帧后退的话，也有类似于 F 的问题
* 按 G 定位时，不会像 mpv 那样自动将时间圆整到下一帧的开始，下面详细说明

因为 F 和 D的问题，使用 potplayer 分析时，一般是长按 F 或 D 粗略定位，然后再 G 来精准定位

### 按 G 定位

比如说，00:00.083是新的一帧开始，按 G 指定不同时间的结果如下：

*  指定 00:00.083: 当前帧的画面
* 指定 00:00.084 ~ 00:00.100: 下一帧的画面，但实际上，00:00.100 才开始下一帧

这个行为会让人感觉迷惑，以为00:00.084是一帧的开始

因为 G 的这种行为方式，分析 potplayer 得到的帧时间时要注意：对于持续时间类的计算，实际的持续时间要+0.016，因为你当前看到的画面可能是下一帧的画面

### 时间间隔的计算问题

* 3.701：切芙芙，但也有可能在3.717才切出来，只不过画面提前了
* 3.934：点按e，但也可能3.950才点按，只不过画面提前了
* 最大的可能性是：3.950 - 3.701 = 0.249
* 最小的可能性是：3.934 - 3.717  = 0.217
* 0.249 - 0.217 - 0.032 = 2 * 0.016
* 两个原始时间点相减得到的是平均值：3.934 - 3.701 = 0.233