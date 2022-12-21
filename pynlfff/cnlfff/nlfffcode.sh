#! /bin/csh -f
    set i = 3
    set k = 1
    touch nlfffstart.mark
    cp grid1.ini grid.ini
    cp allboundaries1.dat allboundaries.dat
    cp mask1.dat mask.dat
    ./relax4 23 0
    ./relax4 40 10000
    ./checkquality Bout.bin
    cp step.log step1.log
    cp prot.log prot1.log
    cp NLFFFquality.log NLFFFquality1.log

    while ($k < $i) 
    @ k = $k + 1
    set grr = 'grid'$k'.ini'
    set grt = 'allboundaries'$k'.dat'
    set grz = 'mask'$k'.dat'
    cp $grr 'grid.ini'
    cp $grt 'allboundaries.dat'
    cp $grz 'mask.dat'
    ./rebin Bout.bin B0.bin
    ./relax4 40 10000
    ./checkquality Bout.bin
    set gra = 'step'$k'.log'
    set grb = 'prot'$k'.log'
    set grc = 'NLFFFquality'$k'.log'
    cp 'step.log' $gra
    cp 'prot.log' $grb
    cp 'NLFFFquality.log' $grc
    ./fftpot4
    ./checkenergy B0.bin Bout.bin
    touch nlfffdone.mark
    end

