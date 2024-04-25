#!/bin/bash

#SBATCH --job-name=pro3
#SBATCH -D /home/bingxing2/home/scx6069/zzr/code/proj/d3/code/output/log/pro2/
#SBATCH --output=LOG-%x.%j-OUTPUT.txt
#SBATCH --error=LOG-%x.%j-ERROR.txt
#SBATCH --nodes=8
#SBATCH --ntasks-per-node=1         # number of MP tasks
#SBATCH --gres=gpu:4                # number of GPUs per node
#SBATCH --time=48:10:00             # maximum execution time (HH:MM:SS)

module load anaconda/2021.11


# module load compilers/cuda/11.7 
module load compilers/cuda/12.2

# module load cudnn/8.4.0.27_cuda11.x
module load cudnn/8.9.5.29_cuda12.x
module load compilers/gcc/12.2.0
# module load llvm/triton-llvm_17.0.0
# source activate accelerate

# rm -rf /home/bingxing2/home/scx6069/zzr/code/proj/d3/code/tool/tools/__pycache__

export GPUS_PER_NODE=4
######################
### 启用IB通信
export NCCL_ALGO=Ring
export NCCL_MAX_NCHANNELS=16
export NCCL_MIN_NCHANNELS=16
export NCCL_DEBUG=INFO
export NCCL_TOPO_FILE=/home/bingxing2/apps/nccl/conf/dump.xml
export NCCL_IB_HCA=mlx5_0,mlx5_2
export NCCL_IB_GID_INDEX=3
export NCCL_IB_TIMEOUT=23
export NCCL_IB_RETRY_CNT=7

PYPHRUN=/home/bingxing2/home/scx6069/zzr/pynlfff/pynlfff/pycomputer/gpu/run_grid1.py
LOP=/home/bingxing2/home/scx6069/zzr/data/nlfff_append/run2/rlog
mkdir -p $LOP

# nohup python $PYPHRUN 1 0 >> $LOP/log1.txt &
# nohup python $PYPHRUN 2 1 >> $LOP/log2.txt &
# nohup python $PYPHRUN 3 2 >> $LOP/log3.txt &
# nohup python $PYPHRUN 4 3 >> $LOP/log4.txt &

# nohup python $PYPHRUN 5 0 >> $LOP/log5.txt &
# nohup python $PYPHRUN 6 1 >> $LOP/log6.txt &
# nohup python $PYPHRUN 7 2 >> $LOP/log7.txt &
# nohup python $PYPHRUN 8 3 >> $LOP/log8.txt &


# nohup python $PYPHRUN 9 0 >> $LOP/log9.txt &
# nohup python $PYPHRUN 10 1 >> $LOP/log10.txt &
# nohup python $PYPHRUN 11 2 >> $LOP/log11.txt &
# nohup python $PYPHRUN 12 3 >> $LOP/log12.txt &


nohup python $PYPHRUN 13 0 >> $LOP/log13.txt &
nohup python $PYPHRUN 14 1 >> $LOP/log14.txt &
nohup python $PYPHRUN 15 2 >> $LOP/log15.txt &
nohup python $PYPHRUN 16 3 >> $LOP/log16.txt &


# 指定输出文件路径
# output_file="/path/to/output.log"

# 循环运行 top 命令，每隔10分钟执行一次
while true; do
    # top -n 1 >> "$output_file"
    # echo "--------------------------------------" >> "$output_file"
    top -n 1
    echo "--------------------------------------"
    # sleep 6  
    date
    sleep 600  # 休眠10分钟
done

# /home/bingxing2/home/scx6069/zzr/pynlfff/pynlfff/cnlfff/wiegelmann_nlfff/compiled.cpu.parallel.arm/checkquality Bout.3.bin

# sbatch -N 1 --gres=gpu:4 --qos=gpugpu  -p vip_gpu_scx6069   --nodelist=paraai-n32-h-01-agent-80  /home/bingxing2/home/scx6069/zzr/pynlfff/pynlfff/pycomputer/gpu/r80.sh



