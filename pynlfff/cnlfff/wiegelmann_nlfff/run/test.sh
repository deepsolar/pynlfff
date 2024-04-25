#!/bin/bash

SH=/home/bingxing2/home/scx6069/zzr/pynlfff/pynlfff/cnlfff/wiegelmann_nlfff/compiled.gpu.nvcc.arm/multigrid.sh
SH2=/home/bingxing2/home/scx6069/zzr/pynlfff/pynlfff/cnlfff/wiegelmann_nlfff/compiled.cpu.parallel.arm/multiprepro.sh
# PRO=/home/bingxing2/home/scx6069/zzr/nlfff/product/demo_01
PRO=/home/bingxing2/home/scx6069/zzr/nlfff/product/hmi.sharp_cea_720s.8729.20221028_031200_TAI
$SH2 $PRO
$SH $PRO 123

echo $PRO


