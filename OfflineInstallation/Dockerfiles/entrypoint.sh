#!/bin/sh
#
# Entrypoint script for docker image of Offline Container
#

/usr/sbin/httpd
rackup -o 0.0.0.0 /root/config.ru
