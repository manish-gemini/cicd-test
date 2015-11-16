#!/bin/bash

LOGFILE=apporbit-install.log
echo "`date` Starting apporbit-chef.sh" >>$LOGFILE
##Docker Run command for Chef
read -p "Do you want to continue Deploy Chef Container ? y or n " -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
  echo "Pull Chef Server from Registry..."
  docker pull registry.gemini-systems.net/gemini/gemini-chef:1.0 >>$LOGFILE
  echo "Continue to run chef ..."
  if docker ps -a |grep -aq gemini-chef; then
        docker rm -f gemini-chef >>$LOGFILE
  fi 
  ip=`curl -s http://whatismyip.akamai.com; echo`
  printf "Enter the Host IP :"
  read -p "Default($ip):" hostip
  hostip=${hostip:-$ip}
  docker run -m 2g -it -p 9443:9443  -v /etc/chef-server/ --name gemini-chef -h $hostip -d registry.gemini-systems.net/gemini/gemini-chef:1.0
  echo "Please change your chef password by logging into the UI at http://${hostip}:9443"
fi
echo "`date` Finished apporbit-chef.sh" >>$LOGFILE
