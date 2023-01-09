#!/bin/bash

# # use init to compiled
# make clean      # clean
# make            # complied
# make install    # mkdir compiled.cc  move file
# make clean      # clean compiled space

make -f Makefile.s clean   # 先清理
make -f Makefile.s         # 直接这个编译
make -f Makefile.s install # 会产生一个compiled.cc文件夹，这个文件夹路径作为参数给python部分
make -f Makefile.s clean   # 清空编译的其他文件


make -f Makefile.p clean   # 先清理
make -f Makefile.p         # 直接这个编译
make -f Makefile.p install # 会产生一个compiled.cc文件夹，这个文件夹路径作为参数给python部分
make -f Makefile.p clean   # 清空编译的其他文件


### use path/multigrid.sh  in data dir  eg
# cd path/datadir
# path/compiled/mutigrid.sh
