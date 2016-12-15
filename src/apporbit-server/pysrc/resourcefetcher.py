from string import Template
import sys
import errno
import os
import socket
import platform
import shutil
import getpass

import utility, docker, config

class ResourceFetcher:

    def __init__(self):
    	self.docker_obj = docker.Docker()
        self.utility_obj = utility.Utility()
        self.config_obj = config.Config()
        self.REMOTE_SERVER = "www.google.com"
        self.internal_registry = ""
        self.CWD = os.getcwd() + "/"

        self.PACKAGESDIR = self.CWD + "appOrbitPackages/"
        self.INFRADIR = self.CWD + "infra_images/"
        self.RPMSDIR = self.CWD + "appOrbitRPMs/"
        self.GEMDIR = self.CWD + "appOrbitGems/"
        self.NOARCHDIR = self.RPMSDIR + "noarch/"
        self.NOARCH507DIR = self.NOARCHDIR + "5.0.7/"
        self.MIST = self.RPMSDIR + "mist/"
        self.MISTMASTER = self.MIST + "master/"

	self.apporbit_apps = {'moneyball-exports':'moneyball-exports', 'moneyball-api':'moneyball-api', 'moneyball-router':'moneyball-router', 'apporbit/apporbit-grafana-app':'apporbit/apporbit-grafana-app', 'apporbit/apporbit-prometheus-app':'apporbit/apporbit-prometheus-app'}

        self.hub_images = {'centos':'centos:centos7.0.1406','mysql':'mysql:5.6.24','registry':'registry:2','google/cadvisor:v0.23.2':'google/cadvisor:v0.23.2','prom/node-exporter:0.12.0':'prom/node-exporter:0.12.0'}

        self.apporbit_images = {'services':'apporbit-services',
                'controller':'apporbit-controller',
                'rmq':'apporbit-rmq',
                'docs':'apporbit-docs',
                'chef':'apporbit-chef:2.0',
                'consul':'consul',
                'locator':'locator',
                'svcd':'svcd',
                'captain':'captain'}

        self.infra_containers = {'dnsmasq:1.1':'dnsmasq:1.1',
        		'kubedns-amd64:1.5':'kubedns-amd64:1.5',
        		'exechealthz-amd64:1.0':'exechealthz-amd64:1.0',
        		'kubernetes-dashboard-amd64:v1.1.0':'kubernetes-dashboard-amd64:v1.1.0',
        		'pause-amd64:3.0':'pause-amd64:3.0'}

    def makedirs(self, path):
        try:
            print "Creating " + path
            os.makedirs(path)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise

    def make_dirs(self):
        self.makedirs(self.INFRADIR)
        self.makedirs(self.NOARCH507DIR)
        self.makedirs(self.MISTMASTER)
        self.makedirs(self.RPMSDIR)
        self.makedirs(self.GEMDIR)
	self.makedirs(self.PACKAGESDIR)
    
    def clean_dirs(self):
	shutil.rmtree(self.RPMSDIR)
	shutil.rmtree(self.GEMDIR)
	shutil.rmtree(self.PACKAGESDIR)

    def check_internet(self):
	REMOTE_SERVER = "www.google.com"
        try:
            host = socket.gethostbyname(REMOTE_SERVER)
            s= socket.create_connection((host,80),2)

            host = socket.gethostbyname("8.8.8.8")
            #s = socket.create_connection((host,80),2)
	    print "Internet Connectivity OK"
            return True
        except:
            pass
	print "Not connected to internet. Exiting."
        sys.exit(1)

    def verifyOS(self):
        self.utility_obj.verifyOSRequirement()

    def get_internal_registry(self):
        print "Enter url of registry(without https://)"
        self.internal_registry = raw_input("Default(https://offline-registry.gsintlab.com): ") or "offline-registry.gsintlab.com"

    def install_docker_and_login(self):
        self.config_obj.createRepoFile()
        self.docker_obj.install_docker(self.utility_obj)
	uname = raw_input("User name[admin] : ") or "admin"
	pwd = getpass.getpass("Password : ")
	self.utility_obj.loginDockerRegistry(uname, pwd, self.internal_registry)
	print "Docker login successfull to https://" + self.internal_registry

    def setup_docker_daemon_insecure_reg(self, docker_reg):
                docker_config_path = "/etc/sysconfig/docker"
                flag = False
                for line in fileinput.input(docker_config_path, inplace=True):
                        if re.compile(r'^INSECURE_REGISTRY.*').match(line):
                                flag = True
                        line = re.sub(r'^INSECURE_REGISTRY.*',"INSECURE_REGISTRY='--insecure-registry " + docker_reg + "'", line.rstrip())
                        print line

                if not flag:
                        with open(docker_config_path, "a") as myfile:
                                myfile.write("INSECURE_REGISTRY='--insecure-registry " + docker_reg + "'")
                self.utility_obj.cmdExecute("systemctl restart docker.service","", False)

    def download_and_tag_images(self):

        self.docker_obj.docker_pull(self.hub_images)
        self.docker_obj.docker_pull(self.apporbit_images, self.internal_registry + "/apporbit/")
        self.docker_obj.docker_tag(self.apporbit_images, self.internal_registry + "/apporbit/", "apporbit/")

        self.docker_obj.docker_pull(self.infra_containers, "gcr.io/google_containers/")
        self.docker_obj.docker_tag(self.infra_containers, "gcr.io/google_containers/", "google_containers/")

	self.docker_obj.docker_pull(self.apporbit_apps, "apporbit-apps.apporbit.io:5000/")


    def save_images_and_create_tar(self):
	print "Saving images "
    	self.docker_obj.docker_save(self.hub_images, self.PACKAGESDIR)
    	self.docker_obj.docker_save(self.apporbit_images, self.PACKAGESDIR, "apporbit/")
    	self.docker_obj.docker_save(self.infra_containers, self.INFRADIR, "google_containers/")

        os.chdir(self.CWD)
        return_code, out, err = self.utility_obj.cmdExecute("tar -czvf appOrbitPackages.tar.gz appOrbitPackages", " Creating appOrbitPAckages.tar.gz", show=False)
        if not return_code:
            print "appOrbitPackages.tar.gz creation failed :- " + str(err)
            sys.exit(1)
	print "Apporbit images tar created successfully"

    def install_required_packages(self):
        packages = "yum-utils createrepo wget"
        return_code, out, err = self.utility_obj.cmdExecute("yum install -y " + packages, " Installing " + packages, False)
        if not return_code:
            print packages + " installation Failed :- " + str(err)
            sys.exit(1)
	print packages + " installed successfully"

    def download_general_packages(self):
        os.chdir(self.NOARCHDIR)
        repo="http://repos.gsintlab.com/release"
        base_cmd = "wget -c '" + repo + "/noarch/"
        return_code, out, err = self.utility_obj.cmdExecute(base_cmd + "nginx-1.6.3.tar.gz'", " Downloading Nginx package", show=False)
        if not return_code:
            print "Nginx download Failed :- " + str(err)
            sys.exit(1)
	print "Nginx downloaded successfully"

        return_code, out, err = self.utility_obj.cmdExecute(base_cmd + "passenger-5.0.10.tar.gz'", " Downloading Passenger package", show=False)
        if not return_code:
            print "Download Failed :- " + str(err)
            return False

        print "Downloading Passenger agent"

        os.chdir(self.NOARCH507DIR)
        base_cmd = base_cmd + "5.0.7/"

        return_code, out, err = self.utility_obj.cmdExecute(base_cmd + "agent-x86_64-linux.tar.gz'", " Downloading agent package", show=False)
        if not return_code:
            print "Download Failed :- " + str(err)
            return False

        return_code, out, err = self.utility_obj.cmdExecute("wget -c 'https://s3.amazonaws.com/phusion-passenger/binaries/passenger/by_release/5.0.7/nginx-1.6.3-x86_64-linux.tar.gz'", " Downloading aws_nginx package", show=False)
        if not return_code:
            print "Download Failed :- " + str(err)
            return False

        print "Downloading mist jar"

        os.chdir(self.MISTMASTER)
        base_cmd = "wget -c '" + repo + "/mist/master/run.jar'"
        return_code, out, err = self.utility_obj.cmdExecute(base_cmd, " Downloading mist jar", show=False)
        if not return_code:
            print "Download Failed :- " + str(err)
            return False

    def rhel_package_setup(self):
        os.chdir(self.CWD)
        if "red hat" in self.utility_obj.osname:
            print "Configuring RHEL repos for syncing..."
            sub_id = ""
            return_code, out, err = self.utility_obj.cmdExecute("basename `ls /etc/pki/entitlement/*-key.pem | head -1` | cut -d'-' -f1", "", False)
            if return_code:
                sub_id = out

            content = Template('''

[rhel-7-server-rpms]
name=Red Hat Enterprise Linux 7 Server (RPMs)
baseurl='https://cdn.redhat.com/content/dist/rhel/server/7/$releasever/$basearch/os'
sslverify=0
sslclientkey=/etc/pki/entitlement/${sub_id}-key.pem
sslclientcert=/etc/pki/entitlement/${sub_id}.pem
gpgcheck=0
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release
includepkgs=
include=rhel-pkglist.conf
                ''')
	    print sub_id

            try:
                flags = os.O_WRONLY | os.O_APPEND
                reposync_file = os.open("reposync.conf",flags)
            except OSError as e:
                if e.errno == errno.EEXIST:
                   pass
                else:
                   raise
            else:
                with os.fdopen(reposync_file, 'a' ) as file_obj:
                    content = content.safe_substitute(
                        sub_id = sub_id,
                    )
                    file_obj.write(content)
                    file_obj.close()


    def generate_rpm_packages(self):
        src = os.getcwd()

        shutil.copyfile(src + "/reposync.conf", self.RPMSDIR + "reposync.conf")
        shutil.copyfile(src + "/offline-pkglist.conf", self.RPMSDIR + "offline-pkglist.conf")
        shutil.copyfile(src + "/updates-pkglist.conf", self.RPMSDIR + "updates-pkglist.conf")
        shutil.copyfile(src + "/docker-pkglist.conf", self.RPMSDIR + "docker-pkglist.conf")
        shutil.copyfile(src + "/rhel-pkglist.conf", self.RPMSDIR + "rhel-pkglist.conf")

	os.chdir(self.RPMSDIR)
        return_code, out, err = self.utility_obj.cmdExecute("reposync -c reposync.conf", "", show=True)
        if not return_code:
            print "Error in running reposync :- " + str(err)
            return False

 	os.remove(self.RPMSDIR + "offline-pkglist.conf")
	os.remove(self.RPMSDIR + "updates-pkglist.conf")
	os.remove(self.RPMSDIR + "docker-pkglist.conf")
	os.remove(self.RPMSDIR + "rhel-pkglist.conf")
        self.utility_obj.cmdExecute("wget -c 'https://opscode-omnibus-packages.s3.amazonaws.com/el/7/x86_64/chef-12.6.0-1.el7.x86_64.rpm'", "", show=False)
        self.utility_obj.cmdExecute("createrepo .", "Creating Repo.... ", show=True)

        os.chdir(self.CWD)
        
        return_code, out, err = self.utility_obj.cmdExecute("tar -cvzf appOrbitRPMs.tar.gz appOrbitRPMs", "Creating appOrbitRPMs.tar", show=True)
        if not return_code:
            print "Error in creating RPMs :- " + str(err)
            return False

    def build_offline_container(self):
    	print "Building apporbit offline container"
    	self.docker_obj.docker_build(self.CWD + "Dockerfiles", "offline-container", "apporbit/apporbit-offline")

    def set_selinux(self):
        print "Setting sestatus to permissive"
        cmd_sesettings = "setenforce 0"
        return_code, out, err = self.utility_obj.cmdExecute(cmd_sesettings, "Setenforce to permissive", False)
        if not return_code:
            print "Error setting selinux :- " + str(err)
            return False

    def download_generate_gems(self):
        print "Downloading ruby gems"
        command = "docker run -v " + self.GEMDIR + ":/opt/rubygems apporbit/apporbit-offline gem mirror"
        return_code, out, err = self.utility_obj.cmdExecute(command, "Downloading ruby gems", show=False)
        if not return_code:
            print "Error downloading ruby gems :- " + str(err)
            return False

        print "Generating ruby gems"
        os.chdir(self.CWD)
        command = "tar -cvzf appOrbitGems.tar.gz appOrbitGems"
        return_code, out, err = self.utility_obj.cmdExecute(command, "", show=True)
        if not return_code:
            print "Error creating appOrbitGems.tar :- " + str(err)
            return False

    def save_containers(self):
        os.chdir(self.CWD)
        commands = ["docker save apporbit/apporbit-offline > apporbit-offline.tar", "docker save registry:2 > registry.tar"]
        for command in commands:
            return_code, out, err = self.utility_obj.cmdExecute(command, "", show=True)
            if not return_code:
                print "Error in saving containers :- " + str(err)
                return False
	print "Saved apporbit-offline and registry containers"

    def finalizing_resources_and_packages(self):
	print "finalizing the tars"
        tars = ["tar -cvf appOrbitResources.tar apporbit-offline.tar registry.tar appOrbitRPMs.tar.gz appOrbitGems.tar.gz infra_images"]
        for tar in tars:
            return_code, out, err = self.utility_obj.cmdExecute(tar, "", show=True)
            if not return_code:
                print "Error in saving containers :- " + str(err)
                return False

        print "Dependent resources of appOrbit successfully downoaded and saved."

    def fetch_resources(self):
        print "Checking Internet Connectivity"
        self.check_internet()
        print "[OK]"

        print "Checking Platform Compatibility"
        self.verifyOS()
        print "[OK]"

        self.set_selinux()
        self.get_internal_registry()

        print "Installing Docker"
        self.install_docker_and_login()
        print "[OK]"

	print "Setting docker daemon for insecure registry"
	self.setup_docker_daemon_insecure_reg("apporbit-apps.gsintlab.com:5000")

        print "Making directories"
        self.make_dirs()

        print "Downloading Images"
        self.download_and_tag_images()

        print "Saving Images and generating tars"
        self.save_images_and_create_tar()

        print "Installing utils"
        self.install_required_packages()

        print "Downloading compressed tar of RPMs"
        self.download_general_packages()

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
