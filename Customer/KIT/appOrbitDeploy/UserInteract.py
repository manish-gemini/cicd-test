import os
import urllib2
import getpass
import ConfigParser
import logging

class UserInteract:

    def __init__(self):
        self.reg_user_name = ""
        self.reg_password = ""
        self.build_id = ""
        self.clean_setup = ""
        self.is_install_cfgmgr = ""
        self.deploy_mode = ""
        self.on_prem_emailid = ""
        self.themeName = ""
        self.hostIp = ""
        return


    def getUserConfigInfo(self):
        logging.info("Starting to get user config info")
        print "DEPLOYMENT CONFIGURATIONS:"
        print "************************** \n "
        print "  Login to appOrbit Docker Registry using the credentials obtained from appOrbit Business contact. "
        self.reg_user_name = raw_input("\n Enter the User Name : ")
        self.reg_password = getpass.getpass()
        self.build_id = raw_input("\n Enter the Build ID [Default:latest] : ") or "latest"
        self.is_install_cfgmgr = raw_input("\n Do you want to deploy config Manager in the same machine? [Y/n] : ") or 'y'

        print "\n Retain old entries or clean it "
        print "  1. Clean the setup "
        print "  2. Retain the old entries "
        self.clean_setup = raw_input("  Choose the setup type from the above [Default : 1] :") or '1'

        logging.info("Clean Setup : %s", self.clean_setup)

        print "\n Enter the Mode of Deployment "
        print "  1. On Prem Mode "
        print "  2. SASS Mode "
        self.deploy_mode = raw_input("  Choose the type of deployment [Default: 1 ]: ") or '1'

        logging.info ("  Mode of deployment : %s", self.deploy_mode)
        if self.deploy_mode == 1:
            self.on_prem_emailid = raw_input("\n Enter the user email id for On-Prem-Mode Deployment \
            [Default:admin@apporbit.com] : ") or "admin@apporbit.com"
            logging.info ("Email ID : %s", self.on_prem_emailid )

        self.themeName = raw_input("\n Enter the theme Name [Default: apporbit-v2] :") or "apporbit-v2"

        logging.info ("Theme name: %s ", self.themeName )
        ip = urllib2.urlopen("http://whatismyip.akamai.com").read()
        self.hostIp = raw_input("\n Enter hostname or host ip [Default:%s] :" %ip) or ip
        logging.info("Host Ip : %s", self.hostIp)

        logging.info("Creating config file...")
        self.createConfigFile()
        logging.info("completed collecting user config info")
        return


    def createConfigFile(self):
        logging.info("Create Config file")
        config = ConfigParser.ConfigParser()
        cfg_file = open('appobit_deploy.conf','w')
        config.add_section('Docker Login')
        config.set('Docker Login' , 'username', self.reg_user_name)
        config.set('Docker Login', 'password', self.reg_password)
        config.add_section('User Config')
        config.set('User Config', 'build_id', self.build_id )
        config.set('User Config', 'clean_setup', self.clean_setup)
        config.set('User Config', 'cfg_mgr', self.is_install_cfgmgr)
        config.set('User Config', 'deploy_mode', self.deploy_mode)
        config.set('User Config', 'on_prem_emailid', self.on_prem_emailid)
        config.set('User Config', 'themeName', self.themeName)
        config.set('User Config', 'hostIP', self.hostIp)

        config.write(cfg_file)

        cfg_file.close()

        logging.info("Create config file success!")
        self.showConfigInfo('appobit_deploy.conf')
        return


    def showConfigInfo(self,fname='local.conf' ):
        logging.info("Started to show summary of configuration")
        print "\n\n"
        print "CONFIGURATION SUMMARY:"
        print "**********************"
        config = ConfigParser.ConfigParser()
        fp = open(fname, 'r')
        config.readfp(fp)

        if fname == 'local.conf':
            print 'Local Deploy'
            print '------------'
        try:
            print "BUILD ID : " + config.get('User Config', 'build_id')
            print "Clean Setup : " + config.get('User Config', 'clean_setup')
            print "Config manager : " + config.get('User Config', 'cfg_mgr')
            print "Deploy Mode : " + config.get('User Config', 'deploy_mode')
            print "On Prem Email ID : " + config.get('User Config', 'on_prem_emailid')
            print "Theme Name : " + config.get('User Config', 'themeName')
            print "Host IP : " + config.get('User Config', 'hostIP')
        except NoSectionError, NoOptionError:
            logging.warning("warning No section or No option error occured...")

        print "\n"
        print "**************************"
        fp.close()
        return
