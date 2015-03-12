#!bin/bash
#  Copyright 2015 Gemini Systems. All rights reserved

#####AUOMATE tar and upload.,


echo "Enter the build type:"
echo "Build a Tar file = 1"
echo "Build and push to internal Reg = 2"
echo "Build both Tar and push to internal Reg = 3"
echo "Build Test = 4"
read buildType
echo $buildType

if [ $buildType -eq 2 ] || [ $buildType -eq 3 ]
then
	## DOCKER LOGIN:::
	echo "Login to the Docker Registry...."
	docker login https://docker-internal.example.com
fi
sourceType=1
if [ $buildType -eq 4 ]
then
	echo "Enter the Source type for build :"
	echo "Clone from Repository =  1"
	echo "Build from the Local Directory = 2"
	read sourceType
	echo $sourceType
fi


if [ $sourceType -eq 2 ]
then
	echo "Enter the directory where Gemini-poc-mgnt and Gemini-poc-stack exist :"
	echo "Example : /opt/Mydir/"
	read dirToCheckOut
	echo $dirToCheckOut
	if [ ! -d $dirToCheckOut ]
	then
		echo "Enter Valid Directory, exit.."
		exit
	fi
	cd $dirToCheckOut
	if [ ! -d Gemini-poc-mgnt ] || [ ! -d Gemini-poc-stack ]
	then
		echo "Check if both Gemini-poc-mgnt and Gemini-poc-stack exist.... Quitting..."
		exit
	fi
		
else
	echo -n "Enter the Directory to checkout source and Save Tar Files"
	read dirToCheckOut
	echo $dirToCheckOut
	echo -n "Enter the commit ID/Tag ID:"
	echo -n "(if left empty will pull the latest code.)"
	read commitID
	echo $commitID

	#STEP 1:GET A DESTINATION DIR TO CHECKOUT CODE AND CREATE DIR

	mkdir -p $dirToCheckOut
	cd $dirToCheckOut
	echo "Created "$dirToCheckOut
	echo "..."

	#echo $buildType  $dirToCheckout $InternalRegistry $commitID


	#STEP 2: URL FROM WHICH CODE IS TO BE CHECKED OUT. GIT LOGIN STUFF SHOULD HAVE ALREADY HAPPENED..
	if [ -d Gemini-poc-stack ]
	then
		echo "pull...."
	        # pull instead of clone
		cd $dirToCheckOut
		cd Gemini-poc-stack
		git checkout master
		git reset --hard
		git fetch --all
		git pull
		if [ ! -z "$commitID" ]
	        then
			echo "git checkout ...."
			git checkout tags/$commitID
			echo "git checkout completed ...."
		fi
	else
		echo "clone..."
	        git clone "git@github.com:Gemini-sys/Gemini-poc-stack.git"
		echo "clone completed..."
		echo "checkout..."
		git checkout tags/$commitID
		echo "Checkout Completed...."
	fi
	cd $dirToCheckOut
	if [ -d Gemini-poc-mgnt ]
	then
		echo "pull..."
	        # pull instead of clone
		cd Gemini-poc-mgnt
		git checkout master
		git reset --hard
		git fetch --all
		git pull
	        if [ ! -z "$commitID" ]
		then
			echo "git checkout ...."
			git checkout tags/$commitID
			echo "git checkout completed..."
	        fi
	else
	        echo "clone..."
		git clone "git@github.com:Gemini-sys/Gemini-poc-mgnt.git"
		echo "git checkout ...."
		git checkout tags/$commitID
		echo "git checkout completed..."
	fi
fi
echo -n "Enter the SECRET_KEY:"
read secretkey
echo $secretkey

echo -n "Enter the INIT_VECTOR:"
read initVector
echo $initVector


#STEP 3: NAVIGATE TO THE DIR WHERE Dockerfile EXIST
cd $dirToCheckOut
cd Gemini-poc-stack
echo "
[config]
SECRET_KEY=$secretkey
INIT_VECTOR=$initVector" > gemini.config.ini

#STEP 4a: Verify if gemini.config.ini exists - user should manually get this file
if [ ! -f gemini.config.ini ]
then
        echo "File gemini.config.ini does not exist! Please copy the file and re-try"
        exit 1
fi

#STEP 5: BUILD THE STACK CODE.
#cp -f Dockerfile_BuildFromBase Dockerfile
#docker build -t gemini/gemini-stack:$commitID .
#BUILD THE BASE IMAGE
echo "Build Base Image..."
docker build -t gemini/gemini-base:$commitID -f Dockerfiles/GeminiBase .
echo "Build Stack Base Image..."
docker build -t gemini/gemini-stack-base:$commitID -f Dockerfiles/GeminiStackBase .
echo "Build Stack Image..."
docker build -t gemini/gemini-stack:$commitID -f Dockerfiles/GeminiStackcpy .

#PLATFORM CODE :

cd $dirToCheckOut/Gemini-poc-mgnt
#cp -f Dockerfile_BuildFromBase Dockerfile
#docker build -t gemini/gemini-platform:$commitID .

echo "Gemini Base Image..."
docker build -t gemini/gemini-base:$commitID -f Dockerfiles/GeminiBase .
echo "Gemini Platform Base Image..."
docker build -t gemini/gemini-platform-base:$commitID -f Dockerfiles/GeminiPlatformBase .
echo "Gemini Platform Image..."
docker build -t gemini/gemini-platform:$commitID -f Dockerfiles/GeminiPlatformcpy .

if [ $buildType -eq 1 ] || [ $buildType -eq 3 ]
then
	mkdir -p $dirToCheckOut/$commitID
	docker save gemini/gemini-platform:$commitID > $dirToCheckOut/$commitID/gemini-platform.tar
	docker save gemini/gemini-stack:$commitID > $dirToCheckOut/$commitID/gemini-stack.tar
fi

if [ $buildType -eq 2 ] || [ $buildType -eq 3 ]
then
	docker tag -f gemini/gemini-base:$commitID docker-internal.example.com/gemini/gemini-base:$commitID
	docker tag -f gemini/gemini-stack-base:$commitID docker-internal.example.com/gemini/gemini-stack-base:$commitID
	docker tag -f gemini/gemini-stack:$commitID docker-internal.example.com/gemini/gemini-stack:$commitID
	docker push docker-internal.example.com/gemini/gemini-base:$commitID
	docker push docker-internal.example.com/gemini/gemini-stack-base:$commitID
	docker push docker-internal.example.com/gemini/gemini-stack:$commitID
	docker tag -f gemini/gemini-platform-base:$commitID docker-internal.example.com/gemini/gemini-platform-base:$commitID
	docker tag -f gemini/gemini-platform:$commitID docker-internal.example.com/gemini/gemini-platform:$commitID
	docker push  docker-internal.example.com/gemini/gemini-platform-base:$commitID
	docker push docker-internal.example.com/gemini/gemini-platform:$commitID
fi
