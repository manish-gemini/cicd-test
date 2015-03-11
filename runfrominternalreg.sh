#!bin/bash
echo "...."
echo "Enter the deploy type:"
echo "Deploy from Local image = 1"
echo "Deploy from internal registry = 2"
read deployType

if [ $deployType -eq 2 ]
then
#Docker LOGIN
## DOCKER LOGIN:::
docker login https://docker-internal.example.com
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


docker rm -f gemini-stack gemini-platform 

docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 -v /RabbitMq/data/log:/data/log -v /RabbitMq/data/mnesia:/data/mnesia dockerfile/rabbitmq
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

else
	echo "gemini stack run..."
	docker run -t --name gemini-stack -p 8888:8888 --link rabbitmq:rmq -e GEMINI_PLATFORM_WS_HOST=$hostip -e GEMINI_PLATFORM_WS_PORT=9999 -d gemini/gemini-stack
	echo "platform run ..."
	docker run -t --name gemini-platform -p 9999:8888 -p 80:3000 -e GEMINI_STACK_WS_HOST=$hostip -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_platform -e ON_PREM_MODE=$onPremMode --link db:db --link rabbitmq:rmq -d gemini/gemini-platform
	echo "end ..."
fi
