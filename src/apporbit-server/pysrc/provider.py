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
		self.docker_obj = docker.Docker()
		self.CWD = os.getcwd() + "/"
		self.AO_DOWNLOADS_PATH = ""
		self.AO_RESOURCE_PATH =""
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
		self.AO_DOWNLOADS_PATH = raw_input("Enter the path of the downloaded archive [Default: " + path + "]: ") or path
		self.AO_RESOURCE_PATH = raw_input("Enter the path for extracting resources [Default: /tmp]: ") or "/tmp/"
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
		command = "tar -xvf " + self.AO_DOWNLOADS_PATH + " -C " + self.AO_RESOURCE_PATH + " && "\
				+ "tar -xvf " + self.AO_RESOURCE_PATH +"appOrbitRPMs.tar.gz && "\
				+ "tar -xvf " + self.AO_RESOURCE_PATH +"appOrbitGems.tar.gz"

		return_code, out, err = self.utility_obj.cmdExecute(command, " Uncompressing resources", show=True)
		if not return_code:
			print "Uncompress Failed :- " + err
			return False

	def setup_local_apporbit_repo(self):
		if not os.path.isfile("/etc/yum.repos.d/apporbit-local.repo"):
			content = Template('''
[apporbit-local]
name=appOrbit Repository
baseurl=file://${AO_RESOURCE_PATH}appOrbitRPMs
enabled=1
gpgcheck=0
''')

			try:
				flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
				ao_repo_file = os.open("/etc/yum.repos.d/apporbit-local.repo",flags)
			except OSError as e:
				if e.errno == errno.EEXIST:
				   pass
				else:
				   raise
			else:
				with os.fdopen(ao_repo_file, 'w' ) as file_obj:
					content = content.safe_substitute(
						AO_RESOURCE_PATH = self.AO_RESOURCE_PATH,
					)
					file_obj.write(content)
					file_obj.close()

	def install_docker(self):
		self.docker_obj.install_docker(self.utility_obj, enablerepo = True)

	def load_containers(self):
		self.docker_obj.docker_load(self.AO_RESOURCE_PATH + "apporbit-offline.tar")
		self.docker_obj.docker_load(self.AO_RESOURCE_PATH + "registry.tar")

	def run_offline_containers(self):
		print "Starting apporbit-offline service..."
		vol_map = {
			self.AO_RESOURCE_PATH + "appOrbitGems":"/opt/rubygems/",
			self.AO_RESOURCE_PATH + "appOrbitRPMs":"/opt/repos/"
		}
		self.docker_obj.docker_run("apporbit-offline", "apporbit/apporbit-offline", vol_map, "-d --restart=always -p 9291:9291 -p 9292:9292", True)

	def run_registry_container(self):
		print "Starting apporbit-registry service..."
		self.makedirs(self.AO_RESOURCE_PATH + "registry-data")
		vol_map = {
			self.AO_RESOURCE_PATH + "registry-data":"/var/lib/registry"
		}
		self.docker_obj.docker_run("apporbit-registry", "registry:2", vol_map, "-d -p 5000:5000 --restart=always", True)

	def get_host_ip(self):
		self.host = raw_input("Enter IP of this host: ")
		self.docker_registry_url = self.host + ":5000"

	def setup_docker_daemon_insecure_reg(self):
		docker_config_path = "/etc/sysconfig/docker"
		flag = False
		for line in fileinput.input(docker_config_path, inplace=True):
			if re.compile(r'^INSECURE_REGISTRY.*').match(line):
				flag = True
			line = re.sub(r'^INSECURE_REGISTRY.*',"INSECURE_REGISTRY='--insecure-registry " + self.docker_registry_url + "'", line.rstrip())
			print line

		if not flag:
			with open(docker_config_path, "a") as myfile:
				myfile.write("INSECURE_REGISTRY='--insecure-registry " + self.docker_registry_url + "'")
		self.utility_obj.cmdExecute("systemctl restart docker.service","", False)

	def load_infra_containers(self):
		for k,v in self.resource_fetcher.infra_containers.iteritems():
			self.docker_obj.docker_load(self.AO_RESOURCE_PATH + "infra_images/" + k + ".tar")

	def tag_push_infra_containers(self):
		print "Waiting for registry container to come up.."
		while urllib2.urlopen("http://" + self.docker_registry_url + "/v2/").getcode() != 200:
			print "."
			time.sleep(5)

		print "Tagging infra containers..."
		#for k,v in self.resource_fetcher.infra_containers.iteritems():
		self.docker_obj.docker_tag(self.resource_fetcher.infra_containers, "google_containers/", self.docker_registry_url + "/google_containers/")
		self.docker_obj.docker_push(self.resource_fetcher.infra_containers, self.docker_registry_url + "/google_containers/")

	def tag_push_apporbit_apps(self):
		print "Tagging apporbit apps..."
		self.docker_obj.docker_tag(self.resource_fetcher.apporbit_apps, "apporbit-apps.apporbit.io:5000/", self.docker_registry_url + "/")
		self.docker_obj.docker_push(self.resource_fetcher.apporbit_apps, self.docker_registry_url + "/")

	def set_selinux(self):
		print "Setting sestatus to permissive"
		cmd_sesettings = "setenforce 0"
		return_code, out, err = self.utility_obj.cmdExecute(cmd_sesettings, "Setenforce to permissive", True)
		if not return_code:
			print "Error setting selinux :- " + err
			return False

	def show_setup_information(self):
		print "/n/n"
		print "################################################################################"
		print "Note down following information for further provisioning."
		print
		print "INTERNAL REGISTRY URL: %s" % (self.docker_registry_url)
		print "PROVIDER IP: %s" % (self.host)
		print
		print "################################################################################"

	def setup_provider(self):

		self.get_resources_package_tar_path()

		if not os.path.isfile(self.AO_DOWNLOADS_PATH):
			print "File not found or unreadable. Exiting.."
			sys.exit(1)
			
		print "Checking Platform Compatibility"
		self.verifyOS()

		self.get_host_ip()
		self.set_selinux()
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
		self.setup_docker_daemon_insecure_reg()

		print "Load Infra containers"
		self.load_infra_containers()

		print "Tag and push infra containers"
		self.tag_push_infra_containers()

		self.show_setup_information()
