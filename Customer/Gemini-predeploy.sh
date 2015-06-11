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

echo "Flush Iptables"

iptables -F

echo "Install Security Certificate for Docker repo access"


numOfTry=0
until [ $numOfTry -ge 5 ]
do
	echo "Enter the Full path of the Certificate file:"
	read -p "Default(${PWD}):" certFilePath
	certFilePath=${certFilePath:-${PWD}}
	echo $certFilePath
        certFile=$certFilePath/server.crt
	echo $certFile
	if [ ! -f $certFile ]
	then
	     echo "File seems to not exist.. "
             if [ $numOfTry = 4 ]
	     then
		echo "ERROR: NO VALID CERTIFICATE FILE ...Exiting..."
		exit
	     fi
	 else
	      break
         fi
	 numOfTry=$[$numOfTry+1]
	     
done
echo "Installing Certificate file"
yum install -y ca-certificates
update-ca-trust enable
cp $certFile /etc/pki/ca-trust/source/anchors/.
update-ca-trust extract
service docker restart
docker login https://secure-registry.gsintlab.com



