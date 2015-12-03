**System Requirements**
=======================

The appOrbit Platform requires the following prerequisite software and
hardware, and ports used.

**Software**
------------

The software requirements for the physical host server include:

-   CentOS 7.0 or Redhat Enterprise Linux 7

-   Docker 1.7.1

-   Script and tar files deployed

**Hardware**
------------

The minimum hardware requirements for the physical host server include:

-   4 vCPU

-   8 GB RAM

-   100 GB disk space

-   8 GB minimum free disk space in the host machine

-   Network public IP or private IP

> **Note**: A private IP can be used only when the entire cloud is
> running in a private, on premise environment without public IPs. If
> the platform needs to create any clusters in the public cloud or
> private cloud on the public network, the configuration management
> server needs to use public IPs, and be accessible to all created
> virtual machines and the appOrbit Platform.

**Ports Used**
--------------

The appOrbit Platform requires the following ports in the host firewall:
80, 443, 9443 and 8080. There are other ports that are used internally.

The use of each of these ports is described below.

**Table 1-1: Ports used by the appOrbit Platform**

  ------------------------------------------------------------------------------------------------------------------------------------------------
  **Port requirement**    **Description**                                  **Ports used**
  ----------------------- ------------------------------------------------ -----------------------------------------------------------------------
  **appOrbit Platform**   Exposed from container                           -   Port 80 for HTTP (redirector)
                                                                           
                                                                           -   Port 443 for HTTPS (SSL)
                                                                           
                                                                           

                          Ports used by the appOrbit Platform              -   Not exposed externally
                                                                           
                                                                           

  **appOrbit Services**   Exposed from container                           -   Not exposed externally
                                                                           
                                                                           

                          Ports of the host used by appOrbit Services      -   Port 9443 (appOrbit Chef)
                                                                           
                                                                           

  **appOrbit Chef**       Exposed from container                           -   Port 9443
                                                                           
                                                                           

                          Ports used by appOrbit Chef                      -   Port 22 of the physical or virtual machines deployed in the cloud
                                                                           
                                                                           

  **appOrbit MQ**         Web port used by appOrbit MQ for communication   -   Not exposed externally
                                                                           
                                                                           

  **appOrbit DB**         Default MYSQL container                          -   Not exposed externally
                                                                           
                                                                           

  **appOrbit Docs**       Default port (documentation server)              -   Port 9080
                                                                           
                                                                           
  ------------------------------------------------------------------------------------------------------------------------------------------------
