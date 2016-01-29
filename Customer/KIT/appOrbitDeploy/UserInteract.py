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

        logging.info("Starting to get user config info")
        print "DEPLOYMENT CONFIGURATIONS:"
        print "************************** \n "
        print "  Login to appOrbit Docker Registry using the credentials obtained from appOrbit Business contact. "
        reg_user_name = raw_input("\n Enter the User Name : ")
        reg_password = getpass.getpass()
        build_id = raw_input("\n Enter the Build ID [Default:latest] : ") or "latest"
        # is_install_cfgmgr = raw_input("\n Do you want to deploy config Manager in the same machine? [Y/n] : ") or 'y'

        print '\n Enter Config Manager Deploy Mode :'
        print '  1. Deploy on the same host '
        print '  2. Do not deploy, will configure it later'
        is_install_cfgmgr = raw_input("  Choose the setup type from the above [Default : 1] :") or '1'
        logging.info ("Chef Mode of deployment : %s", is_install_cfgmgr)

        print "\n Retain old entries or clean it "
        print "  1. Clean the setup "
        print "  2. Retain the old entries "
        clean_setup = raw_input("  Choose the setup type from the above [Default : 1] :") or '1'

        logging.info("Clean Setup : %s", clean_setup)

        print '\n Enter the type of SSL Certificate Type:'
        print '  1. Create a new ssl Certificate'
        print '  2. Use Existing Certificate'
        self_signed_crt = raw_input ("  Choose the type of ssl Certificate [Default 1]:") or '1'
        logging.info ("  Mode of deployment : %s", self_signed_crt)


        print "\n Enter the Mode of Deployment "
        print "  1. On Prem Mode "
        print "  2. SASS Mode "
        deploy_mode = raw_input("  Choose the type of deployment [Default: 1 ]: ") or '1'

        logging.info ("  Mode of deployment : %s", deploy_mode)
        if deploy_mode == '1':
            on_prem_emailid = raw_input("\n Enter the user email id for On-Prem-Mode Deployment \
            [Default:admin@apporbit.com] : ") or "admin@apporbit.com"
            logging.info ("Email ID : %s", on_prem_emailid )

        ip = urllib2.urlopen("http://whatismyip.akamai.com").read()
        hostIp = raw_input("\n Enter hostname or host ip [Default:%s] :" %ip) or ip
        logging.info("Host Ip : %s", hostIp)

        logging.info("Creating config file...")
        config_obj.createConfigFile(reg_user_name, reg_password,\
                                     build_id, is_install_cfgmgr,\
                                     self_signed_crt, clean_setup,\
                                        deploy_mode, hostIp, on_prem_emailid)
        # self.createConfigFile()
        logging.info("completed collecting user config info")
        return


    # def showConfigInfo(self,fname='local.conf' ):
    #     logging.info("Started to show summary of configuration")
    #     print "\n\n"
    #     print "CONFIGURATION SUMMARY:"
    #     print "**********************"
    #     config = ConfigParser.ConfigParser()
    #     fp = open(fname, 'r')
    #     config.readfp(fp)
    #
    #     if fname == 'local.conf':
    #         print 'Local Deploy'
    #         print '------------'
    #     try:
    #         print "BUILD ID : " + config.get('User Config', 'build_id')
    #         print "Clean Setup : " + config.get('User Config', 'clean_setup')
    #         print "Config manager : " + config.get('User Config', 'cfg_mgr')
    #         print "Deploy Mode : " + config.get('User Config', 'deploy_mode')
    #         print "On Prem Email ID : " + config.get('User Config', 'on_prem_emailid')
    #         print "Theme Name : " + config.get('User Config', 'themeName')
    #         print "Host IP : " + config.get('User Config', 'hostIP')
    #     except ConfigParser.NoSectionError, ConfigParser.NoOptionError:
    #         logging.warning("warning No section or No option error occured...")
    #
    #     print "\n"
    #     print "**************************"
    #     fp.close()
    #     return
