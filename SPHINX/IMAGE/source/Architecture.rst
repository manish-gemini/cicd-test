**Architecture**
================

The appOrbit Platform that is used to deploy, manage and control the
lifecycle of an application using containers that reside in the cloud.
Each container in the appOrbit Platform is a lightweight virtualization
of the operating system that is used as a separate instance, within a
larger Linux instance.

The appOrbit Platform allows you to do more with consolidation using
cloud-based servers in a manner that improves productivity and reduces
resource requirements. The appOrbit Platform also manages Infrastructure
as a Service (IaaS) features to deploy virtual machines. It takes
advantage of cloud-specific block storage features, for example, the
Amazon Elastic Block Storage (EBS), by creating a data fabric over the
storage that is provisioned to applications on demand.

The appOrbit Platform architecture consists of the User Interface Server
and a representational state transfer (REST) API packet.

> ![](media/image01.png)

The key components of the appOrbit Platform architecture include:

-   **appOrbit Controller**. User interface (UI), API server and core
    > platform controller.

-   **appOrbit DB**: Database that stores persistent information about
    > the appOrbit Platform.

-   **appOrbit MQ**: Rabbit messaging queue (MQ) for transmitting
    > information between the appOrbit Controller and appOrbit Services.

-   **appOrbit Services**: Services that are consumed by the
    > appOrbit Platform. appOrbit Services consists of the data layer,
    > data controller, cluster controller and cloud management layer.

-   **appOrbit Chef**: Cloud orchestrator that is used to provision
    > scripts on newly created virtual machines. When virtual machines
    > are created in the cloud, appOrbit Chef installs the software to
    > appOrbit Platform requirements for appOrbit Services and clusters.

-   **appOrbit Docs**: Web server that hosts the documentation about the
    > appOrbit Platform.

-   **appOrbit Registry**. The appOrbit Platform uses the Docker
    > registry as a central repository to store a collection of master
    > images, also called templates, that is used by all software. All
    > of the container images are sourced from the Docker Registry. The
    > pubic Docker Hub Registry is located at:
    > [*https://hub.docker.com/*](https://hub.docker.com/). You can also
    > create a private Docker Registry that stores Docker images and
    > works in conjunction with the Docker Hub Registry.

-   **Operating system**. The appOrbit Platform uses either the CentOS
    > 7.x or Redhat Enterprise Linux 7.x operating system.

-   **Host**. The host for the appOrbit Platform consists of one
    > physical server with a minimum configuration of 8 GB RAM, 4 vCPU
    > and 100 GB disk, with 8 GB disk space in the host machine.
