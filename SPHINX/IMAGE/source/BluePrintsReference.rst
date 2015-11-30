**BluePrints Reference**
========================

NEEDS AN LEAD-IN STATEMENT

The appOrbit Platform Docker Lab Manager uses blueprint specifications
(YAML.YML templates) to orchestrate application instances. Each .YML
template uses keys to describe application details such as version and
application name, services, tiers, containers and so on.

For more details, go to “Overview of Docker Compose”
(https://docs.docker.com/compose/).

**.YML Template Example**
-------------------------

Notice the following example of a blueprint specification (.YML
template):

version: "1.0"

schemaVersion: v1

app\_id: MyDVDStore

description: |

The text of the description

here may be different for

different application.

icon:
"http://icons.iconarchive.com/icons/mazenl77/I-like-buttons-3a/512/Cute-Ball-Go-icon.png"

tiers:

- name: ds2db

type: db

replicas: 1

containers:

- name: postgresdb

image: jkshah/postgres:9.4

command:

- postgres

args:

- arg1

environment:

- POSTGRES\_USER: postgres

POSTGRES\_PASSWORD: secret

ports:

- containerPort: 5432

**service: internal/external**

**servicePort: Default | 5432**

**name: “somename” **

**procotol: TCP **

resources:

request:

min-cpus: 0.05

min-memory: 64M

**limits:**

**cpu: 0.5**

**memory: 1024M**

volumes:

- containerVolume: "/var/lib/postgresql/data"

min-size: 1G

**max-size: 10G**

**readOnly: False (Default is False, can be set to True)**

- name: ds2app

type: app

replicas: 1

containers:

- name: phpstoreapp

image: jkshah/dvdstore2:latest

**links:**

**- ds2db: myds2db**

environment:

- POSTGRES\_USER: postgres

POSTGRES\_PASSWORD: secret

**- name: POD\_NAMESPACE**

**valueFrom:**

**fieldRef:**

**fieldPath: metadata.namespace**

ports:

- hostPort: 80

containerPort: 80

**url:**

**- http://GEMINI\_SVC:GEMINI\_PORT/someuri**

**service: external (Denotes port to be added to external service)**

servicePort: 80

**labels:**

**net.gemini-systems.blueprint.name: "Auto accesible to container"**

**net.gemini-systems.blueprint.version “1.0”**

**net.gemini-systems.blueprint.environment “production”**

**com.example.label-with-empty-value: "" **

**remote\_services:**

**- name: oracledb**

**addresses:**

**- IP: ipaddress1**

**- IP: ipaddress2**

**ports:**

**- port: 5432**

**- protocol: TCP**

**- name: Test-Name**

**nodeSelector:**

**nodetype: default,master,compute,data**

**.YML Template Keys**
----------------------

Each .YML template for each blueprint is composed of a group of keys
that are used to orchestrate your application in the appOrbit Docker Lab
Manager.

Each of the keys used in each .YML template are described in the table
below.

**Table x: .YML Keys for Blueprints**

  --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  > **Keys / Associate Keys**   > **Definition**
  ----------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  > **version:**                > Application version. Enables multiple versions of your application to be deployedtested.
                                >
                                > **Note**: Used in Release Candidate version for ROLLING UPDATE
                                >
                                > Example;
                                >
                                > *version*: “1.0”

  > **schemaVersion:**          > API version of Docker Lab Manager.
                                >
                                > Example:
                                >
                                > *schemaVersion*: v1

  > **app\_id:**                > Application name. This is the instance name that is used as a namespace.
                                >
                                > Currently app\_id supports lowercase,namespace and letters only.
                                >
                                > Example:
                                >
                                > *app\_id*: joomla123

  > **description:**            > Description of the application.

  > **tiers:**                  > Tiers defined for each application.
                                >
                                > The associate keys are described below.

  > *name:*                     > User-defined name for each tier.

  > *types:*                    > Type of service running in each tier.
                                >
                                > Example:
                                >
                                > *types*: db
                                >
                                > *types*: web

  > *replicas:*                 > Number of replicas to run in the tier.
                                >
                                > When the value is set as 2, the application is hosted in two servers. In the event one application server goes down, the other server is available.
                                >
                                > This associate key also provisions the same application on another running host.
                                >
                                > It maintain 2 replicas at the same times. It use an internal load balancer to load balance replicas.
                                >
                                > Example:
                                >
                                > *replicas*: 2

  > *label:*                    

  > **containers:**             > Operating system images that bundles the operating system and application.
                                >
                                > The associate keys are described below.

  > *name:*                     > Container name.
                                >
                                > Example:
                                >
                                > *name*: dvdstoreapp
                                >
                                > **Note**: The fieldPath: metadata.namespace associate key uses SUPPORT name , valueFrom (or value) as Macrosupport for Kubernetes.

  > *image:*                    > Images used for the container to bundle the operating system and application.
                                >
                                > Example:
                                >
                                > *images*: jkshah/postgres:9.4

  > *command:*                  

  > *args:*                     

  > *links:*                    > Creates and additional internal service called myds2db with all ports in replication controller ds2db. It also adds environment variables from those tiers that are added with the ENV\_MYDS2DB\_ prefix. This associate key also adds the host with the alias making it accessible from
                                >
                                > Example:
                                >
                                > *ds2db:* myds2db

  > *environment:*              > Environment variables for the container image.
                                >
                                > An environment variable is a named object that contains data used by one or more applications. In simple terms, it is a variable with a name and value.
                                >
                                > However, environment variables provides a simple way to share configuration settings between multiple applications and processes in Linux.
                                >
                                > Example:
                                >
                                > *POSTGRES\_USER*: postgres
                                >
                                > *POSTGRES\_PASSWORD*: secret

  > *ports:*                    > Open port in container that is used to access the application. An open port can be used for a host as well as a container.
                                >
                                > The associated key are described below.

                                

  > *hostPort:*                 > Open port in host to access the application (deprecated).
                                >
                                > **Note**: Do not use this associate key frequently as it uses named resources that are to be consumed, which provides limited copies of the application.
                                >
                                > Example:
                                >
                                > *hostPort*: 5432

  > *containerPort:*            > Container port.
                                >
                                > Example:
                                >
                                > *containerPort*: 5432

  > *service:*                  > When at least one port is ‘external’ creates another common NodePort type of service for the app named ‘gem-pubsvc’ with all ports from all containers marked as external. Default port type – internal
                                >
                                > Example:
                                >
                                > internal/external

  > *servicePort:*              > When service is exposed as an exposed port
                                >
                                > Example:
                                >
                                > *servicePort*:
                                >
                                > Default | 5432

  > *name:*                     > With Kubernetes, the name is mandatory for multiple ports.
                                >
                                > **Note**: Adhere to IANA service name standard -[ ](https://tools.ietf.org/rfc/rfc6335.txt)[rfc6335](https://tools.ietf.org/rfc/rfc6335.txt).
                                >
                                > Example:
                                >
                                > *name:* “somename”

  > *procotol:*                 > Protocal choices include: TCP (default), UDP, http and https.
                                >
                                > **Note**: When HTTP or HTTPS is used for external services, the launch URL is given. Otherwise, the endpoint information is given. Kubernetes uses this information to set iptables rules for TCP or UDP).
                                >
                                > Example:
                                >
                                > *procotol*: TCP

  > *labels:*                   

  > *resources:*                > Allocation of resource for containers in a tier.
                                >
                                > The associate keys are described below.

  > *mincpus:*                  > Allocate minimum CPU share for a container in a tier.
                                >
                                > Example:
                                >
                                > *mincpus*: 0.05

  > *minmemory:*                > Allocate minimum memory for a container in a tier.
                                >
                                > Example:
                                >
                                > *minmemory*: 64M

  > *volumes:*                  > Allocation of volume resource for containers in a tier.
                                >
                                > The associate keys are described below.
                                >
                                > The examples shown indicate mount the host volume into a container under /var/lib/postgresql/data mount point, with the size of 1 GB from the host volume.
                                >
                                > **Note**: The string in the environmental variable requires the use of double quotes "".
                                >
                                > Example:
                                >
                                > environment: AUTH: "no"

  > *containerVolume:*          > Mount point in a container.
                                >
                                > Example :
                                >
                                > *containerVolume*:
                                >
                                > "/var/lib/postgresql/data"

  > *minsize:*                  > 1G (minimum size for mount volume).
                                >
                                > Example:
                                >
                                > *minsize*: 1G

  > **remote\_services:**       

  > *name:*                     > Creates an additional internal service called oracledb pointing to the IP or DNS name and port combination requested.

  > *address:*                  

  > **nodeSelector:**           

  > *nodetype:*                 > Node types include: default,master,compute,data
                                >
                                > **Note**: Default is auto selected when containers with volume goes on data, and without volumes goes on computer while special namespace kube-system goes on master)
                                >
                                > Example:
                                >
                                > nodeType:
  --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
