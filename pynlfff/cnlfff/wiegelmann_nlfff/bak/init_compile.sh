#!/bin/bash

SHELL_FOLDER=$(cd "$(dirname "$0")";pwd)

cd $SHELL_FOLDER

# use init to compiled
make clean      # clean
make            # complied
make install    # mkdir compiled.cc  move file
make clean      # clean compiled space


### use path/multigrid.sh  in data dir  eg
# cd path/datadir
# path/compiled/mutigrid.sh
