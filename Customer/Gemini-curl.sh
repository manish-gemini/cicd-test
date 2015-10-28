#!/bin/bash
url='http://repos.gsintlab.com/install'

command_exists() {
	command -v "$@" > /dev/null 2>&1
}

if  ! command_exists curl 
then
   yum install -y curl
fi
if [ "$http_proxy" != "" ]
then
  cproxy="-x $http_proxy" 
else
  cproxy=""
fi

FILES="Gemini-Chef.sh  Gemini-Deploy.sh  Gemini-LabManager.sh  Gemini-predeploy.sh  Gemini-supportbundle.sh"
for i in $FILES
do
  mkdir -p /opt/gemini/bin
  cd /opt/gemini/bin
  echo "Downloading $i"
  curl --silent -f $cproxy -O "${url}/$i"
  if [ $? -ne 0 ]
  then
     echo "Download failed: ${url}/${i}. Exiting"
     exit 1
  fi

done
chmod a+x /opt/gemini/bin/*.sh
# Running predeploy script
cd /opt/gemini/bin
/opt/gemini/bin/Gemini-Deploy.sh 

echo "Done."
