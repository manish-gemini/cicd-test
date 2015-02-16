#!bin/bash
#####AUOMATE tar and unload.,
regIp=$1
echo $regIp
commitID=$2
echo $commitID

#STEP 1:GET A DESTINATION DIR TO CHECKOUT CODE AND CREATE DIR
mkdir -p /opt/Gemini-stack
mkdir -p /opt/Gemini-mgnt
echo "created dirs..."
#STEP 2: NAVIAGATE TO THAT DIR
cd /opt/Gemini-stack

echo "..."
#STEP 3: URL FROM WHICH CODE IS TO BE CHECKED OUT. GIT LOGIN STUFF SHOULD HAVE ALREADY HAPPENED..
if [ -d Gemini-poc-stack ]
then
	echo "pull...."
	# pull instead of clone
	cd Gemini-poc-stack
	git pull
        if [-z $commitID]
        then
		git checkout $regIp
        fi
else
	echo "clone..."
	git clone "git@github.com:Gemini-sys/Gemini-poc-stack.git"
fi
cd /opt/Gemini-mgnt
if [ -d Gemini-poc-mgnt ]
then
	echo "pull"
        # pull instead of clone
        cd Gemini-poc-mgnt
        git pull
        if [-z $commitID]
        then
	        echo "1checkout"
                git checkout $regIp
        fi
else
	echo "clone"
        git clone "git@github.com:Gemini-sys/Gemini-poc-mgnt.git"
fi



#STEP 4: NAVIGATE TO THE DIR WHERE Dockerfile EXIST
cd /opt/Gemini-stack/Gemini-poc-stack

#STEP 4a: Verify if gemini.config.ini exists - user should manually get this file
if [ ! -f gemini.config.ini ]
then
	echo "File gemini.config.ini does not exist! Please copy the file and re-try"
	exit 1
fi	

#STEP 5: BUILD THE STACK CODE.
docker build -t gemini/gemini-stack .

cd /opt/Gemini-mgnt/Gemini-poc-mgnt
docker build -t gemini/gemini-platform .

docker save gemini/gemini-platform > /opt/gemini-platform.tar
docker save gemini/gemini-stack > /opt/gemini-stack.tar

echo "stack ..."
docker load -i /opt/gemini-stack.tar
echo "platform ..."
docker load -i /opt/gemini-platform.tar
echo "stack run ..."
docker run -t --name gemini-stack -p 8888:8888 -e GEMINI_PLATFORM_WS_HOST=$regIp -e GEMINI_PLATFORM_WS_PORT=9999 -v /var/lib/gemini:/var/lib/gemini -d gemini/gemini-stack
echo "db run .."
docker run --name db -e MYSQL_ROOT_PASSWORD=admin -e MYSQL_USER=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_platform -v /var/dbstore:/var/lib/mysql -d mysql
echo "platform run ..."
docker run -t --name gemini-platform -p 9999:8888 -p 80:3000 -e GEMINI_STACK_WS_HOST=$regIp -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=gemini_platform -v /var/lib/gemini:/var/lib/gemini --link db:db -d gemini/gemini-platform
echo "end ..."
