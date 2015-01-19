#!bin/bash
hostip=$1
echo $hostip
echo "run stack..."
echo "...."
echo "..."

docker run -t --name gemini-stack -p 8888:8888 -e GEMINI_PLATFORM_WS_HOST=$hostip -e GEMINI_PLATFORM_WS_PORT=9999 -v /var/lib/gemini:/var/lib/gemini -d 209.205.208.51:5000/gemini/gemini-stack
echo "db run .."
docker run --name db -e MYSQL_ROOT_PASSWORD=admin -e MYSQL_USER=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_platform -v /var/dbstore:/var/lib/mysql -d mysql
echo "platform run ..."
docker run -t --name gemini-platform -p 9999:8888 -p 80:3000 -e GEMINI_STACK_WS_HOST=$hostip -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_platform -e ON_PREM_MODE=true -v /var/lib/gemini:/var/lib/gemini --link db:db -d 209.205.208.51:5000/gemini/gemini-platform
echo "end ..."
