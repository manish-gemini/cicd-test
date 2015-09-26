#!/bin/bash

echo "Check for PreRequisite...."
#CHECK FOR PREREQUISTE and LETS USER KNOW 

#Print the Number of VCPUs

echo "Number of CPU : "
nproc

echo "Total RAM Size in Bytes :"
vmstat -s | grep 'total memory'

echo "Check for Docker Version "
if docker -v | grep 1.5 > /dev/null
then
	echo "Docker Version 1.5 exists"
elif docker -v | grep 1.6 > /dev/null
then
	echo "Docker Version 1.6 exists"
else 
	yum -y update
	yum -y install docker
	systemctl enable docker.service
	systemctl start docker.service
fi

echo "Setting sestatus to permissive"
response="y"
read -p "Do you want to continue ? [y]/n : " -r
echo
REPLY=${REPLY:-$response}
if [[ $REPLY =~ ^[Yy] ]]
then
    setenforce 0
    echo "successfully set sestatus to permissive";
else
    echo "sestatus must be set to permissive for deployment."
    exit;
fi 

echo "Flush Iptables"

iptables -F

echo "Login to Gemini Docker Registry:"

docker login https://registry.gemini-systems.net/



