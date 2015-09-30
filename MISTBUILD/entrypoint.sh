#!/bin/bash -x

export PATH=$PATH:/opt/gradle-2.7/bin/
echo 'Starting to clone MIST from Repo'
git clone https://github.com/Gemini-sys/mist-cgp.git
if [ $? -ne 0 ];then
  echo "Clone failed..."
  exit
fi
read -p "Enter the branch to checkout [master]:" branch
cd mist-cgp
if [ ! -z "$branch" ]; then
    git checkout $branch
fi
/opt/gradle-2.7/bin/gradle build run:export.run
mv run/generated/distributions/executable/run.jar /tmp/.
