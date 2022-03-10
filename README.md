# pynlfff工具包

用于预处理处理，计算**太阳活动区非线性无力场3D数据集**，以及可视化。

```bash
pip install pynlfff
```

整体包结构如下

+ `pynlfff`
  + `pyprepare`  准备包
    + `rcheck` 检查依赖
      + `RCheck` 依赖检查类，检查是否满足依赖
  + `pydownload` 下载原始数据
    + `downloadjsoc` 下载jsoc数据
  + `pypreprocess`预处理数据包
    + `preprocess` 预处理包
    + `disambiguation` 坐标转换包
  + `pycomputer`计算包
  + `pyproduct`产品使用包
    + `file`产品文件管理包
      + `NlfffFile`文件管理类，文件读写和类型转换
      + `nlfffFind`文件查找类
    + `quality`产品质量控制包
      + `QualityCheck`质量检查类
  + `pyplot`可视化包
    + `plot3d`三维绘制包
      + `NlfffPlotD3CutCake` 绘制三维磁场分量切面图
      + `nlfffPlotD3FieldLine` 绘制三维磁场磁力线 TODO

因为工具包依赖较多，在大部分场景通常用不到所有功能，因此将依赖单独列出，需要时安装，可以使用`pynlfff.pyprepare.rcheck.RCheck()`检查依赖。

