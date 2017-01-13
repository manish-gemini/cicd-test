#!/bin/sh
#
# Entrypoint script for docker image of Offline Container
#

while [ 1 == 1 ];
do

    echo "Starting httpd..."
    /usr/sbin/httpd

    sleep 10

    if [ $(pgrep httpd | wc -l) -gt 1 ];
    then
        echo "found running httpd"
        break
    fi

done

rackup -o 0.0.0.0 /root/config.ru
