#!/bin/bash
echo "...."
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
read -p "Default(1):" cleanSetup
cleanSetup=${cleanSetup:-1}
echo $cleanSetup

if [ $cleanSetup -eq 1 ]
then
	rm -rf "/var/dbstore"
	rm -rf "/var/lib/gemini/sshKey_root"
fi

#mkdir -p "/var/lib/gemini"
mkdir -p "/var/dbstore"
# clean up of ssh key required 
mkdir -p /var/lib/gemini/sshKey_root

chcon -Rt svirt_sandbox_file_t /var/dbstore
chcon -Rt svirt_sandbox_file_t /var/lib/gemini/sshKey_root

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

ip=`curl -s http://ipecho.net/plain; echo`
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
ramgb=$((ramkb/KB))
RAM_PER_PROCESS=$((ramgb/nvcpu))
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

echo $max_app_processes

echo "continue to deploy..."
echo "Removing if any existing docker process with same name to avoid conflicts"
docker rm -f gemini-stack gemini-platform db  

if docker ps -a |grep -a gemini-mist; then
	docker rm -f gemini-mist
fi


echo "Setting up iptables rules..."
iptables -D INPUT -j REJECT --reject-with icmp-host-prohibited
iptables -D  FORWARD -j REJECT --reject-with icmp-host-prohibited

echo "db run .."
docker run --name db -e MYSQL_ROOT_PASSWORD=admin -e MYSQL_USER=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_platform -v /var/dbstore:/var/lib/mysql -d mysql:5.6.24
sleep 60

if [ $deployType -eq 2 ]
then
	#sleep 500
	echo "pull gemini base..."
	docker pull secure-registry.gsintlab.com/gemini/gemini-base
	echo "pull gemini stack base..."
	docker pull secure-registry.gsintlab.com/gemini/gemini-stack-base
	echo "pull gemini stack ..."
	docker pull secure-registry.gsintlab.com/gemini/gemini-stack
	echo "pull gemini platform base..."
	docker pull secure-registry.gsintlab.com/gemini/gemini-platform-base
	echo "pull gemini platform..."
	docker pull secure-registry.gsintlab.com/gemini/gemini-platform
#	echo  "pull gemini-mist..."
#	docker pull secure-registry.gsintlab.com/gemini/gemini-mist
	echo "gemini stack run..."
	if docker ps -a |grep -a gemini-chef; then
		docker run -t --name gemini-stack -p 8888:8888 -e GEMINI_INT_REPO=$internalRepo -e CHEF_URL=https://$hostip:443 -e MYSQL_HOST=db -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_mist -e GEMINI_PLATFORM_WS_HOST=$hostip -e GEMINI_PLATFORM_WS_PORT=9999 -e GEMINI_STACK_IPANEMA=1 --link db:db  -v /var/lib/gemini/sshKey_root:/root --volumes-from gemini-chef -d  secure-registry.gsintlab.com/gemini/gemini-stack	
		echo "platform run ..."
		docker run -t --name gemini-platform -p 9999:8888 -p 80:3000 -e MAX_POOL_SIZE=$max_app_processes  -e CHEF_URL=https://$hostip:443 -e GEMINI_STACK_WS_HOST=$hostip -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_platform -e ON_PREM_MODE=$onPremMode --link db:db --volumes-from gemini-chef -d secure-registry.gsintlab.com/gemini/gemini-platform
	else
		docker run -t --name gemini-stack -p 8888:8888 -e GEMINI_INT_REPO=$internalRepo -e MYSQL_HOST=db -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_mist -e GEMINI_PLATFORM_WS_HOST=$hostip -e GEMINI_PLATFORM_WS_PORT=9999 -e GEMINI_STACK_IPANEMA=1 --link db:db  -v /var/lib/gemini/sshKey_root:/root -d  secure-registry.gsintlab.com/gemini/gemini-stack	
		echo "platform run ..."
		docker run -t --name gemini-platform -p 9999:8888 -p 80:3000  -e MAX_POOL_SIZE=$max_app_processes -e GEMINI_STACK_WS_HOST=$hostip -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_platform -e ON_PREM_MODE=$onPremMode --link db:db -d secure-registry.gsintlab.com/gemini/gemini-platform

	fi
	echo "end ..."

elif [ $deployType -eq 1 ] || [ $deployType -eq 5 ]
then
   
	echo "gemini stack run..."
	if docker ps -a |grep -a gemini-chef; then
		docker run -t --name gemini-stack -p 8888:8888 -e GEMINI_INT_REPO=$internalRepo -e CHEF_URL=https://$hostip:443 -e MYSQL_HOST=db -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_mist -e GEMINI_PLATFORM_WS_HOST=$hostip -e GEMINI_PLATFORM_WS_PORT=9999 -e GEMINI_STACK_IPANEMA=1 --link db:db -v /var/lib/gemini/sshKey_root:/root --volumes-from gemini-chef -d gemini/gemini-stack    	
		echo "platform run ..."
		docker run -t --name gemini-platform -p 9999:8888 -p 80:3000 -e MAX_POOL_SIZE=$max_app_processes -e CHEF_URL=https://$hostip:443 -e GEMINI_STACK_WS_HOST=$hostip -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_platform -e ON_PREM_MODE=$onPremMode --link db:db --volumes-from gemini-chef -d gemini/gemini-platform
	else
		docker run -t --name gemini-stack -p 8888:8888 -e GEMINI_INT_REPO=$internalRepo -e MYSQL_HOST=db -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_mist -e GEMINI_PLATFORM_WS_HOST=$hostip -e GEMINI_PLATFORM_WS_PORT=9999 -e GEMINI_STACK_IPANEMA=1 --link db:db  -v /var/lib/gemini/sshKey_root:/root -d gemini/gemini-stack    	
		echo "platform run ..."
		docker run -t --name gemini-platform -p 9999:8888 -p 80:3000 -e MAX_POOL_SIZE=$max_app_processes -e GEMINI_STACK_WS_HOST=$hostip -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_platform -e ON_PREM_MODE=$onPremMode --link db:db -d gemini/gemini-platform
	fi
	echo "end ..."
elif [ $deployType -eq 4 ]
then
	echo "gemini stack run..."
	if docker ps -a |grep -a gemini-chef; then
		docker run -t --name gemini-stack -p 8888:8888 -e GEMINI_INT_REPO=$internalRepo -e CHEF_URL=https://$hostip:443 -e MYSQL_HOST=db -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_mist -e GEMINI_PLATFORM_WS_HOST=$hostip -e GEMINI_PLATFORM_WS_PORT=9999 -e GEMINI_STACK_IPANEMA=1 --link db:db  -v /var/lib/gemini/sshKey_root:/root --volumes-from gemini-chef -d $insecureRegistry/gemini/gemini-stack
		echo "platform run ..."
		docker run -t --name gemini-platform -p 9999:8888 -p 80:3000 -e MAX_POOL_SIZE=$max_app_processes -e CHEF_URL=https://$hostip:443 -e GEMINI_STACK_WS_HOST=$hostip -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_platform -e ON_PREM_MODE=$onPremMode --link db:db --volumes-from gemini-chef -d $insecureRegistry/gemini/gemini-platform
	else
		docker run -t --name gemini-stack -p 8888:8888 -e GEMINI_INT_REPO=$internalRepo -e MYSQL_HOST=db -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_mist -e GEMINI_PLATFORM_WS_HOST=$hostip -e GEMINI_PLATFORM_WS_PORT=9999 -e GEMINI_STACK_IPANEMA=1 --link db:db -v /var/lib/gemini/sshKey_root:/root -d $insecureRegistry/gemini/gemini-stack
		echo "platform run ..."
		docker run -t --name gemini-platform -p 9999:8888 -p 80:3000  -e MAX_POOL_SIZE=$max_app_processes -e GEMINI_STACK_WS_HOST=$hostip -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_platform -e ON_PREM_MODE=$onPremMode --link db:db -d $insecureRegistry/gemini/gemini-platform
	fi
	echo "end ..."
else
	echo "Enter stack dir : example : /opt/mydevdir/ :"
	read stackDir
	echo "Enter platform dir : example : /opt/mydevDir/ :"
	read platformDir
	echo "gemini stack DEV MODE run..."
	if docker ps -a |grep -a gemini-chef; then
		docker run -t --name gemini-stack -p 8888:8888 -e GEMINI_INT_REPO=$internalRepo -e CHEF_URL=https://$hostip:443 -e MYSQL_HOST=db -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_mist -e GEMINI_PLATFORM_WS_HOST=$hostip -e GEMINI_PLATFORM_WS_PORT=9999 -e GEMINI_STACK_IPANEMA=1 -v $stackDir/Gemini-poc-stack:/home/gemini/gemini-stack --link db:db -v /var/lib/gemini/sshKey_root:/root --volumes-from gemini-chef -d  gemini/gemini-stack
		echo "platform run ..."
		docker run -t --name gemini-platform -p 9999:8888 -p 80:3000 -e MAX_POOL_SIZE=$max_app_processes -e CHEF_URL=https://$hostip:443  -e GEMINI_STACK_WS_HOST=$hostip -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_platform -e ON_PREM_MODE=$onPremMode -v $platformDir/Gemini-poc-mgnt:/home/gemini/gemini-platform --link db:db  --volumes-from gemini-chef -d gemini/gemini-platform
	else
		docker run -t --name gemini-stack -p 8888:8888 -e GEMINI_INT_REPO=$internalRepo -e MYSQL_HOST=db -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_mist -e GEMINI_PLATFORM_WS_HOST=$hostip -e GEMINI_PLATFORM_WS_PORT=9999 -e GEMINI_STACK_IPANEMA=1 -v $stackDir/Gemini-poc-stack:/home/gemini/gemini-stack --link db:db -v /var/lib/gemini/sshKey_root:/root -d  gemini/gemini-stack
		echo "platform run ..."
		docker run -t --name gemini-platform -p 9999:8888 -p 80:3000 -e MAX_POOL_SIZE=$max_app_processes -e GEMINI_STACK_WS_HOST=$hostip -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_platform -e ON_PREM_MODE=$onPremMode -v $platformDir/Gemini-poc-mgnt:/home/gemini/gemini-platform --link db:db -d gemini/gemini-platform
	fi
	echo "end ..."
fi
