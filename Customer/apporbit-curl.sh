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

FILES="apporbit-chef.sh  apporbit-deploy.sh  apporbit-labmanager.sh  apporbit-predeploy.sh  apporbit-supportbundle.sh apporbit.repo"
for i in $FILES
do
  mkdir -p /opt/apporbit/bin
  cd /opt/apporbit/bin
  echo "Downloading $i"
  curl --silent -f $cproxy -O "${url}/$i"
  if [ $? -ne 0 ]
  then
     echo "Download failed: ${url}/${i}. Exiting"
     exit 1
  fi

done
chmod a+x /opt/apporbit/bin/*.sh
# Running predeploy script
cd /opt/apporbit/bin
/opt/apporbit/bin/apporbit-deploy.sh 

echo "Done."
