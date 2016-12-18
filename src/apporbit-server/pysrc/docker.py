from distutils.version import LooseVersion
import os
import re
import sys
import time
import utility
import fileinput

class DockerAO:
    def __init__(self):
        self.utility_obj = utility.Utility()
        self.do_dockerinstall = 0
        self.remove_olddocker = 0
        self.docker_version = "1.11.2"
        self.do_sesettings = 0

    def install_docker(self, utility_obj, enablerepo=False):
        print "Verifying docker installation"
        self.do_sesettings = 1
        docker_cmd = "docker -v"
        return_code, out, err = self.utility_obj.cmdExecute(
            docker_cmd, "Docker Install", show=False)
        docker_ver = LooseVersion(self.docker_version)
        if return_code and out:
            docker_installed = LooseVersion(out.split()[2].split(',')[0])
            if docker_installed < docker_ver:
                opt = raw_input("Do you want to upgrade with docker-" +
                                self.docker_version + " [y]/n ?") or "y"
                if str(opt).lower() in ['y', 'yes']:
                    self.do_dockerinstall = 1
                    self.remove_olddocker = 1
                    print "Older docker " + str(out)
                    print "Upgrading docker to " + self.docker_version
                else:
                    sys.exit(1)
            else:
                print "Docker installed : " + str(out.split()[2].split(',')[0])

        elif not return_code:
            opt = raw_input("Do you want to install docker-" +
                            self.docker_version + " [y]/n ?") or "y"
            if str(opt).lower() in ['y', 'yes']:
                self.do_dockerinstall = 1
                print "Installing docker " + self.docker_version
            else:
                sys.exit(1)
        elif out:
            docker_installed = LooseVersion(out.split()[2].split(',')[0])
            if docker_installed < docker_ver:
                opt = raw_input("Do you want to upgrade with docker-" +
                                self.docker_version + " [y]/n ?") or "y"
                if str(opt).lower() in ['y', 'yes']:
                    self.do_dockerinstall = 1
                    self.remove_olddocker = 1
                    print "Older docker " + str(out)
                    print "Upgrading docker to " + self.docker_version
                else:
                    sys.exit(1)
        else:
            print "Apporbit supports minimum docker version  " +\
                self.docker_version
            print "FAILED - Installation failed due to docker version conflict"
            sys.exit(1)

        # BUG: https://bugzilla.redhat.com/show_bug.cgi?id=1294128
        if enablerepo:
            cmd_upgradelvm = 'yum -y --disablerepo="*" ' +\
                '--enablerepo="apporbit-local" upgrade lvm2'
        else:
            cmd_upgradelvm = 'yum -y upgrade lvm2'
        return_code, out, err = self.utility_obj.cmdExecute(
            cmd_upgradelvm, "lvm upgrade", show=True)
        if not return_code:
            if not self.redhat_subscription:
                print "FAILED- Red Hat is not having a valid subscription. " +\
                    "Get a valid subscription and retry installation."
            return False

        if self.do_dockerinstall:
            if self.remove_olddocker:
                print 'Removing older version of docker'
                cmd_dockerremove =\
                    "yum remove -y docker docker-selinux docker-common"
                return_code, out, err = self.utility_obj.cmdExecute(
                    cmd_dockerremove, "Docker Remove older version if present",
                    show=True
                )
                if not return_code:
                    return False
            elif "centos" in utility_obj.osname:
                cmd_update = "yum -y update"
                return_code, out, err = self.utility_obj.cmdExecute(
                    cmd_update, " yum update", True)
                if not return_code:
                    return False

            print 'Installing docker version %s' % self.docker_version
            if enablerepo:
                cmd_dockerInstall = 'yum install -y --disablerepo="*" ' +\
                    '--enablerepo="apporbit-local" docker-engine-' +\
                    self.docker_version
            else:
                cmd_dockerInstall = 'yum install -y docker-engine-' +\
                     self.docker_version
            return_code, out, err = self.utility_obj.cmdExecute(
                cmd_dockerInstall, "Docker Install", show=True)
            if not return_code:
                return False

        if self.do_sesettings:
            cmd_sesettings = "setenforce 0"
            return_code, out, err = self.utility_obj.cmdExecute(
                cmd_sesettings, "Setenforce to permissive", show=False)
            if not return_code:
                return False

        if os.path.isfile('/etc/sysconfig/docker'):
            dockerConfig = '/etc/sysconfig/docker'
        elif os.path.isfile('/etc/default/docker'):
            dockerConfig = '/etc/default/docker'
        else:
            dockerConfig = None
        if dockerConfig and 'log-driver=journald' in open(dockerConfig).read():
            cmd_docker_daemon_flag =\
                 "sed -i 's/log-driver=journald/log-driver=json-file/'  " +\
                 dockerConfig
            self.utility_obj.cmdExecute(
                cmd_docker_daemon_flag,
                "Enabled docker daemon --log-driver flag with json-file ",
                show=False)

        cmd_dockerservice = "systemctl enable docker.service"
        self.utility_obj.cmdExecute(
                cmd_dockerservice,
                "Enable Docker service on restart", show=False)

        cmd_dockerservice = "systemctl start docker.service"
        return_code, out, err = self.utility_obj.cmdExecute(
            cmd_dockerservice, " Docker service start", show=False)
        if not return_code:
            print "Docker not started :- " + str(out)
            return False

    def docker_pull(self, images, registry=""):
        for k, v in images.iteritems():
            print "Downloading image " + k
            cmd_pull = "docker pull " + registry + v
            return_code, out, err = self.utility_obj.cmdExecute(
                cmd_pull, " Docker pull " + k, show=False)
            if not return_code:
                print "Image " + v + " download failed :- " + str(out)
            time.sleep(1)

    def docker_push(self, images, registry=""):
        for k, v in images.iteritems():
            print "Pushing " + k
            cmd_push = "docker push " + registry + v
            print cmd_push
            return_code, out, err = self.utility_obj.cmdExecute(
                cmd_push, " Docker push " + k, show=False)
            if not return_code:
                print "Docker push failed :- " + str(out)

    def docker_tag(self, images, registry, new_registry):
        for k, v in images.iteritems():
            cmd_tag = "docker tag " + registry + v + " " + new_registry + v
            print cmd_tag
            return_code, out, err = self.utility_obj.cmdExecute(
                cmd_tag, " Docker tag " + k, show=False)
            if not return_code:
                print "Docker tag failed :- " + str(out)

    def docker_save(self, images, directory, registry=""):
        cwd = os.getcwd()
        os.chdir(directory)
        for k, v in images.iteritems():
            print "Saving " + k
            cmd_save = "docker save " + registry + v + " > " + v.replace("/", "-") + ".tar"
            return_code, out, err = self.utility_obj.cmdExecute(
                cmd_save, " Docker save " + k, show=False)
            if not return_code:
                print "Docker save failed :- " + str(out)
        os.chdir(cwd)

    def docker_build(self, dockerfile_directory, dockerfile, image):
        cwd = os.getcwd()
        os.chdir(dockerfile_directory)
        print "Building " + image + " container"
        cmd_build_offline_container =\
            "docker build -t " + image + " -f " + dockerfile + " ."
        return_code, out, err = self.utility_obj.cmdExecute(
            cmd_build_offline_container, "", show=True)
        if not return_code:
            print "Error in building container :- " + str(out)
        os.chdir(cwd)

    def docker_load(self, path_of_image_tar):
        print "loading " +\
            os.path.splitext(os.path.basename(path_of_image_tar))[0]
        cmd_load = "docker load < " + path_of_image_tar
        return_code, out, err = self.utility_obj.cmdExecute(cmd_load, "", True)
        if not return_code:
            print "Error in loading image :- " + str(out)
            return False
        return True

    def docker_run(
            self,
            name_of_container,
            image,
            vol_map,
            otherFlag="",
            removeContainerIfExists=False):
        cmd_run = "docker run " + otherFlags + " --name " + name_of_container
        for k, v in vol_map.iteritems():
            cmd_run += " -v " + k + ":" + v
        cmd_run += " " + image

        if removeContainerIfExists:
            cmd = "docker ps -a | grep " + image
            return_code, out, err = self.utility_obj.cmdExecute(
                cmd, "", show=True)
            if out:
                print "Container " + name_of_container +\
                     " is already runnning. The container will removed first."
                return_code, out, err = self.utility_obj.cmdExecute(
                    "docker rm -f " + name_of_container, "", show=True)
                if not return_code:
                    print "Container not removed."
                    return

        return_code, out, err = self.utility_obj.cmdExecute(
            cmd_run, "", show=True)
        if not return_code:
            print "Error in running container :- " + str(out)
        return True

    def setup_docker_daemon_insecure_reg(self, docker_reg):
        docker_config_path = "/etc/sysconfig/docker"
        regex_find = r'^INSECURE_REGISTRY.*'
        regex_replace = "INSECURE_REGISTRY='--insecure-registry " +\
            docker_reg + "'"
        if self.docker_version == "1.11.2":
            docker_config_path = "/usr/lib/systemd/system/docker.service"
            regex_find = "ExecStart=.*docker daemon -H fd://.*"
            regex_append = ' --insecure-registry ' + docker_reg

        flag = False
        for line in fileinput.input(docker_config_path, inplace=True):
            if re.compile(regex_find).match(line):
                flag = True
                if 'regex_append' in locals():
                    if docker_reg not in line:
                        line = line.rstrip() + regex_append
                else:
                    line = re.sub(regex_find, regex_replace, line.rstrip())
            print line.rstrip()

        if not flag and 'regex_append' not in locals():
            with open(docker_config_path, "a") as myfile:
                myfile.write(regex_replace)
        elif not flag:
            print "Docker not configured, check file " + docker_config_path
            sys.exit(1)
        self.utility_obj.cmdExecute(
            "systemctl daemon-reload && systemctl restart docker.service",
            "", False
        )
