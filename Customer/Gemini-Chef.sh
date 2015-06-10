#!/bin/bash

##Docker Run command for Chef
read -p "Do you want to continue Deploy Chef Container ? y or n " -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
  echo "Login to the Gemini Repo"
  if !(docker login https://secure-registry.gsintlab.com)
  then
	echo "Try Running Again with Corrrect Login Credentials. ERROR: Login Failed...Exiting..."
	exit
  fi         
  echo "Pull Chef Server from Internal Registry..."
  docker pull secure-registry.gsintlab.com/gemini/gemini-chef
  echo "Continue to run chef ..."
  docker rm -f gemini-chef
  ip=`curl -s http://ipecho.net/plain; echo`
  docker run -it -p 443:443 --privileged -v /etc/chef-server/ --name gemini-chef -h $ip -d secure-registry.gsintlab.com/gemini/gemini-chef
fi

