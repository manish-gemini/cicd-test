from string import Template
import os
import sys
import time
import errno
import urllib2
import logging
import docker_ao
import utility
import action
import resourcefetcher


class Provider:

    def __init__(self):
        self.action_obj = action.Action()
        self.utility_obj = utility.Utility()
        self.docker_obj = docker_ao.DockerAO()
        self.CWD = os.getcwd() + "/"
        self.APPORBIT_COMPOSE = self.CWD + "docker-compose"
        self.DEFAULT_EXTRACT_PATH = "/var/apporbit-offline/"
        self.AO_DOWNLOADS_PATH = ""
        self.AO_RESOURCE_PATH = ""
        self.resource_fetcher = resourcefetcher.ResourceFetcher()
        self.compose_file = "provider-compose.yml"
        self.docker_registry_url = ""
        self.host = ""

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
        self.makedirs(self.DEFAULT_EXTRACT_PATH)
        self.AO_RESOURCE_PATH = raw_input(
            "Enter the path for extracting resources [Default: " +
                self.DEFAULT_EXTRACT_PATH + "]: "
        ) or self.DEFAULT_EXTRACT_PATH
        if not os.path.isdir(self.AO_RESOURCE_PATH):
            print "Invalid path : " + self.AO_RESOURCE_PATH
            sys.exit(1)
        if not self.AO_RESOURCE_PATH.endswith('/'):
            self.AO_RESOURCE_PATH += '/'
        self.compose_file = self.AO_RESOURCE_PATH + "provider-compose.yml"

    def verifyOS(self):
        self.utility_obj.cmdExecute("yum makecache", "", show=True)
        self.utility_obj.verifyOSRequirement()

    def uncompress_resources(self):
        self.makedirs(self.AO_RESOURCE_PATH)
        cwd = os.getcwd()
        os.chdir(self.AO_RESOURCE_PATH)
        command =\
            "tar -xvf " + self.AO_DOWNLOADS_PATH + " -C " +\
            self.AO_RESOURCE_PATH + " && " +\
            "tar -xvf " + self.AO_RESOURCE_PATH + "appOrbitRPMs.tar.gz && " +\
            "tar -xvf " + self.AO_RESOURCE_PATH + "appOrbitGems.tar.gz"

        return_code, out, err = self.utility_obj.cmdExecute(
            command, " Uncompressing resources", bexit=True, show=False)
        os.chdir(cwd)

    def setup_local_apporbit_repo(self):
        if not os.path.isfile("/etc/yum.repos.d/apporbit-local.repo"):
            content = Template('''
[apporbit-local]
name=appOrbit Repository
baseurl=file://${AO_RESOURCE_PATH}appOrbitRPMs
enabled=1
gpgcheck=0
''').safe_substitute(AO_RESOURCE_PATH=self.AO_RESOURCE_PATH)

            try:
                with open("/etc/yum.repos.d/apporbit-local.repo", "w") as f:
                    f.write(content)
            except OSError as e:
                logging.info("Couldn't create apporbit-local repo. Exiting")
                logging.error(e)
                print "Couldn't create apporbit-local repo, check logs for details"
                sys.exit(1)

    def install_docker(self):
        self.docker_obj.install_docker(self.utility_obj, enablerepo=True)

    def load_containers(self):
        self.docker_obj.docker_load(
            self.AO_RESOURCE_PATH + "apporbit-offline.tar")
        self.docker_obj.docker_load(self.AO_RESOURCE_PATH + "registry.tar")

    def create_compose_file(self):
        content = ('''

version: "2"
services:


  apporbit-offline:
    container_name: apporbit-offline
    image: apporbit/apporbit-offline
    restart: always
    network_mode: "bridge"
    ports:
      - "9291:9291"
      - "9292:9292"
    volumes:
      - {AO_RESOURCE_PATH}appOrbitGems:/opt/rubygems/:Z
      - {AO_RESOURCE_PATH}appOrbitRPMs:/opt/repos/:Z

  apporbit-registry:
    container_name: apporbit-registry
    image: registry:2
    restart: always
    network_mode: "bridge"
    ports:
      - "5000:5000"
    mem_limit: 2100000000
    volumes:
      - {AO_RESOURCE_PATH}registry-data:/var/lib/registry:Z
        ''').format(AO_RESOURCE_PATH=self.AO_RESOURCE_PATH)

        try:
            with open(self.compose_file, "w") as f:
                f.write(content)
        except OSError as e:
            logging.info("Couldn't create offline compose file")
            logging.error(e)
            print "Couldn't create offline compose file, check logs"
            sys.exit(1)

    def run_offline_containers(self):
        print "Creating compose file for registry and offline container"
        self.create_compose_file()
        print "Starting apporbit-offline and registry service..."
        self.makedirs(self.AO_RESOURCE_PATH + "registry-data")
        command = 'COMPOSE_HTTP_TIMEOUT=300 ' + self.APPORBIT_COMPOSE +\
            ' -f ' + self.compose_file + ' down'
        self.utility_obj.cmdExecute(command, "", bexit=True, show=True)
        time.sleep(5)
        command = 'COMPOSE_HTTP_TIMEOUT=300 ' + self.APPORBIT_COMPOSE +\
            ' -f ' + self.compose_file + ' up -d'
        self.utility_obj.cmdExecute(command, "", bexit=True, show=True)

    def get_host_ip(self):
        self.host = raw_input("Enter IP of this host: ")
        self.docker_registry_url = self.host + ":5000"

    def load_infra_containers(self):
        for k, v in self.resource_fetcher.infra_containers.iteritems():
            self.docker_obj.docker_load(
                self.AO_RESOURCE_PATH + "infra_images/" + v.replace("/", "-") + ".tar")

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
            self.resource_fetcher.apps_insecure_reg + "/",
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

        print "Checking platform compatibility"
        self.verifyOS()

        self.get_host_ip()

        self.action_obj.set_selinux(self.utility_obj)

        print "Uncompressing resources"
        self.uncompress_resources()

        print "Set up local apporbit repo"
        self.setup_local_apporbit_repo()

        print "Install docker"
        self.install_docker()

        print "Loading offline and registry containers"
        self.load_containers()

        print "Set docker daemon for insecure registry"
        self.docker_obj.setup_docker_daemon_insecure_reg(
            self.utility_obj, self.docker_registry_url)

        print "Run offline and registry container"
        self.run_offline_containers()

        print "Load Infra containers"
        self.load_infra_containers()

        print "Tag and push infra containers"
        self.tag_push_infra_containers()

        self.show_setup_information()
