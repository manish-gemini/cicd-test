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
from time import sleep

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
        self.do_ntpinstall = 0
        self.do_wgetinstall = 0
        self.do_sesettings = 0
        self.redhat_subscription = True
        return


    def cmdExecute(self, cmd_str, cmd_desc = '', bexit = False):
        try:
            process = subprocess.Popen(cmd_str, shell=True, stdout=subprocess.PIPE, \
                                   stderr=subprocess.PIPE)
            out, err =  process.communicate()
            if process.returncode == 0:
                logging.info("Success - %s",cmd_desc)
                logging.info(out)
            else:
                if bexit :
                    logging.error("FAILED - %s", cmd_desc)
                    logging.error(err)
                    print "FAILED - " + cmd_desc
                    print "Check log for details."
                    sys.exit(1)
                else:
                    logging.warning("WARNING - %s", cmd_desc)
                    logging.warning(err)
                    return False, out, err
        except Exception as exp:
            if bexit :
                    logging.error("FAILED - %s", cmd_desc)
                    logging.error("Exception: %d : %s", exp.errno, exp.strerror)
                    print "[FAILED] - " + cmd_desc
                    print "Check log for details."
                    sys.exit(1)
            else:
                    logging.warning("WARNING - %s", cmd_desc)
                    logging.warning("Exception: %d : %s", exp.errno, exp.strerror)
                    return False, out, err

        return True, out, err


    # Progress Bar Impleementaion
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
    def createTempFile(self):
        open("install.tmp", 'w').close()
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
    def loginDockerRegistry(self, uname, passwd, repo_str = "secure-registry.gsintlab.com" ):
        # print "Login to Docker Registry " + repo_str
        if passwd:
            cmd_str = 'docker login -e=admin@apporbit.com -u=' + uname + ' -p=' + passwd +' '+ repo_str
            self.cmdExecute(cmd_str, "Docker login ", True)
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
            print "ERROR: System Memory is expected to be alteast 4GB. Upgrade your system and proceed with installation."
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
        if os.path.isfile('apporbit.repo'):
            logging.info('copying apporbit.repo to yum.repos.d directory.')
            shutil.copyfile('apporbit.repo', '/etc/yum.repos.d/apporbit.repo')

        else:
            logging.error('apporbit.repo file is missing in the package.\
                          check with AppOrbit Business contact.')
            print ("ERROR: package files missing! check with your appOrbit Business contact.")
            return False

        logging.info ("Verifying docker installation")

        docker_cmd = "docker -v > /dev/null"

        return_code, out, err = self.cmdExecute(docker_cmd, "Docker Install", False)

        if not return_code:
            self.do_dockerinstall = 1

        logging.info ("Verify NTP Installation!")
        ntp_cmd = "ntpdate time.nist.gov > /dev/null"
        return_code, out, err = self.cmdExecute(ntp_cmd, "ntp Install", False)
        if not return_code:
            self.do_ntpinstall = 1

        logging.info("Verify wget installation")
        wget_cmd = "wget --version > /dev/null"
        return_code, out, err = self.cmdExecute(wget_cmd, "wget Install", False)
        if not return_code:
            self.do_wgetinstall = 1

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

    def fixSysRequirements(self):
        cmd_upgradelvm = "yum -y upgrade lvm2"
        return_code, out, err = self.cmdExecute(cmd_upgradelvm, "lvm upgrade", False)
        if not return_code:
            if not self.redhat_subscription:
                print "FAILED- Red Hat is not having a valid subscription. Get a valid subscription and retry installation."
            return False

        if self.do_wgetinstall:
            cmd_wgetInstall = "yum install -y wget"
            return_code, out, err = self.cmdExecute(cmd_wgetInstall, "Wget Install", False)
            if not return_code:
                if not self.redhat_subscription:
                    print "FAILED- Red Hat is not having a valid subscription. Get a valid subscription and retry installation."
                return False

        self.progressBar(12)
        if self.do_ntpinstall:
            cmd_ntpInstall = "yum install -y ntp"
            return_code, out, err = self.cmdExecute(cmd_ntpInstall, "Ntp Install", False)
            if not return_code:
                return False

        self.progressBar(14)

        if self.do_dockerinstall:
            cmd_dockerInstall = "yum install -y docker-1.7.1"
            return_code, out, err = self.cmdExecute(cmd_dockerInstall, "Docker Install", False)
            if not return_code:
                return False
        self.progressBar(16)

        if self.do_sesettings:
            cmd_sesettings = "setenforce 0"
            return_code, out, err = self.cmdExecute(cmd_sesettings, "Setenforce to permissive", False)
            if not return_code:
                return False

        self.progressBar(17)
        cmd_dockerservice = "systemctl enable docker.service"
        self.cmdExecute(cmd_dockerservice, "Enable Docker service on restart", False)

        cmd_dockerservice = "systemctl start docker.service"
        return_code, out, err = self.cmdExecute(cmd_dockerservice, " Docker service start", False)
        if not return_code:
            return False
        self.progressBar(18)

        cmd_ntpupdate = "ntpdate -b -u time.nist.gov"
        self.cmdExecute(cmd_ntpupdate, "Sync network time", False)

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
            b_return, out, err = self.cmdExecute("hostname -I", "Checking Hostname -I for local ip of the machine", False)
            if b_return and hostip in out :
                result = True
            else:
                logging.error("Given IP is not accessible publicly or on private network. \
                Please check network configuration or host IP entered.")

        return result

