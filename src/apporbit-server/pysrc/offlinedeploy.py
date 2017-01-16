from string import Template
import logging
import errno
import os
import shutil
import time
import urllib
import sys

import docker_ao
import config
import utility
import resourcefetcher
import action


class OfflineDeploy(object):
    """docstring for OfflineDeploy"""
    def __init__(self):
        self.action_obj = action.Action()
        self.config_obj = config.Config()
        self.utility_obj = utility.Utility()
        self.docker_obj = docker_ao.DockerAO()
        self.emailid = "admin@apporbit.com"
        self.host = ""
        self.repohost = ""
        self.internal_repo = ""
        self.internal_docker_reg = ""
        self.internal_gems_repo = ""
        self.CWD = os.getcwd() + "/"
        self.TMPDIR = "/tmp/"
        self.AO_PACKAGES_PATH = ""
        self.EXTRACTED_PACKAGES = self.TMPDIR + "appOrbitPackages/"

        self.chef_port = 9443

    def makedirs(self, path):
        try:
            os.makedirs(path)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise

    def verifyOS(self):
        self.utility_obj.cmdExecute("yum makecache", "", show=True)
        self.utility_obj.verifyOSRequirement()

    def check_repo_status(self):
        try:
            if urllib.urlopen(self.internal_repo).getcode() == 200:
                return True
            else:
                return False
        except Exception as exc:
            print "Internal repo not hosted.\
                Please run apporbit-server --setupprovider"
            sys.exit(1)

    def get_internal_apporibit_repo_uri(self):
        self.repohost = raw_input("Enter IP of internal repo host : ")
        self.internal_repo = "http://" + self.repohost + ":9291/repos"
        self.internal_gems_repo = "http://" + self.repohost + ":9292"
        self.internal_docker_reg = self.repohost + ":5000"

        if not self.check_repo_status():
            print "Unable to connect repositories. Check Network settings\
                 and enable connection to " + self.internal_repo
            sys.exit(1)
        else:
            print "Verified connection with the repos... OK"

    def setup_internal_apporbit_repo(self):
        if not os.path.isfile("/etc/yum.repos.d/apporbit-offline.repo"):
            content = Template('''
[apporbit-offline]
name=appOrbit Repository
baseurl=${internal_repo}
enabled=1
gpgcheck=0
''').safe_substitute(internal_repo=self.internal_repo)

            try:
                with open("/etc/yum.repos.d/apporbit-offline.repo", "w") as f:
                    f.write(content)
            except OSError as e:
                logging.info("Could not create apporbit-offline repo. Exiting")
                logging.error(e)
                print "Could not create apporbit-offline repo, check logs"
                sys.exit(1)

    def setup_ntp(self):
        print "Time will be synchronized with time.nist.gov for this host"
        command = "yum install -y ntp && ntpdate -b -u time.nist.gov"
        return_code, out, err = self.utility_obj.cmdExecute(
            command, "", show=True)
        if not return_code:
            logging.warning("Time not in sync, sync time via date command")

    def install_docker(self):
        self.docker_obj.install_docker(self.utility_obj, enablerepo=True)

    def set_iptables(self):
        print "Setting up iptables rules..."
        cmd_list = [
            "iptables -D INPUT -j REJECT --reject-with icmp-host-prohibited",
            "iptables -D FORWARD -j REJECT --reject-with icmp-host-prohibited"]
        command = " && ".join(cmd_list)
        return_code, out, err = self.utility_obj.cmdExecute(
            command, "", show=True)
        if not return_code:
            logging.warning("Iptables not set " + out)

    def uncompress_resources(self):
        print "Enter path to Packages tar"
        self.AO_PACKAGES_PATH = raw_input(
            "Default(" + self.CWD + "appOrbitPackages.tar.gz): ")\
            or self.CWD + "appOrbitPackages.tar.gz"
        if not os.path.isfile(self.AO_PACKAGES_PATH):
            print "Path does not exist. Exiting.."
            sys.exit(1)
        command = "tar -xvf " + self.AO_PACKAGES_PATH + " -C " + self.TMPDIR
        return_code, out, err = self.utility_obj.cmdExecute(
            command, "Extract " + self.AO_PACKAGES_PATH, bexit=True, show=True)

    def add_chef_port_to_firewall(self):
        if os.path.isfile("/usr/bin/firewall-cmd"):
            print "Adding port " + str(self.chef_port) + " to firewall..."
            command = "firewall-cmd --permanent --add-port=" +\
                str(self.chef_port) + "/tcp"
            return_code, out, err = self.utility_obj.cmdExecute(
                command, "Adding Chef port to firewall", bexit=True, show=True)

        print "Saving Iptables"
        return_code, out, err = self.utility_obj.cmdExecute(
            "/sbin/iptables-save", "", show=False)
        if not return_code:
            print "WARNING : Iptables not saved" +\
                "The rule will reset after machine restarts"
            logging.warning("Iptables not saved")
        else:
            logging.info("Iptables saved")

    def set_config_info(self):
        emailid = "admin@apporbit.com"
        onPremMode = True

        self.emailid = raw_input(
            "Enter the User Email id for On Prem Deployment. Default(" +
            emailid + "):") or emailid

    def setup_logrotate(self):
        if not os.path.isfile("/etc/logrotate.d/apporbitLogRotate"):
            content = '''\
/var/log/apporbit/controller/*log /var/log/apporbit/services/*log {
          daily
          missingok
          size 50M
          rotate 20
          compress
          copytruncate
        }'''

            try:
                with open('/etc/logrotate.d/apporbitLogRotate', 'w') as f:
                    f.write(content)
            except OSError as e:
                logging.info("Couldn't create logrotate file. Exiting")
                logging.error(e)
                print "Couldn't create logrotate file, check logs"
                sys.exit(1)

    def get_host_ip(self):
        self.host = raw_input("Enter the Host IP: ")
        if self.host == "":
            print "Host IP is Mandatory.. Exiting.."
            sys.exit(1)

    def generate_ssl_certs(self):
        AO_KEYPATH = self.config_obj.APPORBIT_KEY
        if not os.path.isfile(
                AO_KEYPATH + "apporbitserver.key") or not os.path.isfile(
                    AO_KEYPATH + "apporbitserver.crt"):
            print "1) Use existing certificate"
            print "2) Create a self-signed certificate"
            ssltype = raw_input(
                "Enter the type of ssl certificate [Default:2]:") or 2
            if ssltype == 2:
                # Generate SSL Certiticate for https and
                # put it in a volume mount controller location.
                command = '''
openssl req -new -newkey rsa:4096 -days 365 -nodes -x509\
 -subj "/C=US/ST=NY/L=appOrbit/O=Dis/CN=www.apporbit.com"\
 -keyout /opt/apporbit/key/apporbitserver.key\
 -out /opt/apporbit/key/apporbitserver.crt'''
                return_code, out, err = self.utility_obj.cmdExecute(
                    command, "Generate SSL key and Certificate",
                    bexit=True, show=True)
            else:
                print "Rename your certificate files as apporbitserver.crt\
 and key as apporbitserver.key"
                sslkeydir = raw_input(
                    "Enter the location where certificate and key file exist:")
                if not os.path.exists(sslkeydir):
                    print "Dir does not exist, Exiting..."
                    sys.exit(1)

                os.chdir(sslkeydir)
                if not os.path.isfile(
                        "apporbitserver.key") or not os.path.isfile(
                            "apporbitserver.crt"):
                    print '''Key and certificate files are missing.
Note that key and crt file name should be apporbitserver.key
and apporbitserver.crt. Rename your files accordingly and retry.'''
                    sys.exit(1)
                src = os.getcwd()
                dest = self.config_obj.APPORBIT_KEY
                shutil.copyfile(
                    src + "/apporbitserver.key", dest + "/apporbitserver.key")
                shutil.copyfile(
                    src + "/apporbitserver.crt", dest + "/apporbitserver.crt")

    def clean_setup_maybe(self):
        opt = raw_input("Do you want to clean up the setup y/[n] ?") or 'n'
        if str(opt).lower() in ['y', 'yes']:
            clean_setup = 1
        else:
            clean_setup = 2

        if clean_setup == 1:
            cmd_list = ['rm -rf ' + self.config_obj.APPORBIT_DATA,
                        'rm -rf ' + self.config_obj.APPORBIT_LOG,
                        'rm -rf ' + self.config_obj.APPORBIT_HOME]
            command = " && ".join(cmd_list)
            return_code, out, err = self.utility_obj.cmdExecute(
                command, "", bexit=True, show=True)
            self.config_obj.upgrade = False
        else:
            self.config_obj.upgrade = True
        containers = ['controller', 'services',
                      'rmq', 'consul', 'locator', 'svcd', 'captain']
        datas = ['mysql', 'sshKey_root', 'sslkeystore', 'consul', 'locator',
                 'services', 'chefconf', 'chef-server', 'controller/ui']
        log_dirs = [self.config_obj.APPORBIT_LOG + "/" + d for d in containers]
        data_dirs = [self.config_obj.APPORBIT_DATA + "/" + d for d in datas]
        bin_dir = [self.config_obj.APPORBIT_BIN]
        conf_dir = [self.config_obj.APPORBIT_CONF]
        key_dir = [self.config_obj.APPORBIT_KEY]

        directories = log_dirs + data_dirs + bin_dir + conf_dir + key_dir

        print "Creating Directories"
        for dirs in directories:
            self.makedirs(dirs)
            command = "chcon -Rt svirt_sandbox_file_t " + dirs
            self.utility_obj.cmdExecute(command, "", bexit=True, show=True)

        apporbit_ini = self.config_obj.APPORBIT_CONF + '/apporbit.ini'
        command = ('''\
touch -a "{apporbit_ini}" && \
chcon -Rt svirt_sandbox_file_t {apporbit_ini}''')
        command = command.format(apporbit_ini=apporbit_ini)
        self.utility_obj.cmdExecute(command, "", bexit=True, show=True)

    def load_containers(self):
        rf = resourcefetcher.ResourceFetcher()
        containers = rf.apporbit_images.values()
        path = self.EXTRACTED_PACKAGES
        for container in containers:
            self.docker_obj.docker_load(
                path + container.replace("/", "-") + '.tar')

        containers = rf.apporbit_apps.values()
        for container in containers:
            self.docker_obj.docker_load(
                path + container.replace("/", "-") + '.tar')
        self.docker_obj.docker_tag(
            rf.apporbit_apps, "apporbit/",
            self.internal_docker_reg + '/')
        self.docker_obj.docker_push(
            rf.apporbit_apps, self.internal_docker_reg + '/')

        containers = rf.hub_images.values()
        for container in containers:
            self.docker_obj.docker_load(
                path + container.replace("/", "-") + ".tar")
        self.docker_obj.docker_tag(
            rf.hub_images, "", self.internal_docker_reg + '/')
        self.docker_obj.docker_push(
            rf.hub_images, self.internal_docker_reg + '/')

    def start_services(self):
        content = Template('''
# The first two sections are mandatory
[Registry Setup]
apporbit_registry =
username =
password =
apporbit_repo = http://${repohost}:9291/repos
datasvc_registry =${repohost}:5000

[System Setup]
apporbit_host = ${hostip}
apporbit_domain =
consul_host = ${hostip}
chef_host = ${hostip}

[Deployment Setup]
remove_data = False
apporbit_deploy = all
deploy_chef = True
deploy_consul = True
build_id = latest
self_signed_crt = 1
self_signed_crt_dir =
chef_ssl_crt = 0
chef_ssl_crt_dir =
deploy_mode = onprem
volume_mount =
systemreqs = False

[Software Setup]
apporbit_loginid = ${email}
themename = apporbit-v2
api_version = v2
''')

        try:
            flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
            install_tmp = os.open("install.tmp", flags)
        except OSError as e:
            if e.errno == errno.EEXIST:
                pass
            else:
                raise
        else:
            with os.fdopen(install_tmp, 'w') as file_obj:
                content = content.safe_substitute(
                    hostip=self.host,
                    repohost=self.repohost,
                    email=self.emailid,
                )
                file_obj.write(content)
                file_obj.close()

        config_obj = config.Config()
        config_obj.loadConfig("install.tmp")
        config_obj.offline_mode = "true"
        os.remove("install.tmp")
        config_obj.createComposeFile(self.utility_obj)
        shutil.copyfile(
            self.CWD + 'docker-compose',
            config_obj.APPORBIT_BIN + '/docker-compose')
        self.utility_obj.cmdExecute(
            "chmod a+x " + config_obj.APPORBIT_BIN + '/docker-compose',
            "", bexit=True, show=False)
        self.action_obj.removeCompose(config_obj, True)
        self.action_obj.deployCompose(config_obj, True)
        print "Apporbit server is deployed"
        print "Now login to the appOrbit server using"
        print "Login: " + self.emailid
        print "and default password 'admin1234'"
        logging.info("END OF DEPLOYMENT")

    def check_offline_repo(self):
        t = 12
        while not self.check_repo_status():
            if t <= 0:
                print "WARNING : Offline repo not reachable, please restart"\
                    " the offline and apporbit-controller containers"\
                    " after installation completes"
            time.sleep(15)
            t -= 1
        print "Offline repo reachable"

    def deploy_apporbit(self):
        print "Checking Platform Compatibility"
        self.verifyOS()

        print "Internal apporbit repo details"
        self.get_internal_apporibit_repo_uri()

        print "Setup internal apporbit repo"
        self.setup_internal_apporbit_repo()

        print "Set enforce Selinux"
        if not self.action_obj.set_selinux(self.utility_obj):
            sys.exit(1)

        print "Install docker"
        self.install_docker()

        print "Set Iptables"
        self.set_iptables()

        print "Uncompressing resources"
        self.uncompress_resources()

        print "Clean setup details"
        self.clean_setup_maybe()

        print "Get host ip"
        self.get_host_ip()

        print "Add chef port to firewall"
        self.add_chef_port_to_firewall()

        print "Set config info"
        self.set_config_info()

        print "Setup log rotate"
        self.setup_logrotate()

        print "Generate SSL certificates"
        self.generate_ssl_certs()

        if self.repohost != self.host:
            print "Setting docker daemon for insecure registry"
            self.docker_obj.setup_docker_daemon_insecure_reg(
                self.utility_obj, self.internal_docker_reg)

        print "Waiting for offline repo to come up"
        self.check_offline_repo()

        print "Loading images"
        self.load_containers()

        print "Starting services"
        self.start_services()
