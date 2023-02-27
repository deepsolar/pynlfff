# ! /bin/bash


# python /home/zzr/project/linff/linff-main/deploy/app_python/linff_main_run.py /home/zzr/project/linff/linff-main/deploy/app_c/ compiled.cc /home/zzr/project/linff/linff-main/deploy/raw_data_eg /home/zzr/project/linff/linff-main/deploy/space

PYTHON="/home/ma-user/app/py37/bin/python" # python program
PY_RUN="/home/ma-user/work/build-nlfff/app_python/com_group_pre.py" # main run script file, need to download the environment in advance
RAW="/home/ma-user/work/f234" # The original file directory with the fits in it
PRE="/home/ma-user/work/f235" # Save the catalog
WORKERNUM=0 # Number of threads running 0 is the same as the system core 0.x means how much of the system core is accounted for x means how many threads

$PYTHON $PY_RUN $RAW $PRE $WORKERNUM #