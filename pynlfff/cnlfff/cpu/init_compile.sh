#!/bin/bash

# use init to compiled
make clean      # clean
make            # complied
make install    # mkdir compiled.cc  move file
make clean      # clean compiled space


### use path/multigrid.sh  in data dir  eg
# cd path/datadir
# path/compiled/mutigrid.sh
