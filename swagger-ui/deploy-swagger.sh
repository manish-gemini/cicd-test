#!/bin/bash

docker run --name apporbit-api-docs -v /var/www/apporbit/api-docs -p 90:8080 -p 8443:443 -d apporbit/apporbit-api-docs
