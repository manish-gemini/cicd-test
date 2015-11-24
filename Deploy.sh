#!/bin/bash

_LOG_LEVEL_="DEBUG"
echo "Enter the deploy type:"
echo "Deploy from Local image = 1"
echo "Deploy from internal registry = 2"
echo "Dev Mode with Volume Mount Option = 3"

read -p "Default(1):" deployType
deployType=${deployType:-1}
echo $deployType

if [ $deployType -eq 2 ]
then
docker login https://secure-registry.gsintlab.com
read -p  "Enter the Build ID [Default: latest]:" pullId
fi

intrepo="http://repos.gsintlab.com/repos/"
echo "Enter the Internal Package Repo :[http://repos.gsintlab.com/repos]:"
read -p "Default($intrepo):" internalRepo
internalRepo=${internalRepo:-$intrepo}
echo $internalRepo
echo "Do you want to clean up the setup (removes db, Rabbitmq Data etc.,) ?"
echo "press 1 to clean the setup."
echo "press 2 to retain the older entries.."
read -p "Default(2):" cleanSetup
cleanSetup=${cleanSetup:-2}
echo $cleanSetup

if [ $cleanSetup -eq 1 ]
then
	rm -rf "/var/dbstore"
	rm -rf "/var/lib/apporbit/"
	rm -rf "/var/log/apporbit/"
fi

mkdir -p "/var/dbstore"
mkdir -p "/var/log/apporbit/controller"
mkdir -p "/var/log/apporbit/services"
mkdir -p "/var/lib/apporbit/sshKey_root"
mkdir -p "/var/lib/apporbit/sslkeystore"

chcon -Rt svirt_sandbox_file_t /var/dbstore
chcon -Rt svirt_sandbox_file_t /var/lib/apporbit/sshKey_root
chcon -Rt svirt_sandbox_file_t /var/log/apporbit/services
chcon -Rt svirt_sandbox_file_t /var/log/apporbit/controller
chcon -Rt svirt_sandbox_file_t /var/lib/apporbit/sslkeystore

printf "Mode of Operation: \n Type 1 for ON PREM MODE \n Type 2 for SAAS MODE :"
read -p "Default(1):" onPremMode
onPremMode=${onPremMode:-1}
echo $onPremMode
if [ $onPremMode -eq 1 ]
then
	onPremMode=true
else
	onPremMode=false
fi
echo $onPremMode

theme="apporbit"
printf "Enter the Theme Name :"
read -p "Default($theme):" themeName
themeName=${themeName:-$theme}
echo $themeName

ip=`curl -s http://whatismyip.akamai.com ; echo`
printf "Enter the Host IP :"
read -p "Default($ip):" hostip
hostip=${hostip:-$ip}
echo $hostip
if [ -z $hostip ]
then
	printf "HostIp is Mandatory .. exiting....\n"
exit
fi

echo "Max pool Size"
B=1024
KB=$((B * B))
nvcpu=`nproc`
ramkb=$(grep MemTotal /proc/meminfo | awk '{print $2}')
ramgb=$(((ramkb+(KB-1))/KB))
RAM_PER_PROCESS=$(((ramgb+(nvcpu-1))/nvcpu))
echo "RAM_PER_PROCESS: " $RAM_PER_PROCESS
adjvar1=75
adjvar2=100
if [ $RAM_PER_PROCESS = 0 ]
then
	RAM_PER_PROCESS=1
fi
max_app_processes=$(((ramgb*adjvar1)/(RAM_PER_PROCESS*adjvar2)))
if [ $max_app_processes = 0 ]
then
	max_app_processes=1
fi

echo "Setting MAX PHUSION PROCESS:"$max_app_processes

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

rpm -q ntp
if [ $? -ne 0 ]
then
   yum install -y ntp
fi

echo "Time sync processing..."
ntpdate -b -u time.nist.gov

if [ ! -f /etc/logrotate.d/apporbitLogRotate ]
then
        echo "/var/log/apporbit/controller/*log /var/log/apporbit/services/*log {
          daily
          missingok
          size 50M
          rotate 20
          compress
          copytruncate
        }" > /etc/logrotate.d/apporbitLogRotate
fi

echo "continue to deploy..."
echo "Removing if any existing docker process with same name to avoid conflicts"

if docker ps -a |grep -aq apporbit-services;
then
   docker rm -f apporbit-services
fi

if docker ps -a |grep -aq apporbit-controller;
then
   docker rm -f apporbit-controller
fi

if docker ps -a |grep -aq db;
then
   docker rm -f db
fi

if docker ps -a |grep -a apporbit-mist; then
   docker rm -f apporbit-mist
fi

if docker ps -a |grep -a apporbit-rmq; then
   docker rm -f apporbit-rmq
fi

if docker ps -a | grep -a apporbit-docs; then
   docker rm -f apporbit-docs
fi

#Generate SSL Certiticate for https and put it in a volume mount controller location.
openssl genrsa -des3 -passout pass:x -out /var/lib/apporbit/sslkeystore/apporbitserver.pass.key 2048
openssl rsa -passin pass:x -in /var/lib/apporbit/sslkeystore/apporbitserver.pass.key -out /var/lib/apporbit/sslkeystore/apporbitserver.key
rm -f /var/lib/apporbit/sslkeystore/apporbitserver.pass.key
echo "Enter required information to generate self signed certificate"
openssl req -new -key /var/lib/apporbit/sslkeystore/apporbitserver.key -out /var/lib/apporbit/sslkeystore/apporbitserver.csr
openssl x509 -req -days 365 -in /var/lib/apporbit/sslkeystore/apporbitserver.csr -signkey server.key -out /var/lib/apporbit/sslkeystore/apporbitserver.crt

#docs container
docker run --name apporbit-docs --restart=always -p 9080:80 -d secure-registry.gsintlab.com/apporbit/apporbit-docs
echo "db run .."
docker run --name db --restart=always -e MYSQL_ROOT_PASSWORD=admin -e MYSQL_USER=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=apporbit_controller -v /var/dbstore:/var/lib/mysql -d mysql:5.6.24
# Setting rabbit mq menory to 2GB
# Rabbit mq uses 40% of memory, so rabbit mq will use 800MB 
docker run -m 2g -d --hostname rmq --restart=always --name apporbit-rmq -d secure-registry.gsintlab.com/apporbit/apporbit-rmq
#apporbit/apporbit-rmq
sleep 60

if [ $deployType -eq 2 ]
then
        echo $pullId
	echo "pull apporbit base..."
	docker pull secure-registry.gsintlab.com/apporbit/apporbit-base
	echo "pull apporbit services base..."
	docker pull secure-registry.gsintlab.com/apporbit/apporbit-services-base
	echo "pull apporbit services  ..."
	docker pull secure-registry.gsintlab.com/apporbit/apporbit-services:$pullId
	echo "pull apporbit controller base..."
	docker pull secure-registry.gsintlab.com/apporbit/apporbit-controller-base
	echo "pull apporbit controller..."
	docker pull secure-registry.gsintlab.com/apporbit/apporbit-controller:$pullId


	if docker ps -a |grep -a apporbit-chef; then
		docker run -t --name apporbit-services --restart=always -e GEMINI_INT_REPO=$internalRepo -e CHEF_URL=https://$hostip:9443 -e MYSQL_HOST=db -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=apporbit_mist -e GEMINI_STACK_IPANEMA=1 --link db:db --link apporbit-rmq:rmq -v /var/lib/apporbit/sshKey_root:/root --volumes-from apporbit-chef -v /var/log/apporbit/services:/var/log/apporbit -d  secure-registry.gsintlab.com/apporbit/apporbit-services

		echo "controller run ..."
		docker run -t --name apporbit-controller --restart=always -p 80:80 -p 443:443 -e LOG_LEVEL=$_LOG_LEVEL_ -e MAX_POOL_SIZE=$max_app_processes  -e CHEF_URL=https://$hostip:9443 -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=apporbit_controller -e ON_PREM_MODE=$onPremMode -e THEME_NAME=$themeName --link db:db --link apporbit-rmq:rmq --volumes-from apporbit-chef -v /var/log/apporbit/controller:/var/log/apporbit -v /var/lib/apporbit/sslkeystore:/root/sslkeystore -d secure-registry.gsintlab.com/apporbit/apporbit-controller
	else
		docker run -t --name apporbit-services --restart=always -e GEMINI_INT_REPO=$internalRepo -e MYSQL_HOST=db -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=apporbit_mist  -e GEMINI_STACK_IPANEMA=1 --link db:db --link apporbit-rmq:rmq -v /var/lib/apporbit/sshKey_root:/root -v /var/log/apporbit/services:/var/log/apporbit -d  secure-registry.gsintlab.com/apporbit/apporbit-services	
		echo "controller run ..."
		docker run -t --name apporbit-controller --restart=always -p 80:80 -p 443:443 -e LOG_LEVEL=$_LOG_LEVEL_ -e MAX_POOL_SIZE=$max_app_processes -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=apporbit_controller -e ON_PREM_MODE=$onPremMode -e THEME_NAME=$themeName --link db:db --link apporbit-rmq:rmq -v /var/log/apporbit/controller:/var/log/apporbit -v /var/lib/apporbit/sslkeystore:/root/sslkeystore -d secure-registry.gsintlab.com/apporbit/apporbit-controller

	fi

	echo "end ..."

elif [ $deployType -eq 1 ]
then
   
	echo "apporbit services run..."
	if docker ps -a |grep -a apporbit-chef; then
		docker run -t --name apporbit-services --restart=always -e GEMINI_INT_REPO=$internalRepo -e CHEF_URL=https://$hostip:9443 -e MYSQL_HOST=db -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=apporbit_mist -e GEMINI_STACK_IPANEMA=1 --link db:db --link apporbit-rmq:rmq -v /var/lib/apporbit/sshKey_root:/root -v /var/log/apporbit/services:/var/log/apporbit --volumes-from apporbit-chef -d apporbit/apporbit-services  	
		echo "controller run ..."
		docker run -t --name apporbit-controller --restart=always -p 80:80 -p 443:443 -e LOG_LEVEL=$_LOG_LEVEL_ -e MAX_POOL_SIZE=$max_app_processes -e CHEF_URL=https://$hostip:9443 -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=apporbit-controller -e ON_PREM_MODE=$onPremMode -e THEME_NAME=$themeName  --link db:db --link apporbit-rmq:rmq --volumes-from apporbit-chef -v /var/log/apporbit/controller:/var/log/apporbit -v /var/lib/apporbit/sslkeystore:/root/sslkeystore -d apporbit/apporbit-controller
	else
		docker run -t --name apporbit-services --restart=always -e GEMINI_INT_REPO=$internalRepo -e MYSQL_HOST=db -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=apporbit_mist -e GEMINI_STACK_IPANEMA=1 --link db:db --link apporbit-rmq:rmq -v /var/log/apporbit/services:/var/log/apporbit  -v /var/lib/apporbit/sshKey_root:/root -d apporbit/apporbit-services    	
		echo "controller run ..."
		docker run -t --name apporbit-controller --restart=always -p 80:80 -p 443:443 -e LOG_LEVEL=$_LOG_LEVEL_ -e MAX_POOL_SIZE=$max_app_processes -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=apporbit_controller -e ON_PREM_MODE=$onPremMode -e THEME_NAME=$themeName --link db:db --link apporbit-rmq:rmq -v /var/log/apporbit/controller:/var/log/apporbit -v /var/lib/apporbit/sslkeystore:/root/sslkeystore -d apporbit/apporbit-controller
	fi
	echo "end ..."
else
	echo "Enter services dir : example : /opt/mydevdir/ :"
	read servicesDir
	echo "Enter controller dir : example : /opt/mydevDir/ :"
	read controllerDir
        cd $servicesDir/Gemini-poc-stack/mist-cgp

   	echo "Enter the Mist Branch to pull jar file:"
	echo "Master = 1"
        echo "Integration = 2"
        echo "Integration-features = 3"
        read -p "Default(2):" mistRepo
        mistRepo=${mistRepo:-"2"}
        echo $mistRepo
        if [ -f run.jar ]; then
            rm -f run.jar
        fi
        if [ $mistRepo == 1 ]
        then
           wget http://repos.gsintlab.com/repos/mist/master/run.jar
        elif [ $mistRepo == 2 ]
        then
           wget http://repos.gsintlab.com/repos/mist/integration/run.jar
        else
           wget http://repos.gsintlab.com/repos/mist/integration-features/run.jar
        fi

        cd $controllerDir/Gemini-poc-mgnt/
	rm -rf Gemfile.lock
        cp -f Gemfile-master Gemfile

	echo "apporbit services DEV MODE run..."
	if docker ps -a |grep -a apporbit-chef; then
		docker run -t --name apporbit-services -e GEMINI_INT_REPO=$internalRepo -e CHEF_URL=https://$hostip:9443 -e MYSQL_HOST=db -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=apporbit_mist -e GEMINI_STACK_IPANEMA=1 -v $servicesDir/Gemini-poc-stack:/home/apporbit/apporbit-services --link db:db --link apporbit-rmq:rmq -v /var/lib/apporbit/sshKey_root:/root -v /var/log/apporbit/services:/var/log/apporbit --volumes-from apporbit-chef -d  apporbit/apporbit-services
		echo "controller run ..."
		docker run -t --name apporbit-controller -p 80:80 -p 443:443 -e LOG_LEVEL=$_LOG_LEVEL_ -e MAX_POOL_SIZE=$max_app_processes -e CHEF_URL=https://$hostip:9443 -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=apporbit_controller -e ON_PREM_MODE=$onPremMode -e THEME_NAME=$themeName  -v $controllerDir/Gemini-poc-mgnt:/home/apporbit/apporbit-controller --link db:db --link apporbit-rmq:rmq --volumes-from apporbit-chef -v /var/log/apporbit/controller:/var/log/apporbit -v /var/lib/apporbit/sslkeystore:/root/sslkeystore -d apporbit/apporbit-controller
	else
		docker run -t --name apporbit-services -e GEMINI_INT_REPO=$internalRepo -e MYSQL_HOST=db -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=apporbit_mist -e GEMINI_STACK_IPANEMA=1 -v $servicesDir/Gemini-poc-stack:/home/apporbit/apporbit-services --link db:db --link apporbit-rmq:rmq -v /var/lib/apporbit/sshKey_root:/root -v /var/log/apporbit/services:/var/log/apporbit -d  apporbit/apporbit-services
		echo "controller run ..."
		docker run -t --name apporbit-controller -p 80:80 -p 443:443 -e LOG_LEVEL=$_LOG_LEVEL_ -e MAX_POOL_SIZE=$max_app_processes -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=apporbit_controller -e ON_PREM_MODE=$onPremMode -e THEME_NAME=$themeName -v $controllerDir/Gemini-poc-mgnt:/home/apporbit/apporbit-controller --link db:db --link apporbit-rmq:rmq -v /var/log/apporbit/controller:/var/log/apporbit -v /var/lib/apporbit/sslkeystore:/root/sslkeystore -d apporbit/apporbit-controller
	fi
	echo "end ...."
fi

