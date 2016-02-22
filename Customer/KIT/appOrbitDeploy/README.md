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

Run the below command.

```
bash <(curl -s  http://repos.gsintlab.com/install/appOrbitKit/install.sh)
```

* This will Start to download the installer binaries in /opt/apporbit/bin

* System requirements as specified in the requirement documentations is verified. On success the installation proceeds, in case of failure error message is displayed and you can verify the detailed installation logs at /opt/apporbit/bin/appOrbitInstall.log

* Login to the appOrbit registry using the credentials sent to you by email by your appOrbit sales representative admin/<password>
	
	Enter the user name: admin
	Password:
		
* Enter the build ID, by default is latest
	Enter the build id [latest] :
	
* Enter the chef server deploy mode :

	1. Deploy on the same host
	2. Do not deploy, will configure it later
	choose the setup type from the above [1] :1
		
 * New install or upgrade :
 
	1. New install
	2. Upgrade
	choose the setup type from the above [2] :1
		
 * Enter the type of SSL certificate type:
 
	1. Create a new ssl Certificate
	2. Use Existing Certificate
	Choose the type of ssl Certificate [1]:1

 * Enter the Mode of Deployment:
 
	1. Singe-Tenant
	2. Multi-Tenant
	Choose the type of deployment [1]:1

 * Enter the user email id for single-tenant deployment [admin@apporbit.com] :
	
 * Enter hostname or host ip [Default:<IP ADDRESSS>] :
	
 * Now, the appOrbit management server starts to deploy.

##Login to appOrbit Management server

 * On Successful deployment, you will be able to login into the User Management Console in the UI at https://${hostip} using default password 'admin1234'
 
 * Please change your default password 'admin1234' by logging into the User Management Console in the UI at https://${hostip}/users

 * Now you can refer to the product documentation in  http://${hostip}:9080. It is recommended to change the chef-server password. 

   Refer the below link for details.
   http://${hostip}:9080deploying-the-apporbit-platform.html#to-change-the-apporbit-chef-default-password 

##Installation Logs

In case of Installation issues, you can refer to /opt/apporbit/bin/appOrbitInstall.log .





