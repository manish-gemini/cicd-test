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


    def deployRMQ(self, reg_url):
        if not reg_url:
            reg_url = "secure-registry.gsintlab.com"

        rmq_image_name = reg_url + "/apporbit/apporbit-rmq"

        cmd_deploy_rmq = "docker run -m 2g -d --hostname rmq --restart=always \
        --name apporbit-rmq -d " + rmq_image_name

        cmd_desc = "Deploying message service"

        self.utilityobj.cmdExecute(cmd_deploy_rmq, cmd_desc, True)

        sleep(10)

        return True


    def deployDocs(self, reg_url):
        if not reg_url:
            reg_url = "secure-registry.gsintlab.com"

        rmq_image_name = reg_url + "/apporbit/apporbit-docs"

        cmd_deploy_docs = "docker run --name apporbit-docs --restart=always -p 9080:80 -d " + rmq_image_name

        cmd_desc = "Deploying document service"

        self.utilityobj.cmdExecute(cmd_deploy_docs, cmd_desc, True)

        sleep(10)

        return True

    def deployDB(self):
        cmd_deploy_db = "docker run --name apporbit-db --restart=always -e MYSQL_ROOT_PASSWORD=admin \
        -e MYSQL_USER=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=apporbit_controller \
        -v /var/dbstore:/var/lib/mysql:Z -d mysql:5.6.24"
        cmd_desc = "Deploying database container"

        self.utilityobj.cmdExecute(cmd_deploy_db, cmd_desc, True)
        sleep(60)
        return  True

    def deployAlertmanager(self):
        alertmanager_image_name = "prom/alertmanager:master"
        cmd_deploy_alertmanager = "docker run -d -p 9093:9093 -v /var/lib/apporbit/monitoring/alertmanager.yml:/alertmanager.yml:Z -v /var/lib/apporbit/monitoring/alert-data:/alert-data:Z --restart=always --name=apporbit-alertmanager " + alertmanager_image_name + " -config.file=/alertmanager.yml -storage.path=/alert-data"
        cmd_desc = "Deploying Alertmanager container"

        self.utilityobj.cmdExecute(cmd_deploy_alertmanager, cmd_desc, True)
        sleep(10)
        return True

    def deployPrometheus(self, host_ip):
        prometheus_image_name = "prom/prometheus:v1.0.1"
        cmd_deploy_prometheus = "docker run -d -p 9090:9090 -v /var/lib/apporbit/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:Z -v /var/lib/apporbit/monitoring/alert.rules:/etc/prometheus/alert.rules:Z -v /var/lib/apporbit/monitoring/prom-data:/prom-data:Z -v /var/lib/apporbit/monitoring/targets:/var/lib/apporbit/monitoring/targets:Z --restart=always --name=apporbit-prometheus " + prometheus_image_name + " -config.file=/etc/prometheus/prometheus.yml -storage.local.path=/prom-data -alertmanager.url=http://" + host_ip + ":9093"
        cmd_desc = "Deploying Prometheus container"

        self.utilityobj.cmdExecute(cmd_deploy_prometheus, cmd_desc, True)
        sleep(10)
        return True

    def deployGrafana(self, config_obj):
        reg_url = config_obj.registry_url
        if not reg_url:
            reg_url = "secure-registry.gsintlab.com"
        grafana_image_name = reg_url + "/apporbit/apporbit-grafana:3.1.0"
        cmd_deploy_grafana = "docker run -d -p 3000:3000 -v /var/lib/apporbit/monitoring/grafana-data:/var/lib/grafana:Z -e GF_AUTH_ANONYMOUS_ENABLED=true -e GF_AUTH_ANONYMOUS_ORG_ROLE=Admin -e GF_USERS_DEFAULT_THEME=light --restart=always --name=apporbit-grafana " + grafana_image_name
        cmd_desc = "Deploying Grafana container"

        self.utilityobj.cmdExecute(cmd_deploy_grafana, cmd_desc, True)
        sleep(10)
        return True

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

    def deployLocator(self, consul_ip_port, reg_url, build_deploy_mode):
        if not reg_url:
            locator_image_name = "apporbit/locator"
        else:
            locator_image_name = reg_url + "/apporbit/locator"

        if build_deploy_mode == '1':
            locator_image_name = 'apporbit/locator'

        cmd_deploy_locator = ("docker run -d --name apporbit-locator "
                              "--restart=always -p 8080:8080 "
                              "-e CONSUL_IP_PORT=" + consul_ip_port +
                              " " + locator_image_name)
        cmd_desc = "Deploying Locator container"

        self.utilityobj.cmdExecute(cmd_deploy_locator, cmd_desc, True)
        sleep(10)
        return True

    def deployChef(self, host_ip, clean_setup, reg_url = ""):
        if reg_url:
            chef_image_name = reg_url + '/apporbit/apporbit-chef:2.0'
        else:
            print "Failed - registry url not found, please verify registry url in local.conf"
            sys.exit(1)

        if clean_setup == '1':
            chef_upgrade = " -e UPGRADE=1 " #1 is Clean Setup
        else:
            chef_upgrade = " -e UPGRADE=2 " #2 is Chef Upgrade Mode

        cmd_chefDeploy = "docker run -m 2g -it --restart=always "
        cmd_chefDeploy += chef_upgrade
        cmd_chefDeploy += "-p 9443:9443 \
        -v /opt/apporbit/chef-server:/var/opt/chef-server:Z  -v /opt/apporbit/chef-serverkey/:/var/opt/chef-server/nginx/ca/:Z\
         -v /etc/chef-server/ --name apporbit-chef -h "+ host_ip + " -d " + chef_image_name


        cmd_desc = "Deploying chef container "

        self.utilityobj.cmdExecute(cmd_chefDeploy, cmd_desc, True)
        sleep(120)

        return True

    def deploySvcd(self, config_obj):
        reg_url = config_obj.registry_url
        build_deploy_mode = config_obj.build_deploy_mode

        if not (config_obj.registry_url):
            svcd_image = "apporbit/svcd"
        else:
            svcd_image = reg_url + "/apporbit/svcd"

        if build_deploy_mode == '1':
            svcd_image = 'apporbit/svcd'

        cmd_deploy_svcd = ("docker run -d --name apporbit-svcd "
                           "--restart=always" + " -p 8888:8080 "
                           "--link apporbit-db:db "
                           "--link apporbit-locator:locator " +
                           svcd_image)
        cmd_desc = "Deploying svcd container"

        self.utilityobj.cmdExecute(cmd_deploy_svcd, cmd_desc, True)
        sleep(10)
        return True

    def deployCaptain(self, config_obj):
        reg_url = config_obj.registry_url
	build_deploy_mode = config_obj.build_deploy_mode

        if not (config_obj.registry_url):
            captain_image = "apporbit/captain"
        else:
            captain_image = reg_url + "/apporbit/captain"
	if build_deploy_mode == '1':
            captain_image = 'apporbit/captain'

        cmd_deploy_captain = ("docker run -d --name apporbit-captain "
                           "--restart=always" + " -p 8090:8080 "
                           "--link apporbit-controller:controller "
                           "-e CONTROLLER_ALIAS_NAME=controller " +
                           captain_image)
        cmd_desc = "Deploying captain container"

        self.utilityobj.cmdExecute(cmd_deploy_captain, cmd_desc, True)
        sleep(10)
        return True
    
    def deployServices(self, config_obj):
        internal_repo = config_obj.internal_repo
        host_ip = config_obj.hostip
        repo_str = config_obj.registry_url
        mode = config_obj.build_deploy_mode
        vol_mount = config_obj.volume_mount
        deploy_chef = config_obj.deploy_chef
        upgrade = config_obj.clean_setup

        cmd_str = "touch /var/lib/apporbit/apporbit.ini"
        self.utilityobj.cmdExecute(cmd_str, 'create apporbit stack config file.', True)

        # Varaiable Declaration
        image_name = ""
        vol_mount_str = ""

        if repo_str:
            image_name = repo_str + "/apporbit/apporbit-services:" + config_obj.buildid
        else:
            image_name = "apporbit/apporbit-services"

        if mode == '1':
            image_name = "apporbit/apporbit-services"

        if vol_mount:
            volonhost = vol_mount + "/Gemini-poc-stack"
            voloncontainer = "/home/apporbit/apporbit-services"
            vol_mount_str = " -v " + volonhost + ":" + voloncontainer + ":Z"
            logging.info("volume mount str" + vol_mount_str)
            pull_mist_binary = "wget -P " + volonhost + "/mist-cgp http://repos.gsintlab.com/repos/mist/integration/run.jar"
            self.utilityobj.cmdExecute(pull_mist_binary, 'pull mist binary ', True)

        cmd_deploy_services = "docker run -t --name apporbit-services --restart=always \
        -e GEMINI_INT_REPO=" + internal_repo
        if deploy_chef == "1":
            cmd_deploy_services = cmd_deploy_services + " -e CHEF_URL=https://" + host_ip +":9443 "

        cmd_deploy_services = cmd_deploy_services + " -e UPGRADE=" + upgrade + " -e MYSQL_HOST=db \
        -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=apporbit_mist \
        -e GEMINI_STACK_IPANEMA=1 --link apporbit-db:db --link apporbit-rmq:rmq \
        -v /var/lib/apporbit/sshKey_root:/root:Z "

        if deploy_chef == "1":
            cmd_deploy_services = cmd_deploy_services + "--volumes-from apporbit-chef "

        cmd_deploy_services = cmd_deploy_services + " -v /var/lib/apporbit/apporbit.ini:/etc/apporbit.ini:Z \
         -v /var/log/apporbit/services:/var/log/apporbit:Z \
         -v /var/lib/apporbit/chefconf:/opt/apporbit/chef:Z" + vol_mount_str + " -d  \
        " + image_name

        cmd_desc = "Deploying services container"

        self.utilityobj.cmdExecute(cmd_deploy_services, cmd_desc, True)
        sleep(10)
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


    def deployController (self, config_obj, consul_ip, consul_port):

        onprem_emailID = config_obj.onprem_emailID
        hostip = config_obj.hostip
        deploy_mode = config_obj.deploy_mode
        theme_name = config_obj.theme_name
        api_version = config_obj.api_version
        registry_url = config_obj.registry_url
        build_deploy_mode = config_obj.build_deploy_mode
        vol_mount = config_obj.volume_mount
        deploy_chef = config_obj.deploy_chef
        consulip = consul_ip
        consulport = consul_port


        log_level = 'DEBUG'
        onpremmode = 'true'
        cntrlimageName = ''
        vol_mount_str = ''

        max_phusion_process = self.calcMaxPhusionProcess()

        if deploy_mode == '1':
            onpremmode = 'true'
        else:
            onpremmode = 'false'

        if registry_url:
            cntrlimageName = registry_url + '/apporbit/apporbit-controller:' + config_obj.buildid
        else:
            cntrlimageName = 'apporbit/apporbit-controller'

        if  build_deploy_mode == '1':
            cntrlimageName = 'apporbit/apporbit-controller'

        if vol_mount:
            volonhost = vol_mount + "/Gemini-poc-mgnt"
            voloncontainer = "/home/apporbit/apporbit-controller"
            vol_mount_str = " -v " + volonhost + ":" + voloncontainer + ":Z"
            logging.info("volume mount str" + vol_mount_str)
            gemfile = volonhost + "/Gemfile"
            if not os.path.isfile(gemfile):
                rename_gemfile = "cp -f " + gemfile + "-master " + gemfile
                self.utilityobj.cmdExecute(rename_gemfile, 'copy Gemfile-master as Gemfile ', True)
          

        cmd_deploy_controller = "docker run -t --name apporbit-controller --restart=always \
        -p 80:80 -p 443:443 -e ONPREM_EMAIL_ID="+ onprem_emailID + " \
        -e LOG_LEVEL="+log_level + " -e MAX_POOL_SIZE=" + str(max_phusion_process)

        if deploy_chef == "1":
            cmd_deploy_controller = cmd_deploy_controller + " -e CHEF_URL=https://"+ hostip +":9443"

        cmd_deploy_controller = cmd_deploy_controller + " -e AO_HOST=" + hostip
        cmd_deploy_controller = cmd_deploy_controller + " -e CONSUL_IP=" + consulip
        cmd_deploy_controller = cmd_deploy_controller + " -e CONSUL_PORT=" + consulport
        cmd_deploy_controller = cmd_deploy_controller + " -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=apporbit_controller \
        -e ON_PREM_MODE=" + onpremmode + " -e THEME_NAME="+ theme_name + "\
        -e CURRENT_API_VERSION=" + api_version + " --link apporbit-db:db --link apporbit-rmq:rmq " + "\
	--link apporbit-svcd:svcd "
        if deploy_chef == "1":
            cmd_deploy_controller = cmd_deploy_controller + "--volumes-from apporbit-chef "

        cmd_deploy_controller = cmd_deploy_controller + vol_mount_str + " -v /var/log/apporbit/controller:/var/log/apporbit:Z \
        -v /var/lib/apporbit/sslkeystore/:/home/apporbit/apporbit-controller/sslkeystore:Z \
        -d " + cntrlimageName

        cmd_desc = "Deploying controller container."

        self.utilityobj.cmdExecute(cmd_deploy_controller, cmd_desc, True)

        sleep(5)

        return True


    def createSelfSignedCert(self, isChef=False, hostIP = ""):
        #Generate SSL Certificate
        if isChef:
            cmd_sslcert = 'openssl req -new -newkey rsa:4096 -days 365 -nodes -x509 \
            -subj "/C=US/ST=NY/L=appOrbit/O=Dis/CN='+ hostIP + '"\
            -keyout /opt/apporbit/chef-serverkey/'+ hostIP +'.key \
            -out /opt/apporbit/chef-serverkey/'+ hostIP + '.crt'

            cmd_desc = "Creating Chef SSL Certificate."

        else:
            cmd_sslcert = 'openssl req -new -newkey rsa:4096 -days 365 -nodes -x509\
            -subj "/C=US/ST=NY/L=appOrbit/O=Dis/CN=www.apporbit.com" \
            -keyout /var/lib/apporbit/sslkeystore/apporbitserver.key \
            -out /var/lib/apporbit/sslkeystore/apporbitserver.crt'

            cmd_desc = "Creating SSL Certificate."

        self.utilityobj.cmdExecute(cmd_sslcert, cmd_desc, True)

        return True

    def copySSLCertificate(self, dir, hostIP = "", is_chef = False):
        if is_chef == True:
            sslkeyfile = dir + "/" + hostIP + ".key"
            sslkeycrt = dir + "/" + hostIP + ".crt"
            cmd_cpysslkey = "cp -f " + sslkeyfile + " /opt/apporbit/chef-serverkey/."
            cmd_cpysslcrt = "cp -f " + sslkeycrt + " /opt/apporbit/chef-serverkey/."
            cmd_desckey = "Copying Chef SSL key"
            cmd_desccert = "Copying Chef SSL certificate"

        else:
            sslkeyfile = dir + "/apporbitserver.key"
            sslkeycrt = dir + "/apporbitserver.crt"
            cmd_cpysslkey = "cp -f " + dir +"/apporbitserver.key /var/lib/apporbit/sslkeystore/apporbitserver.key"
            cmd_cpysslcrt = "cp -f " + dir +"/apporbitserver.crt /var/lib/apporbit/sslkeystore/apporbitserver.crt"
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


    def deployAppOrbit(self, config_obj):
        consul_ip_port = config_obj.consul_ip_port
        consul_ip = config_obj.hostip
        consul_port = '8500'
        if consul_ip_port:
            consul_ip_port = urlparse(consul_ip_port)
            consul_ip = consul_ip_port.hostname
            consul_port = str(consul_ip_port.port)
        self.utilityobj.progressBar(1)
        # LOGIN to DOCKER REGISTRY
        if config_obj.build_deploy_mode in ['0', '1', '3']:
            self.utilityobj.loginDockerRegistry(config_obj.docker_uname, config_obj.docker_passwd, config_obj.registry_url)
            self.pullImagesformRepos(config_obj.registry_url, config_obj.buildid)

        self.utilityobj.progressBar(5)
        self.removeRunningContainers(config_obj)
        self.utilityobj.progressBar(6)
        self.utilityobj.createLogRoatateFile()

        # CLEAN or RETAIN OLD ENTRIES
        if config_obj.clean_setup == '1':
             self.clearOldEntries()

        # SETUP or CREATE DIRECTORIES for VOL MOUNT
        self.setupDirectoriesForVolumeMount()
        self.copyAOMonitoringConfFiles(["alertmanager.yml", "prometheus.yml", "alert.rules"], consul_ip, consul_port)

        if config_obj.chef_self_signed_crt == '1':
            self.createSelfSignedCert(True, config_obj.hostip)
        elif config_obj.chef_self_signed_crt == '2':
            self.copySSLCertificate(config_obj.chef_self_signed_crt_dir, config_obj.hostip, True)
        else:
            logging.info("Skipping chef certificate creation on upgrade.")

        if config_obj.self_signed_crt == '1':
            self.createSelfSignedCert()
        else:
            logging.info("Copying SSL Certificate from the dir %s", config_obj.self_signed_crt_dir)
            self.copySSLCertificate(config_obj.self_signed_crt_dir)

        # DEPLOY CHEF CONTAINER
        if config_obj.clean_setup == '1':
            if config_obj.deploy_chef == '1' or config_obj.deploy_chef == '3':
                self.deployChef(config_obj.hostip, config_obj.clean_setup, config_obj.registry_url) #CUSTOMER DEPLOYMENT or Master Deployment
            elif config_obj.deploy_chef == '0':
                self.deployChef(config_obj.hostip, config_obj.clean_setup)                        #LOCAL DEPLOYMENT- LOCAL IMAGE
            else:
                logging.info("Chef is chosen to be deployed in a different machine.")


        self.utilityobj.progressBar(10)

        # DEPLOY DATABASE CONTAINER
        self.deployDB()
        self.utilityobj.progressBar(12)
        #DEPLOY DOCS CONTAINER
        self.deployDocs(config_obj.registry_url)
        self.utilityobj.progressBar(13)
        # DEPLOY RABBIT MQ
        self.deployRMQ(config_obj.registry_url)
        self.utilityobj.progressBar(14)
        # DEPLOY SERVICES
        self.deployServices(config_obj)
        self.utilityobj.progressBar(15)
	
        #DEPLOY CONSUL
        self.deployConsul(config_obj.registry_url, config_obj.consul_host, config_obj.consul_domain, config_obj.build_deploy_mode)
        self.utilityobj.progressBar(16)

        #DEPLOY LOCATOR
        self.deployLocator(config_obj.consul_ip_port, config_obj.registry_url, config_obj.build_deploy_mode)
        self.utilityobj.progressBar(17)

        # DEPLOY SVCD
        self.deploySvcd(config_obj)
        self.utilityobj.progressBar(18)

        # DEPLOY ALERTMANAGER
        self.deployAlertmanager()

        # DEPLOY PROMETHEUS
        self.deployPrometheus(config_obj.hostip)

        # DEPLOY GRAFANA
        self.deployGrafana(config_obj)

        # DEPLOY PLATFORM
        self.deployController(config_obj, consul_ip, consul_port)
        self.utilityobj.progressBar(19)

	#DEPLOY DETA CAPTAIN
        self.deployCaptain(config_obj)
        self.utilityobj.progressBar(20)

        return True

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

    def removeRunningContainers(self, config_obj):
        container_name_list = ["db","apporbit-db", "apporbit-controller",
                               "apporbit-services","apporbit-docs",
                               "apporbit-rmq", "apporbit-consul",
                               "apporbit-locator", "apporbit-svcd",
                               "apporbit-alertmanager",
                               "apporbit-prometheus", "apporbit-grafana",
                               "apporbit-captain"]
        if config_obj.clean_setup == '1':
            container_name_list.append("apporbit-chef")

        for container_name in container_name_list:
            cmd_dockerps = "docker ps -a -q -f name=" + container_name
            cmd_desc = "Checking container existence." + container_name
            return_code, out, err = self.utilityobj.cmdExecute(cmd_dockerps, cmd_desc, False)
            if return_code and out:
                container_id_list = re.split("\n+", out)
                for container_id in container_id_list:
                    if container_id:
                        self.removeContainer(container_id)
        return True

    def clearChefData(self):
        try:
            shutil.rmtree('/opt/apporbit/chef-server', ignore_errors = True)
        except OSError as e:
            logging.warning("Failed to clean old Entries : " + e.strerror)
        return


    def clearOldEntries(self):
        logging.info("clean old entries to create freash setup STARTED!!!")
        try:
            shutil.rmtree('/var/dbstore', ignore_errors = True)
            shutil.rmtree('/var/lib/apporbit/', ignore_errors = True)
            logtimestamp = '/var/log/apporbit/oldlogs_' + str(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
            os.makedirs(logtimestamp)
            if os.path.exists("/var/log/apporbit/controller"):
   	        shutil.move('/var/log/apporbit/controller/', logtimestamp )
            if os.path.exists("/var/log/apporbit/services"):
                shutil.move('/var/log/apporbit/services/', logtimestamp )
            for filename in glob.glob(os.path.join('/var/log/apporbit/', 'apporbitInstall-*')):
                shutil.move(filename, logtimestamp)
            shutil.rmtree('/opt/apporbit/chef-server', ignore_errors = True)
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

    def setupDirectoriesForVolumeMount(self):
        logging.info("Setting up Directories for Volume Mount location  STARTED!!!")
        dirList = ["/var/dbstore", "/var/log/apporbit", "/var/lib/apporbit","/var/log/apporbit/controller",
                   "/var/log/apporbit/services", "/var/lib/apporbit/sshKey_root", "/var/lib/apporbit/sslkeystore",
                   "/var/lib/apporbit/chefconf","/opt/apporbit/chef-serverkey", "/opt/apporbit/chef-server", "/var/lib/apporbit/consul",
                   "/var/lib/apporbit/monitoring", 
                   "/var/lib/apporbit/monitoring/alert-data", "/var/lib/apporbit/monitoring/prom-data",
                   "/var/lib/apporbit/monitoring/grafana-data", "/var/lib/apporbit/monitoring/targets"]

        for dirName in dirList:
            self.createDirSetSeLinuxPermission(dirName)

        return True

    def copyAOMonitoringConfFiles(self, mon_conf_files, consul_ip, consul_port):
        # Copy the configuration yaml files in /var/lib/apporbit/monitoring for 
        # prometheus grafana and alertmanager
        logging.info("Copying appOrbit monitoring configuration files.")
        #path = os.path.dirname(os.path.realpath(__file__))
        for conf_file in mon_conf_files:
            #cnf = path + "/"+ conf_file
            if os.path.isfile(conf_file):
                cmd_exec = "cp -f " + conf_file + " /var/lib/apporbit/monitoring/"
                cmd_desc = "Copying configuration file " + conf_file
                self.utilityobj.cmdExecute(cmd_exec, cmd_desc, True)
            else:
                logging.error("Configuration file "+ conf_file + " doesn't exist")

        cmd_exec = "sed -i \"s/CONSUL_HOST_ADDR/" + consul_ip + ":" + str(consul_port) + "/g\" /var/lib/apporbit/monitoring/prometheus.yml"
        cmd_desc = "Adding consul host ip "+ consul_ip + ":" + str(consul_port) + " to prometheus configuration"
        self.utilityobj.cmdExecute(cmd_exec, cmd_desc, True)

        return True


    def pullImagesformRepos(self, repo_str, build_id):
        controller_image = repo_str + '/apporbit/apporbit-controller:' + build_id
        services_image = repo_str + '/apporbit/apporbit-services:' + build_id
        message_queue_image = repo_str + '/apporbit/apporbit-rmq'
        docs_image = repo_str + '/apporbit/apporbit-docs'
        database_image = 'mysql:5.6.24'
        svcd_image = repo_str + '/apporbit/svcd:' + build_id
        locator_image = repo_str + '/apporbit/locator:' + build_id
        consul_image = repo_str + '/apporbit/consul:' + build_id
        prometheus_image = 'prom/prometheus:v1.0.1'
        alertmanager_image = 'prom/alertmanager:master'
        grafana_image = repo_str + '/apporbit/apporbit-grafana:3.1.0'
	captain_image = repo_str + '/apporbit/captain:' + build_id

        cmd_ctrl_image = 'docker pull ' + controller_image
        cmd_srvc_image = 'docker pull ' + services_image
        cmd_msg_image = 'docker pull ' + message_queue_image
        cmd_docs_image = 'docker pull ' + docs_image
        cmd_dbs_image = 'docker pull ' + database_image
        cmd_svcd_image = 'docker pull ' + svcd_image
        cmd_locator_image = 'docker pull ' + locator_image
        cmd_consul_image = 'docker pull ' + consul_image
        cmd_prometheus_image = 'docker pull ' + prometheus_image
        cmd_alertmanager_image = 'docker pull ' + alertmanager_image
        cmd_grafana_image = 'docker pull ' + grafana_image
	cmd_captain_image = 'docker pull ' + captain_image

        self.utilityobj.progressBar(2)
        self.utilityobj.cmdExecute(cmd_ctrl_image , "Pull controller image",True)
        self.utilityobj.cmdExecute(cmd_srvc_image , "Pull services image",True)
        self.utilityobj.progressBar(3)
        self.utilityobj.cmdExecute(cmd_msg_image , "Pull message server image",True)
        self.utilityobj.cmdExecute(cmd_docs_image , "Pull document server image",True)
        self.utilityobj.progressBar(4)
        self.utilityobj.cmdExecute(cmd_dbs_image , "Pull database server image",True)
        self.utilityobj.cmdExecute(cmd_svcd_image, "Pull svcd  image",True)
        self.utilityobj.cmdExecute(cmd_locator_image, "Pull locator image",True)
        self.utilityobj.cmdExecute(cmd_consul_image, "Pull consul image",True)
        self.utilityobj.progressBar(5)
        self.utilityobj.cmdExecute(cmd_prometheus_image, "Pull prometheus image", True)
        self.utilityobj.cmdExecute(cmd_alertmanager_image, "Pull alertmanager image", True)
        self.utilityobj.cmdExecute(cmd_grafana_image, "Pull grafana image", True)
	self.utilityobj.cmdExecute(cmd_captain_image, "Pull captain image",True)

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
            self.user_interact_obj.deployChefOnly(self)
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
            self.action_obj.clearChefData()

        if self.chef_self_signed_crt == '1' :
            self.action_obj.createSelfSignedCert(True, self.hostIP)
        else:
            self.action_obj.copySSLCertificate(self.chef_ssldir, self.hostIP, True)
        print "Chef Server is getting deployed. This process may take some time."
        self.action_obj.deployChef(self.hostIP, self.chef_deploy_mode, self.reg_url)
        print "- Deployed successfully."
        print "Now you can access the chef-server ui at https://" + self.hostIP + ":9443. It is recommended to change the default password."


class DeployConsul:
    def __init__(self):
        self.utility_obj = utility.Utility()
        self.action_obj = Action()

    def deploy_consul(self):
         if os.path.isfile('local.conf'):
            config = ConfigParser.ConfigParser()
            fp = open('local.conf', 'r')
            config.readfp(fp)
            try:
                self.uname = config.get('Docker Login', 'username')
                self.password = config.get('Docker Login', 'password')
                self.reg_url = config.get('User Config', 'registry_url')
                self.utility_obj.loginDockerRegistry(self.uname, self.password, self.reg_url)
                self.consul_host = config.get('User Config', 'consul_host')
                self.consul_domain = config.get('User Config', 'consul_domain')
                logging.info("Consul deployment started..")
                print "Consul deployment started.."
                self.action_obj.removeConsulContainer()
                self.action_obj.deployConsul(self.reg_url, self.consul_host, self.consul_domain)
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
              self.action_obj.deployConsul("registry.apporbit.com", consul_host, consul_domain)

              if self.utility_obj.isConsulDeployed():
                  print "Consul deployed successfully"
                  logging.info("Consul deployed successfully..")
