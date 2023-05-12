
SHELL_FOLDER=$(cd "$(dirname "$0")";pwd)
cd $SHELL_FOLDER
pip install mkdocs
pip install -r requirements.txt


rm -rf $SHELL_FOLDER/../zh

cd $SHELL_FOLDER/zh
# build
mkdocs build
mv site $SHELL_FOLDER/../zh
# clean cache
# mkdocs build --clean
rm -rf $SHELL_FOLDER/../en
cd $SHELL_FOLDER/en
mkdocs build
mv site $SHELL_FOLDER/../en