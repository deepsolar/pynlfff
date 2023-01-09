# !/bin/bash


# python /home/zzr/project/linff/linff-main/deploy/app_python/linff_main_run.py /home/zzr/project/linff/linff-main/deploy/app_c/compiled.cc /home/zzr/project/linff/linff-main/deploy/raw_data_eg /home/zzr/project/linff/linff-main/deploy/space

PYTHON="/home/ma-user/app/py37/bin/python"          # python程序
PY_RUN="/home/ma-user/work/build-nlfff/app_python/com_group_run.py"             # 主运行脚本文件，需要提前下载好环境
SHS="/home/ma-user/work/build-nlfff/app_c/compiled.nonparallel/multigrid.sh"    # 单线程程序路径
SHP="/home/ma-user/work/build-nlfff/app_c/compiled.parallel/multigrid.sh"       # 多线程程序路径
SAVE_PATH="/home/ma-user/work/pro"                  # 保存预处理产品的目录，里面有todo1.txt num_0700_0799/hmixxx 等

$PYTHON $PY_RUN $SAVE_PATH $SHS $SHP                 # 运行
# python linff_main_run.py脚本  c编译的单线程 c多线程  最终产品保存路径的根目录

