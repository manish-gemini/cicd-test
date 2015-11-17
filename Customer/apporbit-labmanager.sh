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
	rm -rf "/var/lib/apporbit/sshKey_root"
fi

mkdir -p "/var/dbstore"
# clean up of ssh key required 
mkdir -p /var/lib/apporbit/sshKey_root

chcon -Rt svirt_sandbox_file_t /var/dbstore >>$LOGFILE
chcon -Rt svirt_sandbox_file_t /var/lib/apporbit/sshKey_root >>$LOGFILE

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

if [ $# -eq 0 ]
  then
    themeName="apporbit"
fi

themeName=$1

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


echo "Setting up iptables rules..."
iptables -D INPUT -j REJECT --reject-with icmp-host-prohibited >>$LOGFILE
iptables -D  FORWARD -j REJECT --reject-with icmp-host-prohibited >>$LOGFILE

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
#docker rm -f apporbit-services apporbit-controller db  

#if docker ps -a |grep -a apporbit-mist; then
#	docker rm -f apporbit-mist
#fi

if docker ps -a |grep -aq apporbit-services; then
        docker rm -f apporbit-services >>$LOGFILE
fi

if docker ps -a |grep -aq apporbit-controller; then
        docker rm -f apporbit-controller >>$LOGFILE
fi

if docker ps -a |grep -aq db; then
        docker rm -f db >>$LOGFILE
fi

if docker ps -a |grep -aq apporbit-rmq; then
        docker rm -f apporbit-rmq >>$LOGFILE
fi

echo "db run .."
docker run --name db -e MYSQL_ROOT_PASSWORD=admin -e MYSQL_USER=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=apporbit_controller -v /var/dbstore:/var/lib/mysql -d mysql:5.6.24 >>$LOGFILE

docker run -m 2g -d --hostname rmq  --name apporbit-rmq -d registry.gemini-systems.net/gemini/gemini-rmq >>$LOGFILE
echo "Sleeping for 60 seconds"
sleep 60

if [ $deployType -eq 1 ]
then
	#sleep 500
	echo "pull apporbit base..."
	docker pull registry.gemini-systems.net/apporbit/apporbit-base >>$LOGFILE
	echo "pull gemini stack base..."
	docker pull registry.gemini-systems.net/gemini/gemini-stack-base >>$LOGFILE
	echo "pull gemini stack ..."
	docker pull registry.gemini-systems.net/gemini/gemini-stack:$pullId >>$LOGFILE
	echo "pull gemini platform base..."
	docker pull registry.gemini-systems.net/gemini/gemini-platform-base >>$LOGFILE
	echo "pull gemini platform..."
	docker pull registry.gemini-systems.net/gemini/gemini-platform:$pullId >>$LOGFILE
#	echo  "pull gemini-mist..."
#	docker pull registry.gemini-systems.net/gemini/gemini-mist
	echo "gemini stack run..."
	if docker ps -a |grep -aq gemini-chef; then
		docker run -t --name gemini-stack -e GEMINI_INT_REPO=$internalRepo -e CHEF_URL=https://$hostip:9443 -e MYSQL_HOST=db -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_mist -e GEMINI_STACK_IPANEMA=1 --link db:db --link gemini-rmq:rmq -v /var/lib/gemini/sshKey_root:/root --volumes-from gemini-chef -v /var/log/gemini/stack:/var/log/gemini -d registry.gemini-systems.net/gemini/gemini-stack:$pullId	
		echo "platform run ..."
		docker run -t --name gemini-platform -p 80:3000 -e LOG_LEVEL=$_LOG_LEVEL_ -e MAX_POOL_SIZE=$max_app_processes  -e CHEF_URL=https://$hostip:9443 -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_platform -e ON_PREM_MODE=$onPremMode -e THEME_NAME=$themeName --link db:db --link gemini-rmq:rmq --volumes-from gemini-chef -v /var/log/gemini/platform:/var/log/gemini -d registry.gemini-systems.net/gemini/gemini-platform:$pullId
	else
		docker run -t --name gemini-stack -e GEMINI_INT_REPO=$internalRepo -e MYSQL_HOST=db -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_mist  -e GEMINI_STACK_IPANEMA=1 --link db:db --link gemini-rmq:rmq -v /var/lib/gemini/sshKey_root:/root -v /var/log/gemini/stack:/var/log/gemini -d  registry.gemini-systems.net/gemini/gemini-stack:$pullId	
		echo "platform run ..."
		docker run -t --name gemini-platform -p 80:3000 -e LOG_LEVEL=$_LOG_LEVEL_ -e MAX_POOL_SIZE=$max_app_processes -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_platform -e ON_PREM_MODE=$onPremMode -e THEME_NAME=$themeName --link db:db --link gemini-rmq:rmq -v /var/log/gemini/platform:/var/log/gemini -d registry.gemini-systems.net/gemini/gemini-platform:$pullId

	fi
	echo "end ..."

elif [ $deployType -eq 2 ]
then
   
	echo "gemini stack run..."
	if docker ps -a |grep -aq gemini-chef; then
		docker run -t --name gemini-stack -e GEMINI_INT_REPO=$internalRepo -e CHEF_URL=https://$hostip:9443 -e MYSQL_HOST=db -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_mist -e GEMINI_STACK_IPANEMA=1 --link db:db --link gemini-rmq:rmq -v /var/lib/gemini/sshKey_root:/root -v /var/log/gemini/stack:/var/log/gemini --volumes-from gemini-chef -d gemini/gemini-stack    	
		echo "platform run ..."
		docker run -t --name gemini-platform -p 80:3000 -e LOG_LEVEL=$_LOG_LEVEL_ -e MAX_POOL_SIZE=$max_app_processes -e CHEF_URL=https://$hostip:9443 -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_platform -e ON_PREM_MODE=$onPremMode -e THEME_NAME=$themeName  --link db:db --link gemini-rmq:rmq --volumes-from gemini-chef -v /var/log/gemini/platform:/var/log/gemini -d gemini/gemini-platform
	else
		docker run -t --name gemini-stack -e GEMINI_INT_REPO=$internalRepo -e MYSQL_HOST=db -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_mist -e GEMINI_STACK_IPANEMA=1 --link db:db --link gemini-rmq:rmq -v /var/log/gemini/stack:/var/log/gemini  -v /var/lib/gemini/sshKey_root:/root -d gemini/gemini-stack    	
		echo "platform run ..."
		docker run -t --name gemini-platform -p 80:3000 -e LOG_LEVEL=$_LOG_LEVEL_ -e MAX_POOL_SIZE=$max_app_processes -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_platform -e ON_PREM_MODE=$onPremMode -e THEME_NAME=$themeName --link db:db --link gemini-rmq:rmq -v /var/log/gemini/platform:/var/log/gemini -d gemini/gemini-platform
	fi
	echo "end ..."
fi
echo "`date` Finishing apporbit-labmanager.sh" >>$LOGFILE
