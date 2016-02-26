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
from time import sleep

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
                    exit()
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
                    exit()
            else:
                    logging.warning("WARNING - %s", cmd_desc)
                    logging.warning("Exception: %d : %s", exp.errno, exp.strerror)
        return True, out, err


    # Progress Bar Impleementaion
    def progressBar(self, i):
        sys.stdout.write('\r')
        # the exact output you're looking for:
        sys.stdout.write("[%-20s] %d%%" % ('='*i, 5*i))
        sys.stdout.flush()
        sleep(0.25)


    # Check for System Information if it satisfy all Pre Deploy Requirements
    # If not fixable errors found exit the process and log the errors.
    def verifySystemInfo(self):
        logging.info("Hardware Requirement Check   -STARTED")
        self.progressBar(1)
        if not self.verifyHardwareRequirement():
            logging.error("Hardware requirements are not satisfied !")
            print "ERROR : Hardware requirement verification failed! Check log for details."
            exit()
        logging.info("Hardware Requirement Check   -COMPLETED")
        self.progressBar(2)

        logging.info("Software Requirement Check   -STARTED")
        if not self.verifySoftwareRequirement():
            logging.error("Software requirements are not satisfied !")
            #print ("ERROR : Software requirement check failed! \
            # Check log for details.")
            exit()
        logging.info("Software Requirement Check   -COMPLETED")
        self.progressBar(5)

        # print "Security Requirement Check  - STARTED"
        logging.info("Security Requirement Check   -STARTED")
        if not self.verifySecuirtyIssues():
            logging.error('security requirements not satisfied')
            # print "ERROR: Security Requirements not satified."
            exit()
        logging.info("Security Requirement Check   -COMPLETED")
        # print "Security Requirement Check  - COMPLETED"
        self.progressBar(8)
        # print "Repo Connectivity Requirement Check  - STARTED"
        logging.info("Repo Connectivity Requirement Check   -STARTED")
        if not self.verifyRepoConnection():
            logging.error("Network requirement not satisfied !")
            # print " ERROR: Network requirement not satisfied !"
            exit()
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
            # print "ERROR: Number of processor is expected to be alteast two"
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
            # print "ERROR: System Memory is expected to be alteast 4GB"
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
            exit()

        if "7.0" in osversion:
            logging.info("OS Version is 7.0")
        elif "7.1" in osversion:
            logging.info("OS Version is 7.1")
        else:
            logging.error("Incompatible Operating System Version. Check the System Requirement Documentation.")
            print "Incompatible Operating System Version. Check logs for more information"
            exit()

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
        if not self.cmdExecute(docker_cmd, "Docker Install", False):
            self.do_dockerinstall = 1

        logging.info ("Verify NTP Installation!")
        ntp_cmd = "ntpdate time.nist.gov > /dev/null"
        if not self.cmdExecute(ntp_cmd, "ntp Install", False):
            self.do_ntpinstall = 1

        logging.info("Verify wget installation")
        wget_cmd = "wget --version > /dev/null"

        if not self.cmdExecute(wget_cmd, "wget Install", False):
            self.do_wgetinstall = 1

        return True

    # Verify Sestatus
    def verifySecuirtyIssues(self):
        securitysettings = True
        selinux_status = os.popen("getenforce").read()
        selinux_status = selinux_status.lower().strip()
        logging.info ("selinux status is %s", selinux_status)
        permissive_str = 'permissive'
        disabled_str = 'disabled'
        enforcing_str = 'enforcing'
        if selinux_status == permissive_str:
            securitysettings = True
        elif selinux_status == disabled_str:
            securitysettings = True
        elif selinux_status == enforcing_str:
            securitysettings = False
            self.do_sesettings = 1
        else:
            logging.warning("Not able to get selinux status")
            # print ("Not able to get selinux status. ")

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
            return False

    def fixSysRequirements(self):
        cmd_upgradelvm = "yum -y upgrade lvm2"
        if not self.cmdExecute(cmd_upgradelvm, "lvm upgrade", False)
            return False


        out, err =  process.communicate()

        if process.returncode == 0:
            # print out
            logging.info("Upgrade lvm2. %s", out)

        else:
            logging.warning("Upgrade lvm2 failed. %s", err)
            print "Upgrade lvm2 failed!. Check log for details."
            return False

        if self.do_wgetinstall:
            cmd_wgetInstall = "yum install -y wget"
            code, out, err = self.cmdExecute(cmd_wgetInstall, "Wget Install", False)
            if not code:
                if self.redhat_subscription:
                    print "FAILED- Red Hat is not having a valid subscription. Get a valid subscription and retry installation."
                return False

        self.progressBar(12)
        if self.do_ntpinstall:
            cmd_ntpInstall = "yum install -y ntp"
            if not self.cmdExecute(cmd_ntpInstall, "Ntp Install", False):
                return False

        self.progressBar(14)

        if self.do_dockerinstall:
            cmd_dockerInstall = "yum install -y docker-1.7.1"
            if not self.cmdExecute(cmd_dockerInstall, "Docker Install", False):
                return False
        self.progressBar(16)

        if self.do_sesettings:
            cmd_sesettings = "setenforce 0"
            if not self.cmdExecute(cmd_sesettings, "Setenforce to permissive", False):
                return False

        self.progressBar(17)
        cmd_dockerservice = "systemctl enable docker.service"
        self.cmdExecute(cmd_dockerservice, "Enable Docker service on restart", False)

        cmd_dockerservice = "systemctl start docker.service"
        if not self.cmdExecute(cmd_dockerservice, " Docker service start", False):
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

