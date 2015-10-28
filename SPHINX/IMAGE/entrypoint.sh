#!/bin/bash -x

/usr/sbin/nginx

tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log
