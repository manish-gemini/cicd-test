#!/bin/bash
#python encryption

#rm -rf ./replicate-transport-python
#rm -rf ./orchestrate
#rm -rf ./replicate
#rm -rf ./appdb

find . -name "*.pyc" -print -exec rm -f {} \;

python -m compileall .
find . -name "*.pyc" -print -exec chmod +x {} \;
find . -name "*.py" -print -exec rm -f {} \;

#rm -rf ./jcommon
#rm -rf ./p2v_convert
