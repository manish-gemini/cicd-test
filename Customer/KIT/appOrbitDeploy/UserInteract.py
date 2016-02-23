#!/usr/bin/env python

import os
import urllib2
import getpass
import ConfigParser
import logging

import Config

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
        print "Enter the user configuration informations."
        print "------------------------------------------"
        print "Login to the appOrbit registry using the credentials sent to you by email by your appOrbit sales representative"
        reg_user_name = raw_input("Enter the user name: ")
        reg_password = getpass.getpass()
        build_id = raw_input("Enter the build id [latest] : ") or "latest"
        # is_install_cfgmgr = raw_input("\n Do you want to deploy config manager in the same machine? [Y/n] : ") or 'y'

        print 'Enter the chef server deploy mode :'
        print '1. Deploy on the same host '
        print '2. Do not deploy, will configure it later'
        is_install_cfgmgr = raw_input("choose the setup type from the above [1] :") or '1'
        logging.info ("Chef mode of deployment : %s", is_install_cfgmgr)

        print "New install or upgrade : "
        print "1. New install "
        print "2. Upgrade "
        clean_setup = raw_input("choose the setup type from the above [2] :") or '2'

        logging.info("Clean Setup : %s", clean_setup)

        print 'Enter the type of SSL certificate type:'
        print '1. Create a new ssl Certificate'
        print '2. Use Existing Certificate'
        self_signed_crt = raw_input ("Choose the type of ssl Certificate [1]:") or '1'
        logging.info ("self signed certificate : %s", self_signed_crt)
        if self_signed_crt == '2':
            print "Rename your SSL certificate files as apporbitserver.crt and key as apporbitserver.key"
            ssldir = raw_input("Enter the location where your certificate and key file exist [/opt/certs]:") or "/opt/certs"
            logging.info ("SSL Certs Directory is  : %s", ssldir )

        print "Enter the Mode of Deployment "
        print "1. Singe-Tenant"
        print "2. Multi-Tenant"
        deploy_mode = raw_input("Choose the type of deployment [1]: ") or '1'

        logging.info ("Mode of deployment : %s", deploy_mode)
        if deploy_mode == '1':
            on_prem_emailid = raw_input("Enter the user email id for single-tenant deployment [admin@apporbit.com] : ") or "admin@apporbit.com"
            logging.info ("Email ID : %s", on_prem_emailid )

        ip = urllib2.urlopen("http://whatismyip.akamai.com").read()
        hostIp = raw_input("Enter hostname or host ip [Default:%s] :" %ip) or ip
        logging.info("Host Ip : %s", hostIp)

        logging.info("Creating config file...")
        config_obj.createConfigFile(reg_user_name, reg_password,\
                                     build_id, is_install_cfgmgr,\
                                     self_signed_crt, clean_setup,\
                                        deploy_mode, hostIp, on_prem_emailid, ssldir)
        # self.createConfigFile()
        logging.info("completed collecting user config info")
        return


