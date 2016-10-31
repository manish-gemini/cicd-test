#!/usr/bin/env python

import logging
import multiprocessing
import os
import sys
import re
import shutil
import glob
import datetime
import ConfigParser
import errno
from time import sleep
import getpass
import ConfigParser

import utility
import userinteract
import subprocess
from urlparse import urlparse

class Action:

    def __init__(self):
        self.utilityobj = utility.Utility()
        return

    def routableDomain(self, consul_host):
        process = subprocess.Popen(["nslookup", consul_host], stdout=subprocess.PIPE)
        output = process.communicate()[0].split('\n')
        #print output
        routable = 'false'
        for data in output:
                if 'Non-authoritative' in data:
                        routable = 'true'
        #print routable
        return routable

    def deployConsul(self, reg_url, consul_host, consul_domain, build_deploy_mode):
        routable = 'false'
        if not reg_url:
            consul_image_name  = "apporbit/consul"
        else:
            consul_image_name = reg_url + "/apporbit/consul"

        if build_deploy_mode == '1':
            consul_image_name = 'apporbit/consul'

        if not consul_domain:
            #print "\nconsul_domain is missing"
            cmd_deploy_consul = ("docker run -d -p 8400:8400 -p 8500:8500 -p 53:53/udp "
                             "--restart=always -v /var/lib/apporbit/consul:/data:Z --name apporbit-consul -h consul " +
                             consul_image_name + " -server -bootstrap")
            cmd_desc = "Deploying Consul container"
        elif not consul_host:
            #print "\nconsul_host is missing"
                cmd_deploy_consul = ("docker run -d -p 8400:8400 -p 8500:8500 -p 53:53/udp "
                             "--restart=always -v /var/lib/apporbit/consul:/data:Z --name apporbit-consul -h consul " +
                             consul_image_name + " -server -bootstrap")
                cmd_desc = "Deploying Consul container"
        else:
            #print "\nBoth values are present"
            #check if domain is routable
            routable = self.routableDomain(consul_host)
            if routable == 'true':
                cmd_deploy_consul = ("docker run -d -p 8400:8400 -p 8500:8500 -p 53:53/udp "
                              "--restart=always -v /var/lib/apporbit/consul:/data:Z --name apporbit-consul -h consul " +
                             consul_image_name + " -server -domain="+consul_domain +" -bootstrap")
                cmd_desc = "Deploying Consul container with domain name"    
            else:
                cmd_deploy_consul = ("docker run -d -p 8400:8400 -p 8500:8500 -p 53:53/udp "
                             "--restart=always -v /var/lib/apporbit/consul:/data:Z --name apporbit-consul -h consul " +
                             consul_image_name + " -server -bootstrap")
                cmd_desc = "Deploying Consul container"

        self.utilityobj.cmdExecute(cmd_deploy_consul, cmd_desc, True)
        sleep(10)
        return True


    def deployChef(self, config_obj, host_ip, remove_data, reg_url = ""):
        if reg_url:
            chef_image_name = reg_url + '/apporbit/apporbit-chef:2.0'
        else:
            print "Failed - registry url not found, please verify registry url in setup.conf"
            sys.exit(1)

        if remove_data:
            chef_upgrade = " -e UPGRADE=1 " #1 is Clean Setup
        else:
            chef_upgrade = " -e UPGRADE=2 " #2 is Chef Upgrade Mode

        cmd_chefDeploy = "docker run -m 2g -it --restart=always "
        cmd_chefDeploy += chef_upgrade
        cmd_chefDeploy += "-p 9443:9443 \
        -v  " + config_obj.APPORBIT_DATA + "/chef-server:/var/opt/chef-server:Z  -v " + config_obj.APPORBIT_KEY + "/:/var/opt/chef-server/nginx/ca/:Z\
         -v /etc/chef-server/ --name apporbit-chef -h "+ host_ip + " -d " + chef_image_name

        cmd_desc = "Deploying chef container "

        self.utilityobj.cmdExecute(cmd_chefDeploy, cmd_desc, True)
        sleep(120)

        return True


    def calcMaxPhusionProcess(self):
        logging.info( 'Max Pool Size' )
        cpu_count = multiprocessing.cpu_count()
        meminfo = open('/proc/meminfo').read()
        matched = re.search(r'^MemTotal:\s+(\d+)', meminfo)
        ram_size = int(matched.groups()[0])

        B = 1024
        KB = B * B
        ram_size_gb = ( ram_size + (KB - 1)/KB )
        ram_per_process = ( ram_size_gb + (cpu_count - 1)/cpu_count )

        adjvar1=75
        adjvar2=100

        if ram_per_process == 0 :
            ram_per_process = 1

        max_app_process = (ram_size_gb * adjvar1 )/( ram_per_process * adjvar2 )

        if max_app_process == 0:
            max_app_process = 1

        return max_app_process


    def createSelfSignedCert(self, config_obj, isChef=False, hostIP = ""):
        #Generate SSL Certificate
        try:
            os.stat(config_obj.APPORBIT_KEY)
        except:
            os.mkdir(config_obj.APPORBIT_KEY)   

        if isChef:
            if (os.path.isfile(config_obj.APPORBIT_KEY + hostIP + '.key') and
                os.path.isfile(config_obj.APPORBIT_KEY + hostIP + '.key')):
                logging.info("Chef Key already exists. Not creating.")
                return True
            else:
                logging.info("Chef Key to be created.")
                cmd_sslcert = 'openssl req -new -newkey rsa:4096 -days 365 -nodes -x509 \
                -subj "/C=US/ST=NY/L=appOrbit/O=Dis/CN='+ hostIP + '"\
                -keyout  ' + config_obj.APPORBIT_KEY + '/'+ hostIP +'.key \
                -out ' + config_obj.APPORBIT_KEY + '/'+ hostIP + '.crt'
                cmd_desc = "Creating Chef SSL Certificate."
        else:
            if (os.path.isfile(config_obj.APPORBIT_KEY + 'apporbitserver.key') and
                os.path.isfile(config_obj.APPORBIT_KEY + 'apporbitserver.crt')):
                logging.info("appOrbit Server Key already exists. Not creating.")
                return True
            else:
                logging.info("appOrbit Key to be created.")
                cmd_sslcert = 'openssl req -new -newkey rsa:4096 -days 365 -nodes -x509\
                -subj "/C=US/ST=NY/L=appOrbit/O=Dis/CN=www.apporbit.com" \
                -keyout ' + config_obj.APPORBIT_KEY + '/apporbitserver.key \
                -out ' +  config_obj.APPORBIT_KEY + '/apporbitserver.crt'
                cmd_desc = "Creating SSL Certificate."

        self.utilityobj.cmdExecute(cmd_sslcert, cmd_desc, True)
        return True

    def copySSLCertificate(self, config_obj, dir, hostIP = "", is_chef = False):
        try:
            os.stat(config_obj.APPORBIT_KEY)
        except:
            os.mkdir(config_obj.APPORBIT_KEY)   
        if is_chef == True:
            sslkeyfile = dir + "/" + hostIP + ".key"
            sslkeycrt = dir + "/" + hostIP + ".crt"
            cmd_cpysslkey = "cp -f " + sslkeyfile + " " + config_obj.APPORBIT_KEY  + "/."
            cmd_cpysslcrt = "cp -f " + sslkeycrt + " " + config_obj.APPORBIT_KEY + "/."
            cmd_desckey = "Copying Chef SSL key"
            cmd_desccert = "Copying Chef SSL certificate"

        else:
            sslkeyfile = dir + "/apporbitserver.key"
            sslkeycrt = dir + "/apporbitserver.crt"
            cmd_cpysslkey = "cp -f " + dir +"/apporbitserver.key " + config_obj.APPORBIT_KEY + "/apporbitserver.key"
            cmd_cpysslcrt = "cp -f " + dir +"/apporbitserver.crt " + config_obj.APPORBIT_KEY + "/apporbitserver.crt"
            cmd_desckey = "Copying SSL key"
            cmd_desccert = "Copying SSL certificate"
        if not os.path.isfile(sslkeyfile):
            logging.error('%s SSL key file does not exist.', sslkeyfile)
            print "SSL key file does not exist. Check logs for details."
            sys.exit(1)
        if not os.path.isfile(sslkeycrt):
            logging.error('%s SSL certificate file does not exist.', sslkeycrt)
            print "SSL certificate file does not exist. Check logs for details."
            sys.exit(1)
        self.utilityobj.cmdExecute(cmd_cpysslkey, cmd_desckey, True)
        self.utilityobj.cmdExecute(cmd_cpysslcrt, cmd_desccert, True)
        return True

    def deployCompose(self, config_obj, show = False):
        cmd_deploy_db = config_obj.APPORBIT_COMPOSE + " -f " + config_obj.composeFile + " up -d"
        cmd_desc = "Start deploying AppOrbit containers.."
        self.utilityobj.cmdExecute(cmd_deploy_db, cmd_desc, True, show)
        logging.info("Deployed appOrbit containers.")
        return  True

    def restartAppOrbitCompose(self, config_obj, restartlist, show = False):
        cmd_restart = config_obj.APPORBIT_COMPOSE + " -f " + config_obj.composeFile + " restart " + restartlist
        cmd_desc = "Restarting AppOrbit containers.."
        self.utilityobj.cmdExecute(cmd_restart, cmd_desc, True, show)
        logging.info("Restarting appOrbit containers.")
        return  True

    def removeCompose(self, config_obj, show = False, tries = 2):
        cmd_deploy_db = config_obj.APPORBIT_COMPOSE + " -f " + config_obj.composeFile + " down"
        cmd_desc = "Undeploying AppOrbit containers using docker compose"
        return_code = False
        while  (tries > 0 and not return_code) :
            logging.info("Removing appOrbit containers.")
            return_code, out, err = self.utilityobj.cmdExecute(cmd_deploy_db, cmd_desc, False, show)
            tries -= 1
        if (not return_code):
            logging.error("Could not remove appOrbit containers. Exiting")
            print "Unable to remove apporbit Containers. Check Log for details and fix it"
            sys.exit(1)
        return  True

    def deployAppOrbitCompose(self, config_obj, show= False):
        logging.info("Deploying appOrbit containers using docker compose ..")
        self.deployCompose(config_obj, show)
        return True

    def predeployAppOrbit(self, config_obj):
        consul_ip = config_obj.consul_host
        consul_port = config_obj.consul_port
        self.utilityobj.progressBar(5)

        self.removeRunningContainers(config_obj)
        self.utilityobj.progressBar(10)
        self.utilityobj.createLogRoatateFile()

        self.utilityobj.progressBar(12)
        # CLEAN or RETAIN OLD ENTRIES
        if config_obj.remove_data == True :
             self.clearOldEntries(config_obj)
        self.utilityobj.progressBar(14)

        # SETUP or CREATE DIRECTORIES for VOL MOUNT
        self.setupDirectoriesForVolumeMount(config_obj)
        # Upgrade V1 installer volumes
        self.upgradeV1Volumes(config_obj)

        self.utilityobj.progressBar(16)
        if config_obj.chef_self_signed_crt == '1':
            self.createSelfSignedCert(config_obj, True, config_obj.apporbit_host)
        elif config_obj.chef_self_signed_crt == '2':
            self.copySSLCertificate(config_obj, config_obj.chef_self_signed_crt_dir, config_obj.apporbit_host, True)
        else:
            logging.info("Skipping chef certificate creation on upgrade.")

        if config_obj.self_signed_crt == '1' or config_obj.create_keys:
            self.createSelfSignedCert(config_obj)
        else:
            logging.info("Copying SSL Certificate from the dir %s", config_obj.import_keys_from_dir)
            self.copySSLCertificate(config_obj, config_obj.import_keys_from_dir)

        self.utilityobj.progressBar(18)

        return True


    def removeData(self,config_obj):
        if config_obj.APPORBIT_DATA and config_obj.APPORBIT_DATA <> '/':
            cmd_removedata = "rm -rf " + config_obj.APPORBIT_DATA
        else:
            cmd_removedata = "rm -rf /var/lib/apporbit"
        cmd_desc = "Remove old data"
        code, out, err = self.utilityobj.cmdExecute(cmd_removedata, cmd_desc, True)
        config_obj.remove_data = True
        config_obj.initial_install = True
        return code


    def removeChefContainer(self):
        cmd_dockerps = "docker ps -a "
        cmd_desc = "Checking Docker ps"
        code, out, err = self.utilityobj.cmdExecute(cmd_dockerps, cmd_desc, True)
        if "apporbit-chef" in out:
                logging.info( "apporbit-chef exist remove it")
                self.removeContainer("apporbit-chef")
        return

    def removeConsulContainer(self):
        cmd_dockerps = "docker ps -a "
        cmd_desc = "Checking Docker ps"
        code, out, err = self.utilityobj.cmdExecute(cmd_dockerps, cmd_desc, True)
        if "apporbit-consul" in out:
                logging.info( "apporbit-consul exist remove it")
                self.removeContainer("apporbit-consul")
        return

    def removeContainer(self, container_name):
        cmd_stop = "docker stop " + container_name
        cmd_desc = "Stop docker container " + container_name
        self.utilityobj.cmdExecute(cmd_stop, cmd_desc, True)
        cmd_remove = "docker rm " + container_name
        cmd_desc = "Removing container: " + container_name
        self.utilityobj.cmdExecute(cmd_remove, cmd_desc, True)
        return True

    def removeRunningContainers(self, config_obj, show = False):
        # First down compose
        self.removeCompose(config_obj,show)

        # Now kill and remove any stray apporbit-containers
        logging.info("Killing and removing old apporbit containers." )
        cmd_killcmd = 'docker kill $(docker ps -a -q --filter "name=apporbit-*")'
        return_code, out, err = self.utilityobj.cmdExecute(cmd_killcmd, "Killing old appOrbit containers", False)
        if (not return_code):
            logging.warning("Could not kill appOrbit containers. %d %s %s" % (return_code, out, err))
        cmd_rmcont = 'docker rm -f $(docker ps -a -q --filter "name=apporbit-*")'
        return_code, out, err = self.utilityobj.cmdExecute(cmd_rmcont, "Removing old appOrbit containers", False)
        if (not return_code):
            logging.warning("Could not remove appOrbit containers. %d %s %s" % (return_code, out, err))

        return True

    def clearChefData(self,config_obj):
        try:
            shutil.rmtree( config_obj.APPORBIT_DATA + '/chef-server', ignore_errors = True)
        except OSError as e:
            logging.warning("Failed to clean old Entries : " + e.strerror)
        return


    def clearOldEntries(self, config_obj):
        logging.info("clean old entries to create fresh setup STARTED!!!")
        try:
            shutil.rmtree(config_obj.APPORBIT_DATA, ignore_errors = True)
            logtimestamp = config_obj.APPORBIT_LOG + '/oldlogs_' + str(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
            os.makedirs(logtimestamp)
            if os.path.exists(config_obj.APPORBIT_LOG + "/controller"):
                shutil.move(config_obj.APPORBIT_LOG + '/controller/', logtimestamp )
            if os.path.exists(config_obj.APPORBIT_LOG + "/services"):
                shutil.move(config_obj.APPORBIT_LOG + '/services/', logtimestamp )
            for filename in glob.glob(os.path.join(config_obj.APPORBIT_LOG, 'apporbitInstall-*')):
                shutil.move(filename, logtimestamp)
        except OSError as e:
            logging.warning("Failed to clean old Entries : " + e.strerror)
        logging.info("Clean old entries COMPLETED !!!")
        return


    def createDirSetSeLinuxPermission(self, dir_path):
        try:
            os.makedirs(dir_path)
        except OSError as ose:
            if ose.errno == errno.EEXIST and os.path.isdir(dir_path):
                logging.info("Dir exist - %s", dir_path)
            else:
                logging.error("Unable to create dir %s", dir_path)
                print "Unable to setup volume required for the setup. Check log for details."
                sys.exit(1)
        return

    def upgradeV1Volumes(self,config_obj):
        logging.info("Checking if old installer volumes exists and need to be migrated")
        try:
            logging.info("Found /var/dbstore. Doing upgrade routine")
            os.stat("/var/dbstore")
        except:
            logging.info("Upgrade not required as /var/dbstore does not exist")
            return True

        mysqldir = config_obj.APPORBIT_DATA + '/mysql'
        try:
            os.stat(config_obj.APPORBIT_DATA)
        except:
            os.makedirs(config_obj.APPORBIT_DATA)
        try:
            os.stat(mysqldir)
            logging.info ("New MySQL dir exists. Skipping mysql directory rename")
        except:
            if os.listdir("/var/dbstore"):
                cmd_upgrade= "mv /var/dbstore " + mysqldir
                return_code, out, err = self.utilityobj.cmdExecute(cmd_upgrade, "Upgrading mysql database location", True)
                logging.info ("Moving mysql directory to new location")
        try:
            if os.listdir("/var/lib/apporbit/sslkeystore"):
                cmd_upgrade= "mv /var/lib/apporbit/sslkeystore " + config_obj.APPORBIT_KEY 
                return_code, out, err = self.utilityobj.cmdExecute(cmd_upgrade, "Moving keys directory", True)
                logging.info ("Moving key directory to new location")
        except:
            logging.warning("Skipping moving key directory")
               
        try:
            try:
                os.stat(config_obj.APPORBIT_KEY)
            except:
                os.makedirs(config_obj.APPORBIT_KEY)
            if os.listdir("/opt/apporbit/chef-serverkey"):
                cmd_upgrade= "cp -f /opt/apporbit/chef-serverkey/* " + config_obj.APPORBIT_KEY 
                return_code, out, err = self.utilityobj.cmdExecute(cmd_upgrade, "Copying chef keys ", True)
                cmd_upgrade= "rm -rf /opt/apporbit/chef-serverkey/"
                return_code, out, err = self.utilityobj.cmdExecute(cmd_upgrade, "Removing old chef keys directory", True)
                logging.info ("Copying  key directory to new location")
        except:
            logging.warning("Skipping moving key directory")
               
        try:
            if os.listdir("/opt/apporbit/chef-server"):
                cmd_upgrade= "mv /opt/apporbit/chef-server " + config_obj.APPORBIT_DATA + "/chef-server" 
                return_code, out, err = self.utilityobj.cmdExecute(cmd_upgrade, "Moving chef-server directory", True)
                logging.info ("Moving chef-server directory to new location")
        except:
            logging.warning("Skipping moving chef-server directory")

        logging.info("Upgrade volume locations completed")
        return True

    def setupDirectoriesForVolumeMount(self,config_obj):
        logging.info("Setting up Directories for Volume Mount location  STARTED!!!")
        dirList = [config_obj.APPORBIT_DATA, config_obj.APPORBIT_LOG] 
        for dirName in dirList:
            self.createDirSetSeLinuxPermission(dirName)
        return True


    def pullImages(self, config_obj):
        self.utilityobj.loginDockerRegistry(config_obj.registry_uname, config_obj.registry_passwd, config_obj.apporbit_registry)
        logging.info("Pulling new images from registry: " + config_obj.apporbit_registry)
        cmd_pull_images = config_obj.APPORBIT_COMPOSE + " -f " +  config_obj.composeFile + " pull"
        return_code, out, err = self.utilityobj.cmdExecute(cmd_pull_images, "Pulling new images",True)
        if (not return_code):
            logging.error("Could not pull appOrbit containers. Exiting")
            print "Unable to pull new images. Check Log."
            sys.exit(1)
        return True

    def showStatus(self,config_obj):
        cmd_status = config_obj.APPORBIT_COMPOSE + " -f " +  config_obj.composeFile + " ps"
        self.utilityobj.cmdExecute(cmd_status , "Showing status images", show=True)
        return True


class DeployChef:
    def __init__(self):
        self.user_interact_obj = userinteract.UserInteract()
        self.utility_obj = utility.Utility()
        self.action_obj = Action()
        self.chef_deploy_mode = '2'
        self.hostIP = ""
        self.chef_self_signed_crt = ""
        self.chef_ssldir = ""


    def deploy_chef(self):
        if os.path.isfile('cheflocal.conf'):
            config = ConfigParser.ConfigParser()
            fp = open('cheflocal.conf', 'r')
            config.readfp(fp)
            try:
                self.APPORBIT_HOME = '/opt/apporbit'
                self.APPORBIT_BIN = self.APPORBIT_HOME + '/bin'
                self.APPORBIT_CONF = self.APPORBIT_HOME + '/conf'
                self.APPORBIT_KEY = self.APPORBIT_HOME + '/key'
                self.APPORBIT_DATA = '/var/lib/apporbit'
                self.APPORBIT_LOG = '/var/log/apporbit'
                self.APPORBIT_COMPOSE = 'COMPOSE_HTTP_TIMEOUT=120 ' + self.APPORBIT_BIN + '/docker-compose -p apporbit' 
                self.uname = config.get('Docker Login', 'username')
                self.password = config.get('Docker Login', 'password')
                self.reg_url = config.get('Chef Config', 'reg_url')
                self.utility_obj.loginDockerRegistry(self.uname, self.password, self.reg_url )
                self.chef_deploy_mode = config.get('Chef Config', 'chef_deploy_mode')
                self.hostIP = config.get('Chef Config', 'hostIP')
                self.chef_self_signed_crt = config.get('Chef Config', 'chef_self_signed_crt')
                self.chef_ssldir = config.get('Chef Config', 'chef_ssldir')
            except ConfigParser.NoSectionError, ConfigParser.NoOptionError:
                pass

            fp.close()

        else:
            # Get User Configuration for Customer CHEF Deployment
            self.user_interact_obj.deployChefOnly(self, self.utility_obj)
            self.reg_url = "registry.apporbit.com"

        logging.info("DEPLOY CHEF ONLY")
        logging.info("Configuration details")
        logging.info("=====================")
        logging.info("regurl - %s", self.reg_url)
        logging.info("chef_deploy_mode - %s", self.chef_deploy_mode)
        logging.info("hostIP - %s", self.hostIP)
        logging.info("chef_self_signed_crt - %s", self.chef_self_signed_crt)
        logging.info("chef_ssldir - %s", self.chef_ssldir)

        self.action_obj.removeChefContainer()
        if self.chef_deploy_mode == '1':
            self.action_obj.clearChefData(self)

        if self.chef_self_signed_crt == '1' :
            self.action_obj.createSelfSignedCert(self, True, self.hostIP)
        else:
            self.action_obj.copySSLCertificate(self, self.chef_ssldir, self.hostIP, True)
        print "Chef Server is getting deployed. This process may take some time."
        self.action_obj.deployChef(self.hostIP, self.chef_deploy_mode, self.reg_url)
        print "- Deployed successfully."
        print "Now you can access the chef-server ui at https://" + self.hostIP + ":9443. It is recommended to change the default password."


class DeployConsul:
    def __init__(self):
        self.utility_obj = utility.Utility()
        self.action_obj = Action()

    def deploy_consul(self):
         if os.path.isfile('setup.conf'):
            config = ConfigParser.ConfigParser()
            fp = open('setup.conf', 'r')
            config.readfp(fp)
            try:
                self.uname = config.get('Docker Login', 'username')
                self.password = config.get('Docker Login', 'password')
                self.reg_url = config.get('User Config', 'apporbit_registry')
                self.utility_obj.loginDockerRegistry(self.uname, self.password, self.reg_url)
                self.consul_host = config.get('User Config', 'consul_host')
                self.consul_domain = config.get('User Config', 'consul_domain')
                self.build_deploy_mode = config.get('User Config', 'build_deploy_mode')
                logging.info("Consul deployment started..")
                print "Consul deployment started.."
                self.action_obj.removeConsulContainer()
                self.action_obj.deployConsul(self.reg_url, self.consul_host, self.consul_domain, self.build_deploy_mode)
                if self.utility_obj.isConsulDeployed():
                    print "Consul deployed successfully.."
                    logging.info("Consul deployed successfully..")
            except ConfigParser.NoSectionError, ConfigParser.NoOptionError:
                pass
            fp.close()
         else:
              print "Login to the appOrbit registry using the credentials sent to you by email, by appOrbit support team."
              reg_user_name = raw_input("Enter the user name: ")
              reg_password = getpass.getpass()
              self.utility_obj.loginDockerRegistry(reg_user_name, reg_password, "registry.apporbit.com")
              consul_domain = raw_input("Enter consul domain [default]:") or ''
              consul_host = raw_input("Enter consul host [default]:") or ''
              logging.info("Consul deployment started.. ")
              print "Consul deployment started.."
              self.action_obj.removeConsulContainer()
              self.action_obj.deployConsul("registry.apporbit.com", consul_host, consul_domain, self.build_deploy_mode)

              if self.utility_obj.isConsulDeployed():
                  print "Consul deployed successfully"
                  logging.info("Consul deployed successfully..")

