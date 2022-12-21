# !/bin/bash


# python /home/zzr/project/linff/linff-main/deploy/app_python/linff_main_run.py /home/zzr/project/linff/linff-main/deploy/app_c/compiled.cc /home/zzr/project/linff/linff-main/deploy/raw_data_eg /home/zzr/project/linff/linff-main/deploy/space

PYTHON="/home/ma-user/app/py37/bin/python"       # python程序
PY_RUN="/home/ma-user/work/build-nlfff/app_python/com_group_pre.py"     # 主运行脚本文件，需要提前下载好环境
RAW="/home/ma-user/work/f234"                   # 原始文件目录，里面有fits
PRE="/home/ma-user/work/f235"                   # 保存产品目录
WORKERNUM=0 # 运行线程数量 0是和系统核心一样  0.x表示占比系统核心多少  x表示多少线程

$PYTHON $PY_RUN $RAW $PRE $WORKERNUM # 



