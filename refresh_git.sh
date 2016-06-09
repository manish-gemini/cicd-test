#!/bin/bash
cpwd=`pwd`
if [ "$1" == "" ]
then 
  BRANCH=master
else
  #OPTIONS for BRANCH master, integration, dev
  BRANCH=$1
fi
function git_refresh() {
echo "Refreshing Git code on:" `pwd`
git reset --hard HEAD
git pull
git checkout $BRANCH
git pull

}

array=( Gemini-poc-stack Gemini-poc-mgnt Gemini-CLI docs cicd mist-cgp deta )
for i in "${array[@]}"
do
    cd ${cpwd}/$i
    git_refresh
done
cd ${cpwd}

