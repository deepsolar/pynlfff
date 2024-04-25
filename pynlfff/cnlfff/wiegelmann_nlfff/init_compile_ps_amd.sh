#!/bin/bash

SHELL_FOLDER=$(cd "$(dirname "$0")";pwd)

cd $SHELL_FOLDER

# # use init to compiled
# make clean      # clean
# make            # complied
# make install    # mkdir compiled.cc  move file
# make clean      # clean compiled space

make -f Makefile.cpu.s.amd clean   # 先清理
make -f Makefile.cpu.s.amd         # 直接这个编译
make -f Makefile.cpu.s.amd install # 会产生一个compiled.cc文件夹，这个文件夹路径作为参数给python部分
make -f Makefile.cpu.s.amd clean   # 清空编译的其他文件


make -f Makefile.cpu.p.amd clean   # 先清理
make -f Makefile.cpu.p.amd         # 直接这个编译
make -f Makefile.cpu.p.amd install # 会产生一个compiled.cc文件夹，这个文件夹路径作为参数给python部分
make -f Makefile.cpu.p.amd clean   # 清空编译的其他文件


make -f Makefile.gpu.nvcc.amd clean   # 先清理
make -f Makefile.gpu.nvcc.amd         # 直接这个编译
make -f Makefile.gpu.nvcc.amd install # 会产生一个compiled.cc文件夹，这个文件夹路径作为参数给python部分
make -f Makefile.gpu.nvcc.amd clean   # 清空编译的其他文件


### use path/multigrid.sh  in data dir  eg
# cd path/datadir
# path/compiled/mutigrid.sh
