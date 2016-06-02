#!/bin/bash
#  Copyright 2015 appOrbit. All rights reserved

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
	echo "Enter the directory where Gemini-poc-mgnt, Gemini-poc-stack and deta exist :"
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
	if [ ! -d Gemini-poc-mgnt ] || [ ! -d Gemini-poc-stack ] || [ ! -d deta ]
	then
		echo "Check if Gemini-poc-mgnt, Gemini-poc-stack and deta exist.... Quitting..."
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
        if [ ! -z "$commitID" ]
        then
           commitIDstr=":${commitID}"
        else
           commitIDstr=""
        fi
	

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

        cd $dirToCheckOut
        if [ -d deta ]
        then
                echo "pull..."
                # pull instead of clone
                cd deta
                git checkout integration
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
                git clone -b integration "https://$gituserName@github.com/Gemini-sys/deta.git"
        fi
fi
echo -n "Enter the SECRET_KEY:"
read -p "Default(71Z2LBKnRr6EzVsGcvysQYhqAHgEcm1e8oF/xCZdhbw=):" secretkey
secretkey=${secretkey:-"71Z2LBKnRr6EzVsGcvysQYhqAHgEcm1e8oF/xCZdhbw="}
echo $secretkey

echo -n "Enter the INIT_VECTOR:"
read -p "Default(f7BjRhMOAfuDNafQTSRJmg==):" initVector
initVector=${initVector:-"f7BjRhMOAfuDNafQTSRJmg=="}
echo $initVector

echo "Enter the Repos to test:"
echo "Release Repo = 1"
echo "Master Repo = 2"
echo "Test Repo = 3"
echo "Dev Repo = 4"
read -p "Default(2):" repoType
repoType=${repoType:-"2"}
echo $repoType

if docker images |grep -a apporbit/apporbit-services-base; then
	echo "apporbit-services-base exists.,"
	quickBuildStack=1

else
	echo "apporbit-services-base does not exist"
	quickBuildStack=2
fi

echo  "Enter 1 for Quick Build apporbit-services & apporbit-controller or 2 for to build all "
read -p "Default($quickBuildStack):" quickBuild
quickBuild=${quickBuild:-$quickBuildStack}
echo $quickBuild

echo "copying Executables.."

cd $dirToCheckOut/Gemini-poc-stack/mist-cgp/
if [ -f run.jar ]; then
	rm -f run.jar
fi
echo "1) Build Mist Locally"
echo "2) Use the Mist Build from repo"
read -p "Enter Mist Build you want to try [Default: 2]:" mistBuildType

if [[ ( -z "$mistBuildType" ) || ( $mistBuildType -eq 2) ]]; then
   echo "Enter the Mist Branch to pull jar file:"
   echo "Master = 1"
   echo "Integration = 2"
   echo "Integration-features = 3"
   read -p "Default(2):" mistRepo
   mistRepo=${mistRepo:-"2"}
   echo $mistRepo
   if [ $mistRepo == 1 ]
   then
      wget http://repos.gsintlab.com/repos/mist/master/run.jar
   elif [ $mistRepo == 2 ]
   then
      wget http://repos.gsintlab.com/repos/mist/integration/run.jar
   else
      wget http://repos.gsintlab.com/repos/mist/integration-features/run.jar
   fi
else
   docker pull secure-registry.gsintlab.com/apporbit/mist-builder
   rm -rf /tmp/mist-cgp
   mkdir -p /tmp
   docker run --rm -it -v /tmp:/tmp secure-registry.gsintlab.com/apporbit/mist-builder
   cp /tmp/run.jar .
fi

#STEP 3: NAVIGATE TO THE DIR WHERE Dockerfile EXIST
cd $dirToCheckOut
cd Gemini-poc-stack
echo "
[config]
SECRET_KEY=$secretkey
INIT_VECTOR=$initVector" > apporbit.config.ini

#STEP 4a: Verify if apporbit.config.ini exists - user should manually get this file
if [ ! -f apporbit.config.ini ]
then
        echo "File apporbit.config.ini does not exist! Please copy the file and re-try"
        exit 1
fi


#BUILD THE CHEF CONTAINER


# If any docker build fails bail out
set -o errexit

#STEP 5: BUILD THE STACK CODE.
#BUILD THE BASE IMAGE
cd Dockerfiles
cp ../CentOS-Base.repo .
if [ $repoType == 4 ]
then
    echo "copying repoType Dev"
    cp ../apporbit-dev.repo .
    cp ../apporbit-test.repo .
    cp ../apporbit-master.repo .
elif [ $repoType == 3 ]
then
    echo "copying repoType Integration"
    cp ../apporbit-test.repo .
    cp ../apporbit-master.repo .
elif [ $repoType == 2 ]
then
    echo "copying repoType Master"
    cp ../apporbit-master.repo .
else
    echo "copying repoType RELEASE"
    cp ../apporbit-release.repo .
fi

if [ $quickBuild != 1 ]
then
  echo "Build Base Image..."
  docker build -t apporbit/apporbit-base$commitIDstr -f apporbitBase .
  echo "Build Stack Base Image..."
  docker build -t apporbit/apporbit-services-base$commitIDstr -f apporbitservicesBase .
fi 

cd ..
echo "Build Tar file for apporbit-services ..."
cp apporbit.config.ini Dockerfiles/
tar cf Dockerfiles/apporbit-services.tar -T Dockerfiles/apporbitservices.lst
cd Dockerfiles
echo "Build apporbit services Image..."
docker build -t apporbit/apporbit-services$commitIDstr -f apporbitservices .
rm apporbit-services.tar apporbit.config.ini apporbit*.repo CentOS-Base.repo

#PLATFORM CODE :

cd $dirToCheckOut/Gemini-poc-mgnt

cd Dockerfiles
if [ $repoType == 4 ]
then
    echo "copying repoType Dev"
    cp ../apporbit-dev.repo .
    cp ../apporbit-test.repo .
    cp ../apporbit-master.repo .
    cp ../Gemfile-master Gemfile
elif [ $repoType == 3 ]
then
    echo "copying repoType Integration"
    cp ../apporbit-master.repo .
    cp ../apporbit-test.repo .
    cp ../Gemfile-master Gemfile
elif [ $repoType == 2 ]
then
    echo "copying repoType Master"
    cp ../apporbit-master.repo .
    cp ../Gemfile-master Gemfile
else
    echo "copying repoType RELEASE"
    cp ../apporbit-release.repo .
    cp ../Gemfile-release Gemfile
fi

if [ $quickBuild != 1 ]
then
  # echo "apporbit Base Image..."
  # docker build -t apporbit/apporbit-base$commitIDstr -f apporbitBase .
  echo "apporbit Platform Base Image..."
  docker build -t apporbit/apporbit-controller-base$commitIDstr -f apporbit-controller-base .
fi
rm Gemfile apporbit*.repo
cd ..

echo "apporbit controller Image..."
docker build -t apporbit/apporbit-controller$commitIDstr -f Dockerfiles/apporbit-controller .

if [ $buildType -eq 1 ] || [ $buildType -eq 3 ]
then
	mkdir -p $dirToCheckOut/$commitID
	docker save apporbit/apporbit-controller$commitIDstr > $dirToCheckOut/$commitID/apporbit-controller.tar
	docker save apporbit/apporbit-services$commitIDstr > $dirToCheckOut/$commitID/apporbit-services.tar
fi

if [ $buildType -eq 2 ] || [ $buildType -eq 3 ]
then
	docker tag -f apporbit/apporbit-services$commitIDstr secure-registry.gsintlab.com/apporbit/apporbit-services$commitIDstr
	docker push secure-registry.gsintlab.com/apporbit/apporbit-services$commitIDstr
	docker tag -f apporbit/apporbit-controller$commitIDstr secure-registry.gsintlab.com/apporbit/apporbit-controller$commitIDstr
	docker push secure-registry.gsintlab.com/apporbit/apporbit-controller$commitIDstr
fi

if [ $buildType -eq 4 ]
then
        cd $dirToCheckOut/deta
        echo "Compiling deta.."
        make setup
        make 
fi
cd ..




