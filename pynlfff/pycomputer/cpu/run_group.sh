# !/bin/bash

# config
PYTHON="/home/ma-user/app/py37/bin/python"                                      # python program
PY_RUN="/home/ma-user/work/build-nlfff/app_python/group_run.py"             # Main run script file, need to download the environment in advance
SHS="/home/ma-user/work/build-nlfff/app_c/compiled.nonparallel/multigrid.sh"    # Single-threaded program path
SHP="/home/ma-user/work/build-nlfff/app_c/compiled.parallel/multigrid.sh"       # Multi-threaded program path
SAVE_PATH="/home/ma-user/work/pro"                                              # The directory where the preprocessed products are saved, with todo1.txt num_0700_0799/hmixxx etc.

# RUN
# python [com_group_run.py script] [root of preprocessing folder (also root of final product save path)] [c compiled single-threaded] [c multi-threaded]
$PYTHON $PY_RUN $SAVE_PATH $SHS $SHP                                            # RUN

