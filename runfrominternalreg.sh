#!bin/bash
hostip=$1
echo $hostip
echo "run stack..."
echo "...."
#Docker LOGIN
## DOCKER LOGIN:::
docker login https://docker-internal.example.com
mkdir -p "/RabbitMq/data/log"
mkdir -p "/RabbitMq/data/mnesia"
mkdir -p "/var/lib/gemini"
mkdir -p "/var/dbstore"
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 -v /RabbitMq/data/log:/data/log -v /RabbitMq/data/mnesia:/data/mnesia dockerfile/rabbitmq
docker run -t --name gemini-stack -p 8888:8888 --link rabbitmq:rmq -e GEMINI_PLATFORM_WS_HOST=$hostip -e GEMINI_PLATFORM_WS_PORT=9999 -v /var/lib/gemini:/var/lib/gemini -d docker-internal.example.com/gemini/gemini-stack
echo "db run .."
docker run --name db -e MYSQL_ROOT_PASSWORD=admin -e MYSQL_USER=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_platform -v /var/dbstore:/var/lib/mysql -d mysql
echo "platform run ..."
docker run -t --name gemini-platform -p 9999:8888 -p 80:3000 -e GEMINI_STACK_WS_HOST=$hostip -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_platform -e ON_PREM_MODE=true -v /var/lib/gemini:/var/lib/gemini --link db:db --link rabbitmq:rmq -d docker-internal.example.com/gemini/gemini-platform
echo "end ..."
