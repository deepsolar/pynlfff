#!/bin/bash

SHELL_FOLDER=$(cd "$(dirname "$0")";pwd)

cd $SHELL_FOLDER


make -f Makefile.cpu.s.arm clean   # 先清理
make -f Makefile.cpu.s.arm         # 直接这个编译
make -f Makefile.cpu.s.arm install # 会产生一个compiled.cc文件夹，这个文件夹路径作为参数给python部分
make -f Makefile.cpu.s.arm clean   # 清空编译的其他文件


make -f Makefile.cpu.p.arm clean   # 先清理
make -f Makefile.cpu.p.arm         # 直接这个编译
make -f Makefile.cpu.p.arm install # 会产生一个compiled.cc文件夹，这个文件夹路径作为参数给python部分
make -f Makefile.cpu.p.arm clean   # 清空编译的其他文件


make -f Makefile.gpu.nvcc.arm clean   # 先清理
make -f Makefile.gpu.nvcc.arm         # 直接这个编译
make -f Makefile.gpu.nvcc.arm install # 会产生一个compiled.cc文件夹，这个文件夹路径作为参数给python部分
make -f Makefile.gpu.nvcc.arm clean   # 清空编译的其他文件


### use path/multigrid.sh  in data dir  eg
# cd path/datadir
# path/compiled/mutigrid.sh
