#!/bin/bash


#### SCRIPT TO DO PRE INSTALLATION STEPS FOR GEMINI

## Check if RAM size is 4GB

## Display valid Sys info and see if any value needs to consider for Minimum Requirements

##Docker Run command for Chef
if docker ps -a |grep -aq gemini-chef; then
  echo "Gemini Chef Container is already runnning. The container will first be removed."
  read -r -p "Do you want to continue? y or n " -n 1 -r installChef
  echo    # (optional) move to a new line
  if [[ $installChef =~ ^[Yy]$ ]]
  then
   echo "Removing existing Chef Server container"
   docker rm -f gemini-chef 
  else
   echo "Exiting without installing Chef Server"
   exit 1
  fi
fi
  echo "Login to the Internal Registry"
  docker login https://secure-registry.gsintlab.com
  echo "Pull Chef Server from Internal Registry..."
  docker pull secure-registry.gsintlab.com/gemini/gemini-chef:0.9
  echo "Continue to run chef ..."
  ip=`curl -s http://whatismyip.akamai.com; echo`
  echo "Using ip address: $ip"
  docker run -it -p 443:443 --privileged -v /etc/chef-server/ --name gemini-chef -h $ip -d secure-registry.gsintlab.com/gemini/gemini-chef:0.9
