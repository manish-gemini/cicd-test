#!/bin/sh -x

CWD=`pwd`
SRC_DIR=$CWD/Gemini-poc-stack
DST_DIR=$CWD/Gemini-poc-stack-encrypted
rm -rf $DST_DIR
cp -r $SRC_DIR $DST_DIR

# cleanup - remove unwanted files
rm -rf $DST_DIR/replicate-transport-python
rm -rf $DST_DIR/orchestrate
rm -rf $DST_DIR/replicate
rm -rf $DST_DIR/appdb

cd $DST_DIR
# remove all .pyc files
for file in `find . -name "*.pyc" -print`
do
	rm -rf $file
done

# now compile all python files to bytecode (.pyc)
python -m compileall .

# remove all .py files
for file in `find . -name "*.py" -print`
do
	rm -rf $file
done

# remove java module src files
rm -rf $DST_DIR/jcommon

# remove p2v_convert src files
rm -rf $DST_DIR/p2v_convert