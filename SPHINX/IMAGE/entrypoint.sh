#!/bin/bash -x

# make builder from within container
#sourceDir - /home/SpinxDir/source
#DestDir   - /home/SpinxDir/source/_build

echo " Build your source using Sphinx Builder"

echo " Make sure you have your Source in /opt/SPHINX/Source"

cd /home/SpinxDir/source/

if [ -f conf.py ]
then
echo 'conf eit'
fi

read -r -p "Do you want to continue ? [Y]/n " result

if [[ $result =~ ^[Yy]$ ]]
then
  sphinx-build -b html . _build/html
#  sphinx-build -b builder /home/Source /home/Dest
fi
echo 'exiting '
