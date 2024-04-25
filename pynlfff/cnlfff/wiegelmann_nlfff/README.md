
# NLFFF

## 简介

基于c语言，支持gcc/nvcc版本的势场和非线性无力场太阳活动区三维磁场外推程序。

## 支持版本


|              | 势场green                             | 势场fftpot4                       | 非线性无力场nlfff                |
| ------------ | ------------------------------------- | --------------------------------- | -------------------------------- |
| 支持硬件     |                                       |                                   |                                  |
| cpu单进程    | support                               | support                           | support                          |
| cpu多进程    | support                               | support                           | support                          |
| gpu单卡      | support                               | not support                       | support                          |
| 支持体系结构 |                                       |                                   |                                  |
| arm          | support                               | support                           | support                          |
| amd          | support                               | support                           | support                          |
|              |                                       |                                   |                                  |
| 说明         | 小磁图ny<1000，gpu单卡和cpu多进程均快 | 大磁图ny>1000，多进程相对单卡较快 | 小磁图ny<1000约占小于10g左右显存 |




## 使用步骤
### 编译
#### [可选]设置编译选项

> 要求有gcc、make环境，如果cpu并行要求有openmp环境，如果使用显卡要求有nvcc环境，即可以直接运行gcc，make、nvcc等


amd架构：

编辑 init_compile_ps_amd.sh ， 选择编译哪些东西


arm架构：

编辑 init_compile_ps_arm.sh ， 选择编译哪些东西




#### 编译

amd架构：

```bash
bash ./init_compile_ps_amd.sh
```

arm架构：

```bash
bash ./init_compile_ps_arm.sh
```

### 运行

#### 完整运行流程

以amd架构为例子

```bash


# 项目文件夹
PROJECTDIR=./project_dir

# 运行等级，可选 1 12 123 23 2 3
GRID=123

# 设置运行脚本路径，可选：
# cpu单进程   ./compiled.cpu.nonparallel.amd/multigrid.sh
# cpu多进程   ./compiled.cpu.parallel.amd/multigrid.sh
# gpu单卡   ./compiled.gpu.nvcc.amd/multigrid.sh
NLFFF=./compiled.gpu.nvcc.amd/multigrid.sh

# 运行
bash  $NLFFF $PROJECTDIR $GRID

# this program NLFFF multigrid.sh need 2 parameter  
# 1 workspace path, which allboundaries123.dat grid123.ini mask123.dat boundary.ini etc. in it
# 2 which grid computer now, can be 1 12 123 2 23 3 , pay attenction if set 2 it has been run grid 1 before
# and need other app compiled bin in root along with this

```

#### 自定义运行流程

以amd架构为例子

```bash


# 项目文件夹
PROJECTDIR=./project_dir

# 运行等级，可选 1 12 123 23 2 3
GRID=123

# 设置运行脚本路径，可选：
# cpu单进程   ./compiled.cpu.nonparallel.amd/multigrid.sh
# cpu多进程   ./compiled.cpu.parallel.amd/multigrid.sh
# gpu单卡   ./compiled.gpu.nvcc.amd/multigrid.sh
NLFFF=./compiled.gpu.nvcc.amd/multigrid.sh

# 编辑NLFFF路径的multigrid.sh，设置具体运行哪些程序，如只运行势场或者非线性无力场
# vim $NLFFF

# 运行
bash  $NLFFF $PROJECTDIR $GRID

# this program NLFFF multigrid.sh need 2 parameter  
# 1 workspace path, which allboundaries123.dat grid123.ini mask123.dat boundary.ini etc. in it
# 2 which grid computer now, can be 1 12 123 2 23 3 , pay attenction if set 2 it has been run grid 1 before
# and need other app compiled bin in root along with this

```


#### 运行单个程序

以amd架构为例子

```bash

# 配置项目文件夹，要求里面有allboundaries123.dat grid123.ini mask123.dat boundary.ini etc.
PROJECT=./project_dir

# 配置程序，具体程序路径，使用绝对路径
PROGRAM=ROOT/compiled.gpu.nvcc.arm/fftpot4

# 进入目录，因为有些是写死的文件路径
cd $PROJECT

# 配置程序需要的文件，因为有些文件路径是写死的，运行程序时需要改为指定文件名，如：
# cp grid1.ini  grid.ini，具体需要改哪些文件名，可以参考multigrid.sh里面配置

# 运行程序，参数可以参考multigrid.sh里面配置
$PROJECT 参数

```



## 引用

### CPU Version

```latex
@article{Wiegelmann2012Nov,
    author = {Wiegelmann, T. and Thalmann, J. K. and Inhester, B. and Tadesse, T. and Sun, X. and Hoeksema, J. T.},
    title = {{How Should One Optimize Nonlinear Force-Free Coronal Magnetic Field Extrapolations from SDO/HMI Vector Magnetograms?}},
    journal = {Sol. Phys.},
    volume = {281},
    number = {1},
    pages = {37--51},
    year = {2012},
    month = nov,
    issn = {1573-093X},
    publisher = {Springer Netherlands},
    doi = {https://doi.org/10.1007/s11207-012-9966-z}
}
```

### GPU Version

```latex
@misc{Zhang2024,
  author = {Xinze, Zhang and Zhongrui Zhao},
  title = {The cuda version for nlfff},
  year = {2024},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/deepsolar/pynlfff}},
}
```



