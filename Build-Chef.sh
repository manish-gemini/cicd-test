#!/bin/bash
echo "Starting to build apporbit-chef"
cd  ChefContainer
docker build -t apporbit/apporbit-chef .
echo "Build Completed!"

