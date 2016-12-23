#!/bin/bash

url='http://repos.apporbit.com/install/appOrbitKit'

command_exists() {
	command -v "$@" > /dev/null 2>&1
}

if  ! command_exists nslookup
then
   yum install -y bind-utils
fi

if [ "$http_proxy" != "" ]
then
  cproxy="-x $http_proxy" 
else
  cproxy=""
fi

FILES="README.md apporbit-server  docker-compose apporbit-supportbundle.sh"

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
chmod a+x /opt/apporbit/bin/apporbit-server /opt/apporbit/bin/docker-compose /opt/apporbit/bin/*.sh
# Running predeploy script
cd /opt/apporbit/bin
#/opt/apporbit/bin/apporbit-deploy.sh
cmdstr="/opt/apporbit/bin/apporbit-server"

   for arg in "$@"; do
   case $arg in
     "--deploychef")
       cmdstr+=" --deploychef"
      ;;
     "--consul")
       cmdstr+=" --consul"
     ;;
     "--upgrade")
       cmdstr+=" --upgrade"
     ;; 
     "--offline")
       cmdstr+=" --offline"
     ;;
     *) echo "Invalid options ..!!(Flags: --upgrade, --deploychef, --consul, --offline)" 
       exit
     ;;
   esac
   done

$cmdstr

