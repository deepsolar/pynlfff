
主要产品文件为Bout.bin文件，存储nlfff磁场数据，存储格式为按行优先级的四维数组（c风格），数组的第0维为分量标志，123维分别表示Bx、By、Bz的xyz坐标值，xyz取值范围与上一层网格一致，存储数据单位为高斯，你可以从[本文](https://www.nature.com/articles/s41597-023-02091-5)获得的更多细节，如果你使用python，你也可以使用[pynlfff](https://github.com/deepsolar/pynlfff)进行读写操作，如果你使用其他语言，你可以参考python的实现。

![img](https://media.springernature.com/full/springer-static/image/art%3A10.1038%2Fs41597-023-02091-5/MediaObjects/41597_2023_2091_Fig8_HTML.png)

