Use this file as Read me for local config edit.


NOTE: In general Rename the file example.local.conf to local.conf and edit the fields refering to this doc

1) For Master Build Verification., use master.local.conf and rename to local.conf, Provide Hostip and modify cleansetup attribute as per requirment
2) For Integration Build Verification, use integration.local.conf and rename to local.conf , Provide Hostip and modify cleansetup attribute as per requirement

[Registry Login]
username:
	User Name of appOrbit Docker Registry
password :
	Passoword of appOrbit Docker Registry

[User Config]
	User Config Information.
build_deploy_mode:
    # This sets up Mode of Deploy
    # 0 - QA/Dev Deploy for Master/Integration Build
    # 1 - Dev/QA local Deploy for local volume mount build ( prerequisite: run Build.sh for local images)
    [NOTE: For any build mode, if you specify volume_mount attribute,
    the specified volume will be mounted to the image chosen for deployment.

    Example:
    build_deploy_mode = 0
    reg_url = secure-registry.gsintlab.com
    volume_mount = /opt

    In this case, controller and service will be lauched using Master Images and will be volume mounted to
    /opt/Gemini-poc-stack and /opt/Gemini-poc-mgnt respectively.
    ]
	
build_id :
	latest
remove_data : 
    # True  - Python case sensitive boolean - REMOVES /var/lib/apporbit
    # False - Default option - Reuse data already existing
self_signed_crt :
    # 1 - Create new SSL
    # 2 - Use Existing SSL
self_signed_crt_dir :
    In case you are using Use Existing SSL, Provide the Directory where to pick apporbitserver.key apporbitserver.crt files

chef_ssl_crt :
    # 1 - Create new SSL for chef server
    # 2 - Use Existing SSL
chef_ssl_crt_dir :
    In case you are using Use Existing SSL, Provide the Directory where to pick <HOSTIP>.key <HOSTIP>.crt files.
    HOSTIP is to be replaced with what you provide as the value of hostip below.

deploy_chef :
    # 0 - Deploy Chef in the same machine using Locally Build Chef Image
     [Note: Chef Image can be build locally using Build-chef.sh in cicd root dir ].
    # 1 - Deploy Chef in the same machine Using Repo, repo is as specified in registry_url parameter
    # 2 - Dont Deploy Chef in the same machine
    # 3 - Option Same as [1]
deploy_mode :
    # 1 - Single Tenanat
    # 2 - Multi Tenanat
on_prem_emailid = admin@apporbit.com
hostip = <HOST IP>
themename = apporbit-v2
api_version = v2
registry_url :
	Sepicify it if you use build_deploy_mode = 0 for QA Master/Integration build
	by specifying " secure-registry.gsintlab.com" for Master test
	"jenkin-registry.gsintlab.com" for integration test
internal_repo = http://repos.gsintlab.com/repos
volume_mount : 
Location for Code of Controller and Services to be volume mounted.
consul_ip_port = http://<HOST_IP>:8500
 	Consul is a distributed service discovery tool and key value store
	The variable "consul_ip_port" is used to locate consul and is used by Locator
consul_host = 
	The consul will configure its domain using the value specified in "consul_domain"
        (mentioned below) only if 'consul_host' is routable.
	example: consul_host= myhost.mycompany.com
consul_domain = 
	This variable is used by Consul to configure its domain name. If the host name 		  specified in 'consul_host' is routable, it is configured else the default 
        configuration is used.
	example: consul_domain=apporbit.mycompany.com
