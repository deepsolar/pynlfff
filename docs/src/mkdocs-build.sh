
SHELL_FOLDER=$(cd "$(dirname "$0")";pwd)

rm -rf $SHELL_FOLDER/../zh

cd $SHELL_FOLDER/zh
# build
# apt install mkdocs
mkdocs build
mv site $SHELL_FOLDER/../zh
# clean cache
# mkdocs build --clean
rm -rf $SHELL_FOLDER/../en
cd $SHELL_FOLDER/en
mkdocs build
mv site $SHELL_FOLDER/../en