#!/bin/bash
# Deploy Docs 

#Remove running gemini-docs

docker rm -f gemini-docs

#Run the existing container
docker run --name gemini-docs -p 3000:80 -d gemini/gemini-docs

