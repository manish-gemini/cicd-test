#!/bin/bash
echo "Time sync processing..."
yum install -y ntp
ntpdate -b -u time.nist.gov
echo "...."
>>>>>>> Deploy update
echo "Enter the deploy type:"
echo "Deploy from Local image = 1"
echo "Deploy from internal registry = 2"
echo "Dev Mode with Volume Mount Option = 3"
echo "Deploy from a insecure registry = 4"
echo "Deploy from tar file = 5"

read -p "Default(1):" deployType
deployType=${deployType:-1}
echo $deployType

if [ $deployType -eq 5 ]
then
	echo "Enter the Full location of the Tar File :"
	read tarballLocation
	echo $tarballLocation

	echo "Check for File Existence."

	echo "untar the package..."

	mkdir -p /tmp
	cd /tmp
	tar -xvf $tarballLocation

	cd /tmp/GeminiPackages/

	echo "Loading Platform ... "
	docker load < gemini-platform.tar
	echo "Loading Stack ..."
	docker load < gemini-stack.tar
	echo "Loading Mysql ..."
	docker load < mysql.tar
fi

if [ $deployType -eq 2 ]
then
#Docker LOGIN
## DOCKER LOGIN:::
docker login https://secure-registry.gsintlab.com
read -p  "Enter the Build ID [Default: latest]:" pullId
fi

if [ $deployType -eq 4 ]
then
 echo "Enter the Insecure Registry Access URL : \n Example : 209.205.208.111:5000"
 read insecureRegistry
 echo $insecureRegistry

 if [ -z $insecureRegistry ]
 then
	echo "Specify a valid Insecure Registry ! Exiting..."
	exit
 fi
 echo "[Warning] Ensure that you have started the docker service in the host machine with --insecure-registry option , else deploy will fail"

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
	rm -rf "/var/lib/gemini/sshKey_root"
	rm -rf "/var/log/gemini/"
fi

mkdir -p "/var/dbstore"
mkdir -p "/var/log/gemini/platform"
mkdir -p "/var/log/gemini/stack"
mkdir -p "/var/lib/gemini/sshKey_root"

chcon -Rt svirt_sandbox_file_t /var/dbstore
chcon -Rt svirt_sandbox_file_t /var/lib/gemini/sshKey_root
chcon -Rt svirt_sandbox_file_t /var/log/gemini/stack
chcon -Rt svirt_sandbox_file_t /var/log/gemini/platform

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

theme="gemini"
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

rpm -q ntp
if [ $? -ne 0 ]
then
yum install -y ntp
fi

echo "Time sync processing..."
ntpdate -b -u time.nist.gov
echo "...."

echo "continue to deploy..."
echo "Removing if any existing docker process with same name to avoid conflicts"

if docker ps -a |grep -aq gemini-stack;
then
   docker rm -f gemini-stack
fi

if docker ps -a |grep -aq gemini-platform;
then
   docker rm -f gemini-platform
fi

if docker ps -a |grep -aq db;
then
   docker rm -f db
fi

if docker ps -a |grep -a gemini-mist; then
   docker rm -f gemini-mist
fi


echo "Setting up iptables rules..."
iptables -D INPUT -j REJECT --reject-with icmp-host-prohibited
iptables -D  FORWARD -j REJECT --reject-with icmp-host-prohibited



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


echo "Time sync processing..."
yum install -y ntp
ntpdate -b -u time.nist.gov
echo "...."

if [ ! -f /etc/logrotate.d/geminiLogRotate ]
then
	echo "/var/log/gemini/platform/*log /var/log/gemini/stack/*log  /var/log/gemini/stack/mist/*log {
	  daily
	  missingok
	  size 50M
	  rotate 20
	  compress
	  copytruncate
	}" > /etc/logrotate.d/geminiLogRotate
fi


echo "db run .."
docker run --name db -e MYSQL_ROOT_PASSWORD=admin -e MYSQL_USER=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_platform -v /var/dbstore:/var/lib/mysql -d mysql:5.6.24
sleep 60

if [ $deployType -eq 2 ]
then
        echo $pullId
	echo "pull gemini base..."
	docker pull secure-registry.gsintlab.com/gemini/gemini-base
	echo "pull gemini stack base..."
	docker pull secure-registry.gsintlab.com/gemini/gemini-stack-base
	echo "pull gemini stack ..."
	docker pull secure-registry.gsintlab.com/gemini/gemini-stack:$pullId
	echo "pull gemini platform base..."
	docker pull secure-registry.gsintlab.com/gemini/gemini-platform-base
	echo "pull gemini platform..."
	docker pull secure-registry.gsintlab.com/gemini/gemini-platform:$pullId
#	echo  "pull gemini-mist..."
#	docker pull secure-registry.gsintlab.com/gemini/gemini-mist

	echo "gemini stack run..."
	if docker ps -a |grep -a gemini-chef; then
		docker run -t --name gemini-stack -p 8888:8888 -e GEMINI_INT_REPO=$internalRepo -e CHEF_URL=https://$hostip:9443 -e MYSQL_HOST=db -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_mist -e GEMINI_PLATFORM_WS_HOST=$hostip -e GEMINI_PLATFORM_WS_PORT=9999 -e GEMINI_STACK_IPANEMA=1 --link db:db  -v /var/lib/gemini/sshKey_root:/root --volumes-from gemini-chef -v /var/log/gemini/stack:/var/log/gemini -d  secure-registry.gsintlab.com/gemini/gemini-stack:$pullId	
		echo "platform run ..."
		docker run -t --name gemini-platform -p 9999:8888 -p 80:3000 -e MAX_POOL_SIZE=$max_app_processes  -e CHEF_URL=https://$hostip:9443 -e GEMINI_STACK_WS_HOST=$hostip -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_platform -e ON_PREM_MODE=$onPremMode -e THEME_NAME=$themeName --link db:db --volumes-from gemini-chef -v /var/log/gemini/platform:/var/log/gemini  -d secure-registry.gsintlab.com/gemini/gemini-platform:$pullId
	else
		docker run -t --name gemini-stack -p 8888:8888 -e GEMINI_INT_REPO=$internalRepo -e MYSQL_HOST=db -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_mist -e GEMINI_PLATFORM_WS_HOST=$hostip -e GEMINI_PLATFORM_WS_PORT=9999 -e GEMINI_STACK_IPANEMA=1 --link db:db  -v /var/lib/gemini/sshKey_root:/root -v /var/log/gemini/stack:/var/log/gemini -d  secure-registry.gsintlab.com/gemini/gemini-stack:$pullId	
		echo "platform run ..."
		docker run -t --name gemini-platform -p 9999:8888 -p 80:3000  -e MAX_POOL_SIZE=$max_app_processes -e GEMINI_STACK_WS_HOST=$hostip -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_platform -e ON_PREM_MODE=$onPremMode -e THEME_NAME=$themeName  --link db:db -v /var/log/gemini/platform:/var/log/gemini -d secure-registry.gsintlab.com/gemini/gemini-platform:$pullId

	fi

	echo "end ..."

elif [ $deployType -eq 1 ] || [ $deployType -eq 5 ]
then
   
	echo "gemini stack run..."
	if docker ps -a |grep -a gemini-chef; then
		docker run -t --name gemini-stack -p 8888:8888 -e GEMINI_INT_REPO=$internalRepo -e CHEF_URL=https://$hostip:9443 -e MYSQL_HOST=db -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_mist -e GEMINI_PLATFORM_WS_HOST=$hostip -e GEMINI_PLATFORM_WS_PORT=9999 -e GEMINI_STACK_IPANEMA=1 --link db:db -v /var/lib/gemini/sshKey_root:/root -v /var/log/gemini/stack:/var/log/gemini --volumes-from gemini-chef -d gemini/gemini-stack    	
		echo "platform run ..."
		docker run -t --name gemini-platform -p 9999:8888 -p 80:3000 -e MAX_POOL_SIZE=$max_app_processes -e CHEF_URL=https://$hostip:9443 -e GEMINI_STACK_WS_HOST=$hostip -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_platform -e ON_PREM_MODE=$onPremMode -e THEME_NAME=$themeName  --link db:db --volumes-from gemini-chef -v /var/log/gemini/platform:/var/log/gemini -d gemini/gemini-platform
	else
		docker run -t --name gemini-stack -p 8888:8888 -e GEMINI_INT_REPO=$internalRepo -e MYSQL_HOST=db -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_mist -e GEMINI_PLATFORM_WS_HOST=$hostip -e GEMINI_PLATFORM_WS_PORT=9999 -e GEMINI_STACK_IPANEMA=1 --link db:db -v /var/log/gemini/stack:/var/log/gemini  -v /var/lib/gemini/sshKey_root:/root -d gemini/gemini-stack    	
		echo "platform run ..."
		docker run -t --name gemini-platform -p 9999:8888 -p 80:3000 -e MAX_POOL_SIZE=$max_app_processes -e GEMINI_STACK_WS_HOST=$hostip -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_platform -e ON_PREM_MODE=$onPremMode -e THEME_NAME=$themeName --link db:db -v /var/log/gemini/platform:/var/log/gemini -d gemini/gemini-platform
	fi
	echo "end ..."
elif [ $deployType -eq 4 ]
then
	echo "gemini stack run..."
	if docker ps -a |grep -a gemini-chef; then
		docker run -t --name gemini-stack -p 8888:8888 -e GEMINI_INT_REPO=$internalRepo -e CHEF_URL=https://$hostip:9443 -e MYSQL_HOST=db -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_mist -e GEMINI_PLATFORM_WS_HOST=$hostip -e GEMINI_PLATFORM_WS_PORT=9999 -e GEMINI_STACK_IPANEMA=1 --link db:db  -v /var/lib/gemini/sshKey_root:/root -v /var/log/gemini/stack:/var/log/gemini --volumes-from gemini-chef -d $insecureRegistry/gemini/gemini-stack
		echo "platform run ..."
		docker run -t --name gemini-platform -p 9999:8888 -p 80:3000 -e MAX_POOL_SIZE=$max_app_processes -e CHEF_URL=https://$hostip:9443 -e GEMINI_STACK_WS_HOST=$hostip -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_platform -e ON_PREM_MODE=$onPremMode -e THEME_NAME=$themeName  --link db:db --volumes-from gemini-chef -v /var/log/gemini/platform:/var/log/gemini -d $insecureRegistry/gemini/gemini-platform
	else
		docker run -t --name gemini-stack -p 8888:8888 -e GEMINI_INT_REPO=$internalRepo -e MYSQL_HOST=db -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_mist -e GEMINI_PLATFORM_WS_HOST=$hostip -e GEMINI_PLATFORM_WS_PORT=9999 -e GEMINI_STACK_IPANEMA=1 --link db:db -v /var/lib/gemini/sshKey_root:/root -v /var/log/gemini/stack:/var/log/gemini -d $insecureRegistry/gemini/gemini-stack
		echo "platform run ..."
		docker run -t --name gemini-platform -p 9999:8888 -p 80:3000  -e MAX_POOL_SIZE=$max_app_processes -e GEMINI_STACK_WS_HOST=$hostip -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_platform -e ON_PREM_MODE=$onPremMode -e THEME_NAME=$themeName --link db:db -v /var/log/gemini/platform:/var/log/gemini -d $insecureRegistry/gemini/gemini-platform
	fi
	echo "end ..."
else
	echo "Enter stack dir : example : /opt/mydevdir/ :"
	read stackDir
	echo "Enter platform dir : example : /opt/mydevDir/ :"
	read platformDir
        cd $stackDir/Gemini-poc-stack
   	if [ -f run.jar ]; then
        	rm -f run.jar
	fi
	wget http://repos.gsintlab.com/repos/mist/run.jar

        cd $platformDir/Gemini-poc-mgnt/
	rm -rf Gemfile.lock
        cp -f Gemfile-master Gemfile

	echo "gemini stack DEV MODE run..."
	if docker ps -a |grep -a gemini-chef; then
		docker run -t --name gemini-stack -p 8888:8888 -e GEMINI_INT_REPO=$internalRepo -e CHEF_URL=https://$hostip:9443 -e MYSQL_HOST=db -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_mist -e GEMINI_PLATFORM_WS_HOST=$hostip -e GEMINI_PLATFORM_WS_PORT=9999 -e GEMINI_STACK_IPANEMA=1 -v $stackDir/Gemini-poc-stack:/home/gemini/gemini-stack --link db:db -v /var/lib/gemini/sshKey_root:/root -v /var/log/gemini/stack:/var/log/gemini --volumes-from gemini-chef -d  gemini/gemini-stack
		echo "platform run ..."
		docker run -t --name gemini-platform -p 9999:8888 -p 80:3000 -e MAX_POOL_SIZE=$max_app_processes -e CHEF_URL=https://$hostip:9443  -e GEMINI_STACK_WS_HOST=$hostip -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_platform -e ON_PREM_MODE=$onPremMode -e THEME_NAME=$themeName  -v $platformDir/Gemini-poc-mgnt:/home/gemini/gemini-platform --link db:db  --volumes-from gemini-chef -v /var/log/gemini/platform:/var/log/gemini -d gemini/gemini-platform
	else
		docker run -t --name gemini-stack -p 8888:8888 -e GEMINI_INT_REPO=$internalRepo -e MYSQL_HOST=db -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_mist -e GEMINI_PLATFORM_WS_HOST=$hostip -e GEMINI_PLATFORM_WS_PORT=9999 -e GEMINI_STACK_IPANEMA=1 -v $stackDir/Gemini-poc-stack:/home/gemini/gemini-stack --link db:db -v /var/lib/gemini/sshKey_root:/root -v /var/log/gemini/stack:/var/log/gemini -d  gemini/gemini-stack
		echo "platform run ..."
		docker run -t --name gemini-platform -p 9999:8888 -p 80:3000 -e MAX_POOL_SIZE=$max_app_processes -e GEMINI_STACK_WS_HOST=$hostip -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_platform -e ON_PREM_MODE=$onPremMode -e THEME_NAME=$themeName -v $platformDir/Gemini-poc-mgnt:/home/gemini/gemini-platform --link db:db -v /var/log/gemini/platform:/var/log/gemini -d gemini/gemini-platform
	fi
	echo "end ...."
fi
