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

docker run -rm -it  -v /opt/SPHINX/Source:/home/SpinxDir/source -v /opt/SPHINX/Dest:/home/SpinxDir/source/_build  gemini/gemini-docs

docker rm -f gemini-nginx

docker run --name gemini-nginx -p 3000:80 -p 8443:443  -v  /opt/SPHINX/Dest/html:/usr/share/nginx/html -d nginx
