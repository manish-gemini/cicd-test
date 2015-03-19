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

# now collect all python files and obfuscate
#for file in `find . -name "*.py" -print`
#do
#	echo $file
#	pyobfuscate $file > $file.pyo
#	mv $file.pyo $file
#done

# workaround for utils.py - for some reason pyobfuscate fails for it - so for now we just compile it alone
#cp $SRC_DIR/common/utils.py $DST_DIR/common/utils.py

# now compile all python files to bytecode (.pyc)
python -m compileall .

# remove all .py files
for file in `find . -name "*.py" -print`
do
	rm -rf $file
done

# compile java modules and remove src files
# first - the java common
source ./jenv-setup
cd $DST_DIR/jcommon
mkdir -p bin
javac -d bin -sourcepath src src/com/gemini/jcommon/*.java
rm -rf src

# p2v_convert
cd $DST_DIR/p2v_convert
source ./jenv-setup
mkdir -p bin
javac -d bin -sourcepath src src/com/gemini/p2v_convert/sdk/*.java src/com/gemini/p2v_convert/*.java
rm -rf src