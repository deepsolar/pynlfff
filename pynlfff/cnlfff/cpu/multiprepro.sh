#! /bin/csh -f
    set i = $1
    set k = 1
    set mu3 = 0.001
    set mu4 = 0.01
    
    cp grid1.ini grid.ini
    cp allboundaries1.dat input.dat
    ./prepro $mu3 $mu4
    cp output.dat allboundaries1.dat

    
    while ($k < $i) 
    @ k = $k + 1
    set grr = 'grid'$k'.ini'
    set grt = 'allboundaries'$k'.dat'
    cp $grr 'grid.ini'
    cp $grt 'input.dat'
    ./prepro $mu3 $mu4
    cp output.dat $grt
    
    end
