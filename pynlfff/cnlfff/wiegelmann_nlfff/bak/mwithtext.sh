#! /bin/bash

# this program need 2 parameter  
# 1 workspace path, which allboundaries123.dat grid123.ini mask123.dat boundary.ini etc. in it
# 2 which grid computer now, can be 1 12 123 2 23 3 , pay attenction if set 2 it has been run grid 1 before
# and need other app compiled bin in root along with this


RELAX=relax4
CHECKQUALITY=checkquality
REBIN=rebin
FFTPOT=fftpot4
CHECKENERGY=checkenergy

echo "BASE INFORMATION:"
echo "File name:        linff run log"
echo "App file name:    $0"  # this program path (default)
echo "Compute platform: "
lscpu | grep -i byte
uname -a

echo "-----------------------------------------------"

echo "RUN LOG:"
echo "RUN grid:"
echo "${2}"
echo "start run date:"
date

# get workspace
if [ "${1}" == '' ];
then
        echo "use run dir as workspace:"
        workspace="./"
        cd ${workspace}
        pwd
else
        echo "workspace:"
        workspace=${1}
        cd ${workspace}
        pwd
fi


echo "================================================"


LR_RUN_DIR=$(dirname $(readlink -f "$0")) 
NOWRUN="${2}"

if [[ "$NOWRUN" == *"1"* ]];
then
    cp grid1.ini grid.ini
    cp allboundaries1.dat allboundaries.dat
    cp mask1.dat mask.dat
    $LR_RUN_DIR/$RELAX 23 0   # 产生B0表示势场
    $LR_RUN_DIR/$RELAX 40 10000 # 使用B0为初始条件（输入） Bout非线性无力场为输出    !!!可能有其他输入
    $LR_RUN_DIR/$CHECKQUALITY Bout.bin #Bout为输入计算夹脚评估质量
    cp step.log step1.log
    cp prot.log prot1.log
    cp NLFFFquality.log NLFFFquality1.log
    touch "done1.txt"  # flag
fi


if [[ "$NOWRUN" == *"2"* ]];
then
    cp 'grid2.ini' 'grid.ini'
    cp 'allboundaries2.dat' 'allboundaries.dat'
    cp 'mask2.dat' 'mask.dat'
    $LR_RUN_DIR/$REBIN Bout.bin B0.bin  # 输入Bout(rebin上一层Bout) 输出B0为这一层初始条件(即这一层初始添加不再是势场，而是rebin的非线性无力场)   
    $LR_RUN_DIR/$RELAX 40 10000 # 输入B0为初始条件  输出Bout非线性无力场
    $LR_RUN_DIR/$CHECKQUALITY Bout.bin # 输入Bout评估质量
    cp 'step.log' 'step2.log'
    cp 'prot.log' 'prot2.log'
    cp 'NLFFFquality.log' 'NLFFFquality2.log'
    $LR_RUN_DIR/$FFTPOT  # 计算势场，输出势场为B0   grid2不进行这个和CHECKENERGY计算也行，下面会覆盖B0和CHECKENERGY日志
    $LR_RUN_DIR/$CHECKENERGY B0.bin Bout.bin # 计算CHECKENERGY，grid2不进行这个计算也行
    touch "done2.txt"
fi


if [[ "$NOWRUN" == *"3"* ]];
then
    cp 'grid3.ini' 'grid.ini'
    cp 'allboundaries3.dat' 'allboundaries.dat'
    cp 'mask3.dat' 'mask.dat'
    $LR_RUN_DIR/$REBIN Bout.bin B0.bin  # 将上一层Bout进行输入，输出rebain后文件为B0，作为初始化条件，这个B0不是势场文件
    $LR_RUN_DIR/$RELAX 40 10000 # nlfff  计算非线性无力场，输入为B0 输出为Bout  doc is old
    $LR_RUN_DIR/$CHECKQUALITY Bout.bin # 计算质量
    cp 'step.log' 'step3.log'
    cp 'prot.log' 'prot3.log'
    cp 'NLFFFquality.log' 'NLFFFquality3.log'
    $LR_RUN_DIR/$FFTPOT   # 产生势场文件，这个B0才是势场文件
    $LR_RUN_DIR/$CHECKENERGY B0.bin Bout.bin # 对比势场和非线性无力场能量差异
    touch "done.txt"
fi

# B0.bin  

echo "================================================"

echo "end run date:"
date

echo "================================================"


