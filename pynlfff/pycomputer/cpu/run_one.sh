# !/bin/bash

# config
SH="/home/ma-user/work/build-nlfff/app_c/compiled.nonparallel/multigrid.sh"    # Single-threaded program path
# SH="/home/ma-user/work/build-nlfff/app_c/compiled.parallel/multigrid.sh"     # Multi-threaded program path
SAVE_PATH="/home/ma-user/work/pro"                                             # The directory where the preprocessed products are saved, with todo1.txt num_0700_0799/hmixxx etc.
GRID=123 # or 1 12 123 23(need run 1 before) 3(need run 12 before)

# RUN
$SH $SAVE_PATH  $GRID

