AppOrbit Installer Documentation
=================================

# System Requirements

## Hardware

- 4 vCPU
- 8 GB RAM
- 100 GB disk space
- 8 GB minimum free disk space in the host machine

Network public IP or private IP
A private IP can be used only when the entire cloud is running in a private, on premise environment without public IPs. If the platform needs to create any clusters in the public cloud or private cloud on the public network, the configuration management server needs to use public IPs, and be accessible to all created virtual machines and the appOrbit Platform.

## Supported Operating System

CentOS 7.0 or Redhat Enterprise Linux 7

## Ports Used
The appOrbit Platform requires the following ports in the host firewall accessible from the internet:
- 80
- 443
- 9443
- 9080 

## Software

Have python and curl installed.

# Installation Steps

## Install appOrbit Management server :

1) Run the below command.

```
bash <(curl -s  http://repos.gsintlab.com/install/appOrbitKit/install.sh)
```

** Start to download installer binaries
		  Downloading apporbit installer

	b) This will verify system requirements as specified in the requirement documentations
	
		Verifying system informations.
		[====================] 100%   -- [Done]
	
	c) Login to the appOrbit registry using the credentials sent to you by email by your appOrbit sales representative

		Enter the user name: admin
		Password:
		
	d) Enter the build ID by default is latest
		Enter the build id [latest] :
	
	g) Enter the chef server deploy mode :
		1. Deploy on the same host
		2. Do not deploy, will configure it later
		choose the setup type from the above [1] :1
		
	h) New install or upgrade :
		1. New install
		2. Upgrade
		choose the setup type from the above [2] :1
		


	i) Enter the type of SSL certificate type:
		1. Create a new ssl Certificate
		2. Use Existing Certificate
		Choose the type of ssl Certificate [1]:1

	j) Enter the Mode of Deployment
		1. Singe-Tenant
		2. Multi-Tenant
		Choose the type of deployment [1]:1

	k) Enter the user email id for single-tenant deployment [admin@apporbit.com] :
	
	l) Enter hostname or host ip [Default:<IP ADDRESSS>] :
	
	m) Deploying appOrbit management server.
		[====================] 100%   -- [Done]
		
		Please change your default password 'admin1234' by logging into the User Management Console in the UI at https://${hostip}/users

Login to appOrbit Management server

Now you can start using appOrbit Management server by browsing  https://${hostip} and refer to the product documentation in  http://${hostip}:9080. It is recommended to changge the chef-server password. 

Refer the below link for details.
 http://${hostip}:9080deploying-the-apporbit-platform.html#to-change-the-apporbit-chef-default-password 

Installation Logs

In case of Installation issues, you can refer to /opt/apporbit/bin/appOrbitInstall.log .





