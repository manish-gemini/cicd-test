#!/usr/bin/env python

import logging
import ConfigParser
import exceptions
import os
import stat
import sys
import errno
import time
from string import Template

class Config():

    def __init__(self):
        self.NUM_CONTAINERS = 13
        self.APPORBIT_HOME = '/opt/apporbit'
        self.APPORBIT_BIN = self.APPORBIT_HOME + '/bin'
        self.APPORBIT_CONF = self.APPORBIT_HOME + '/conf'
        self.APPORBIT_KEY = self.APPORBIT_HOME + '/key'
        self.APPORBIT_DATA = '/var/lib/apporbit'
        self.APPORBIT_LOG = '/var/log/apporbit'
        self.APPORBIT_COMPOSE = 'COMPOSE_HTTP_TIMEOUT=300 ' + self.APPORBIT_BIN + '/docker-compose -p apporbit' 
        self.apporbit_serverconf = self.APPORBIT_CONF + '/apporbit-server.conf'
        self.systemreqs = False
        self.apporbit_ini = self.APPORBIT_CONF + '/apporbit.ini'
        self.composeTemplate = 'apporbit-compose-template.yml'
        self.composeFile = self.APPORBIT_CONF + '/apporbit-compose.yml'
        # From Config files
        self.apporbit_loginid = 'admin@apporbit.com'
        self.apporbit_host = ''
        self.apporbit_domain = ''
        self.consul_host = ''
        self.consul_port = '8500'
        self.chef_host = ''
        self.apporbit_deploy = 'all'
        self.apporbit_registry = 'registry.apporbit.com'
        self.datasvc_registry = 'docker.io'
        self.remove_data= False
        self.initial_setup= False
        self.apporbit_repo = 'http://repos.gsintlab.com/release'
        self.registry_uname = ''
        self.registry_passwd = ''
        self.initial_install = False
        self.deploy_apporbit = True
        self.deploy_chef = True
        self.deploy_consul = True
        self.upgrade = False
        self.create_keys = True
        self.import_keys_from_dir = ''
        self.build_deploy_mode = '3'
        self.deploy_mode = 'onprem'
        self.theme_name = 'apporbit-v2'
        self.api_version = 'v2'
        self.self_signed_crt = '1'
        self.self_signed_crt_dir = ''
        self.chef_self_signed_crt = '0'
        self.chef_self_signed_crt_dir = ''
        self.buildid = 'latest'
        self.volume_mount = ''
        return


    def touch(self, fname, times=None):
        with open(fname, 'a+'):
            os.utime(fname, times)


    def setupConfig(self, utilityobj, max_api_users):
        try:
            os.stat(self.APPORBIT_BIN)
        except:
            os.makedirs(self.APPORBIT_BIN)   
        try:
            os.stat(self.APPORBIT_CONF)
        except:
            os.makedirs(self.APPORBIT_CONF)   
        self.downloadCompose(utilityobj)
        self.touch(self.apporbit_ini )
        self.createMonitoringConfig()
        self.createComposeFile(utilityobj, max_api_users)
        self.createConfigFile(self.apporbit_serverconf)


    def downloadCompose(self, utilityobj):
        flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
        try:
            repo_file = os.open(self.APPORBIT_BIN + '/docker-compose',flags)
        except OSError as e:
            if e.errno == errno.EEXIST:
               pass
            else:
               raise
        else:
            composeFileName = self.APPORBIT_BIN + "/docker-compose"
            cmd_downloadCompose = ("curl -L " +
                " https://github.com/docker/compose/releases/download/1.8.0/docker-compose-Linux-x86_64 > "
                + composeFileName )
            cmd_desc = "Download compose binary .."
            utilityobj.cmdExecute(cmd_downloadCompose, cmd_desc, True)
            logging.debug("Sleep to complete download.")
            time.sleep(1)
            st = os.stat(composeFileName)
            #os.chmod(composeFileName, st.st_mode | stat.S_IEXEC)
            cmd_chmod = ("chmod a+x " + composeFileName )
            cmd_desc = "Make compose executable .."
            utilityobj.cmdExecute(cmd_chmod, cmd_desc, True)
            cmd_sync = ("sync")
            cmd_desc = "Sync chmod changes to disk .."
            utilityobj.cmdExecute(cmd_sync, cmd_desc, True)
            utilityobj.cmdExecute(cmd_sync, cmd_desc, True)
            utilityobj.cmdExecute(cmd_sync, cmd_desc, True)
            logging.debug("Sleep to complete sync.")
            time.sleep(1)
            logging.info("Downloaded compose binary.")
            logging.error("Restart apporbit-server required to use compose binary.")
            print "Downloaded compose binary. However to use it, apporbit-server has to be re-run"
            print "Please re-run apporbit-server command"
            sys.exit(1)


    def loadConfig(self, fileName="setup.conf"):
        logging.info("Loading Config File from file name %s", fileName)
        config = ConfigParser.ConfigParser()
        fp = open(fileName, 'r')
        config.readfp(fp)

        try:
           for key in config.options('Registry Setup'):
               val = config.get('Registry Setup', key)
               if key== 'username':
                  self.registry_uname = val
               elif key == 'password':
                  self.registry_passwd = val
               elif key == 'apporbit_registry':
                  self.apporbit_registry = val
               elif key == 'apporbit_repo':
                  self.apporbit_repo = val
               elif key == 'datasvc_registry':
                  self.datasvc_registry = val

           for key in config.options('System Setup'):
               val = config.get('System Setup', key)
               if key== 'apporbit_host':
                  self.apporbit_host = val
               elif key == 'apporbit_domain':
                  self.apporbit_domain = val
               elif key == 'consul_host':
                  self.consul_host = val
               elif key == 'chef_host':
                  self.chef_host = val

           if self.apporbit_host and not self.consul_host:
               self.consul_host = self.apporbit_host
           if self.apporbit_host and not self.chef_host:
               self.chef_host = self.apporbit_host

           for key in config.options('Deployment Setup'):
               val = config.get('Deployment Setup', key)
               if key == 'remote_data':
                  self.remote_data = val
               elif key == 'apporbit_deploy':
                  self.apporbit_deploy = val
               elif key == 'systemreqs':
                  self.systemreqs = val
               elif key == 'build_deploy_mode':
                  self.build_deploy_mode = val
               elif key == 'build_id':
                  self.buildid = val
               elif key == 'self_signed_crt':
                  self.self_signed_crt = val
               elif key == 'self_signed_crt_dir':
                  self.self_signed_crt_dir = val
               elif key == 'chef_ssl_crt':
                  self.chef_self_signed_crt = val
               elif key == 'chef_ssl_crt_dir':
                  self.chef_self_signed_crt_dir = val
               elif key == 'deploy_chef':
                  self.deploy_chef = val
               elif key == 'deploy_consul':
                  self.deploy_consul = val
               elif key == 'upgrade':
                  self.upgrade = val
               elif key == 'deploy_mode':
                  self.deploy_mode = val
               elif key == 'volume_mount':
                  self.volume_mount = val

           for key in config.options('Software Setup'):
               val = config.get('Software Setup', key)
               if key == 'apporbit_loginid':
                  self.apporbit_loginid = val
               elif key == 'themeName':
                  self.theme_name = val
               elif key == 'api_version':
                  self.api_version = val

        except ConfigParser.NoSectionError, ConfigParser.NoOptionError:
            logging.warning("warning No section or No option error were found in the file...")

        fp.close()
        return


    def createConfigFile(self,fileName):

        logging.info("Creating Config Filename %s", fileName)
        config = ConfigParser.ConfigParser()
        cfg_file = open(fileName,'w+')

        config.add_section('Registry Setup')
        config.set('Registry Setup', 'apporbit_registry', self.apporbit_registry)
        config.set('Registry Setup' , 'username', self.registry_uname)
        config.set('Registry Setup', 'password', self.registry_passwd)
        config.set('Registry Setup', 'apporbit_repo', self.apporbit_repo)
        if self.datasvc_registry <> '':
            config.set('Registry Setup', 'datasvc_registry', self.datasvc_registry)

        config.add_section('System Setup')
        config.set('System Setup', 'apporbit_host', self.apporbit_host)
        config.set('System Setup', 'apporbit_domain', self.apporbit_domain)
        config.set('System Setup', 'consul_host', self.consul_host)
        config.set('System Setup', 'chef_host', self.chef_host)

        config.add_section('Deployment Setup')
        config.set('Deployment Setup', 'remove_data', self.remove_data)
        config.set('Deployment Setup', 'apporbit_deploy', self.apporbit_deploy)
        config.set('Deployment Setup', 'build_deploy_mode', self.build_deploy_mode)
        config.set('Deployment Setup', 'build_id', self.buildid )
        config.set('Deployment Setup', 'self_signed_crt', self.self_signed_crt)
        config.set('Deployment Setup', 'self_signed_crt_dir', self.self_signed_crt_dir)
        config.set('Deployment Setup', 'chef_ssl_crt', self.chef_self_signed_crt)
        config.set('Deployment Setup', 'chef_ssl_crt_dir', self.chef_self_signed_crt_dir)
        config.set('Deployment Setup', 'deploy_chef', self.deploy_chef)
        config.set('Deployment Setup', 'deploy_consul', self.deploy_consul)
        config.set('Deployment Setup', 'upgrade', self.upgrade)
        config.set('Deployment Setup', 'deploy_mode', self.deploy_mode)
        config.set('Deployment Setup', 'volume_mount', self.volume_mount)
        config.set('Deployment Setup', 'systemreqs', self.systemreqs)

        config.add_section('Software Setup')
        config.set('Software Setup', 'apporbit_loginid', self.apporbit_loginid)
        config.set('Software Setup', 'themeName', self.theme_name)
        config.set('Software Setup', 'api_version', self.api_version)

        config.write(cfg_file)
        cfg_file.close()

        logging.info("Create config file success!")
        return

    def createMonitoringConfig(self):

        logging.info("Create Monitoring configuration files")
        flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
        try:
            rules_file = os.open(self.APPORBIT_CONF + '/alert.rules',flags)
        except OSError as e:
            if e.errno == errno.EEXIST:
               pass
            else:
               raise
        else:
            with os.fdopen(rules_file, 'w' ) as file_obj:
                 content = '''
ALERT rabbitmq_down
  IF node_external_rabbitmq_state == 0
    FOR 1m
      LABELS {
              severity="page"
                    }
  ANNOTATIONS {
        summary = "Instance {{$labels.instance}} down",
                  description = "{{$labels.instance}} of job {{$labels.job}} has been down for more than 1 minutes.",
                    }
                 '''
                 file_obj.write (content)
                 file_obj.close()
                 logging.info("Create alert.rules success!")

        try:
            manager_file = os.open(self.APPORBIT_CONF + '/alertmanager.yml',flags)
        except OSError as e:
            if e.errno == errno.EEXIST:
               pass
            else:
               raise
        else:
            with os.fdopen(manager_file, 'w' ) as file_obj:
                 content = Template('''
route:
 repeat_interval: 1m
 receiver: default
 routes:
   - receiver: 'email-demo'
     match:
       severity: page

receivers:
 - name: default
 - name: 'email-demo'
   email_configs:
       - to: '${APPORBIT_LOGINID}'
         from: '${APPORBIT_LOGINID}'
         smarthost: '${APPORBIT_HOST}'
         require_tls: false
         send_resolved: true
                 ''')
                 content = content.safe_substitute(
                            APPORBIT_HOST = self.apporbit_host,
                            APPORBIT_LOGINID = self.apporbit_loginid)
                 file_obj.write (content)
                 file_obj.close()
                 logging.info("Create alertmanager.yml success!")

        try:
            prometheus_file = os.open(self.APPORBIT_CONF + '/prometheus.yml',flags)
        except OSError as e:
            if e.errno == errno.EEXIST:
               pass
            else:
               raise
        else:
            with os.fdopen(prometheus_file, 'w' ) as file_obj:
                 content = '''
global:
  scrape_interval: 1m
  evaluation_interval: 1m

  external_labels:
    monitor: 'apporbit'

scrape_configs:
- job_name: 'host'
  consul_sd_configs:
      - server: 'consul:8500'
  relabel_configs:
    - source_labels: [__meta_consul_tags]
      regex: .*,monitor,.*
      action: keep

rule_files:
  - 'etc/prometheus/alert.rules'
'''
                 file_obj.write(content)
                 file_obj.close()
                 logging.info("Create prometheus.yml success!")

        return


    def createRepoFile(self):
        flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
        try:
            repo_file = os.open('/etc/yum.repos.d/apporbit.repo',flags)
        except OSError as e:
            if e.errno == errno.EEXIST:
               pass
            else:
               raise
        else:
            with os.fdopen(repo_file, 'w' ) as file_obj:
                 content = '''
[apporbit-base]
name=apporbit base repository
baseurl=http://repos.gsintlab.com/release/
enabled=1
gpgcheck=0
protect=0

[apporbit-release]
name=apporbit release repository
baseurl=http://repos.gsintlab.com/1.5.1/
enabled=1
gpgcheck=0
protect=0
'''
                 file_obj.write(content)
                 file_obj.close()
                 logging.info("Create approbit.repo success!")
        # Use Docker.com binaries         
        try:
            repo_file = os.open('/etc/yum.repos.d/docker.repo',flags)
        except OSError as e:
            if e.errno == errno.EEXIST:
               pass
            else:
               raise
        else:
            with os.fdopen(repo_file, 'w' ) as file_obj:
                 content = '''
[dockerrepo]
name=Docker Repository
baseurl=https://yum.dockerproject.org/repo/main/centos/7/
enabled=1
gpgcheck=1
gpgkey=https://yum.dockerproject.org/gpg
'''
                 file_obj.write(content)
                 file_obj.close()
                 logging.info("Create docker.repo success!")




    def createComposeFile(self, utilityobj, max_api_users=1):

        logging.info("Creating Compose configuration files")
        content=Template('''

version: "2"
services:


  apporbit-chef:
    container_name: apporbit-chef
    image: ${APPORBIT_REGISTRY}apporbit/apporbit-chef:2.0
    mem_limit: 2100000000
    hostname: ${APPORBIT_HOST}
    dns:  
      - 8.8.8.8
      - ${APPORBIT_DNS}
    dns_search: 
      - ${APPORBIT_DNSSEARCH}
    restart: always
    network_mode: "bridge"
    ports:
      - "9443:9443"
    environment:
      - UPGRADE
    volumes:
      - ${APPORBIT_LIB}/chef-server:/var/opt/chef-server:Z
      - ${APPORBIT_KEY}:/var/opt/chef-server/nginx/ca/:Z
      - chef-conf:/etc/chef-server/:Z

  apporbit-rmq:
    container_name: apporbit-rmq
    image: ${APPORBIT_REGISTRY}apporbit/apporbit-rmq:${APPORBIT_BUILDID}
    hostname: rmq
    dns:  
      - 8.8.8.8
      - ${APPORBIT_DNS}
    dns_search: 
      - ${APPORBIT_DNSSEARCH}
    restart: always
    network_mode: "bridge"
    mem_limit: 2100000000
    environment:
      - RABBITMQ_VM_MEMORY_HIGH_WATERMARK_PAGING_RATIO=0.1
    volumes:
      - rabbitmq-data:/var/lib/rabbitmq:Z
      - ${APPORBIT_LOG}/rmq:/var/log/rabbitmq:Z

  apporbit-db:
    container_name: apporbit-db
    image: mysql:5.6.24
    network_mode: "bridge"
    hostname: db
    dns:  
      - 8.8.8.8
      - ${APPORBIT_DNS}
    dns_search: 
      - ${APPORBIT_DNSSEARCH}
    restart: always
    ports:
      - "3306"
    environment:
      - MYSQL_USER=root
      - MYSQL_ROOT_PASSWORD=admin
      - MYSQL_PASSWORD=admin
      - MYSQL_DATABASE=apporbit_controller
    volumes:
      - ${APPORBIT_LIB}/mysql:/var/lib/mysql:Z


  apporbit-consul:
    container_name: apporbit-consul
    image: ${APPORBIT_REGISTRY}apporbit/consul:${APPORBIT_BUILDID}
    command: -server -bootstrap --domain=${APPORBIT_DOMAIN}
    hostname: consul
    dns:  
      - 8.8.8.8
      - ${APPORBIT_DNS}
    dns_search: 
      - ${APPORBIT_DNSSEARCH}
    restart: always
    network_mode: "bridge"
    ports:
      - "8400:8400"
      - "8500:8500"
      - "53:53/udp"
      - "53:53"
      - "8301:8301/udp"
      - "8302:8302/udp"
    volumes:
      - ${APPORBIT_LIB}/consul:/data:Z

  apporbit-services:
    container_name: apporbit-services
    image: ${APPORBIT_REGISTRY}apporbit/apporbit-services:${APPORBIT_BUILDID}
    restart: always
    hostname: services
    dns:  
      - 8.8.8.8
      - ${APPORBIT_DNS}
    dns_search: 
      - ${APPORBIT_DNSSEARCH}
    network_mode: "bridge"
    environment:
      - TERM=xterm
      - GEMINI_INT_REPO=${APPORBIT_REPO}
      - CHEF_URL=https://${APPORBIT_CHEFHOST}:9443
      - UPGRADE
      - MYSQL_HOST=db
      - MYSQL_USERNAME=root
      - MYSQL_PASSWORD=admin
      - MYSQL_DATABASE=apporbit_mist
      - GEMINI_STACK_IPANEMA=1
    links:
      - apporbit-db:db 
      - apporbit-rmq:rmq
    volumes_from:
      - apporbit-chef
    depends_on:
      - apporbit-captain
    volumes:
      - ${APPORBIT_LIB}/sshKey_root:/root:Z
      - ${APPORBIT_CONF}/apporbit.ini:/etc/apporbit.ini:Z
      - ${APPORBIT_LIB}/services:/var/lib/apporbit:Z
      - ${APPORBIT_LOG}/services:/var/log/apporbit:Z
      - ${APPORBIT_LIB}/chefconf:/opt/apporbit/chef:Z
      ${SERVICES_DEVMOUNT}


  apporbit-locator:
    container_name: apporbit-locator
    image: ${APPORBIT_REGISTRY}apporbit/locator:${APPORBIT_BUILDID}
    hostname: locator
    dns:  
      - 8.8.8.8
      - ${APPORBIT_DNS}
    dns_search: 
      - ${APPORBIT_DNSSEARCH}
    restart: always
    network_mode: "bridge"
    ports:
      - "8080"
    environment:
      - CONSUL_IP_PORT=http://consul:8500
    links:
      - apporbit-consul:consul
    volumes:
      - ${APPORBIT_LIB}/locator:/data:Z
      - ${APPORBIT_LOG}/locator:/var/log/apporbit:Z


  apporbit-svcd:
    container_name: apporbit-svcd
    image: ${APPORBIT_REGISTRY}apporbit/svcd:${APPORBIT_BUILDID}
    hostname: svcd
    dns:  
      - 8.8.8.8
      - ${APPORBIT_DNS}
    dns_search: 
      - ${APPORBIT_DNSSEARCH}
    restart: always
    network_mode: "bridge"
    environment:
      - CONTROLLER_ALIAS_NAME=${APPORBIT_HOST}
    ports:
      - "8080"
    links:
      - apporbit-db:db 
      - apporbit-locator:locator
    volumes:
      - ${APPORBIT_LOG}/svcd:/var/log/apporbit:Z

  apporbit-alertmanager:
    container_name: apporbit-alertmanager
    image: prom/alertmanager:master
    command: "-config.file=/alertmanager.yml -storage.path=/alert-data"
    hostname: alertmanager
    dns:  
      - 8.8.8.8
      - ${APPORBIT_DNS}
    dns_search: 
      - ${APPORBIT_DNSSEARCH}
    restart: always
    network_mode: "bridge"
    ports:
      - "9093:9093"
    volumes:
      - ${APPORBIT_CONF}/alertmanager.yml:/alertmanager.yml:Z
      - ${APPORBIT_LIB}/monitoring/alert-data:/alert-data:Z 


  apporbit-prometheus:
    container_name: apporbit-prometheus
    image: prom/prometheus:v1.0.1
    command: "-config.file=/etc/prometheus/prometheus.yml -storage.local.path=/prom-data -alertmanager.url=http://alertmanager:9093"
    restart: always
    hostname: prometheus
    dns:  
      - 8.8.8.8
      - ${APPORBIT_DNS}
    dns_search: 
      - ${APPORBIT_DNSSEARCH}
    network_mode: "bridge"
    ports:
      - "9090:9090"
    links:
      - apporbit-consul:consul 
      - apporbit-alertmanager:alertmanager 
    volumes:
      - ${APPORBIT_CONF}/prometheus.yml:/etc/prometheus/prometheus.yml:Z
      - ${APPORBIT_CONF}/alert.rules:/etc/prometheus/alert.rules:Z
      - ${APPORBIT_LIB}/monitoring/prom-data:/prom-data:Z
      - ${APPORBIT_LIB}/monitoring/targets:/var/lib/apporbit/monitoring/targets:Z

  apporbit-grafana:
    container_name: apporbit-grafana
    image: ${APPORBIT_REGISTRY}apporbit/apporbit-grafana:3.1.0
    restart: always
    hostname: grafana
    dns:  
      - 8.8.8.8
      - ${APPORBIT_DNS}
    dns_search: 
      - ${APPORBIT_DNSSEARCH}
    network_mode: "bridge"
    ports:
      - "3000:3000"
    environment:
      - GF_AUTH_ANONYMOUS_ENABLED=true 
      - GF_AUTH_ANONYMOUS_ORG_ROLE=Admin 
      - GF_USERS_DEFAULT_THEME=light 
    depends_on:
      - apporbit-prometheus
    volumes:
      - ${APPORBIT_LIB}/monitoring/grafana-data:/var/lib/grafana:Z


  apporbit-captain:
    container_name: apporbit-captain
    image: ${APPORBIT_REGISTRY}apporbit/captain:${APPORBIT_BUILDID}
    restart: always
    hostname: captain
    dns:  
      - 8.8.8.8
      - ${APPORBIT_DNS}
    dns_search: 
      - ${APPORBIT_DNSSEARCH}
    network_mode: "bridge"
    ports:
      - "8080"
    environment:
      - CONTROLLER_ALIAS_NAME=${APPORBIT_HOST}
      - AO_REGISTRY=${DATASVC_REGISTRY}
    links:
      - apporbit-svcd:svcd
    volumes:
      - ${APPORBIT_LOG}/captain:/var/log/apporbit:Z


  apporbit-controller:
    container_name: apporbit-controller
    image: ${APPORBIT_REGISTRY}apporbit/apporbit-controller:${APPORBIT_BUILDID}
    hostname: ${APPORBIT_HOST}
    dns:  
      - 8.8.8.8
      - ${APPORBIT_DNS}
    dns_search: 
      - ${APPORBIT_DNSSEARCH}
    restart: always
    network_mode: "bridge"
    ports:
      - "80:80"
      - "443:443"
    environment:
      - TERM=xterm
      - ON_PREM_MODE=true
      - THEME_NAME=apporbit-v2
      - CURRENT_API_VERSION=v2
      - ONPREM_EMAIL_ID=${APPORBIT_LOGINID}
      - LOG_LEVEL=WARN
      - MAX_POOL_SIZE=${MAX_API_USERS}
      - CHEF_URL=https://${APPORBIT_CHEFHOST}:9443
      - AO_HOST=${APPORBIT_HOST}
      - CONSUL_IP=consul
      - CONSUL_PORT=8500
      - CAPTAIN_TCP_ADDR=captain
      - CAPTAIN_TCP_PORT=8080
      - MYSQL_HOST=db
      - MYSQL_PORT=3306
      - MYSQL_USERNAME=root
      - MYSQL_PASSWORD=admin
      - MYSQL_DATABASE=apporbit_controller
    links:
      - apporbit-db:db 
      - apporbit-rmq:rmq
      - apporbit-svcd:svcd
      - apporbit-consul:consul
      - apporbit-captain:captain
    volumes_from:
      - apporbit-chef
    volumes:
      - ${APPORBIT_LOG}/controller:/var/log/apporbit:Z
      - ${APPORBIT_KEY}:/home/apporbit/apporbit-controller/sslkeystore:Z
      ${CONTROLLER_DEVMOUNT}

  apporbit-docs:
    container_name: apporbit-docs
    image: ${APPORBIT_REGISTRY}apporbit/apporbit-docs:${APPORBIT_BUILDID}
    restart: always
    hostname: docs
    dns:  
      - 8.8.8.8
      - ${APPORBIT_DNS}
    dns_search: 
      - ${APPORBIT_DNSSEARCH}
    network_mode: "bridge"
    ports:
      - "9080:80"
    depends_on:
      - apporbit-controller

networks:
  default:
    external:
      name: bridge

volumes:
  chef-conf:
    driver: local
  rabbitmq-data:
    driver: local

        '''
        )

        # Check if composeFile already exists then skip creating it.
        flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
        try:
            compose_file = os.open(self.composeFile ,flags)
        except OSError as e:
            if e.errno == errno.EEXIST:
               pass
            else:
               raise
        else:
            with os.fdopen(compose_file, 'w' ) as file_obj:
                 # cat apporbit-compose-template.yml |awk '{ for(i=1; i<=NF; i++) 
                 # { if (match($i, /\$\{([a-z|A-Z|0-9|_]+)\}/))  {print substr($i,RSTART+2,RLENGTH-3)} } }' |sort |uniq
                 if self.volume_mount:
                     logging.warning("DEVELOPER MOUNT ENABLED")
                     services_devmount = '- ' + self.volume_mount + '/Gemini-poc-stack:/home/apporbit/apporbit-services:Z'
                     if not os.path.isfile(self.volume_mount + "/Gemini-poc-stack/mist-cgp/run.jar"):
                         pull_mist_binary = "wget -P " + self.volume_mount + "/Gemini-poc-stack/mist-cgp http://repos.gsintlab.com/repos/mist/integration/run.jar"
                         utilityobj.cmdExecute(pull_mist_binary, 'pull mist binary ', True)
                     controller_devmount = '- ' + self.volume_mount + '/Gemini-poc-mgnt:/home/apporbit/apporbit-controller:Z'
                     gemfile = self.volume_mount  + "/Gemini-poc-mgnt/Gemfile"
                     if not os.path.isfile(gemfile):
                        rename_gemfile = "cp -f " + gemfile + "-master " + gemfile
                        utilityobj.cmdExecute(rename_gemfile, 'copy Gemfile-master as Gemfile ', True)

                 else:
                     services_devmount = ''
                     controller_devmount = ''

                 # aoreg has / so local or full qualified images are handled in template
                 aoreg = self.apporbit_registry
                 if aoreg:
                    aoreg += '/'

                 datareg = self.apporbit_registry
                 if self.datasvc_registry != '':
                    datareg = self.datasvc_registry

                 if self.apporbit_domain:
                    domain = self.apporbit_domain
                 else:
                    domain = 'consul.'


                 content = content.safe_substitute(
                            APPORBIT_CHEFHOST = self.chef_host,
                            APPORBIT_CONF = self.APPORBIT_CONF,
                            APPORBIT_HOST = self.apporbit_host,
                            APPORBIT_DOMAIN = domain,
                            APPORBIT_DNS = self.consul_host,
                            APPORBIT_DNSSEARCH = domain,
                            APPORBIT_KEY = self.APPORBIT_KEY,
                            APPORBIT_LIB = self.APPORBIT_DATA,
                            APPORBIT_LOG = self.APPORBIT_LOG,
                            APPORBIT_LOGINID = self.apporbit_loginid,
                            APPORBIT_REGISTRY = aoreg,
                            APPORBIT_REPO = self.apporbit_repo,
                            APPORBIT_BUILDID = self.buildid,
                            MAX_API_USERS = max_api_users,
                            DATASVC_REGISTRY = datareg,
                            SERVICES_DEVMOUNT = services_devmount,
                            CONTROLLER_DEVMOUNT = controller_devmount,
                            )
                 file_obj.write(content)
                 file_obj.close()
                 logging.info("Create composeFile success!")

        return True
