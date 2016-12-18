#!/usr/bin/env python

import multiprocessing
import exceptions
import re
import subprocess
import httplib
import logging
import os
import os.path
import shutil
import ConfigParser
import sys
import platform
import threading
import urllib2
import socket
import traceback
from io import StringIO
from time import sleep
from distutils.version import LooseVersion

# Implementation of DotProgress class
class DotProgress(threading.Thread):
    def __init__(self, msg):
        threading.Thread.__init__(self)
        self.msg = msg
        self.event = threading.Event()
    def __enter__(self):
        self.start()
    def __exit__(self, ex_type, ex_value, ex_traceback):
        self.event.set()
        self.join()
    def run(self):
        #sys.stdout.write(self.msg)
        while not self.event.isSet():
            sys.stdout.write(".")
            sys.stdout.flush()
            sleep(15)
            self.event.wait(1)


class Utility:

    def __init__(self):
        self.do_dockerinstall = 0
        self.remove_olddocker = 0
        self.docker_version = "1.11.2"
        self.do_ntpinstall = 0
        self.do_bindutilsinstall = 0
        self.do_wgetinstall = 0
        self.do_sesettings = 1
        self.redhat_subscription = True
        return


    def cmdExecute(self, cmd_str, cmd_desc = '', bexit = False, show = False, sensitive = False):
        try:
            if not sensitive:
                logging.debug("CMD: %s",  cmd_str)
            result = []
            process = subprocess.Popen(cmd_str, bufsize=4096, shell=True, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
            err =  process.stderr
            while True:
                line = process.stdout.readline()
                if not line: 
                    break
                else:
                    line = line.rstrip()
                    result.append(line)
                    if not sensitive:
                        logging.debug(line)
                    if show:
                        print line
            while process.poll() == None:
                    sleep(1)
            out = '\n'.join(result)
            if process.returncode == 0:
                logging.info("Success - %s",cmd_desc)
            else:
                if bexit :
                    logging.error("FAILED - %s [ %s ]", cmd_desc, cmd_str)
                    logging.error("OUTPUT: %d %s %s", process.returncode, out, err)
                    print "FAILED - " + cmd_desc + "[" + cmd_str + "]"
                    print process.returncode, err
                    print "Check log for details."
                    sys.exit(1)
                else:
                    logging.warning("FAILED - %s [ %s ]", cmd_desc, cmd_str)
                    logging.warning("OUTPUT: %d %s %s", process.returncode, out, err)
                    return False, out, err
        except Exception as exp:
            out = '\n'.join(result)
            if bexit :
                    logging.error("FAILED - %s [ %s  ]", cmd_desc, cmd_str)
                    logging.error(" FAILED ERR: %s %s", out, err)
                    print "[FAILED] - " + cmd_desc + "[" + cmd_str + "]"
                    print str(exp)
                    print "Check log for details."
                    sys.exit(1)
            else:
                    logging.warning("FAILED - %s [ %s  ]", cmd_desc, cmd_str)
                    logging.warning(" FAILED ERR: %s %s", out, err)
                    logging.warning(" Exception %s", exp)
                    print "[FAILED] - " + cmd_desc + "[" + cmd_str + "]"
                    print str(exp)
                    print "Check log for details."
                    return False, out, err

        return True, out, err


    # Progress Bar Implementation
    def progressBar(self, i):
        sys.stdout.write('\r')
        # the exact output you're looking for:
        sys.stdout.write("[%-20s] %d%%" % ('='*i, 5*i))
        sys.stdout.flush()
        sleep(0.25)


    #Check if this Machine already runs apporbit management servers .
    def isFreshInstall(self):
        ret_val = True
        cmd_dockerps = "docker ps -a "
        cmd_desc = "Docker ps"
        code, out, err = self.cmdExecute(cmd_dockerps, cmd_desc, True)
        if "apporbit-controller" in out or "apporbit-services" in out:
            logging.info("Not Fresh Install")
            ret_val = False
        return ret_val

    #Check if this Machine already runs apporbit-chef container.
    def isChefDeployed(self):
        ret_val = False
        cmd_dockerps = "docker ps"
        cmd_desc = "Docker ps"
        code, out, err = self.cmdExecute(cmd_dockerps, cmd_desc, True)
        if "apporbit-chef" in out:
            logging.info("Chef server is deployed in this host")
            ret_val = True
        return ret_val

    def isConsulDeployed(self):
        ret_val = False
        cmd_dockerps = "docker ps"
        cmd_desc = "Docker ps"
        code, out, err = self.cmdExecute(cmd_dockerps, cmd_desc, True)
        if "apporbit-consul" in out:
            logging.info("Consul server is deployed in this host")
            ret_val = True
        return ret_val

    def isPreviousInstallSuccess(self):
        ret_val = True
        if os.path.isfile("install.tmp"):
            logging.info("Previous Installation Failed or Interrupted.")
            ret_val = False
        return  ret_val

    #Remove Temp file.
    def removeTempFile(self):
        if os.path.isfile("install.tmp"):
            os.remove("install.tmp")
            logging.info("Removed tmp file created during installation.")
        return True

    # Create Temp file
    def loadTempFile(self,config_obj):
        logging.debug("Checking install.tmp if it exists")
        if os.path.isfile("install.tmp"):
            config_obj.loadConfig("install.tmp")
            logging.debug("Loading install.tmp config")
        return True

    # Create Temp file
    def createTempFile(self,config_obj):
        config_obj.createConfigFile("install.tmp")
        return True

    #Create logRotate File

    def createLogRoatateFile(self):
        if not os.path.isfile("/etc/logrotate.d/apporbitLogRotate"):
            str_to_write = "/var/log/apporbit/controller/*log /var/log/apporbit/services/*log { \n \
            daily \n \
            missingok \n \
            size 50M \n \
            rotate 20 \n \
            compress \n \
            copytruncate \n \
            }"
            fileobj = open("/etc/logrotate.d/apporbitLogRotate", "w")
            fileobj.write(str_to_write)
            fileobj.close()

        return True



    #Docker Login
    def loginDockerRegistry(self, uname, passwd, repo_str = "registry.apporbit.com" ):
        # print "Login to Docker Registry " + repo_str
        if passwd:
            cmd_str = 'docker login -u=' + uname + ' -p=' + passwd +' '+ repo_str
            self.cmdExecute(cmd_str, "Docker login ", True, sensitive=True)
        else:
            logging.error("Docker Login Failed ")
            print 'Docker login -[Failed!]'
            sys.exit(1)

        return True

    # Check for System Information if it satisfy all Pre Deploy Requirements
    # If not fixable errors found exit the process and log the errors.
    def verifySystemInfo(self):
        logging.info("Hardware Requirement Check   -STARTED")
        self.progressBar(1)
        if not self.verifyHardwareRequirement():
            logging.error("Hardware requirements are not satisfied !")
            print "ERROR : Hardware requirement verification failed! Check log for details."
            sys.exit(1)
        logging.info("Hardware Requirement Check   -COMPLETED")
        self.progressBar(2)

        logging.info("Software Requirement Check   -STARTED")
        if not self.verifySoftwareRequirement():
            logging.error("Software requirements are not satisfied !")
            sys.exit(1)
        logging.info("Software Requirement Check   -COMPLETED")
        self.progressBar(5)

        logging.info("Repo Connectivity Requirement Check   -STARTED")
        if not self.verifyRepoConnection():
            logging.error("Network requirement not satisfied !")
            sys.exit(1)
        logging.info("Repo Connectivity Requirement Check   -COMPLETED")
        # print "Repo Connectivity Requirement Check  - COMPLETED"
        self.progressBar(10)
        return

    # Check for cpu count
    # Check for RAM Size
    def verifyHardwareRequirement(self):
        logging.info("No of cpu is %d", multiprocessing.cpu_count())
        if multiprocessing.cpu_count() < 2:
            logging.error("No of cpu is expected to be atleast two.\
                          Increase your system cpu count and try again.")
            print "ERROR: Number of processor is expected to be alteast two. Increase your system cpu count and try again."
            return False
        else:
            logging.info("verify cpu count success!")


        meminfo = open('/proc/meminfo').read()
        matched = re.search(r'^MemTotal:\s+(\d+)', meminfo)
        ram_size = int(matched.groups()[0])
        logging.info("RAM size = %d", ram_size)
        if ram_size < 3000000: #4194304:
            logging.info("RAM size is less than expected 4 GB.\
                         Upgrade your system and proceed with installation.")
            print "ERROR: System Memory is expected to be minimum 4GB. Upgrade your system and proceed with installation."
            return False


        rootdisk_cmd = "df --output=avail / |tail -1"
        code, out, err = self.cmdExecute(rootdisk_cmd, "Check Freespace", False)
        root_size = int(out)
        logging.info("Root disk size = %d", root_size)
        if root_size < 10 * 1000 * 1000: # 10GB Free
            logging.info("Root disk should have atleast 10GB free.\
                         Upgrade your system and proceed with installation.")
            print "ERROR: System / disk  is expected to have minimum 10GB free. Upgrade your system and proceed with installation."
            return False

        if os.path.isdir("/var/lib/docker"):
           dockerdisk_cmd = "df --output=avail /var/lib/docker |tail -1"
           code, out, err = self.cmdExecute(dockerdisk_cmd, "Check Freespace", False)
           docker_size = int(out)
           logging.info("Docker (/var/lib/docker)  disk size = %d", docker_size)
           if docker_size < 5 * 1000 * 1000: # 5GB Free
               logging.info("Docker data /var/lib/docker disk should have atleast 5GB free.\
                            Upgrade your system and proceed with installation.")
               print "ERROR: Docker data /var/lib/docker  disk  is expected to have minimum 5GB free. Upgrade your system and proceed with installation."
               return False

        logging.info("Hardware requirement verified successfully")
        return True


    # Check if OS is REDHAT/Centos and also check for Version compatibility.

    def verifyOSRequirement(self):
        logging.info("Verifying OS Requirement.")
        logging.info(platform.linux_distribution())
        osname = platform.linux_distribution()[0]
        osversion = platform.linux_distribution()[1]

        osname = osname.lower()

        self.osname = osname
        if "centos" in osname:
            logging.info("OS is Centos")
        elif "red hat" in osname:
            logging.info("OS is Redhat")
        else:
            logging.error("Incompatible Operating System. Only Redhat and Centos are supported.")
            print "Incompatible Operating System. Check logs for more information."
            sys.exit(1)

        if "7.0" in osversion:
            logging.info("OS Version is 7.0")
        elif "7.1" in osversion:
            logging.info("OS Version is 7.1")
        elif "7.2" in osversion:
            logging.info("OS Version is 7.2")
        else:
            logging.error("Incompatible Operating System Version. Check the System Requirement Documentation.")
            print "Incompatible Operating System Version. Check logs for more information"
            sys.exit(1)

        if "red hat" in osname:
            logging.info("Verifying Subscription Details.")
            subscription_cmd = "subscription-manager version"
            code, out, err = self.cmdExecute(subscription_cmd, "Check Red Hat Subscription", False)
            if code:
                if "currently not registered" in out:
                    self.redhat_subscription = False

        return True


    # Check - apporbit.repo file
    # Check - docker, ntp, wget
    def verifySoftwareRequirement(self):
        logging.info("started verifying software requirements")
        # Check for Operating System compatibility.
        self.verifyOSRequirement()
        if os.path.isfile('/etc/yum.repos.d/apporbit.repo'):
            logging.info('Found apporbit.repo in yum.repos.d directory.')
        else:
            logging.error('apporbit.repo file is missing in the package.\
                          check with AppOrbit Business contact.')
            print ("ERROR: apporbit.repo package files missing! check with your appOrbit Business contact.")
            return False

        logging.info ("Verifying docker installation")

        docker_cmd = "docker -v"
        return_code, out, err = self.cmdExecute(docker_cmd, "Docker Install", False)
        docker_ver = LooseVersion(self.docker_version)
        if return_code and out:
            docker_installed = LooseVersion(out.split()[2].split(',')[0])
            if docker_installed < docker_ver:
                self.do_dockerinstall = 1
                self.remove_olddocker = 1
                logging.info ("Older docker " + str(out))
                logging.info ("Upgrading docker to " + self.docker_version)
            else:
                logging.info ("Docker installed : " + str(out.split()[2].split(',')[0]))

        if not return_code:
            self.do_dockerinstall = 1
        elif out :
            docker_installed = LooseVersion(out.split()[2].split(',')[0])
            if docker_installed < docker_ver:
                self.do_dockerinstall = 1
                self.remove_olddocker = 1
                logging.info ("Older " + str(out))
                logging.info ("Upgrading docker to " + self.docker_version)
        else:
            print "Apporbit supports minimum docker version  " + self.docker_version 
            print "FAILED - Installation failed due to docker version conflict"
            sys.exit(1)

        logging.info ("Verify NTP Installation!")
        ntp_cmd = "ntpstat  > /dev/null"
        return_code, out, err = self.cmdExecute(ntp_cmd, "verify NTP Install", False)
        if not return_code:
            self.do_ntpinstall = 1
        else:
             cmd_ntpd = "systemctl stop ntpd.service"
             self.cmdExecute(cmd_ntpd, "Stop ntpd daemon service", False)
        
        logging.info("Verify wget installation")
        wget_cmd = "wget --version > /dev/null"
        return_code, out, err = self.cmdExecute(wget_cmd, "wget Install", False)
        if not return_code:
            self.do_wgetinstall = 1

        logging.info("Verify nslookup installation")
        nslookup_cmd = "which nslookup > /dev/null"
        return_code, out, err = self.cmdExecute(nslookup_cmd, "nslookup (bind-utils) Install", False)
        if not return_code:
            self.do_bindutilsinstall = 1

        return True


    # Verify RepoConnection
    def verifyRepoConnection(self):
        host = "repos.apporbit.com"
        path = "/"
        try:
            conn = httplib.HTTPConnection(host)
            conn.request("GET", path)
            if conn.getresponse().status == 200 :
                logging.info("Verified connection with the repos... OK")
                return True
            else:
                logging.error("Unable to connect to repository \
                 Check Network settings and Enable connection to http://repos.gsintlab.com \
                 %d", conn.getresponse().status )
                print ("Unable to connect to appOrbit repository. Check Network settings and Enable connection to http://repos.apporbit.com ")
                return False
        except StandardError:
            logging.error ("Unable to connect repositories.\
             Check Network settings and Enable connection to http://repos.gsintlab.com")
            print ("Unable to connect to appOrbit repository. Check Network settings and Enable connection to http://repos.apporbit.com ")
            return False

    def preSysRequirements(self,config_obj):
        cmd_yuminstall = "/bin/yum install -y  curl bind-utils ntp wget "
        return_code, out, err = self.cmdExecute(cmd_yuminstall, "Pre Install packages", False)
        if not return_code:
            if not self.redhat_subscription:
                print "FAILED- Red Hat is not having a valid subscription. Get a valid subscription and retry installation."
            return False
        config_obj.createRepoFile()
        self.progressBar(11)
        return True

    def fixSysRequirements(self):
        cmd_upgradelvm = "yum -y upgrade lvm2"
        return_code, out, err = self.cmdExecute(cmd_upgradelvm, "lvm upgrade", False)
        if not return_code:
            if not self.redhat_subscription:
                print "FAILED- Red Hat is not having a valid subscription. Get a valid subscription and retry installation."
            return False

        self.progressBar(12)

        if self.do_dockerinstall:
            if self.remove_olddocker:
                logging.info('Removing older version of docker')
                cmd_dockerremove = "/bin/yum remove -y docker docker-selinux docker-common" 
                return_code, out, err = self.cmdExecute(cmd_dockerremove, "Docker Remove older version if present", False)
                if not return_code:
                    return False
            logging.info('Installing docker version %s' % self.docker_version)
            cmd_dockerInstall = "/bin/yum install -y docker-engine-" + self.docker_version
            return_code, out, err = self.cmdExecute(cmd_dockerInstall, "Docker Install", False)
            if not return_code:
                return False
        self.progressBar(14)

        if self.do_sesettings:
            cmd_sesettings = "setenforce 0"
            return_code, out, err = self.cmdExecute(cmd_sesettings, "Setenforce to permissive", False)
            if not return_code:
                return False

        self.progressBar(17)
       
        if os.path.isfile('/etc/sysconfig/docker'):
           dockerConfig = '/etc/sysconfig/docker'
        elif os.path.isfile('/etc/default/docker'):
           dockerConfig = '/etc/default/docker'  
        else:
           dockerConfig = None
        if dockerConfig and 'log-driver=journald' in open(dockerConfig).read():
             cmd_docker_daemon_flag = "sed -i 's/log-driver=journald/log-driver=json-file/'  " + dockerConfig
             self.cmdExecute(cmd_docker_daemon_flag, "Enabled docker daemon --log-driver flag with json-file ",False)

        cmd_dockerservice = "systemctl enable docker.service"
        self.cmdExecute(cmd_dockerservice, "Enable Docker service on restart", False)

        cmd_dockerservice = "systemctl start docker.service"
        return_code, out, err = self.cmdExecute(cmd_dockerservice, " Docker service start", False)
        if not return_code:
            return False
        self.progressBar(18)

        cmd_ntpdate_sync = "ntpdate -b -u time.nist.gov"
        self.cmdExecute(cmd_ntpdate_sync, "ntpdate sync before ntpd enable", False)
        cmd_sysclk_update = "hwclock --systohc"
        self.cmdExecute(cmd_sysclk_update, "Synchronize the system clock", False)
        
        cmd_ntpd_enable = "systemctl enable ntpd.service"
        self.cmdExecute(cmd_ntpd_enable, "Enable ntpd daemon service", False)
        cmd_ntpd = "systemctl start ntpd.service"
        self.cmdExecute(cmd_ntpd, "Start ntpd daemon service", False)

        #Setup IPTableRules
        cmd_iptablerule1 = "iptables -D INPUT -j REJECT --reject-with icmp-host-prohibited "
        cmd_iptablerule2 = "iptables -D  FORWARD -j REJECT --reject-with icmp-host-prohibited"
        cmd_iptablesaverule = "/sbin/service iptables save"

        self.cmdExecute(cmd_iptablerule1, "Setting iptables input rule", False)
        self.cmdExecute(cmd_iptablerule2, "Setting iptables forward rule", False)
        self.cmdExecute(cmd_iptablesaverule, "iptables save", False)

        if os.path.isfile('/usr/bin/firewall-cmd'):
            cmd_firewall = "firewall-cmd --permanent --add-port=9443/tcp"
            self.cmdExecute(cmd_firewall, "Setting firewall rules", False)

        self.progressBar(19)

        return True

    def validateDomain(self, domainname):
        logging.info('Validating domainname ')
        code, out, err = self.cmdExecute("ping -c 1 -w 5 " + domainname, "Ping test for domain", False)
        if code:
           logging.error("Domain is an hostname. Wrong entry for domain")
           return False
        return True

    def validateHostIP(self, hostip):
        result = False
        logging.info('Validating host IP/hostname for public accessibility' )
        try:
            external_host_ip = urllib2.urlopen("http://whatismyip.akamai.com/").read()
        except urllib2.HTTPError, e:
            logging.error('HTTPError = %s', e.strerror)
        except urllib2.URLError, e:
            logging.error ('URLError = %s', e.strerror)
        except httplib.HTTPException, e:
            logging.error ('HTTPException %s', e.strerror)
        except:
            logging.error("Exception %s", str(sys.exc_info()[0]))
            logging.error(str(traceback.format_exc()))

        try:
            logging.info(external_host_ip)
            hostip_name_tup = socket.gethostbyaddr(external_host_ip)
            logging.info("HOST/IP found :" + str(hostip_name_tup))
        except socket.herror as e:
            hostip_name_tup = ()
            logging.info("HOST/IP not found")
            logging.error( "Socket Error" + e.strerror)

        for elem in hostip_name_tup:
            if hostip in elem:
                logging.info("VALID HOSTIP %s" , hostip)
                result = True
                break
            else:
                continue

        #Check if the hostip is a private accessible ip of the machine.
        if not result:
            logging.warning("Given IP is not publicly accessible %s" , hostip)
            logging.info('Validating host IP/hostname for private accessibility' )
            cmdlist = ["hostname -I", "hostname -f", "hostname -A", "hostname", "dnsdomainname"]
            for cmd in cmdlist:
                 b_return, out, err = self.cmdExecute(cmd, "Checking '" + cmd +"' of the machine", False)
                 if b_return and hostip in out :
                      result = True
                      break
            if not result:
                logging.error("Given IP is not accessible publicly or on private network. \
                Please check network configuration or host IP entered.")

        return result


        def resource_path(self,relative_path):
            try:
                # PyInstaller creates a temp folder and stores path in _MEIPASS
                base_path = sys._MEIPASS
            except Exception:
                base_path = os.path.abspath(".")

            return os.path.join(base_path, relative_path)

    def wait_net_service(self, server, port, timeout=None):
        """ Wait for network service to appear 
            @param timeout: in seconds, if None or 0 wait forever
            @return: True of False, if timeout is None may return only True or
                     throw unhandled network exception
        """
        import socket
        import errno
        from time import time as now
        from time import sleep

        s = socket.socket()
        if timeout:
            # time module is needed to calc timeout shared between two exceptions
            end = now() + timeout
    
        while True:
            try:
                if timeout:
                    next_timeout = end - now()
                    if next_timeout < 0:
                        return False
                    else:
                        s.settimeout(next_timeout)

                s.connect((server, port))
        
            except socket.timeout, err:
                # this exception occurs only if timeout is set
                if timeout:
                    return False
      
            except socket.error, err:
                # catch timeout exception from underlying network library
                # this one is different from socket.timeout
                if type(err.args) != tuple or err[0] != errno.ETIMEDOUT:
                    sleep(2)
                    next
            else:
                s.close()
                return True

