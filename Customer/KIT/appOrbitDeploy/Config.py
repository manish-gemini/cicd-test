#!/usr/bin/env python

import logging
import ConfigParser
import exceptions

class Config():

    def __init__(self):
        self.docker_uname = ''
        self.docker_passwd = ''
        self.deploy_chef = '1'
        self.build_deploy_mode = '3'
        self.internal_repo = 'http://repos.gsintlab.com/repos'
        self.clean_setup = '2'
        self.deploy_mode = '1'
        self.onprem_emailID = 'admin@apporbit.com'
        self.theme_name = 'apporbit-v2'
        self.api_version = 'v2'
        self.hostip = ''
        self.self_signed_crt = '1'
        self.volume_mount = ''
        self.registry_url = 'registry.apporbit.com'
        return


    #  This sets up the docker login Credentials
    #  UserName - Docker Registry Username
    #  passwd   - Docker Registry Password
    def set_docker_login(self,uname,passwd):
        self.docker_uname = uname
        self.docker_passwd = passwd
        return


    # This sets up the type of Chef Deployment
    # 0 - Dont Deploy Chef in the same machine
    # 1 - Deploy Chef in the same machine Using Customer Repo
    # 2 - Deploy Chef in the same machine using Local Chef Image.
    # 3 - Deploy Chef in the same Macine using  Master Repo.
    def set_deploy_chef(self, val='1'):
        self.deploy_chef = val
        return


    # This sets up Mode of Deploy
    # 0 - QA Deploy for Master Build
    # 1 - Dev Deploy for local volume mount build
    # 2 - QA/DEV local deploy.
    # 3 - Customer Deploy
    # 4 - Jenkins Deploy
    def set_build_deploy_mode(self, val='3'):
        self.build_deploy_mode = val
        return

    # Set Internal Repo for Packages
    # Default Internal Repo Pacakage is
    # http://repos.gsintlab.com/repos
    def set_internal_repo(self, val = 'http://repos.gsintlab.com/repos'):
        self.internal_repo = val
        return

    # BUILD ID
    def set_build_id(self, val='latest'):
        self.buildid = val
        return

    # Clean Setup or Retain old entries
    #  1 - clean the setup
    #  2 - retain old entries
    def set_clean_setup(self, val = '2'):
        self.clean_setup = val
        return

    # MODE OF OPERATION
    # 1 - ON Prem Mode
    # 2 - SASS Mode
    def set_deploy_mode_operation(self, val = '1'):
        self.deploy_mode = val
        return

    # OnPREM EMAIL ID
    def set_onprem_emailid(self, val='admin@apporbit.com'):
        self.onprem_emailID = val
        return

    # ThemeName of Deployment
    def set_theme_name(self, val = 'apporbit-v2'):
        self.theme_name = val
        return

    # API Version
    def set_api_version(self, val = 'v2'):
        self.api_version = val
        return

    # set host ip
    def set_hostip(self, val):
        self.hostip = val
        return

    #//TODO: calculate MAX_PHUSION PROCESS:

    # Create Self Signed Certificate - 1
    #  Use existing signed certificate - 2
    def set_create_selfsigned_crt(self, val = '1'):
        self.self_signed_crt = val
        return


    # For Dev Mode Deployment - Need to add volume Mount of Code.
    def set_volume_mount_location(self, val = '/opt'):
        self.volume_mount = val
        return



    def loadConfig(self, fileName="local.conf"):
        logging.info("Create Config File from file name %s", fileName)
        config = ConfigParser.ConfigParser()
        fp = open(fileName, 'r')
        config.readfp(fp)

        try:
            self.docker_uname = config.get('Docker Login', 'username')
            self.docker_passwd = config.get('Docker Login', 'password')

            self.build_deploy_mode = config.get('User Config', 'build_deploy_mode')
            self.buildid = config.get('User Config', 'build_id')
            self.clean_setup = config.get('User Config', 'clean_setup')
            self.self_signed_crt = config.get('User Config', 'self_signed_crt')
            self.deploy_chef = config.get('User Config', 'deploy_chef')
            self.deploy_mode = config.get('User Config', 'deploy_mode')
            self.onprem_emailID = config.get('User Config', 'on_prem_emailid')
            self.hostip = config.get('User Config', 'hostIP')
            self.theme_name = config.get('User Config', 'themeName')
            self.api_version = config.get('User Config','api_version' )
            self.registry_url = config.get('User Config', 'registry_url')
            self.internal_repo = config.get('User Config', 'internal_repo')
            self.volume_mount = config.get('User Config', 'volume_mount')


        except ConfigParser.NoSectionError, ConfigParser.NoOptionError:
            logging.warning("warning No section or No option error occured...")

        fp.close()
        return


    def createConfigFile(self, reg_user_name, reg_password,\
                                     build_id, is_install_cfgmgr,\
                                     self_signed_crt, clean_setup, deploy_mode,\
                                     hostIp, on_prem_emailid = '',\
                                     themeName = 'apporbit-v2',\
                                     api_version = 'v2',\
                                     build_deploy_mode = '3', reg_url='registry.apporbit.com',\
                                     internal_repo = 'http://repos.gsintlab.com/repos',\
                                     volume_mount = '' ):

        logging.info("Create Config file")
        config = ConfigParser.ConfigParser()
        cfg_file = open('appobit_deploy.conf','w')
        config.add_section('Docker Login')
        config.set('Docker Login' , 'username', reg_user_name)
        config.set('Docker Login', 'password', reg_password)
        config.add_section('User Config')
        config.set('User Config', 'build_deploy_mode', build_deploy_mode)
        config.set('User Config', 'build_id', build_id )
        config.set('User Config', 'clean_setup', clean_setup)
        config.set('User Config', 'self_signed_crt',self_signed_crt)
        config.set('User Config', 'deploy_chef', is_install_cfgmgr)
        config.set('User Config', 'deploy_mode', deploy_mode)
        config.set('User Config', 'on_prem_emailid', on_prem_emailid)
        config.set('User Config', 'hostIP', hostIp)
        config.set('User Config', 'themeName', themeName)
        config.set('User Config', 'api_version', api_version)
        config.set('User Config', 'registry_url', reg_url)
        config.set('User Config', 'internal_repo', internal_repo)
        config.set('User Config', 'volume_mount', volume_mount)

        config.write(cfg_file)

        cfg_file.close()

        logging.info("Create config file success!")
        return







