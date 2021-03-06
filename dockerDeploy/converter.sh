#!/bin/bash
echo 'Logging to gemini docker registry'
docker login -u=admin -p=dogreat12 secure-registry.gsintlab.com
if [ "$?" = "0" ]; then  
    echo 'Login Success'
else
    echo 'Login Failed'
    exit 1
fi

echo 'pulling general images...'
echo 'pulling chef images'
docker pull secure-registry.gsintlab.com/gemini/gemini-chef
echo 'pulling mysql images...'
docker pull mysql:5.6.24
echo 'pulling Rabbit Mq Message...'
docker pull secure-registry.gsintlab.com/gemini/gemini-rmq:latest
echo 'Completed General Images...'

echo 'Tag chef and Rmq images'
docker tag -f secure-registry.gsintlab.com/gemini/gemini-chef gemini/gemini-chef
docker tag -f secure-registry.gsintlab.com/gemini/gemini-rmq gemini/gemini-rmq
echo 'Completed Tag Process...'

echo '1) Pull images from gemini docker registry'
echo '2) Deploy gemini using local images'
read -p 'Which images you wish to use ? [2]:' deployType
deployType=${deployType:-2}
if [ $deployType -eq 1 ]
then
        echo 'pulling gemini images...'
	docker pull secure-registry.gsintlab.com/gemini/gemini-base
	docker pull secure-registry.gsintlab.com/gemini/gemini-stack-base
	docker pull secure-registry.gsintlab.com/gemini/gemini-platform-base
	docker pull secure-registry.gsintlab.com/gemini/gemini-stack
	docker pull secure-registry.gsintlab.com/gemini/gemini-platform
	docker tag -f secure-registry.gsintlab.com/gemini/gemini-stack gemini/gemini-stack
	docker tag -f secure-registry.gsintlab.com/gemini/gemini-platform gemini/gemini-platform
fi


echo '1) ON PREM MODE'
echo '2) SAAS MODE'
read -p 'Which mode do you want to deploy? [1]:' onPremMode
onPremMode=${onPremMode:-1}
if [ $onPremMode -eq 1 ]
then
	onPremMode=true
else
	onPremMode=false
fi

theme="gemini"
read -p "Enter the Theme Name [$theme] :" themeName
themeName=${themeName:-$theme}

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

HOSTIP=`curl -s http://whatismyip.akamai.com; echo`


#sed -e "s/HOSTIP/$HOSTIP/g" docker-compose.yml
#sed -e "s/mode/$onPremMode/g" docker-compose.yml
#sed -e "s/theme/$themeName/g" docker-compose.yml

#
cat docker-compose-template.yml | sed -e "s/HOSTIP/$HOSTIP/g" > compose1.yml
cat compose1.yml | sed -e "s/mode/$onPremMode/g" > compose2.yml
cat compose2.yml | sed -e "s/theme/$themeName/g" > docker-compose.yml

rm -f compose*.yml
read -p "Do you wish to launch gemini ? [y/n]:" launch
if [ $launch = "y" ]; then
  docker-compose up --allow-insecure-ssl
else
  echo "you can continue running later, docker-compose up --allow-insecure-ssl"
fi

