#!/bin/bash
if [ "$1" == "" ]
then 
  BRANCH=master
else
  #OPTIONS for BRANCH master, integration, dev
  BRANCH=$1
fi
cd ./Gemini-poc-stack
echo "Working on:" `pwd`
git reset --hard HEAD
git pull
git checkout $BRANCH
#git checkout tags/$commitID
cd ../Gemini-poc-mgnt
echo "Working on:" `pwd`
git reset --hard HEAD
git pull
git checkout $BRANCH
#git checkout tags/$commitID
cd ../Gemini-CLI
echo "Working on:" `pwd`
git reset --hard HEAD
git pull
git checkout $BRANCH
#git checkout tags/$commitID
cd ../docs
echo "Working on:" `pwd`
git reset --hard HEAD
git pull
git checkout $BRANCH
#git checkout tags/$commitID
cd ../cicd
echo "Working on:" `pwd`
git reset --hard HEAD
git pull
git checkout $BRANCH
#git checkout tags/$commitID
cd ../
