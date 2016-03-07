#!/bin/sh -x
#
# Entrypoint script for docker image of GeminiStack
#
#dpkg-divert --local --rename --add /sbin/initctl
ln -sf /bin/true /sbin/initctl
# sysctl -w kernel.shmmax=17179869184
# Make file changes to run postgresql in less memory
cp postgresql.rb /opt/chef-server/embedded/cookbooks/chef-server/recipes/postgresql.rb
if [ -z $UPGRADE]
then
	export UPGRADE=0
else
	export UPGRADE=$UPGRADE
fi
 
# Now start Chef Server
/opt/chef-server/embedded/bin/runsvdir-start &
chef-server-ctl reconfigure
# UPGRADE is 2 for Upgrade to happen.
if [ $UPGRADE == 2]
then
	cp -pa /var/opt/chef-server/*.json /etc/chef-server/
    cp -pa /var/opt/chef-server/*.pem  /etc/chef-server/
fi
cp -pa /etc/chef-server/*.json /var/opt/chef-server/
cp -pa /etc/chef-server/*.pem /var/opt/chef-server/ 
tail -F /var/log/*.log &
chef-server-ctl tail
