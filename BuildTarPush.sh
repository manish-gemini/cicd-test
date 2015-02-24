#!bin/bash
#  Copyright 2015 Gemini Systems. All rights reserved

#####AUOMATE tar and upload.,
echo -n "Enter the build type:"
echo -n "Build a Tar file = 1"
echo -n "Build and push to internal Reg = 2"
echo -n "Build both Tar and push to internal Reg = 3"
echo -n "Build Test = 4"
read buildType
echo $buildType

echo -n "Enter the Directory to checkout source and Save Tar Files"
read dirToCheckOut
echo $dirToCheckOut

echo -n "Enter the Internal Registry Ip "
read internRegIp
echo $internRegIp

echo -n "Enter the commit ID/Tag ID:"
echo -n "(if left empty will pull the latest code.)"
read commitID
echo $commitID

echo -n "Enter the SECRET_KEY:"
read secretkey
echo $secretkey

echo -n "Enter the INIT_VECTOR:"
read initVector
echo $initVector

#echo $buildType  $dirToCheckout $InternalRegistry $commitID

#STEP 1:GET A DESTINATION DIR TO CHECKOUT CODE AND CREATE DIR

mkdir -p $dirToCheckOut
cd $dirToCheckOut
echo "Created "$dirToCheckOut
echo "..."


#STEP 2: URL FROM WHICH CODE IS TO BE CHECKED OUT. GIT LOGIN STUFF SHOULD HAVE ALREADY HAPPENED..
if [ -d Gemini-poc-stack ]
then
        echo "pull...."
        # pull instead of clone
        cd $dirToCheckOut
	cd Gemini-poc-stack
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
cp -f Dockerfile_BuildFromBase Dockerfile
docker build -t gemini/gemini-stack:$commitID .

#PLATFORM CODE :

cd $dirToCheckOut/Gemini-poc-mgnt
cp -f Dockerfile_BuildFromBase Dockerfile
docker build -t gemini/gemini-platform:$commitID .

if [ $buildType==1 ] || [ $buildType==3 ]
then
mkdir -p $dirToCheckOut/$commitID
docker save gemini/gemini-platform:$commitID > $dirToCheckOut/$commitID/gemini-platform.tar
docker save gemini/gemini-stack:$commitID > $dirToCheckOut/$commitID/gemini-stack.tar
fi

if [ $buildType==2 ] || [ $buildType==3 ]
then
docker tag gemini/gemini-stack:$commitID $internRegIp:5000/gemini/gemini-stack:$commitID
docker push $internRegIp:5000/gemini/gemini-stack:$commitID
docker tag gemini/gemini-platform:$commitID $internRegIp:5000/gemini/gemini-platform:$commitID
docker push $internRegIp:5000/gemini/gemini-platform:$commitID
fi
