#!/bin/bash -x

# make builder from within container
#sourceDir - /home/Source
#DestDir   - /home/Dest

echo " Build your source using Sphinx Builder"

echo " Make sure you have your Source in /opt/SPHINX/Source"

read -r -p "Do you want to continue ? [Y] " resp

#if [[ $resp =~ ^[Yy]$ ]]
#then
  sphinx-build -b builder /home/Source /home/Dest
#fi 
