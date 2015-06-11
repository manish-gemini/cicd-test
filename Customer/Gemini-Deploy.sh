#!/bin/bash

echo "Setting up env Variables!"
if ! bash Gemini-predeploy.sh
then
	exit
fi

read -p "Do you want to execute Configuration manager in the same Machine ?Default(y):" yn
yn=${yn:-'y'}
case $yn in
        [Yy]* ) bash Gemini-Chef.sh; break;;
        [Nn]* ) break;;
        * ) echo "Please answer yes or no.";;
esac

echo "Deploy GeminiLabManager...."
if ! bash Gemini-LabManager.sh
then
        exit
fi




