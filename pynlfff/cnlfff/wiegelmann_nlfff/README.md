
# NLFFF

## 使用步骤
### 编译
#### [可选]设置编译选项

> 要求有gcc环境，如果并行要求有openmp环境，如果使用显卡要求有nvcc环境


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
PROJECTDIR=./

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
PROJECTDIR=./

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
PROJECT=./

# 配置程序，具体程序路径，使用绝对路径
PROGRAM=ROOT/compiled.gpu.nvcc.arm/fftpot4

# 进入目录，因为有些是写死的文件路径
cd $PROJECT

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



