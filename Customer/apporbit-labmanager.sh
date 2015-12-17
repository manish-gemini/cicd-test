#!/bin/bash
_LOG_LEVEL_="DEBUG"
LOGFILE=apporbit-install.log
echo "`date` Starting apporbit-labmanager.sh" >>$LOGFILE
echo "Enter the deploy type:"
echo "Deploy from Registry = 1"
echo "Deploy from Tar file = 2"

read -p "Default(1):" deployType
deployType=${deployType:-1}
echo $deployType

if [ $deployType -eq 2 ]
then
	echo "Enter the Full location of the Tar File :"
	read tarballLocation
	echo $tarballLocation

	echo "Check for File Existence."

	echo "untar the package..."

	mkdir -p /tmp
	cd /tmp
	tar -xvf $tarballLocation

	cd /tmp/appOrbitPackages/

	echo "Loading Platform ... "
	docker load < apporbit-controller.tar
	echo "Loading Stack ..."
	docker load < apporbit-services.tar
	echo "Loading Mysql ..."
	docker load < mysql.tar
	echo "Loading Rmq ..."
	docker load < apporbit-rmq.tar
	echo "Loading Docs ..."
	docker load < apporbit-docs.tar
fi

if [ $deployType -eq 1 ]
then
	read -p "Enter the Build ID [Default: latest]:" pullId
fi

intrepo="http://repos.gsintlab.com/repos/"

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

chcon -Rt svirt_sandbox_file_t /var/dbstore >>$LOGFILE
chcon -Rt svirt_sandbox_file_t /var/lib/apporbit/sshKey_root >>$LOGFILE
chcon -Rt svirt_sandbox_file_t /var/lib/apporbit/sslkeystore >>$LOGFILE
chcon -Rt svirt_sandbox_file_t /var/log/apporbit/services >>$LOGFILE
chcon -Rt svirt_sandbox_file_t /var/log/apporbit/controller >>$LOGFILE


if [ ! -f /var/lib/apporbit/sslkeystore/apporbitserver.key ] || [ ! -f /var/lib/apporbit/sslkeystore/apporbitserver.crt ]
then
	echo "1) use existing certificate"
	echo "2) Create a self signed certificate"
	read -p "Enter the type of ssl certificate [Default:2]:" ssltype
	ssltype=${ssltype:-2}
	if [ $ssltype -eq 2 ]
	then
		#Generate SSL Certiticate for https and put it in a volume mount controller location.
		openssl req -new -newkey rsa:4096 -days 365 -nodes -x509 -subj "/C=US/ST=NY/L=appOrbit/O=Dis/CN=www.apporbit.com" -keyout /var/lib/apporbit/sslkeystore/apporbitserver.key -out /var/lib/apporbit/sslkeystore/apporbitserver.crt
	else
		echo "Rename your certificate files as apporbitserver.crt and key as apporbitserver.key"
		read -p "Enter the location where your certificate and key file exist:" sslKeyDir
		if [ ! -d $sslKeyDir ]
		then
			echo "Dir does not exist, Exiting..."
			exit
		fi
		cd $sslKeyDir
		if [ ! -f apporbitserver.key ] || [ ! -f apporbitserver.crt ]
		then
			echo "key and certificate files are missing."
			echo "Note that key and crt file name should be apporbitserver.key and apporbitserver.crt. Rename your files accordingly and retry."
			exit
		fi
		cp -f apporbitserver.key /var/lib/apporbit/sslkeystore/apporbitserver.key
		cp -f apporbitserver.crt /var/lib/apporbit/sslkeystore/apporbitserver.crt
	fi
fi

email_id="admin@apporbit.com"
EMAILID=$email_id
printf "Mode of Operation: \n Type 1 for ON PREM MODE \n Type 2 for SAAS MODE :"
read -p "Default(1):" onPremMode
onPremMode=${onPremMode:-1}
echo $onPremMode
if [ $onPremMode -eq 1 ]
then
	onPremMode=true
	read -p "Enter the User Email id for On Prem Deployment. Default($email_id):" emailID
	EMAILID=${emailID:-$email_id}
else
	onPremMode=false
fi
echo $onPremMode

if [ $# -eq 0 ]
then
    themeName="apporbit"
else
	themeName=$1
fi
echo $themeName

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


ip=`curl -s http://whatismyip.akamai.com; echo`
printf "Enter the Host IP :"
read -p "Default($ip):" hostip
hostip=${hostip:-$ip}
echo $hostip

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

if docker ps -a |grep -a apporbit-rmq; then
   docker rm -f apporbit-rmq
fi

if docker ps -a | grep -a apporbit-docs; then
   docker rm -f apporbit-docs
fi

echo "db run .."
docker run --name db --restart=always -e MYSQL_ROOT_PASSWORD=admin -e MYSQL_USER=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=apporbit_controller -v /var/dbstore:/var/lib/mysql -d mysql:5.6.24 >>$LOGFILE

echo "Sleeping for 60 seconds"
sleep 60

if [ $deployType -eq 1 ]
then
	#sleep 500
	echo "pull apporbit base..."
	docker pull registry.apporbit.com/apporbit/apporbit-base >>$LOGFILE
	echo "pull apporbit services base..."
	docker pull registry.apporbit.com/apporbit/apporbit-services-base >>$LOGFILE
	echo "pull apporbit services ..."
	docker pull registry.apporbit.com/apporbit/apporbit-services:$pullId >>$LOGFILE
	echo "pull apporbit controller base..."
	docker pull registry.apporbit.com/apporbit/apporbit-controller-base >>$LOGFILE
	echo "pull apporbit controller..."
	docker pull registry.apporbit.com/apporbit/apporbit-controller:$pullId >>$LOGFILE
	echo "pull apporbit Rabbit Mq"
	docker pull registry.apporbit.com/apporbit/apporbit-rmq >> $LOGFILE
	echo "pull apporbit Docs"
	docker pull registry.apporbit.com/apporbit/apporbit-docs >> $LOGFILE
	
	docker run -m 2g -d --hostname rmq --name apporbit-rmq --restart=always -d registry.apporbit.com/apporbit/apporbit-rmq >>$LOGFILE
	docker run --name apporbit-docs --restart=always -p 9080:80 -d registry.apporbit.com/apporbit/apporbit-docs >>$LOGFILE

	echo "apporbit services run..."
	if docker ps |grep -aq apporbit-chef; then
		docker run -t --name apporbit-services --restart=always -e GEMINI_INT_REPO=$internalRepo -e CHEF_URL=https://$hostip:9443 -e MYSQL_HOST=db -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=apporbit_mist -e GEMINI_STACK_IPANEMA=1 --link db:db --link apporbit-rmq:rmq -v /var/lib/apporbit/sshKey_root:/root --volumes-from apporbit-chef -v /var/log/apporbit/services:/var/log/apporbit -d registry.apporbit.com/apporbit/apporbit-services:$pullId
		echo "controller run ..."
		docker run -t --name apporbit-controller --restart=always -p 80:80 -p 443:443 -e ONPREM_EMAIL_ID=$EMAILID -e LOG_LEVEL=$_LOG_LEVEL_ -e MAX_POOL_SIZE=$max_app_processes  -e CHEF_URL=https://$hostip:9443 -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=apporbit_controller -e ON_PREM_MODE=$onPremMode -e THEME_NAME=$themeName --link db:db --link apporbit-rmq:rmq --volumes-from apporbit-chef -v /var/log/apporbit/controller:/var/log/apporbit  -v /var/lib/apporbit/sslkeystore/:/home/apporbit/apporbit-controller/sslkeystore -d registry.apporbit.com/apporbit/apporbit-controller:$pullId
	else
		docker run -t --name apporbit-services --restart=always -e GEMINI_INT_REPO=$internalRepo -e MYSQL_HOST=db -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=apporbit_mist  -e GEMINI_STACK_IPANEMA=1 --link db:db --link apporbit-rmq:rmq -v /var/lib/apporbit/sshKey_root:/root -v /var/log/apporbit/services:/var/log/apporbit -d  registry.apporbit.com/apporbit/apporbit-services:$pullId	
		echo "controller run ..."
		docker run -t --name apporbit-controller --restart=always -p 80:80 -p 443:443 -e ONPREM_EMAIL_ID=$EMAILID -e LOG_LEVEL=$_LOG_LEVEL_ -e MAX_POOL_SIZE=$max_app_processes -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=apporbit_controller -e ON_PREM_MODE=$onPremMode -e THEME_NAME=$themeName --link db:db --link apporbit-rmq:rmq -v /var/log/apporbit/controller:/var/log/apporbit  -v /var/lib/apporbit/sslkeystore/:/home/apporbit/apporbit-controller/sslkeystore -d registry.apporbit.com/apporbit/apporbit-controller:$pullId

	fi
	echo "end ..."

elif [ $deployType -eq 2 ]
then
    docker run -m 2g -d --hostname rmq  --name apporbit-rmq --restart=always -d apporbit/apporbit-rmq >>$LOGFILE
	docker run --name apporbit-docs --restart=always -p 9080:80 -d apporbit/apporbit-docs >>$LOGFILE
	echo "apporbit services run..."
	if docker ps -a |grep -aq apporbit-chef; then
		docker run -t --name apporbit-services -e GEMINI_INT_REPO=$internalRepo -e CHEF_URL=https://$hostip:9443 -e MYSQL_HOST=db -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=apporbit_mist -e GEMINI_STACK_IPANEMA=1 --link db:db --link apporbit-rmq:rmq -v /var/lib/apporbit/sshKey_root:/root -v /var/log/apporbit/services:/var/log/apporbit --volumes-from apporbit-chef -d apporbit/apporbit-services
		echo "controller run ..."
		docker run -t --name apporbit-controller -p 80:80 -p 443:443  -e LOG_LEVEL=$_LOG_LEVEL_ -e ONPREM_EMAIL_ID=$EMAILID -e MAX_POOL_SIZE=$max_app_processes -e CHEF_URL=https://$hostip:9443 -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=apporbit_controller -e ON_PREM_MODE=$onPremMode -e THEME_NAME=$themeName  --link db:db --link apporbit-rmq:rmq --volumes-from apporbit-chef -v /var/log/apporbit/controller:/var/log/apporbit  -v /var/lib/apporbit/sslkeystore/:/home/apporbit/apporbit-controller/sslkeystore -d apporbit/apporbit-controller
	else
		docker run -t --name apporbit-services -e GEMINI_INT_REPO=$internalRepo -e MYSQL_HOST=db -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=apporbit_mist -e GEMINI_STACK_IPANEMA=1 --link db:db --link apporbit-rmq:rmq -v /var/log/apporbit/services:/var/log/apporbit  -v /var/lib/apporbit/sshKey_root:/root -d apporbit/apporbit-services    	
		echo "controller run ..."
		docker run -t --name apporbit-controller -p 80:80 -p 443:443  -e LOG_LEVEL=$_LOG_LEVEL_ -e ONPREM_EMAIL_ID=$EMAILID -e MAX_POOL_SIZE=$max_app_processes -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=apporbit_controller -e ON_PREM_MODE=$onPremMode -e THEME_NAME=$themeName --link db:db --link apporbit-rmq:rmq -v /var/log/apporbit/controller:/var/log/apporbit  -v /var/lib/apporbit/sslkeystore/:/home/apporbit/apporbit-controller/sslkeystore -d apporbit/apporbit-controller
	fi
	echo "end ..."
fi
echo "`date` Finishing apporbit-labmanager.sh" >>$LOGFILE

echo "Please change your default password 'admin1234' by logging into the User Management Console in the UI at https://${hostip}/users"