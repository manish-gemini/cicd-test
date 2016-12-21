AppOrbit Installer Documentation
=================================

# System Requirements

## Hardware

- 4 vCPU
- 8 GB RAM
- 100 GB disk space recommended disk space in the host machine

Network public IP or private IP
A private IP can be used only when the entire cloud is running in a private, on premise environment without public IPs. If the platform needs to create any clusters in the public cloud or private cloud on the public network, the configuration management server needs to use public IPs, and be accessible to all created virtual machines and the appOrbit Platform.

## Supported Operating System

CentOS 7.1, 7.2  or Redhat Enterprise Linux 7.1, 7.2

## Ports Used
The appOrbit Platform requires the following ports in the host firewall accessible from the internet:
- 80
- 443
- 9443
- 9080 
- 8500 (consul)
- 53 /tcp/udp (consul)

## Software

Have curl  installed.

# Installation Steps

## Install appOrbit Management server :

Run the below command.

```
bash <(curl -s http://repos.apporbit.com/install/appOrbitKit/install.sh)
```

This command:
    
    - Starts to download installer binaries.
        Downloads the appOrbit installer.
    - This verifies the system requirements as specified in the “Prerequisite requirements”.
        
    - After the installation begins, the following prompt displays:

	appOrbit server is not installed.
	apporbit-server will install/upgrade the appOrbit server in this machine
	Installation log will be in : /var/log/apporbit/apporbit-server.log
	Verifying system information.
	[====================] 100%   -- [Done]

	appOrbit Registry setup (sent to you by email, by appOrbit support team):
	    appOrbit registry name [registry.apporbit.com]: 
	    Registry user name[]: 
	    Password:
	    dataservice registry name [apporbit-apps.apporbit.io:5000]: 

	appOrbit Deployment setup:

     DNS/FQDN/IP for apporbit host [X.X.X.X]:

     DNS Domain that will be managed by appOrbit Server []:
        
     Configure SSL certificate for the apporbit server:

        [1] Create new SSL certificate

        [2] Use existing certificate
 
     Choose the type of SSL configuration [1]:

	Deploy Chef on this host:

	   [1] Yes: Deploy on the same host

	   [2] No: Chef is deployed on another server

	   Choose Chef deployment [1]:
	    
	Configure the SSL certificate for chef-server:

	   [1] Create new SSL certificate

	   [2] Use an existing certificater

	   Choose SSL configurationfor Chef [1]:

	Deploy Consul server on this host:

	   [1] Yes: Deploy on the same host

	   [2] No: Use existing consul deployed on different host

	   Choose the deployment mode from the above [1]:

	appOrbit Software Setup

	    appOrbit version [latest]:

	    Enter admin user email id for server login [admin@apporbit.com]:

	Configuring appOrbit setup

	Preparing and removing old containers for appOrbit server.

	[====================] 100%   -- [Done]
	
	Download appOrbit Server container images

	[====================] 100%   -- [Done]
	
	Deploying appOrbit server.

	[====================] 100%   -- [Done]
	
	Waiting for appOrbit server to be active

	[====================] 100%   -- [Done]
	
	Now login to the appOrbit server using

	https://X.X.X.X

	Login: admin@apporbit.com

	and default password 'admin1234'

	Server logs moved to /var/log/apporbit/apporbit-server-XXXXXXXX.log


