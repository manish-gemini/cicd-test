#!/bin/bash
if [ -z "$1" ]
then
    url='http://repos.apporbit.com/install/appOrbitKit'
else
    if [ "$1" == "deploychef" ]
    then
       print "Update Chef Server"
    else
        url=$1
    fi
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

FILES="action.pyc  config.pyc  README.md  userinteract.pyc  utility.pyc  apporbitlauncher.pyc  apporbit.repo apporbit-supportbundle.sh"

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
if [ "$1" == "deploychef" -a "$#" -eq 1 ]
then
    python /opt/apporbit/bin/apporbitlauncher.pyc deploychef
elif [ "$1" == "skipipvalidity" -a "$#" -eq 1 ]
then
    python /opt/apporbit/bin/apporbitlauncher.pyc skipipvalidity
elif [ "$#" -eq 2 ]
then
     if [ "$1" == "deploychef" -a "$2" == "skipipvalidity" ] || [ "$2" == "deploychef" -a "$1" == "skipipvalidity" ]
     then
          python /opt/apporbit/bin/apporbitlauncher.pyc deploychef skipipvalidity
     else
	  print "Invalid arguments..!!"
     fi
else
    python /opt/apporbit/bin/apporbitlauncher.pyc
fi
