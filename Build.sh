#!/bin/bash
#  Copyright 2015 Gemini Systems. All rights reserved

#####AUTOMATE tar and upload.,

trap times EXIT

echo "Enter the build type:"
echo "Build a Tar file = 1"
echo "Build and push to internal Reg = 2"
echo "Build both Tar and push to internal Reg = 3"
echo "Build Test = 4"

read -p "Default(4):" buildType
buildType=${buildType:-4}
echo $buildType

if [ $buildType -eq 2 ] || [ $buildType -eq 3 ]
then
	## DOCKER LOGIN:::
	echo "Login to the Docker Registry...."
	docker login https://secure-registry.gsintlab.com
fi
sourceType=1
if [ $buildType -eq 4 ]
then
	echo "Enter the Source type for build :"
	echo "Clone from Repository =  1"
	echo "Build from the Local Directory = 2"
	read -p "Default(2):" sourceType
        sourceType=${sourceType:-2}
	echo $sourceType
fi


if [ $sourceType -eq 2 ]
then
	echo "Enter the directory where Gemini-poc-mgnt and Gemini-poc-stack exist :"
	echo "Example: /opt/Mydir/"
	read -p "Default(${PWD}):" dirToCheckOut
        dirToCheckOut=${dirToCheckOut:-${PWD}}
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
	echo "Example: /opt/Mydir/"
	read -p "Default(${PWD}):" dirToCheckOut
	dirToCheckOut=${dirToCheckOut:-${PWD}}
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

	echo "Enter the git user name"
	read gituserName
	echo $gituserName


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
	        git clone "https://$gituserName@github.com/Gemini-sys/Gemini-poc-stack.git"
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
		git clone "https://$gituserName@github.com/Gemini-sys/Gemini-poc-mgnt.git"
		echo "git checkout ...."
		git checkout tags/$commitID
		echo "git checkout completed..."
	fi
fi
echo -n "Enter the SECRET_KEY:"
read -p "Default(71Z2LBKnRr6EzVsGcvysQYhqAHgEcm1e8oF/xCZdhbw=):" secretkey
secretkey=${secretkey:-"=71Z2LBKnRr6EzVsGcvysQYhqAHgEcm1e8oF/xCZdhbw="}
echo $secretkey

echo -n "Enter the INIT_VECTOR:"
read -p "Default(f7BjRhMOAfuDNafQTSRJmg=):" initVector
initVector=${initVector:-"f7BjRhMOAfuDNafQTSRJmg="}
echo $initVector

if docker images |grep -a gemini/gemini-stack; then
	echo "gemini-stack exists.,"
	quickBuildStack=1

else
	echo "gemini-stack does not exist"
	quickBuildStack=2
fi

echo "copying Executables.."
#scp root@209.205.208.181:/var/lib/jenkins/jobs/dev-mist-cgp/lastSuccessful/archive/run/generated/distributions/executable/run.jar $dirToCheckOut/Gemini-poc-stack/mist-cgp/.
cd $dirToCheckOut/Gemini-poc-stack/mist-cgp/

if [ -f run.jar ]; then
	rm -f run.jar
fi
wget http://repos.gsintlab.com/repos/mist/run.jar

echo  "Enter 1 for Quick Build Gemini-stack & Gemini-platform or 2 for to build all "
read -p "Default($quickBuildStack):" quickBuild
quickBuild=${quickBuild:-$quickBuildStack}
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


#BUILD THE CHEF CONTAINER


# If any docker build fails bail out
set -o errexit

#STEP 5: BUILD THE STACK CODE.
#BUILD THE BASE IMAGE
cd Dockerfiles
cp ../gemini.repo .
cp ../CentOS-Base.repo .
if [ $quickBuild != 1 ]
then
  echo "Build Base Image..."
  docker build -t gemini/gemini-base:$commitID -f GeminiBase .
  echo "Build Stack Base Image..."
  docker build -t gemini/gemini-stack-base:$commitID -f GeminiStackBase .
fi 

cd ..
echo "Build Tar file for GeminiStack ..."
cp gemini.config.ini Dockerfiles/
tar cf Dockerfiles/GeminiStack.tar -T Dockerfiles/GeminiStack.lst
cd Dockerfiles
echo "Build Stack Image..."
docker build -t gemini/gemini-stack:$commitID -f GeminiStack .
rm GeminiStack.tar gemini.config.ini gemini.repo

#PLATFORM CODE :

cd $dirToCheckOut/Gemini-poc-mgnt

cd Dockerfiles
cp ../gemini.repo .
cp ../Gemfile .
if [ $quickBuild != 1 ]
then
  # echo "Gemini Base Image..."
  # docker build -t gemini/gemini-base:$commitID -f GeminiBase .
  echo "Gemini Platform Base Image..."
  docker build -t gemini/gemini-platform-base:$commitID -f GeminiPlatformBase .
fi
rm Gemfile gemini.repo
cd ..

#echo "pull gemini-stack image from the internal repo"
#docker pull docker-internal.example.com/gemini/gemini-platform-base
#echo "tag as gemini/gemini-stack..."
#docker tag -f docker-internal.example.com/gemini/gemini-platform-base gemini/gemini-platform-base


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
	docker tag -f gemini/gemini-stack:$commitID secure-registry.gsintlab.com/gemini/gemini-stack:$commitID
	docker push secure-registry.gsintlab.com/gemini/gemini-stack:$commitID
	docker tag -f gemini/gemini-platform:$commitID secure-registry.gsintlab.com/gemini-platform:$commitID
	docker push secure-registry.gsintlab.com/gemini/gemini-platform:$commitID
fi
