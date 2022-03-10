#!/bin/bash
# config
todolist='Bout.txt'
prolog="Bout.csv"
grid="grid3.ini"

# creat list
if [ -f "$todolist" ]; then
    echo "todolist Exist";
else
    find ./*/*/Bout.bin > $todolist
fi

# do work
i=1
while read line; do
    # print log
    echo "$i:$line"
    # echo $line

    # write line and name
    echo -e "$i;$line;\t\c" >> $prolog

    # write bx by bz
    parentdir="$(dirname "$line")"
    gridthis="$parentdir/$grid"
    # echo "$gridthis"
    if [ -f "$gridthis" ]; then
        # echo "todolist Exist";
        nx=$(sed -n '2p'  $gridthis)
        ny=$(sed -n '4p'  $gridthis)
        nz=$(sed -n '6p'  $gridthis)
        echo -e "$nx;$ny;$nz;\t\c" >> $prolog
    else
        echo -e "\t;\t;\t;\t\c" >> $prolog
    fi

    # write size
    size=$(stat -c %s $line)
    echo -e "$size;\t\c" >> $prolog

    # write sha256
    sha256str12=$(sha256sum -b $line)
    sha256str1=${sha256str12:0:64}
    echo -e "$sha256str1\c" >> $prolog
    echo -e ";\t" >> $prolog

    i=$((i+1))
done < $todolist

echo "all done"
