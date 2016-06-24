#!/bin/bash

docker run --name swagger -p 90:8080 -p 8443:443 -d apporbit/swager
