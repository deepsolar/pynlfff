#!/bin/bash

RAW_ROOT="./nas/18T1"
TO_ROOT="./nas/nlfff-data-2022/grid3.done"

for fnum in {0..7..1}
do
    for snum in {0..9..1}
    do
        THIS_NUM=$fnum$snum
        echo $THIS_NUM
        RAW_DIR="${RAW_ROOT}/num_${THIS_NUM}00_${THIS_NUM}99"
        TO_DIR="${TO_ROOT}/num_${THIS_NUM}00_${THIS_NUM}99"
        if [ -d "$RAW_DIR" ]; then
            if [ ! -d "$TO_DIR" ]; then
                mkdir "$TO_DIR"
            fi
            echo "mv -b $RAW_DIR/* $TO_DIR"
            mv -b $RAW_DIR/* $TO_DIR
        fi
        
    done

done