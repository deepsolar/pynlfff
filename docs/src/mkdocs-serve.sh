
SHELL_FOLDER=$(cd "$(dirname "$0")";pwd)

RUNDIR=$SHELL_FOLDER/../


# install
# pip install mkdocs

# new
# mkdocs new pynlfff

# # serve
# mkdocs serve

# edit
# mkdocs.yml

python -m http.server --directory $RUNDIR