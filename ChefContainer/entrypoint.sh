#!/bin/sh
#
# Entrypoint script for docker image of GeminiStack
#
#dpkg-divert --local --rename --add /sbin/initctl
ln -sf /bin/true /sbin/initctl
sysctl -w kernel.shmmax=17179869184
/opt/chef-server/embedded/bin/runsvdir-start &
chef-server-ctl reconfigure
tail -F /var/log/*.log
