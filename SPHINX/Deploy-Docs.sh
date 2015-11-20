#!/bin/bash
# Deploy Docs 

#Remove running apporbit-docs

docker rm -f apporbit-docs

#Run the existing container
docker run --name apporbit-docs -p 9080:80 -d apporbit/apporbit-docs

