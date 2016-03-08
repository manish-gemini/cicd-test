Use this file as Read me for local config edit.


NOTE: In general Rename the file example.local.conf to local.conf and edit the fields refering to this doc

1) For Master Build Verification., use master.local.conf and rename to local.conf, Provide Hostip and modify cleansetup attribute as per requirment
2) For Integration Build Verification, use integration.local.conf and rename to local.conf , Provide Hostip and modify cleansetup attribute as per requirement

[Docker Login]
username:
	User Name of appOrbit Docker Registry
password :
	Passoword of appOrbit Docker Registry

[User Config]
	User Config Information.
build_deploy_mode:
    # This sets up Mode of Deploy
    # 0 - QA Deploy for Master/Integration Build
    # 1 - Dev Deploy for local volume mount build
    # 2 - QA/DEV local deploy.
	
build_id :
	latest
clean_setup : 
    # 1 - Install
    # 2 - Upgrade
self_signed_crt :
    # 1 - Create new SSL
    #2 - Use Existing SSL
self_signed_crt_dir :
    In case you are using Use Existing SSL, Provide the Directory where to pick apporbitserver.key apporbitserver.crt files

chef_ssl_crt :
    # 1 - Create new SSL for chef server
    # 2 - Use Existing SSL
chef_ssl_crt_dir :
    In case you are using Use Existing SSL, Provide the Directory where to pick <HOSTIP>.key <HOSTIP>.crt files.
    HOSTIP is to be replaced with what you provide as the value of hostip below.

deploy_chef :
    # 0 - Deploy Chef in the same machine using Local Chef Image.
    # 1 - Deploy Chef in the same machine Using Customer Repo
    # 2 - Dont Deploy Chef in the same machine
    # 3 - Deploy Chef in the same Macine using  Master/Jenkins Repo.
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
