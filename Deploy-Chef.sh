#!/bin/bash


#### SCRIPT TO DO PRE INSTALLATION STEPS FOR GEMINI

## Check if RAM size is 4GB

## Display valid Sys info and see if any value needs to consider for Minimum Requirements

##Docker Run command for Chef
read -p "Do you want to continue Deploy Chef Container ? y or n " -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
  echo "Login to the Internal Registry"
  docker login https://secure-registry.gsintlab.com
  echo "Pull Chef Server from Internal Registry..."
  docker pull secure-registry.gsintlab.com/gemini/gemini-chef
  echo "Continue to run chef ..."
  docker rm -f gemini-chef
  ip=`curl -s http://ipecho.net/plain; echo`
  docker run -it -p 443:443 --privileged -v /etc/chef-server/ --name gemini-chef -h $ip -d secure-registry.gsintlab.com/gemini/gemini-chef
fi

