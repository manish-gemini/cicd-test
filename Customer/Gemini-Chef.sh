#!/bin/bash

##Docker Run command for Chef
read -p "Do you want to continue Deploy Chef Container ? y or n " -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
#  echo "Login to the Gemini Repo"
#  if !(docker login https://registry.gemini-systems.net/)
#  then
#	echo "Try Running Again with Corrrect Login Credentials. ERROR: Login Failed...Exiting..."
#	exit
#  fi         
  echo "Pull Chef Server from Registry..."
  docker pull registry.gemini-systems.net/gemini/gemini-chef
  echo "Continue to run chef ..."
  if docker ps -a |grep -aq gemini-chef; then
        docker rm -f gemini-chef
  fi
  echo "Listing the ips used in the setup..."
  /sbin/ifconfig |grep -B1 "inet addr" |awk '{ if ( $1 == "inet" ) { print $2 } else if ( $2 == "Link" ) { printf "%s:" ,$1 } }' |awk -F: '{ print $1 ": " $3 }'  
  echo "Choose one of the above accessible ips for Chef Deployment"
  read -p  "Enter the ip:" ip
  echo $ip
  if [ -z $ip ]
  then
        printf "HostIp is Mandatory .. exiting....\n"
        exit
  fi

  docker run -it -p 443:443 --privileged -v /etc/chef-server/ --name gemini-chef -h $ip -d registry.gemini-systems.net/gemini/gemini-chef
fi

