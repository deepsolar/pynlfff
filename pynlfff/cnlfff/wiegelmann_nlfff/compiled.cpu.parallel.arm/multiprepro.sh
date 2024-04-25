#! /bin/bash


PREPRO=prepro
mu3=0.001
mu4=0.01

echo "================================================"

echo "use prepro"
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

LR_RUN_DIR=$(dirname $(readlink -f "$0")) 




k=1
cp grid1.ini grid.ini
# cp allboundaries1.dat allboundaries1.raw.dat
# cp allboundaries1.dat input.dat
if [ ! -f "allboundaries1.raw.dat" ]; then
  cp allboundaries1.dat allboundaries1.raw.dat
  cp allboundaries1.dat input.dat
else
  cp allboundaries1.raw.dat input.dat
fi
$LR_RUN_DIR/$PREPRO $mu3 $mu4
cp output.dat allboundaries1.dat

k=2
cp grid2.ini grid.ini
# cp allboundaries2.dat allboundaries2.raw.dat
# cp allboundaries2.dat input.dat
if [ ! -f "allboundaries2.raw.dat" ]; then
  cp allboundaries2.dat allboundaries2.raw.dat
  cp allboundaries2.dat input.dat
else
  cp allboundaries2.raw.dat input.dat
fi
$LR_RUN_DIR/$PREPRO $mu3 $mu4
cp output.dat allboundaries2.dat

k=3
cp grid3.ini grid.ini
# cp allboundaries3.dat allboundaries3.raw.dat
# cp allboundaries3.dat input.dat
if [ ! -f "allboundaries3.raw.dat" ]; then
  cp allboundaries3.dat allboundaries3.raw.dat
  cp allboundaries3.dat input.dat
else
  cp allboundaries3.raw.dat input.dat
fi
$LR_RUN_DIR/$PREPRO $mu3 $mu4
cp output.dat allboundaries3.dat




echo "================================================"

echo "end run date:"
date

echo "================================================"


