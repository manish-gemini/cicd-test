#!/bin/bash
if [ "$1" == "" ]
then 
  BRANCH=master
else
  #OPTIONS for BRANCH master, integration, dev
  BRANCH=$1
fi
cd ./Gemini-poc-stack
git reset --hard HEAD
git pull
git checkout $BRANCH
#git checkout tags/$commitID
cd ../Gemini-poc-mgnt
git reset --hard HEAD
git pull
git checkout $BRANCH
#git checkout tags/$commitID
cd ../Gemini-CLI
git reset --hard HEAD
git pull
git checkout $BRANCH
#git checkout tags/$commitID
cd ../docs
git reset --hard HEAD
git pull
git checkout $BRANCH
#git checkout tags/$commitID
cd ../cicd
git reset --hard HEAD
git pull
git checkout $BRANCH
#git checkout tags/$commitID
cd ../
