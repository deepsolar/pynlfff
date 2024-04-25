#!/bin/bash

#SBATCH --job-name=pro2
#SBATCH -D /home/bingxing2/home/scx6069/zzr/code/proj/d3/code/output/log/pro2/
#SBATCH --output=LOG-%x.%j-OUTPUT.txt
#SBATCH --error=LOG-%x.%j-ERROR.txt
#SBATCH --nodes=8
#SBATCH --ntasks-per-node=1         # number of MP tasks
#SBATCH --gres=gpu:4                # number of GPUs per node
#SBATCH --time=48:10:00             # maximum execution time (HH:MM:SS)


## #SBATCH --cpus-per-task=160         # number of cores per tasks
#https://github.com/huggingface/accelerate/blob/main/examples/slurm/submit_multinode.sh
######################
### Set enviroment ###
######################
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
# ====
# export NCCL_ALGO=Ring
# export NCCL_MAX_NCHANNELS=16
# export NCCL_MIN_NCHANNELS=16
# export NCCL_DEBUG=INFO
# export NCCL_TOPO_FILE=/home/bingxing2/apps/nccl/conf/dump.xml
# export NCCL_IB_HCA=mx5_0,mlx5_2
# export NCCL_IB_GID_INDEX=3
# export NCCL_IB_TIMEOUT=23
# export NCCL_IB_RETRY_CNT=7
######################
#### Set network #####
######################
# head_node_ip=$(scontrol show hostnames $SLURM_JOB_NODELIST | head -n 1)
# ######################

# export LAUNCHER="accelerate launch \
#     --num_processes $((SLURM_NNODES * GPUS_PER_NODE)) \
#     --num_machines $SLURM_NNODES \
#     --rdzv_backend c10d \
#     --main_process_ip $head_node_ip \
#     --main_process_port 29500 \
#     "
# export SCRIPT="/home/bingxing2/home/scx6069/zzr/code/proj/d3/code/tool/train.py"
# export SCRIPT_ARGS=" \
#     --mixed_precision fp16 \
#     --output_dir /home/bingxing2/home/scx6069/zzr/code/proj/d3/code/output/output_dir/many \
#     --project_dir /home/bingxing2/home/scx6069/zzr/code/proj/d3/code/output/project_dir/many \
#     --with_tracking \
#     --checkpointing_steps epoch \
#     "

# # This step is necessary because accelerate launch does not handle multiline arguments properly
# #export CMD="$LAUNCHER $PYTHON_FILE $ARGS"
# export CMD="$LAUNCHER $PYTHON_FILE $SCRIPT $SCRIPT_ARGS"

# $CMD=ls
# srun $CMD

# 一定全部退干净，source ac环境也不行，必须退
# conda deactivate


# sbatch -N 8 --gres=gpu:4 --qos=gpugpu  -p vip_gpu_scx6069 /home/bingxing2/home/scx6069/zzr/code/proj/d3/code/tool/run/pro3.sh

# sbatch -N 4 --gres=gpu:4 --qos=gpugpu  -p vip_gpu_scx6069 /home/bingxing2/home/scx6069/zzr/code/proj/d3/code/tool/run/pro3.sh

# sbatch -N 2 --gres=gpu:4 --qos=gpugpu  -p vip_gpu_scx6069 /home/bingxing2/home/scx6069/zzr/code/proj/d3/code/tool/run/pro3.sh

# salloc -N 1 --gres=gpu:4 --qos=gpugpu  -p vip_gpu_scx6069

# salloc --gpus=1 -p vip_gpu_scx6069




#  单节点 CPU：128核 GPU：4卡A100

# 任务提交方式：
# 需加-p vip_gpu_scx6069 参数指定vip队列

# 单机4卡任务提交举例：
# sbatch --gpus=4 -p vip_gpu_scx6069  脚本名
# 跨节点任务提交举例
# sbatch -N 2 --gres=gpu:4 --qos=gpugpu -p vip_gpu_scx6069
# 使用NCCL跨节点通信须添加下面参数：
# export NCCL_ALGO=Ring
# export NCCL_MAX_NCHANNELS=16
# export NCCL_MIN_NCHANNELS=16
# export NCCL_DEBUG=INFO
# export NCCL_TOPO_FILE=/home/bingxing2/apps/nccl/conf/dump.xml
# export NCCL_IB_HCA=mx5_0,mlx5_2
# export NCCL_IB_GID_INDEX=3
# export NCCL_IB_TIMEOUT=23
# export NCCL_IB_RETRY_CNT=7
