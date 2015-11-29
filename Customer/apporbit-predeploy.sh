#!/bin/bash


command_exists() {
	command -v "$@" > /dev/null 2>&1
}

LOGFILE=apporbit-install.log
echo "`date` Starting apporbit-predeploy.sh" >>$LOGFILE

echo "Check for PreRequisite...."
#CHECK FOR PREREQUISTE and LETS USER KNOW 

echo "Installing appOrbit  containers requires selinux to be turned off."
response="y"
read -p "Do you want to continue ? [y]/n : " -r 
echo
REPLY=${REPLY:-$response}
if [[ $REPLY =~ ^[Yy] ]]
then
    setenforce 0
    echo "successfully set sestatus to permissive";
else
    echo "SELinux is currently on.1 sestatus must be set to permissive for deployment. Exiting"
    exit;
fi 

if [ ! -f /etc/yum.repos.d/apporbit.repo ]
then
   cp apporbit.repo /etc/yum.repos.d/
fi

rpm -q ntp
if [ $? -ne 0 ]
then
   yum install -y ntp
fi
echo "Time will be synchronized with time.nist.gov for this host"
ntpdate -b -u time.nist.gov >>$LOGFILE
echo "...."

#Print the Number of VCPUs
echo "Number of CPU : " `nproc`
echo "Total RAM Size in Bytes :" `vmstat -s | grep 'total memory'`

echo "Check for Docker Version "
if command_exists docker  
then
	echo "Docker exists:" `docker -v` "from" `rpm -qa docker`
else 
        echo "Docker is not installed. Installing docker..."
	yum -y update >>$LOGFILE
	yum -y install docker-1.7.1 >>$LOGFILE
	systemctl enable docker.service >>$LOGFILE
	systemctl start docker.service >>$LOGFILE
        if ! command_exists docker  
        then
           echo "Docker installation failed. Exiting."
           exit 
        fi
fi

echo "Flush Iptables"
iptables -F

echo "Login to appOrbit Docker Registry using crendentials obtained from your appOrbit business contact:"
docker login https://registry.apporbit.com/



echo "`date` Finishing apporbit-predeploy.sh" >>$LOGFILE
