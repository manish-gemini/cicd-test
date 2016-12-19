from string import Template
import re
import fileinput
import os
import docker
import sys
import errno
import urllib2
import utility
import resourcefetcher


class Provider:

    def __init__(self):
        self.utility_obj = utility.Utility()
        self.docker_obj = docker.DockerAO()
        self.CWD = os.getcwd() + "/"
        self.AO_DOWNLOADS_PATH = ""
        self.AO_RESOURCE_PATH = ""
        self.resource_fetcher = resourcefetcher.ResourceFetcher()

    def makedirs(self, path):
        try:
            os.makedirs(path)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise

    def get_resources_package_tar_path(self):
        path = self.CWD + "appOrbitResources.tar"
        self.AO_DOWNLOADS_PATH = raw_input(
            "Enter the path of the downloaded archive[Default: " + path + "]: "
        ) or path
        self.AO_RESOURCE_PATH = raw_input(
            "Enter the path for extracting resources [Default: /tmp]: "
        ) or "/tmp/"
        if not os.path.isdir(self.AO_RESOURCE_PATH):
            print "Invalid path : " + self.AO_RESOURCE_PATH
            sys.exit(1)
        if not self.AO_RESOURCE_PATH.endswith('/'):
            self.AO_RESOURCE_PATH += '/'

    def verifyOS(self):
        self.utility_obj.verifyOSRequirement()

    def uncompress_resources(self):
        self.makedirs(self.AO_RESOURCE_PATH)
        os.chdir(self.AO_RESOURCE_PATH)
        command =\
            "tar -xvf " + self.AO_DOWNLOADS_PATH + " -C " +\
            self.AO_RESOURCE_PATH + " && " +\
            "tar -xvf " + self.AO_RESOURCE_PATH + "appOrbitRPMs.tar.gz && " +\
            "tar -xvf " + self.AO_RESOURCE_PATH + "appOrbitGems.tar.gz"

        return_code, out, err = self.utility_obj.cmdExecute(
            command, " Uncompressing resources", bexit=True, show=True)

    def setup_local_apporbit_repo(self):
        if not os.path.isfile("/etc/yum.repos.d/apporbit-local.repo"):
            content = Template('''
[apporbit-local]
name=appOrbit Repository
baseurl=file://${AO_RESOURCE_PATH}appOrbitRPMs
enabled=1
gpgcheck=0
''').safe_substitue(AO_RESOURCE_PATH=self.AO_RESOURCE_PATH)

        try:
            with open("/etc/yum.repos.d/apporbit-local.repo", "w") as f:
                f.write(content)
        except OSError as e:
            logging.info("Could not create apporbit-local repo. Exitting")
            print "Could not create apporbit-local repo, check logs"
            sys.exit(1)

    def install_docker(self):
        self.docker_obj.install_docker(self.utility_obj, enablerepo=True)

    def load_containers(self):
        self.docker_obj.docker_load(
            self.AO_RESOURCE_PATH + "apporbit-offline.tar")
        self.docker_obj.docker_load(self.AO_RESOURCE_PATH + "registry.tar")

    def run_offline_containers(self):
        print "Starting apporbit-offline service..."
        vol_map = {
            self.AO_RESOURCE_PATH + "appOrbitGems": "/opt/rubygems/",
            self.AO_RESOURCE_PATH + "appOrbitRPMs": "/opt/repos/"
        }
        self.docker_obj.docker_run(
            "apporbit-offline", "apporbit/apporbit-offline",
            vol_map, "-d --restart=always -p 9291:9291 -p 9292:9292", True)

    def run_registry_container(self):
        print "Starting apporbit-registry service..."
        self.makedirs(self.AO_RESOURCE_PATH + "registry-data")
        vol_map = {
            self.AO_RESOURCE_PATH + "registry-data": "/var/lib/registry"
        }
        self.docker_obj.docker_run(
            "apporbit-registry", "registry:2",
            vol_map, "-d -p 5000:5000 --restart=always", True)

    def get_host_ip(self):
        self.host = raw_input("Enter IP of this host: ")
        self.docker_registry_url = self.host + ":5000"

    def load_infra_containers(self):
        for k, v in self.resource_fetcher.infra_containers.iteritems():
            self.docker_obj.docker_load(
                self.AO_RESOURCE_PATH + "infra_images/" + k + ".tar")

    def tag_push_infra_containers(self):
        print "Waiting for registry container to come up.."
        docker_reg_url = "http://" + self.docker_registry_url + "/v2/"
        code = urllib2.urlopen(docker_reg_url).getcode()
        while code != 200:
            code = urllib2.urlopen(docker_reg_url).getcode()
            print "."
            time.sleep(5)

        print "Tagging infra containers..."
        # for k,v in self.resource_fetcher.infra_containers.iteritems():
        self.docker_obj.docker_tag(
            self.resource_fetcher.infra_containers,
            "google_containers/",
            self.docker_registry_url + "/google_containers/")
        self.docker_obj.docker_push(
            self.resource_fetcher.infra_containers,
            self.docker_registry_url + "/google_containers/")

    def tag_push_apporbit_apps(self):
        print "Tagging apporbit apps..."
        self.docker_obj.docker_tag(
            self.resource_fetcher.apporbit_apps,
            "apporbit-apps.apporbit.io:5000/",
            self.docker_registry_url + "/"
        )
        self.docker_obj.docker_push(
            self.resource_fetcher.apporbit_apps,
            self.docker_registry_url + "/")

    def show_setup_information(self):
        content = Template('''


##############################################################"
Note down following information for further provisioning."

INTERNAL REGISTRY URL : ${docker_registry_url}
PROVIDER IP: ${host}

##############################################################"
''')

        content = content.safe_substitute(
            docker_registry_url=self.docker_registry_url,
            host=self.host,
        )
        print content

    def setup_provider(self):

        self.get_resources_package_tar_path()

        if not os.path.isfile(self.AO_DOWNLOADS_PATH):
            print "File not found or unreadable. Exiting.."
            sys.exit(1)

        print "Checking Platform Compatibility"
        self.verifyOS()

        self.get_host_ip()

        if not self.action_obj.set_selinux(utility_obj):
            print "Set enforce linux failed, check logs, Exitting"
            sys.exit(1)

        print "Uncompressing resources"
        self.uncompress_resources()

        print "set up local apporbit repo"
        self.setup_local_apporbit_repo()

        print "Install docker"
        self.install_docker()

        print "loading offline and registry containers"
        self.load_containers()

        print "Run offline container"
        self.run_offline_containers()

        print "Run Registry container"
        self.run_registry_container()

        print "set docker daemon for insecure registry"
        self.docker_obj.setup_docker_daemon_insecure_reg(
            self.docker_registry_url)

        print "Load Infra containers"
        self.load_infra_containers()

        print "Tag and push infra containers"
        self.tag_push_infra_containers()

        self.show_setup_information()
