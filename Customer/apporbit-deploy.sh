#!/bin/bash

echo "Setting up env Variables!"
if ! bash apporbit-predeploy.sh
then
	exit
fi

read -p "Do you want to execute Configuration manager in the same Machine ?Default(y):" yn
yn=${yn:-'y'}
case $yn in
        [Yy]* ) bash apporbit-chef.sh; break;;
        [Nn]* ) break;;
        * ) echo "Please answer yes or no.";;
esac

while getopts e: option
do
        case "${option}"
        in
                e) theme=${OPTARG};;
        esac
done

if [ -z "$theme" ];
then
	theme="gemini" 
else 
	echo "theme is set to '$theme'";
fi

echo "Deploy appOrbit Lab Manager"
if ! bash apporbit-labmanager.sh $theme
then
        exit
fi

