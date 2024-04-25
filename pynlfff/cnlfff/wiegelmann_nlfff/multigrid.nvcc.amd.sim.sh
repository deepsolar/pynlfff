#! /bin/bash

# /*
#  * @Description: https://github.com/deepsolar/pynlfff/
#  * @Author: Thomas Wiegelmann (wiegelmann@mps.mpg.de)
#  * @Date: 
#  * @LastEditors: Zhongrui Zhao (zhaozhongrui21@mails.ucas.ac.cn), Xinze Zhang (zhangxinze17@mails.ucas.ac.cn),
#  * @LastEditDescription: Update GPU version
#  * @LastEditTime: 20240418
# */


# this program need 2 parameter  
# 1 workspace path, which allboundaries123.dat grid123.ini mask123.dat boundary.ini etc. in it
# 2 which grid computer now, can be 1 12 123 2 23 3 , pay attenction if set 2 it has been run grid 1 before
# and need other app compiled bin in root along with this

RELAX=relax4
RELAXP=../compiled.cpu.parallel.amd/relax4
CHECKQUALITY=checkquality
REBIN=rebin
FFTPOT=fftpot4
FFTPOTP=../compiled.cpu.parallel.amd/fftpot4
CHECKENERGY=checkenergy

echo "BASE INFORMATION:"
echo "File name:        linff run log"
echo "App file name:    $0"                     # this program path (default)
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
    $LR_RUN_DIR/$RELAX 23 0                     # potential field
    $LR_RUN_DIR/$RELAX 40 10000                 # NLFFF,  read B0.bin and so on, write Bout.bin
    $LR_RUN_DIR/$CHECKQUALITY Bout.bin
    cp step.log step1.log
    cp prot.log prot1.log
    cp NLFFFquality.log NLFFFquality1.log
    # ==========
    mv Bout.bin Bout.1.bin
    mv B0.bin B0.1.bin
    date > "done1.txt"                          # flag
    
fi


if [[ "$NOWRUN" == *"2"* ]];
then
    cp 'grid2.ini' 'grid.ini'
    cp 'allboundaries2.dat' 'allboundaries.dat'
    cp 'mask2.dat' 'mask.dat'
    $LR_RUN_DIR/$REBIN Bout.1.bin B0.bin
    $LR_RUN_DIR/$RELAX 40 10000
    $LR_RUN_DIR/$CHECKQUALITY Bout.bin
    cp 'step.log' 'step2.log'
    cp 'prot.log' 'prot2.log'
    cp 'NLFFFquality.log' 'NLFFFquality2.log'
    # cpu
    # $LR_RUN_DIR/$FFTPOTP                         # grid2 is fine without this calculation
    # gpu
    # $LR_RUN_DIR/$RELAX 23 0                     # potential field
    # $LR_RUN_DIR/$CHECKENERGY B0.bin Bout.bin    # grid2 is fine without this calculation
    # cp Energy.log Energy2.log
    # ==========
    mv Bout.bin Bout.2.bin
    # mv B0.bin B0.2.bin
    date > "done2.txt"
fi


if [[ "$NOWRUN" == *"3"* ]];
then
    cp 'grid3.ini' 'grid.ini'
    cp 'allboundaries3.dat' 'allboundaries.dat'
    cp 'mask3.dat' 'mask.dat'
    $LR_RUN_DIR/$REBIN Bout.2.bin B0.bin        # Bout rebain as B0, as the initialization condition, this B0 is not the potential field file
    $LR_RUN_DIR/$RELAX 40 10000                 # nlfff     doc is old
    $LR_RUN_DIR/$CHECKQUALITY Bout.bin
    cp 'step.log' 'step3.log'
    cp 'prot.log' 'prot3.log'
    cp 'NLFFFquality.log' 'NLFFFquality3.log'
    # cpu
    # $LR_RUN_DIR/$FFTPOTP                       # Generate potential field file, this B0 is the potential field file
    # gpu
    # $LR_RUN_DIR/$RELAX 23 0                     # potential field
    # $LR_RUN_DIR/$CHECKENERGY B0.bin Bout.bin    # Contrasting potential field and nonlinear force-free field energy differences
    # cp Energy.log Energy3.log
    # ==========
    mv Bout.bin Bout.3.bin
    # mv B0.bin B0.3.bin
    date > "done3.txt"
fi


echo "================================================"

echo "end run date:"
date

echo "================================================"


