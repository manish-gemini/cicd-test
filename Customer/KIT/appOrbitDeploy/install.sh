#!/bin/bash
if [ -z "$1" ]
then
    url='http://repos.gsintlab.com/install/appOrbitKit'
else
    url=$1
fi

command_exists() {
	command -v "$@" > /dev/null 2>&1
}

if  ! command_exists curl 
then
   yum install -y curl
fi

if  ! command_exists python 
then
   yum install -y python
fi

if [ "$http_proxy" != "" ]
then
  cproxy="-x $http_proxy" 
else
  cproxy=""
fi

FILES="Action.pyc  Config.pyc  README.txt  UserInteract.pyc  Utility.pyc  appOrbitLauncher.pyc  apporbit.repo apporbit-supportbundle.sh"

echo "Downloading apporbit installer"
for i in $FILES
do
  mkdir -p /opt/apporbit/bin
  cd /opt/apporbit/bin
  #echo "Downloading $i"
  #echo -ne '#####                     (33%)\r'
  curl --silent -f $cproxy -O "${url}/$i"
  if [ $? -ne 0 ]
  then
     echo "Download failed: ${url}/${i}. Exiting"
     exit 1
  fi

done
chmod a+x /opt/apporbit/bin/*.pyc
# Running predeploy script
cd /opt/apporbit/bin
#/opt/apporbit/bin/apporbit-deploy.sh 
python /opt/apporbit/bin/appOrbitLauncher.pyc


