import logging
import sys
import errno
import os
import socket
import shutil
import getpass
from ConfigParser import SafeConfigParser, ParsingError

import utility
import docker_ao
import config
import action


class ResourceFetcher:

    def __init__(self):
        self.docker_obj = docker_ao.DockerAO()
        self.utility_obj = utility.Utility()
        self.config_obj = config.Config()
        self.action_obj = action.Action()
        self.internal_registry = ""
        self.reposync_file = 'reposync.conf'
        self.apporbit_repo = "http://repos.gsintlab.com/"
        self.ao_noarch = self.apporbit_repo + "release/noarch/"
        self.mist_url = self.apporbit_repo + "release/mist/master/run.jar"
        self.chef_url = self.apporbit_repo +\
            "1.5.1/chef-12.6.0-1.el7.x86_64.rpm"
        self.CWD = os.getcwd() + "/"

        self.PACKAGESDIR = self.CWD + "appOrbitPackages/"
        self.INFRADIR = self.CWD + "infra_images/"
        self.RPMSDIR = self.CWD + "appOrbitRPMs/"
        self.GEMDIR = self.CWD + "appOrbitGems/"
        self.NOARCHDIR = self.RPMSDIR + "noarch/"
        self.NOARCH507DIR = self.NOARCHDIR + "5.0.7/"
        self.MIST = self.RPMSDIR + "mist/"
        self.MISTMASTER = self.MIST + "master/"
        self.vmImportUrl = "http://repos.gsintlab.com/release/images/AO-PROXY.ova"
        self.VMIMPORT = self.RPMSDIR + "vmsvc/"

        self.AO_RESOURCE_TAR = 'appOrbitResources.tar'
        self.AO_PACKAGES_TAR = 'appOrbitPackages.tar.gz'
        self.AO_GEMS_TAR = 'appOrbitGems.tar.gz'
        self.AO_RPMS_TAR = 'appOrbitRPMs.tar.gz'

        self.apporbit_apps = {
            'moneyball-exports': 'moneyball-exports',
            'moneyball-api': 'moneyball-api',
            'moneyball-router': 'moneyball-router',
            'grafana-app': 'apporbit-grafana-app',
            'prometheus-app': 'apporbit-prometheus-app',
            'swagger-ui': 'apporbit-swagger-ui',
            'hypervisor': 'hypervisor',
            'vmsvc/vdiskimport': 'vmsvc/vdiskimport',
            'vmsvc/vdiskproxy': 'vmsvc/vdiskproxy'
        }

        self.support_packages = {
            self.ao_noarch + "nginx-1.6.3.tar.gz": self.NOARCHDIR,
            self.ao_noarch + "passenger-5.0.10.tar.gz": self.NOARCHDIR,
            self.ao_noarch + "5.0.7/agent-x86_64-linux.tar.gz":
                self.NOARCH507DIR,
            self.ao_noarch + "5.0.7/nginx-1.6.3-x86_64-linux.tar.gz":
                self.NOARCH507DIR,
            self.chef_url: self.RPMSDIR,
            self.mist_url: self.MISTMASTER,
            self.vmImportUrl: self.VMIMPORT
        }

        self.apps_insecure_reg = "apporbit-apps.apporbit.io:5000"

        self.hub_images = {
            'centos': 'centos:centos7.0.1406',
            'mysql': 'mysql:5.6.24',
            'registry': 'registry:2',
            'cadvisor': 'google/cadvisor:v0.23.2',
            'node-exporter': 'prom/node-exporter:0.12.0',
            'postgres': 'postgres',
            'redis': 'redis'
        }

        self.apporbit_images = {
            'apporbit-services': 'apporbit-services',
            'apporbit-controller': 'apporbit-controller',
            'apporbit-rmq': 'apporbit-rmq',
            'apporbit-docs': 'apporbit-docs',
            'apporbit-chef': 'apporbit-chef:2.0',
            'apporbit-consul': 'consul',
            'apporbit-locator': 'locator',
            'apporbit-svcd': 'svcd',
            'apporbit-captain': 'captain'
        }

        self.infra_containers = {
            'dnsmasq': 'dnsmasq:1.1',
            'kubedns': 'kubedns-amd64:1.5',
            'exechealthz': 'exechealthz-amd64:1.0',
            'kubernetes-dashboard': 'kubernetes-dashboard-amd64:v1.1.0',
            'pause': 'pause-amd64:3.0'
        }

    def makedirs(self, path):
        try:
            logging.info("Creating " + path)
            os.makedirs(path)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                logging.error(path + " creation failed")
                sys.exit(1)

    def make_dirs(self):
        if hasattr(sys, '_MEIPASS'):
            os.chdir(sys._MEIPASS)
            files = sys._MEIPASS + "/conf/* "
            copyCmd = "cp -rf " + files + self.CWD
            self.utility_obj.cmdExecute(copyCmd, "", False)

        dir_list = [self.INFRADIR,
                    self.NOARCH507DIR,
                    self.MISTMASTER,
                    self.RPMSDIR,
                    self.GEMDIR,
                    self.PACKAGESDIR,
                    self.VMIMPORT]

        for dirs in dir_list:
            self.makedirs(dirs)

    def clean_dirs(self):
        shutil.rmtree(self.RPMSDIR)
        shutil.rmtree(self.GEMDIR)
        shutil.rmtree(self.PACKAGESDIR)

    def check_internet(self):
        remote_servers = {
            "www.google.com": 80,
            "8.8.8.8": 53,
            "repos.gsintlab.com": 80
        }
        for server, port in remote_servers.iteritems():
            try:
                host = socket.gethostbyname(server)
                s = socket.create_connection((host, port), 2)
            except socket.timeout as e:
                logging.error("Unable to reach Internet, Exiting..")
                print "Unable to reach Internet, Exiting.."
                sys.exit(1)
            except socket.gaierror as e:
                logging.error("DNS resolution failed. Exiting : " + str(e))
                print "DNS resolution failed, check logs for details."
                sys.exit(1)
        logging.info("Internet Connectivity OK")
        print "Internet Connectivity OK"

    def verifyOS(self):
        self.utility_obj.verifyOSRequirement()

    def get_internal_registry(self):
        print "Enter url of registry(without https://)"
        self.internal_registry =\
            raw_input("Default(https://offline-registry.gsintlab.com): ")\
            or "offline-registry.gsintlab.com"

        print "Enter the url of registry for AO apps(without https://)"
        self.apps_insecure_reg =\
            raw_input("Default(https://" + self.apps_insecure_reg + "): ")\
            or self.apps_insecure_reg

    def install_docker_and_login(self):
        self.config_obj.createRepoFile()
        self.docker_obj.install_docker(self.utility_obj)
        uname = raw_input("User name[admin] : ") or "admin"
        pwd = getpass.getpass("Password : ")
        self.utility_obj.loginDockerRegistry(
            uname, pwd,
            self.internal_registry)
        print "Successfully logged in to Docker Registry: " +\
            self.internal_registry
        logging.info("Successfully logged in to Docker Registry: " +
                     self.internal_registry)

    def download_and_tag_images(self):

        self.docker_obj.docker_pull(self.hub_images)
        self.docker_obj.docker_pull(
            self.apporbit_images,
            self.internal_registry + "/apporbit/"
        )
        self.docker_obj.docker_tag(
            self.apporbit_images,
            self.internal_registry + "/apporbit/",
            "apporbit/"
        )

        self.docker_obj.docker_pull(
            self.infra_containers,
            "gcr.io/google_containers/"
        )
        self.docker_obj.docker_tag(
            self.infra_containers,
            "gcr.io/google_containers/",
            "google_containers/"
        )

        self.docker_obj.docker_pull(
            self.apporbit_apps,
            self.apps_insecure_reg + "/apporbit/"
        )

        self.docker_obj.docker_tag(
            self.apporbit_apps,
            self.apps_insecure_reg + "/apporbit/",
            "apporbit/"
        )

    def save_images_and_create_tar(self):
        logging.info("Saving images ")
        print "Saving images "
        self.docker_obj.docker_save(self.hub_images, self.PACKAGESDIR)
        self.docker_obj.docker_save(
            self.apporbit_images,
            self.PACKAGESDIR,
            "apporbit/"
        )
        self.docker_obj.docker_save(
            self.apporbit_apps,
            self.PACKAGESDIR,
            "apporbit/"
        )
        self.docker_obj.docker_save(
            self.infra_containers,
            self.INFRADIR,
            "google_containers/"
        )

        os.chdir(self.CWD)
        return_code, out, err = self.utility_obj.cmdExecute(
            "tar -czvf " + self.AO_PACKAGES_TAR + " appOrbitPackages",
            "Creating " + self.AO_PACKAGES_TAR, bexit=True, show=False
        )
        print "Apporbit images tar created successfully"

    def install_required_packages(self):
        packages = "yum-utils createrepo wget"
        return_code, out, err = self.utility_obj.cmdExecute(
            "yum install -y " + packages,
            " Installing " + packages, bexit=True, show=False
        )
        print packages + " installed successfully"

    def download_general_packages(self):
        os.chdir(self.NOARCHDIR)

        for source, destination in self.support_packages.iteritems():
            os.chdir(destination)
            base_cmd = "wget -c '"
            return_code, out, err = self.utility_obj.cmdExecute(
                base_cmd + source + "'", "", bexit=True, show=False
            )
            print source + " downloaded successfully"

    def centos_package_setup(self):
        os.chdir(self.CWD)
        if 'centos' in self.utility_obj.osname:
            logging.info('Configuring CentOS repos for syncing...')
            try:
                parser = SafeConfigParser()
                parser.read(self.reposync_file)
            except ParsingError, err:
                print 'Could not parse:', err
                logging.exception('Could not parse: ' + self.reposync_file)

            release = self.utility_obj.osversion
            # Other option is to write releasever in /etc/yum/vars/releasever
            parser.set('main', 'distroverpkg', release)
            parser.remove_option('base', 'mirrorlist')
            parser.remove_option('updates', 'mirrorlist')

            mirror_url = 'http://vault.centos.org'
            base_url = mirror_url + '/{rel}/os/$basearch/'.format(rel=release)
            parser.set('base', 'baseurl', base_url)
            update_url = mirror_url + '/{rel}/updates/$basearch/'.format(
                rel=release)
            parser.set('updates', 'baseurl', update_url)

            with open(self.reposync_file, 'wb') as configfile:
                parser.write(configfile)

    def rhel_package_setup(self):
        os.chdir(self.CWD)
        if "red hat" in self.utility_obj.osname:
            logging.info("Configuring RHEL repos for syncing...")
            sub_id = ""
            return_code, out, err = self.utility_obj.cmdExecute(
                "basename `ls /etc/pki/entitlement/*-key.pem |" +
                " head -1` | cut -d'-' -f1", "", bexit=True, show=True
            )
            if return_code:
                sub_id = out

            content = ('''

[rhel-7-server-rpms]
name=Red Hat Enterprise Linux 7 Server (RPMs)
baseurl='https://cdn.redhat.com/content/dist/rhel/server/7/$releasever/$basearch/os'
sslverify=0
sslclientkey=/etc/pki/entitlement/{sub_id}-key.pem
sslclientcert=/etc/pki/entitlement/{sub_id}.pem
gpgcheck=0
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release
includepkgs=
include=rhel-pkglist.conf
                ''').format(sub_id=sub_id)

            try:
                with open(self.reposync_file, 'a') as f:
                    f.write(content)
            except OSError as e:
                logging.info("Could not create/open reposync.conf. Exiting")
                logging.error(e)
                print "Could not create/open reposync.conf, " +\
                      "check logs for more details"
                sys.exit(1)

    def generate_rpm_packages(self):
        src = self.CWD
        file_list = ['reposync.conf',
                     'offline-pkglist.conf',
                     'updates-pkglist.conf',
                     'docker-pkglist.conf',
                     'rhel-pkglist.conf']

        for f in file_list:
            shutil.copyfile(src + f, self.RPMSDIR + f)

        os.chdir(self.RPMSDIR)
        return_code, out, err = self.utility_obj.cmdExecute(
            "reposync -c reposync.conf",
            "", bexit=True, show=True
        )

        for f in file_list:
            os.remove(self.RPMSDIR + f)

        self.utility_obj.cmdExecute("createrepo .", "", bexit=True, show=True)

        os.chdir(self.CWD)

        return_code, out, err = self.utility_obj.cmdExecute(
            "tar -cvzf " + self.AO_RPMS_TAR + " appOrbitRPMs",
            "", bexit=True, show=True)

    def build_offline_container(self):
        logging.info("Building apporbit offline container")
        self.docker_obj.docker_build(
            self.CWD + "Dockerfiles",
            "offline-container", "apporbit/apporbit-offline"
        )

    def download_generate_gems(self):
        logging.info("Downloading ruby gems")
        command = "docker run -v " + self.GEMDIR +\
            ":/opt/rubygems apporbit/apporbit-offline gem mirror"
        return_code, out, err = self.utility_obj.cmdExecute(
            command, "Downloading ruby gems", bexit=True, show=False)

        logging.info("Generating ruby gems")
        os.chdir(self.CWD)
        command = "tar -cvzf " + self.AO_GEMS_TAR + " appOrbitGems"
        return_code, out, err = self.utility_obj.cmdExecute(
            command, "", bexit=True, show=True)

    def save_containers(self):
        os.chdir(self.CWD)
        commands = [
            "docker save apporbit/apporbit-offline > apporbit-offline.tar",
            "docker save registry:2 > registry.tar"
        ]
        for command in commands:
            return_code, out, err = self.utility_obj.cmdExecute(
                command, "", bexit=True, show=True
            )
        logging.info("Saved apporbit-offline and registry containers")

    def finalizing_resources_and_packages(self):
        logging.info("Generating resource packages")
        resource_list = " ".join(["apporbit-offline.tar",
                                  "registry.tar",
                                  self.AO_RPMS_TAR,
                                  self.AO_GEMS_TAR,
                                  "infra_images"])

        tar_cmd = "tar -cvf"
        cmd = " ".join([tar_cmd, self.AO_RESOURCE_TAR, resource_list])
        return_code, out, err = self.utility_obj.cmdExecute(
            cmd, "", bexit=True, show=True)

        print "###############################################################"
        print
        print "Dependent resources of appOrbit successfully downloaded."
        print
        print "Transfer " + self.AO_RESOURCE_TAR + "to a system that will "
        print " act as resource provider for appOrbit Application and run"
        print " installer with --setupprovider."
        print
        print "Transfer " + self.AO_PACKAGES_TAR + " to apporbit host"
        print " and run installer with --deployoffline option."
        print
        print "###############################################################"

    def fetch_resources(self):
        print "Checking Internet Connectivity"
        self.check_internet()
        print "[OK]"

        print "Checking Platform Compatibility"
        self.verifyOS()
        print "[OK]"

        self.action_obj.set_selinux(self.utility_obj)

        self.get_internal_registry()

        print "Installing Docker"
        self.install_docker_and_login()
        print "[OK]"

        print "Setting docker daemon for insecure registry"
        self.docker_obj.setup_docker_daemon_insecure_reg(
            self.utility_obj, self.apps_insecure_reg)

        print "Making directories"
        self.make_dirs()

        print "Downloading Images"
        self.download_and_tag_images()

        print "Saving Images and generating tars"
        self.save_images_and_create_tar()

        print "Installing required packages"
        self.install_required_packages()

        print "Downloading compressed tar of RPMs"
        self.download_general_packages()

        self.centos_package_setup()
        self.rhel_package_setup()

        print "Generating compressed tar of RPMs"
        self.generate_rpm_packages()

        print "Building Offline Container Image"
        self.build_offline_container()

        print "Generating compressed tar of ruby gems"
        self.download_generate_gems()

        print "Saving Offline and registry Container Image"
        self.save_containers()

        print "Generating archives to transfer"
        self.finalizing_resources_and_packages()
