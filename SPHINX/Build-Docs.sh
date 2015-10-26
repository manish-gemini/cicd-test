#!/bin/bash -x
#BUILD HELP DOCS.


#Install pandoc, pandoc is a utility to convert the md files to rst files
# yum install -y pandoc


yum install -y docker git wget

cd IMAGE

docker build -t gemini/gemini-docs .

cd /opt/SPHINX/Source
#TODO
#git clone 

docker run -it -v /opt/SPHINX/Source:/home/SpinxDir/source -v /opt/SPHINX/Dest:/home/SpinxDir/source/_build  gemini/gemini-docs
