#!/usr/bin/env python

import getpass
import logging

import urllib2


class UserInteract:

    def __init__(self):
        return


    def getUserConfigInfo(self, config_obj):
        # Used Variables Decalred
        reg_user_name = ""
        reg_password = ""
        build_id = ""
        clean_setup = ""
        is_install_cfgmgr = ""
        deploy_mode = ""
        on_prem_emailid = ""
        hostIp = ""
        ssldir = ""

        logging.info("Starting to get user config info")
        print "Enter the user configuration information."
        print "------------------------------------------"
        print "Login to the appOrbit registry using the credentials sent to you by email, by appOrbit support team."
        reg_user_name = raw_input("Enter the user name: ")
        reg_password = getpass.getpass()
        build_id = raw_input("Enter the build version [latest]: ") or "latest"
        # is_install_cfgmgr = raw_input("\n Do you want to deploy config manager in the same machine? [Y/n] : ") or 'y'

        print 'Enter the chef server deployment mode:'
        print '1. Deploy on the same host '
        print '2. Do not deploy, configure it later'
        is_install_cfgmgr = raw_input("Choose the deployment mode from the above [1]:") or '1'
        logging.info ("Chef mode of deployment : %s", is_install_cfgmgr)

        print "Install or upgrade:"
        print "1. Install "
        print "2. Upgrade "
        clean_setup = raw_input("Choose the installation type from the above [2]:") or '2'

        logging.info("Clean Setup : %s", clean_setup)

        print 'Configure the SSL certificate:'
        print '1. Create a new SSL certificate'
        print '2. Use an existing certificate'
        self_signed_crt = raw_input ("Choose the type of SSL configuration [1]:") or '1'
        logging.info ("self signed certificate : %s", self_signed_crt)
        if self_signed_crt == '2':
            print "Rename your SSL certificate file as apporbitserver.crt and SSL key file as apporbitserver.key"
            ssldir = raw_input("Enter the location where your certificate and the key files exist [/opt/certs]:") or "/opt/certs"
            logging.info ("SSL Certs Directory is  : %s", ssldir )

        #BELOW LINES ARE INTENTIONALLY COMMENTED TO AVOID ASKING USER.
        #print "Enter the type of deployment:"
        #print "1. Singe-Tenant"
        #print "2. Multi-Tenant"
        #deploy_mode = raw_input("Choose the type of deployment [1]: ") or '1'
        deploy_mode = '1'
        logging.info ("Mode of deployment : %s", deploy_mode)
        if deploy_mode == '1':
            on_prem_emailid = raw_input("Enter the admin user email id for management console login [admin@apporbit.com]:") or "admin@apporbit.com"
            logging.info ("Email ID : %s", on_prem_emailid )

        ip = urllib2.urlopen("http://whatismyip.akamai.com").read()
        hostIp = raw_input("Enter the FQDN or host IP [%s]:" %ip) or ip
        logging.info("Host Ip : %s", hostIp)

        logging.info("Creating config file...")
        config_obj.createConfigFile(reg_user_name, reg_password,\
                                     build_id, is_install_cfgmgr,\
                                     self_signed_crt, clean_setup,\
                                        deploy_mode, hostIp, on_prem_emailid, ssldir)
        # self.createConfigFile()
        logging.info("completed collecting user config info")
        return


