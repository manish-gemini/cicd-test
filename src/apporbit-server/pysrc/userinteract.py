#!/usr/bin/env python

import getpass
import logging
import urllib2
import os
from utility import Utility

class UserInteract:

    def __init__(self):
        self.util_obj = Utility()
        return

    def deployChefOnly(self, config_obj, utility_obj):
        print "Login to the appOrbit registry using the credentials sent to you by email, by appOrbit support team."
        config_obj.apporbit_registry = raw_input("Enter the registry name [%s]: " %config_obj.apporbit_registry) or config_obj.apporbit_registry
        config_obj.registry_uname = raw_input("Enter the user name[%s]: " %config_obj.registry_uname) or config_obj.registry_uname
        if config_obj.registry_passwd <> '':
           password_prompt = 'Password[*****]: '
        else:
           password_prompt = 'Password: '
        passwd  = getpass.getpass(password_prompt)
        if passwd <> '':
           config_obj.registry_passwd = passwd
        # is_install_cfgmgr = raw_input("\n Do you want to deploy config manager in the same machine? [Y/n] : ") or 'y'
        
        utility_obj.loginDockerRegistry(config_obj.registry_uname, config_obj.registry_passwd, config_obj.apporbit_registry)

        if utility_obj.isChefDeployed():
            print "Chef Deployment Mode "
            print "1) Fresh install of Chef (Removes old nodes data)"
            print "2) Upgrade Chef"
            chef_deploy_mode = raw_input("Enter the Chef deployment mode [2]:") or '2'
            config_obj.chef_deploy_mode = chef_deploy_mode

        try:
            ip = urllib2.urlopen("http://whatismyip.akamai.com").read()
        except:
            ip = ''
            logging.warning ("Could not figure out self public ip using web service. Asking user for ip")
        hostIp = raw_input("DNS/FQDN/IP of Chef Server host [%s]:" %ip) or ip
        config_obj.apporbit_host = hostIp
        config_obj.chef_host = hostIp


        print 'Configure the SSL certificate for chef-server:'
        print '1. Create new SSL certificate'
        print '2. Use existing SSL certificate'
        chef_self_signed_crt = raw_input("Choose SSL configuration for chef-server [1]:") or '1'
        config_obj.chef_self_signed_crt = chef_self_signed_crt
        if chef_self_signed_crt == '2':
            hostipcrt = hostIp + ".crt"
            hostipkey = hostIp + ".key"
            print "Rename your SSL certificate file for Chef as " + hostipcrt + " and SSL key file as " + hostipkey
            chef_ssldir = raw_input("Enter location where current SSL certificate and the key files for Chef exist [/opt/chefcerts]:") or "/opt/chefcerts"
            config_obj.hostipcrt = hostipcrt
            config_obj.hostipkey = hostipkey
            config_obj.chef_ssldir = chef_ssldir
            config_obj.create_keys = False
            config_obj.import_keys_from_dir = chef_ssldir

        return



    def getUserConfigInfo(self, config_obj, utility_obj):
        # Used Variables Declared
        is_install_cfgmgr = ""
        on_prem_emailid = ""
        hostIp = ""
        ssldir = ""
        chef_ssldir = ""
        is_fresh_install = True
        chef_self_signed_crt = '0'
        consul_ip_port= ""
        consul_domain = ""
        consul_host = ""

        logging.info("Starting to get user config info")
        # is_install_cfgmgr = raw_input("\n Do you want to deploy config manager in the same machine? [Y/n] : ") or 'y'
        print ""
        print "appOrbit Registry setup (sent to you by email, by appOrbit support team):"
        config_obj.apporbit_registry = raw_input("    appOrbit registry name [%s]: " %config_obj.apporbit_registry) or config_obj.apporbit_registry
        if config_obj.apporbit_registry == 'local':
            config_obj.apporbit_registry = ''

        if config_obj.apporbit_registry:
            config_obj.registry_uname = raw_input("    Registry user name[%s]: " %config_obj.registry_uname) or config_obj.registry_uname
            if config_obj.registry_passwd <> '':
               password_prompt = '    Password[*****]: '
            else:
               password_prompt = '    Password: '
            passwd  = getpass.getpass(password_prompt)
            if passwd <> '':
               config_obj.registry_passwd = passwd
            # is_install_cfgmgr = raw_input("\n Do you want to deploy config manager in the same machine? [Y/n] : ") or 'y'
            utility_obj.loginDockerRegistry(config_obj.registry_uname, config_obj.registry_passwd, config_obj.apporbit_registry)
        utility_obj.createTempFile(config_obj)
        while True:
            config_obj.datasvc_registry = raw_input("    dataservice registry name [%s]: " %config_obj.datasvc_registry) or config_obj.datasvc_registry
            if config_obj.datasvc_registry == 'local':
               print "local registry is not supported"
               next
            else:
               break

        print ""
        print "appOrbit Deployment setup:"

        # Setup is always upgrade
        config_obj.remove_data = False
        try:
            if os.stat(config_obj.APPORBIT_DATA) and os.listdir(config_obj.APPORBIT_DATA):
                config_obj.initial_install = False
            else:
                config_obj.initial_install = True
        except:
            config_obj.initial_install = True

        if config_obj.apporbit_host == "":
           try:
              config_obj.apporbit_host = urllib2.urlopen("http://whatismyip.akamai.com").read()
           except:
              logging.warning ("Could not figure out self public ip using web service. Asking user for ip")
        config_obj.apporbit_host = raw_input("   DNS/FQDN/IP for apporbit host [%s]:" %config_obj.apporbit_host) or config_obj.apporbit_host
        hostIp = config_obj.apporbit_host
        consulDomain = raw_input("   DNS Domain that will be managed by appOrbit Server [%s]:" %config_obj.apporbit_domain ) or config_obj.apporbit_domain
        config_obj.apporbit_domain = consulDomain

        print '    Configure SSL certificate for the apporbit server:'
        print '    1. Create new SSL certificate '
        print '    2. Use existing certificate '
        self_signed_crt = raw_input ("    Choose the type of SSL configuration [1]:") or '1'
        logging.info ("self signed certificate : %s", self_signed_crt)
        if self_signed_crt == '2':
            print "    Rename your SSL certificate file as apporbitserver.crt and SSL key file as apporbitserver.key"
            ssldir = raw_input("    Enter location of certificate/key files [/opt/certs]:") or "/opt/certs"
            config_obj.import_keys_from_dir = ssldir
            config_obj.create_keys = False
            config_obj.self_signed_crt_dir = ssldir
            logging.info ("SSL Certs Directory is : %s", ssldir )
         

        utility_obj.createTempFile(config_obj)

        if config_obj.initial_install and config_obj.deploy_chef:
            print ""
            print 'Deploy Chef on this host:'
            print '    1. Yes: Deploy on the same host '
            print '    2. No: Chef is deployed on another server'
            is_install_cfgmgr = raw_input("    Choose Chef deployment [1]:") or '1'
            logging.info ("Chef mode of deployment : %s", is_install_cfgmgr)
        else:
            if self.util_obj.isChefDeployed() or config_obj.deploy_chef:
                is_install_cfgmgr = "1"
        if is_install_cfgmgr == "2":
             config_obj.deploy_chef = False
             chefIp = raw_input("    DNS/FQDN/IP for Chef Server host [%s]:" %config_obj.chef_host) or config_obj.chef_host
             config_obj.chef_host = chefIp
        else:
             config_obj.deployChef = True
             config_obj.chef_host = config_obj.apporbit_host

        utility_obj.createTempFile(config_obj)

        if config_obj.initial_install and is_install_cfgmgr == "1":
            print '    Configure the SSL certificate for chef-server:'
            print '    1. Create new SSL certificate'
            print '    2. Use an existing certificater'
            chef_self_signed_crt = raw_input("    Choose SSL configurationfor Chef [1]:") or '1'

            if chef_self_signed_crt == '2':
                hostipcrt = hostIp + ".crt"
                hostipkey = hostIp + ".key"
                print "    Rename your SSL certificate file for Chef as " + hostipcrt + " and SSL key file as " + hostipkey
                chef_ssldir = raw_input("    Enter the location of SSL certificate/ key files for Chef [/opt/chefcerts]:") or "/opt/chefcerts"
                logging.info ("Chef SSL Certs Directory is  : %s", chef_ssldir )

        utility_obj.createTempFile(config_obj)
        print ""
        print 'Deploy Consul server on this host:'
        print '    1. Yes: Deploy on the same host '
        print '    2. No: Use existing consul deployed on different host'
        is_install_consul = raw_input("    Choose the deployment mode from the above [1]:") or '1'
        logging.info ("Consul mode of deployment : %s", is_install_consul)
        if is_install_consul == "2":
             config_obj.deploy_consul = False
             config_obj.consul_host = raw_input("    Enter DNS/FQDN or host IP for Consul Server [%s]:" %config_obj.consul_host) or config_obj.consul_host
             config_obj.consul_port = raw_input("    Enter consul port [8500]:") or '8500'
        else:
             config_obj.deploy_consul = True
        if config_obj.consul_host == '':
             config_obj.consul_host = config_obj.apporbit_host

        logging.info ("Consul information : %s %s" % (config_obj.consul_host , config_obj.consul_port))
        utility_obj.createTempFile(config_obj)


        #BELOW LINES ARE INTENTIONALLY COMMENTED TO AVOID ASKING USER.
        #print "Enter the type of deployment:"
        #print "1. Singe-Tenant"
        #print "2. Multi-Tenant"
        #deploy_mode = raw_input("Choose the type of deployment [1]: ") or '1'
        print ""
        print 'appOrbit Software Setup'
        config_obj.buildid = raw_input("    appOrbit version [%s]: " %config_obj.buildid) or config_obj.buildid
        config_obj.deploy_mode = 'onprem'
        logging.info ("Mode of deployment : %s", config_obj.deploy_mode)
        if config_obj.deploy_mode == 'onprem':
            config_obj.apporbit_loginid = raw_input("    Enter admin user email id for server login [admin@apporbit.com]:") or config_obj.apporbit_loginid
            logging.info ("Email ID : %s", config_obj.apporbit_loginid )


        logging.info("completed collecting user config info")
        return
