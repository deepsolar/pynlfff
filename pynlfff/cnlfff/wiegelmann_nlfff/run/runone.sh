#!/bin/bash


LR_RUN_DIR=$(dirname $(readlink -f "$0")) 
# NOWRUN="${2}"

PROJECT=${1}
# /home/bingxing2/home/scx6069/zzr/nlfff/product/hmi.sharp_cea_720s.8729.20221028_031200_TAI
CUDA=${2}
# 0 1 2
GRID=${3}
# 1 2 3  12 123

# SH=/home/bingxing2/home/scx6069/zzr/pynlfff/pynlfff/cnlfff/wiegelmann_nlfff/compiled.gpu.nvcc.arm/multigrid.sim.sh
# SH2=/home/bingxing2/home/scx6069/zzr/pynlfff/pynlfff/cnlfff/wiegelmann_nlfff/compiled.cpu.parallel.arm/multiprepro.sh
# PRO=/home/bingxing2/home/scx6069/zzr/nlfff/product/demo_01


# SH=${LR_RUN_DIR}/../compiled.gpu.nvcc.arm/multigrid.sim.sh
SH=${LR_RUN_DIR}/../compiled.gpu.nvcc.arm/multigrid.sh

SH2=${LR_RUN_DIR}/../compiled.cpu.parallel.arm/multiprepro.sh

# $SH2 $PRO
# 1200 480 630
CUDA_VISIBLE_DEVICES=$CUDA $SH $PROJECT $GRID
echo "end"
echo $PRO

# /home/bingxing2/home/scx6069/zzr/data/nlfff_append/product1/10413/hmi.sharp_cea_720s.10413.20231124_031200_TAI/NLFFFquality1.log




# /home/bingxing2/home/scx6069/zzr/pynlfff/pynlfff/cnlfff/wiegelmann_nlfff/run/runone.sh /home/bingxing2/home/scx6069/zzr/nlfff/product/hmi.sharp_cea_720s.8729.20221028_031200_TAI 0
# /home/bingxing2/home/scx6069/zzr/pynlfff/pynlfff/cnlfff/wiegelmann_nlfff/run/runone.sh /home/bingxing2/home/scx6069/zzr/nlfff/product/demo_01 1
# /home/bingxing2/home/scx6069/zzr/pynlfff/pynlfff/cnlfff/wiegelmann_nlfff/compiled.cpu.parallel.arm/checkquality 







