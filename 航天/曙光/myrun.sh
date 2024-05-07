#!/bin/bash
#SBATCH -J test
#SBATCH -p xahdtest
#SBATCH -N 1
##SBATCH -n 32
#SBATCH --ntasks-per-node=4
#SBATCH --cpus-per-task=8
#SBATCH --gres=dcu:4
#SBATCH --exclusive
source ~/miniconda3/etc/profile.d/conda.sh
conda activate torch_dtk23.04-abi0-py38
#module switch compiler/dtk/23.04
module purge   
module load compiler/devtoolset/7.3.1   mpi/hpcx/gcc-7.3.1
module load compiler/dtk/23.04
#source  /work/home/aca162hl5n/mmrotate/proxy_temp.sh
export HIP_VISIBLE_DEVICES=0,1,2,3
export MIOPEN_USER_DB_PATH=/tmp/miopen-udb
export MIOPEN_CUSTOM_CACHE_DIR=/tmp/miopen-cache
export MIOPEN_FIND_MODE=3
pwd
cd /work/home/aca162hl5n/mmrotate-1.x
sh tools/dist_train.sh  configs/oriented_rcnn/oriented-rcnn-le90_swin-l_pafpn_1x_planeship98_1024_swinL.py  4
#--launcher="slurm"
