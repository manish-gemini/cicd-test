from string import Template
import errno
import os
import docker
import shutil
import urllib
import sys

import config
import utility
import resourcefetcher
import action


class OfflineDeploy(object):
    """docstring for OfflineDeploy"""
    def __init__(self):
        self.action_obj = action.Action()
        self.utility_obj = utility.Utility()
        self.docker_obj = docker.DockerAO()
        self.CWD = os.getcwd() + "/"
        self.host = ""
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
        self.utility_obj.verifyOSRequirement()

    def get_internal_apporibit_repo_uri(self):
        self.repohost = raw_input("Enter IP of internal repo host : ")
        self.internal_repo = "http://" + self.repohost + ":9291/repos"
        self.internal_gems_repo = "http://" + self.repohost + ":9292"
        self.internal_docker_reg = self.reposhost + ":5000"

        print self.internal_repo
        try:
            if urllib.urlopen(self.internal_repo).getcode() == 200:
                print "Verified connection with the repos... OK"
            else:
                print "Unable to connect repositories. Check Network settings\
                     and enable connection to " + self.internal_repo
                sys.exit(1)
        except Exception as exc:
            print "Internal repo not hosted.\
                Please run apporbit-server --setupprovider"
            sys.exit(1)

    def setup_internal_apporbit_repo(self):
        content = Template('''''')
        if not os.path.isfile("/etc/yum.repos.d/apporbit-offline.repo"):
            content = Template('''
[apporbit-offline]
name=appOrbit Repository
baseurl=${internal_repo}
enabled=1
gpgcheck=0
''')

        try:
            flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
            ao_repo_file = os.open(
                "/etc/yum.repos.d/apporbit-offline.repo", flags)
        except OSError as e:
            if e.errno == errno.EEXIST:
                pass
            else:
                raise
        else:
            with os.fdopen(ao_repo_file, 'w') as file_obj:
                content = content.safe_substitute(
                    internal_repo=self.internal_repo,
                )
                file_obj.write(content)
                file_obj.close()

    def set_selinux(self):
        print "Setting sestatus to permissive"
        cmd_sesettings = "setenforce 0"
        return_code, out, err = self.utility_obj.cmdExecute(
            cmd_sesettings, "Setenforce to permissive", False)
        if not return_code:
            print "Error setting selinux :- " + str(err)
            return False
        return True

    def setup_ntp(self):
        print "Time will be synchronized with time.nist.gov for this host"
        command = "yum install -y ntp && ntpdate -b -u time.nist.gov"
        return_code, out, err = self.utility_obj.cmdExecute(
            command, "", show=True)
        if not return_code:
            return False
        return True

    def install_docker(self):
        self.docker_obj.install_docker(self.utility_obj, enablerepo=True)

    def set_iptables(self):
        print "Setting up iptables rules..."
        command = "iptables -D INPUT -j REJECT --reject-with \
icmp-host-prohibited && iptables -D  FORWARD -j \
REJECT --reject-with icmp-host-prohibited"
        return_code, out, err = self.utility_obj.cmdExecute(
            command, "", show=True)
        if not return_code:
            return False
        return True

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
            command, " Untar appOrbitPackages.tar.gz", show=True)
        if not return_code:
            print "Untar appOrbitPackages.tar.gz failed :- " + str(err)
            sys.exit(1)
        return True

    def add_chef_port_to_firewall(self):
        if os.path.isfile("/usr/bin/firewall-cmd"):
            print "Adding port " + str(self.chef_port) + " to firewall..."
            command = "firewall-cmd --permanent --add-port=" +\
                str(self.chef_port) + "/tcp"
            return_code, out, err = self.utility_obj.cmdExecute(
                command, "", show=True)
            if not return_code:
                print "Chef port not added to firewall :- " + str(err)
        print "Saving Iptables"
        return_code, out, err = self.utility_obj.cmdExecute(
            "/sbin/service iptables save", "", show=True)

    def set_config_info(self):
        emailid = "admin@apporbit.com"
        onPremMode = True

        self.emailid = raw_input(
            "Enter the User Email id for On Prem Deployment. Default(" +
            emailid + "):") or emailid
        offline_mode = "true"

    def setup_logrotate(self):
        if not os.path.isfile("/etc/logrotate.d/apporbitLogRotate"):
            command = '''echo "/var/log/apporbit/controller/*log /var/log/apporbit/services/*log {
          daily
          missingok
          size 50M
          rotate 20
          compress
          copytruncate
        }" > /etc/logrotate.d/apporbitLogRotate'''
            return_code, out, err = self.utility_obj.cmdExecute(
                command, "", show=True)
            if not return_code:
                print "logrotate setup failed :- " + str(err)
                return False
            return True

    def get_host_ip(self):
        self.host = raw_input("Enter the Host IP: ")
        if self.host == "":
            print "Host IP is Mandatory.. Exiting.."
            return False
        return True

    def generate_ssl_certs(self):
        if not os.path.isfile(
                "/opt/apporbit/key/apporbitserver.key") or not os.path.isfile(
                "/opt/apporbit/key/apporbitserver.crt"):
            print "1) use existing certificate"
            print "2) Create a self signed certificate"
            ssltype = raw_input(
                "Enter the type of ssl certificate [Default:2]:") or 2
            if ssltype == 2:
                # Generate SSL Certiticate for https and
                # put it in a volume mount controller location.
                command = 'openssl req -new -newkey rsa:4096 -days 365 ' +\
                    '-nodes -x509 -subj "/C=US/ST=NY/L=appOrbit/O=Dis/' +\
                    'CN=www.apporbit.com"' +\
                    ' -keyout /opt/apporbit/key/apporbitserver.key ' +\
                    '-out /opt/apporbit/key/apporbitserver.crt'
                return_code, out, err = self.utility_obj.cmdExecute(
                    command, "", show=True)
                if not return_code:
                    print "Openssl certificate generation failed."
                    return False
                return True
            else:
                print "Rename your certificate files as apporbitserver.crt\
 and key as apporbitserver.key"
                sslkeydir = raw_input(
                    "Enter the location where certificate and key file exist:")
                if not os.path.exists(sslkeydir):
                    print "Dir does not exist, Exiting..."
                    return False

                os.chdir(sslkeydir)
                if not os.path.isfile(
                        "apporbitserver.key") or not os.path.isfile(
                        "apporbitserver.crt"):
                    print "key and certificate files are missing."
                    print "Note that key and crt file name should be apporbitserver.key \
and apporbitserver.crt. Rename your files accordingly and retry."
                    return False
                src = os.getcwd()
                dest = "/opt/apporbit/key/"
                shutil.copyfile(
                    src + "apporbitserver.key", dest + "apporbitserver.key")
                shutil.copyfile(
                    src + "apporbitserver.crt", dest + "apporbitserver.crt")

    def clean_setup_maybe(self):
        print "Do you want to clean up the setup (removes db, Rabbitmq etc.)?"
        print "press 1 to clean the setup."
        print "press 2 to retain the older entries.."
        cleanSetup = raw_input("Default(2):") or 2

        if cleanSetup == 1:
            command = 'rm -rf "/var/lib/apporbit/" && \
rm -rf "/var/log/apporbit/" && rm -rf "/opt/apporbit/"'
            return_code, out, err = self.utility_obj.cmdExecute(
                command, "", show=True)
            self.chef_upgrade = 1
        else:
            self.chef_upgrade = 2

        directories = [
            "/var/lib/apporbit/mysql",
            "/var/log/apporbit/controller",
            "/var/log/apporbit/services",
            "/var/log/apporbit/rmq",
            "/var/log/apporbit/consul",
            "/var/log/apporbit/locator",
            "/var/log/apporbit/svcd",
            "/var/log/apporbit/captain",
            "/var/lib/apporbit/sshKey_root",
            "/var/lib/apporbit/sslkeystore",
            "/var/lib/apporbit/consul",
            "/var/lib/apporbit/locator",
            "/var/lib/apporbit/services",
            "/var/lib/apporbit/chefconf",
            "/var/lib/apporbit/chef-server",
            "var/lib/apporbit/controller/ui",
            "/opt/apporbit/bin",
            "/opt/apporbit/conf",
            "/opt/apporbit/key"
        ]

        print "Creating Directories"
        for dirs in directories:
            self.makedirs(dirs)
            command = "chcon -Rt svirt_sandbox_file_t " + dirs
            self.utility_obj.cmdExecute(command, "", show=True)

        command = 'touch -a "/opt/apporbit/conf/apporbit.ini" && ' +\
            'chcon -Rt svirt_sandbox_file_t /opt/apporbit/conf/apporbit.ini'
        self.utility_obj.cmdExecute(command, "", show=True)

    def remove_conflicting_containers(self):
        rf = resourcefetcher.ResourceFetcher()
        containers = rf.apporbit_images.values()
        for container in containers:
            cmd = "docker ps -a | grep " + container
            return_code, out, err = self.utility_obj.cmdExecute(
                cmd, "", show=True)
            if out:
                print "Container " + container +\
                     " is already runnning. The container will removed first."
                return_code, out, err = self.utility_obj.cmdExecute(
                    "docker rm -f " + container, "", show=True)
                if not return_code:
                    print "Container not removed."
                    return

    def setup_docker_daemon_insecure_reg(self):
        docker_config_path = "/etc/sysconfig/docker"
        flag = False
        insecure_reg = "INSECURE_REGISTRY='--insecure-registry " +\
            self.internal_docker_reg + "'"
        for line in fileinput.input(docker_config_path, inplace=True):
            if re.compile(r'^INSECURE_REGISTRY.*').match(line):
                flag = True
            line = re.sub(
                r'^INSECURE_REGISTRY.*',
                insecure_reg, line.rstrip())
            print line

        if not flag:
            with open(docker_config_path, "a") as myfile:
                myfile.write(insecure_reg)
        self.utility_obj.cmdExecute(
            "systemctl restart docker.service", "", False)

    def load_containers(self):
        rf = resourcefetcher.ResourceFetcher()
        containers = rf.apporbit_images.values()
        path = self.EXTRACTED_PACKAGES
        for container in containers:
            self.docker_obj.docker_load(path + container + '.tar')

        containers = rf.hub_images.values()
        for container in containers:
            self.docker_obj.docker_load(path + container + ".tar")
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
        if self.chef_upgrade == 2:
            config_obj.upgrade = True
        config_obj.offline_mode = offline_mode
        os.remove("install.tmp")
        config_obj.createComposeFile(self.utility_obj)
        shutil.copyfile(
            self.CWD + 'docker-compose',
            config_obj.APPORBIT_BIN + '/docker-compose')
        self.utility_obj.cmdExecute(
            "chmod a+x " + config_obj.APPORBIT_BIN + '/docker-compose',
            "", True)
        self.action_obj.removeCompose(config_obj, True)
        self.action_obj.deployCompose(config_obj, True)
        print "Apporbit server is deployed"

    def deploy_apporbit(self):
        print "Checking Platform Compatibility"
        self.verifyOS()

        print "Internal apporbit repo details"
        self.get_internal_apporibit_repo_uri()

        print "Setup internal apporbit repo"
        self.setup_internal_apporbit_repo()

        print "Set enforce Selinux"
        self.set_selinux()

        print "Install docker"
        self.install_docker()

        print "Set Iptables"
        self.set_iptables()

        print "Uncompressing resources"
        self.uncompress_resources()
        # self.remove_conflicting_containers()

        print "Clean setup details"
        self.clean_setup_maybe()

        print "Get host ip"
        if not self.get_host_ip():
            sys.exit(1)

        print "Add chef port to firewall"
        # self.deploy_chef()
        self.add_chef_port_to_firewall()

        print "Set config info"
        self.set_config_info()
        # self.set_passenger_config()

        print "Setup log rotate"
        self.setup_logrotate()

        print "Generate SSL certificates"
        self.generate_ssl_certs()

        print "Setting docker daemon for insecure registry"
        self.setup_docker_daemon_insecure_reg()

        print "loading images"
        self.load_containers()

        print "Starting services"
        self.start_services()
