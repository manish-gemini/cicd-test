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
        self.self_signed_crt_dir = ''
        self.chef_self_signed_crt = '0'
        self.chef_self_signed_crt_dir = ''
        self.volume_mount = ''
        self.registry_url = 'registry.apporbit.com'
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
            self.self_signed_crt_dir = config.get('User Config', 'self_signed_crt_dir')
            self.chef_self_signed_crt = config.get('User Config', 'chef_self_signed_crt')
            self.chef_self_signed_crt_dir = config.get('User Config', 'chef_self_signed_crt_dir')
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
                                     self_signed_crt, chef_self_signed_crt, clean_setup, deploy_mode,\
                                     hostIp, on_prem_emailid = '',\
                                     ssldir = '',\
                                     chef_ssldir = '',\
                                     themeName = 'apporbit-v2',\
                                     api_version = 'v2',\
                                     build_deploy_mode = '3', reg_url='registry.apporbit.com',\
                                     internal_repo = 'http://repos.gsintlab.com/repos',\
                                     volume_mount = '' ):

        logging.info("Create Config file")
        config = ConfigParser.ConfigParser()
        cfg_file = open('apporbit_deploy.conf','w')
        config.add_section('Docker Login')
        config.set('Docker Login' , 'username', reg_user_name)
        config.set('Docker Login', 'password', reg_password)
        config.add_section('User Config')
        config.set('User Config', 'build_deploy_mode', build_deploy_mode)
        config.set('User Config', 'build_id', build_id )
        config.set('User Config', 'clean_setup', clean_setup)
        config.set('User Config', 'self_signed_crt', self_signed_crt)
        config.set('User Config', 'self_signed_crt_dir', ssldir)
        config.set('User Config', 'chef_ssl_crt', chef_self_signed_crt)
        config.set('User Config', 'chef_ssl_crt_dir', chef_ssldir)
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








