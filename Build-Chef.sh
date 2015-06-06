#!/bin/bash
echo "Starting to build gemini-chef"
cd  ChefContainer
docker build -t gemini/gemini-chef .
echo "Build Completed!"

