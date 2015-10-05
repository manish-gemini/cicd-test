#!/bin/bash
echo "...."
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

	cd /tmp/GeminiPackages/

	echo "Loading Platform ... "
	docker load < gemini-platform.tar
	echo "Loading Stack ..."
	docker load < gemini-stack.tar
	echo "Loading Mysql ..."
	docker load < mysql.tar
fi

#if [ $deployType -eq 1 ]
#then
#	if !(docker login https://registry.gemini-systems.net/)
#	then
#		echo "Docker Secure Registry Login Failed., Exiting..."
#		exit
#	fi
#fi

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
	rm -rf "/var/lib/gemini/sshKey_root"
fi

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

if [ $# -eq 0 ]
  then
    themeName="gemini"
fi

themeName=$1

ip=`curl -s http://whatismyip.akamai.com; echo`
printf "Enter the Host IP :"
read -p "Default($ip):" hostip
hostip=${hostip:-$ip}
echo $hostip

echo "continue to deploy..."
echo "Removing if any existing docker process with same name to avoid conflicts"
#docker rm -f gemini-stack gemini-platform db  

#if docker ps -a |grep -a gemini-mist; then
#	docker rm -f gemini-mist
#fi

if docker ps -a |grep -aq gemini-stack; then
        docker rm -f gemini-stack
fi

if docker ps -a |grep -aq gemini-platform; then
        docker rm -f gemini-platform
fi

if docker ps -a |grep -aq db; then
        docker rm -f db
fi

echo "Setting up iptables rules..."
iptables -D INPUT -j REJECT --reject-with icmp-host-prohibited
iptables -D  FORWARD -j REJECT --reject-with icmp-host-prohibited

echo "Time sync processing..."
yum install -y ntp
ntpdate -b -u time.nist.gov
echo "...."

echo "db run .."
docker run --name db -e MYSQL_ROOT_PASSWORD=admin -e MYSQL_USER=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_platform -v /var/dbstore:/var/lib/mysql -d mysql:5.6.24
sleep 60

if [ $deployType -eq 1 ]
then
	#sleep 500
	echo "pull gemini base..."
	docker pull registry.gemini-systems.net/gemini/gemini-base
	echo "pull gemini stack base..."
	docker pull registry.gemini-systems.net/gemini/gemini-stack-base
	echo "pull gemini stack ..."
	docker pull registry.gemini-systems.net/gemini/gemini-stack
	echo "pull gemini platform base..."
	docker pull registry.gemini-systems.net/gemini/gemini-platform-base
	echo "pull gemini platform..."
	docker pull registry.gemini-systems.net/gemini/gemini-platform
#	echo  "pull gemini-mist..."
#	docker pull registry.gemini-systems.net/gemini/gemini-mist
	echo "gemini stack run..."
	if docker ps -a |grep -aq gemini-chef; then
		docker run -t --name gemini-stack -p 8888:8888 -e GEMINI_INT_REPO=$internalRepo -e CHEF_URL=https://$hostip:443  -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_mist -e GEMINI_PLATFORM_WS_HOST=$hostip -e GEMINI_PLATFORM_WS_PORT=9999 -e GEMINI_STACK_IPANEMA=1 --link db:db -v /var/lib/gemini/sshKey_root:/root --volumes-from gemini-chef -d  registry.gemini-systems.net/gemini/gemini-stack	
		echo "platform run ..."
		docker run -t --name gemini-platform -p 9999:8888 -p 80:3000 -e CHEF_URL=https://$hostip:443 -e GEMINI_STACK_WS_HOST=$hostip -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_platform -e ON_PREM_MODE=$onPremMode -e THEME_NAME=$themeName --link db:db --volumes-from gemini-chef -d registry.gemini-systems.net/gemini/gemini-platform
	else
		docker run -t --name gemini-stack -p 8888:8888 -e GEMINI_INT_REPO=$internalRepo -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_mist -e GEMINI_PLATFORM_WS_HOST=$hostip -e GEMINI_PLATFORM_WS_PORT=9999 -e GEMINI_STACK_IPANEMA=1 --link db:db  -v /var/lib/gemini/sshKey_root:/root -d  registry.gemini-systems.net/gemini/gemini-stack	
		echo "platform run ..."
		docker run -t --name gemini-platform -p 9999:8888 -p 80:3000 -e GEMINI_STACK_WS_HOST=$hostip -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_platform -e ON_PREM_MODE=$onPremMode -e THEME_NAME=$themeName --link db:db -d registry.gemini-systems.net/gemini/gemini-platform

	fi
	echo "end ..."

elif [ $deployType -eq 2 ]
then
   
	echo "gemini stack run..."
	if docker ps -a |grep -aq gemini-chef; then
		docker run -t --name gemini-stack -p 8888:8888 -e GEMINI_INT_REPO=$internalRepo -e CHEF_URL=https://$hostip:443  -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_mist -e GEMINI_PLATFORM_WS_HOST=$hostip -e GEMINI_PLATFORM_WS_PORT=9999 -e GEMINI_STACK_IPANEMA=1 --link db:db -v /var/lib/gemini/sshKey_root:/root --volumes-from gemini-chef -d gemini/gemini-stack    	
		echo "platform run ..."
		docker run -t --name gemini-platform -p 9999:8888 -p 80:3000 -e CHEF_URL=https://$hostip:443 -e GEMINI_STACK_WS_HOST=$hostip -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_platform -e ON_PREM_MODE=$onPremMode -e THEME_NAME=$themeName --link db:db --volumes-from gemini-chef -d gemini/gemini-platform
	else
		docker run -t --name gemini-stack -p 8888:8888 -e GEMINI_INT_REPO=$internalRepo -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_mist -e GEMINI_PLATFORM_WS_HOST=$hostip -e GEMINI_PLATFORM_WS_PORT=9999 -e GEMINI_STACK_IPANEMA=1 --link db:db  -v /var/lib/gemini/sshKey_root:/root -d gemini/gemini-stack    	
		echo "platform run ..."
		docker run -t --name gemini-platform -p 9999:8888 -p 80:3000 -e GEMINI_STACK_WS_HOST=$hostip -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_platform -e ON_PREM_MODE=$onPremMode -e THEME_NAME=$themeName --link db:db -d gemini/gemini-platform
	fi
	echo "end ..."
fi
