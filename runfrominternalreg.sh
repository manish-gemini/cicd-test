#!/bin/bash
echo "...."
echo "Enter the deploy type:"
echo "Deploy from Local image = 1"
echo "Deploy from internal registry = 2"
echo "Dev Mode with Volume Mount Option = 3"
read deployType
echo $deployType

if [ $deployType -eq 2 ]
then
#Docker LOGIN
## DOCKER LOGIN:::
docker login https://docker-internal.example.com
fi

echo "Do you want to clean up the setup (removes db, Rabbitmq Data etc.,) ?"
echo "press 1 to clean the setup."
echo "press 2 to retain the older entries.."
read cleanSetup
echo $cleanSetup

if [ $cleanSetup -eq 1 ]
then
	rm -rf "/RabbitMq/data/log"
	rm -rf "/RabbitMq/data/mnesia"
	rm -rf "/var/dbstore"

fi
mkdir -p "/RabbitMq/data/log"
mkdir -p "/RabbitMq/data/mnesia"
#mkdir -p "/var/lib/gemini"
mkdir -p "/var/dbstore"

printf "Mode of Operation: \n Type 1 for ON PREM MODE \n Type 2 for SAAS MODE :"
read onPremMode
echo $onPremMode
if [ $onPremMode -eq 1 ]
then
onPremMode=true
else
onPremMode=false
fi
echo $onPremMode

printf "Enter the Host IP :"
read hostip
echo $hostip
if [ -z $hostip ]
then
printf "HostIp is Mandatory .. exiting....\n"
exit
fi


echo "continue to deploy..."


docker rm -f gemini-stack gemini-platform db rabbitmq 

echo "db run .."
docker run --name db -e MYSQL_ROOT_PASSWORD=admin -e MYSQL_USER=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_platform -v /var/dbstore:/var/lib/mysql -d mysql

if [ $deployType -eq 2 ]
then
	#sleep 500
	echo "pull gemini base..."
	docker pull docker-internal.example.com/gemini/gemini-base
	echo "pull gemini stack base..."
	docker pull docker-internal.example.com/gemini/gemini-stack-base
	echo "pull gemini stack ..."
	docker pull docker-internal.example.com/gemini/gemini-stack
	echo "pull gemini platform base..."
	docker pull docker-internal.example.com/gemini/gemini-platform-base
	echo "pull gemini platform..."
	docker pull docker-internal.example.com/gemini/gemini-platform
	echo "gemini stack run..."
	docker run -t --name gemini-stack -p 8888:8888 --link rabbitmq:rmq -e GEMINI_PLATFORM_WS_HOST=$hostip -e GEMINI_PLATFORM_WS_PORT=9999 -d docker-internal.example.com/gemini/gemini-stack
	echo "platform run ..."
	docker run -t --name gemini-platform -p 9999:8888 -p 80:3000 -e GEMINI_STACK_WS_HOST=$hostip -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_platform -e ON_PREM_MODE=$onPremMode --link db:db --link rabbitmq:rmq -d docker-internal.example.com/gemini/gemini-platform
	echo "end ..."

elif [ $deployType -eq 1 ]
then
	echo "gemini stack run..."
	docker run -t --name gemini-stack -p 8888:8888 -e GEMINI_PLATFORM_WS_HOST=$hostip -e GEMINI_PLATFORM_WS_PORT=9999 -d gemini/gemini-stack
	echo "platform run ..."
	docker run -t --name gemini-platform -p 9999:8888 -p 80:3000 -e GEMINI_STACK_WS_HOST=$hostip -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_platform -e ON_PREM_MODE=$onPremMode --link db:db -d gemini/gemini-platform
	echo "end ..."
else
	echo "Enter stack dir : example : /opt/mydevdir/ :"
	read stackDir
	echo "Enter platform dir : example : /opt/mydevDir/ :"
	read platformDir
	echo "gemini stack DEV MODE run..."
	docker run -t --name gemini-stack -p 8888:8888 -e GEMINI_PLATFORM_WS_HOST=$hostip -e GEMINI_PLATFORM_WS_PORT=9999 -v $stackDir/Gemini-poc-stack:/home/gemini/gemini-stack -d gemini/gemini-stack
	echo "platform run ..."
	docker run -t --name gemini-platform -p 9999:8888 -p 80:3000 -e GEMINI_STACK_WS_HOST=$hostip -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_platform -e ON_PREM_MODE=$onPremMode -v $platformDir/Gemini-poc-mgnt:/home/gemini/gemini-platform --link db:db -d gemini/gemini-platform
	echo "end ..."
fi
