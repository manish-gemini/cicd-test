**Architecture**
================

appOrbit is a platform that is used to deploy, manage and control the
lifecycle of an application using containers that reside in the cloud.
Each container in appOrbit Platform is a lightweight virtualization of
the operating system that is used as a separate instance, within a
larger Linux instance.

appOrbit Platform allows you to do more with consolidation using
cloud-based servers in a manner that improves productivity and reduces
resource requirements. In addition to managing Infrastructure as a
Service (IaaS) features to deploy virtual machines, appOrbit Platform
also takes advantage of cloud-specific block storage features, including
the Amazon Elastic Block Storage (EBS), and creates a data fabric over
it that is provisioned to applications as needed.

The appOrbit Platform architecture consists of the User Interface Server
and the representational state transfer (REST) API packet.

![](media/image01.jpg)

The key components of appOrbit Platform include:

-   **appOrbit Controller**. User interface (UI) and API Server and core
    > platform controller.

<!-- -->

-   **appOrbit DB**: Database that stores the persistent information
    > about the platform.

-   **appOrbit MQ**: Rabbit messaging queue (MQ) used to transmit
    > information between the appOrbit Controller and appOrbit Services.

-   **appOrbit Services**: Services that are consumed by
    > appOrbit Platform. appOrbit Services consists of the data layer,
    > data controller, and the cluster controller.

-   **appOrbit Chef**: Cloud orchestrator that is used to provision
    > scripts on newly created virtual machines. When virtual machines
    > are created in the cloud, appOrbit Chef is used to install the
    > software to appOrbit Platform requirements for appOrbit Services
    > and clusters.

-   **appOrbit Docs**: Web server that hosts the documentation about
    > appOrbit Platform.

<!-- -->

-   **Docker Registry**. Docker 1.7.1 is an open platform for
    > distributed applications. The Docker registry used with appOrbit
    > Platform is a collection of master images, also called templates,
    > that is used by all software. In Docker, each image is a
    > container, similar to an operating system image. All of the images
    > are stored in a central repository. The pubic repository is[
    > ](https://hub.docker.com/)[*https://hub.docker.com/*](https://hub.docker.com/).
    > You can also create a private central repository to store
    > Docker images. The private repository works in conjunction with
    > the public repository.

-   **CentOS**. The appOrbit Platform uses the Centos 7.0 or Redhat
    > Enterprise Linux 7 operating system.

-   **Host**. The host appOrbit Platform consists of one physical host
    > server with a minimum configuration of 8 GB RAM, 4 vCPU and 100 GB
    > disk, with 8 GB disk space in the host machine.
