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


    def cmdExecute(self, cmd_str):
        try:
            process = subprocess.Popen(cmd_str, shell=True, stdout=subprocess.PIPE, \
                                   stderr=subprocess.PIPE)
            out, err =  process.communicate()
        except Exception as exp:
            raise exp

        return process.returncode, out, err


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
            try:
                subscription_cmd = "subscription-manager version"
                code, out, err = self.cmdExecute(subscription_cmd)
                if code == 0:
                    # print out
                    logging.info("subscription manager version. %s", out)
                    if "currently not registered" in out:
                        logging.error("Red Hat Subscription : This system is not Registered. Register and retry installation.")
                        self.redhat_subscription = False
                else:
                    # print err
                    logging.error("Error in finding subscription details. %s", err)

            except Exception as exp:
                logging.error("subscription manager version command failed.")
                logging.error("Unable to find subscription details..")


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
        try:
            docker_cmd = "docker -v > /dev/null"
            code, out, err = self.cmdExecute(docker_cmd)
            if code == 0:
                # print out
                logging.info("docker is already installed. %s", out)
            else:
                # print err
                logging.warning("docker needs to be installed. %s", err)
                self.do_dockerinstall = 1
        except Exception as exp:
            logging.error("Docker is not installed.")
            self.do_dockerinstall = 1

        logging.info ("Verify NTP Installation!")
        try:
            ntp_cmd = "ntpdate time.nist.gov > /dev/null"
            code, out, err = self.cmdExecute(ntp_cmd)
            if code == 0:
                logging.info("ntp is already installed. %s", out)
            else:
                logging.warning("ntp needs to be installed. %s", err)
                self.do_ntpinstall = 1
        except Exception as exp:
            logging.warning("Exception:ntp needs to be installed! %d : %s", exp.errno, exp.strerror)
            self.do_ntpinstall = 1


        logging.info("Verify wget installation")
        try:
            wget_cmd = "wget --version > /dev/null"
            code, out, err = self.cmdExecute(wget_cmd)
            if code == 0:
                logging.info("wget is already installed. %s", out)
            else:
                logging.info("wget needs to be installed. %s", err)
                self.do_wgetinstall = 1
        except OSError as e:
            logging.error("wget needs to be installed! %d : %s", e.errno, e.strerror)
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

        process = subprocess.Popen(cmd_upgradelvm, shell=True, stdout=subprocess.PIPE, \
                                   stderr=subprocess.PIPE)

        out, err =  process.communicate()

        if process.returncode == 0:
            # print out
            logging.info("Upgrade lvm2. %s", out)

        else:
            logging.warning("Upgrade lvm2 failed. %s", err)
            print "Upgrade lvm2 failed!. Check log for details."
            return False

        if self.do_wgetinstall:
            try:
                cmd_wgetInstall = "yum install -y wget"
                code, out, err = self.cmdExecute(cmd_wgetInstall)
                if code == 0:
                    # print out
                    logging.info("Install wget success. %s", out)
                else:
                    logging.warning("Install wget failed. %s", err)
                if self.redhat_subscription:
                    print "Installing wget failed!. Check log for details."
                else:
                    print "FAILED- Red Hat is not having a valid subscription. Get a valid subscription and retry installation."
                    return False
            except Exception as exp:
                logging.warning("Exception:Install wget failed.! %d : %s", exp.errno, exp.strerror)
                return False

        self.progressBar(12)
        if self.do_ntpinstall:
            try:
                cmd_ntpInstall = "yum install -y ntp"
                code, out, err = self.cmdExecute(cmd_ntpInstall)
                if code == 0:
                    logging.info("Install ntp success. %s", out)
                else:
                    logging.warning("Install ntp failed. %s", err)
                    print "Installing ntp failed!. check log for details."
                    return False
            except Exception as exp:
                logging.warning("Exception:Install ntp failed.! %d : %s", exp.errno, exp.strerror)
                return False

        self.progressBar(14)

        if self.do_dockerinstall:
            try:
                cmd_dockerInstall = "yum install -y docker-1.7.1"
                code, out, err = self.cmdExecute(cmd_dockerInstall)
                if code == 0:
                    logging.info("Install docker success. %s", out)

                else:
                    logging.warning("Install docker failed. %s", err)
                    print "Installing docker failed!. check log for details."
                    return False
            except Exception as exp:
                logging.warning("Exception:Install docker failed.! %d : %s", exp.errno, exp.strerror)
                return False

        self.progressBar(16)
        if self.do_sesettings:
            try:
                # print ("Info: Setting SElinux status to permissive")
                cmd_sesettings = "setenforce 0"
                code, out, err = self.cmdExecute(cmd_sesettings)
                if code == 0:
                    logging.info("setting sestatus success. %s", out)
                else:
                    logging.warning("setting sestatus Failed. %s", out)
                    print "setting sestatus failed!. check log for details."
                    return False
            except Exception as exp:
                logging.warning("Exception:setting sestatus Failed. %d : %s", exp.errno, exp.strerror)
                return False

        self.progressBar(17)
        try:
            # Enable Docker Service
            cmd_dockerservice = "systemctl enable docker.service"
            code, out, err = self.cmdExecute(cmd_dockerservice)
            if code == 0:
                logging.info("service docker enabled on startup  -success. %s", out)
            else:
                logging.warning("service docker enabled on startup - Failed. %s", err)
        except Exception as exp:
            logging.warning("Exception:service docker enabled on startup - Failed. %d : %s", exp.errno, exp.strerror)

        try:
            #Enable Docker service on restart
            cmd_dockerservice = "systemctl start docker.service"
            code, out, err = self.cmdExecute(cmd_dockerservice)
            if code == 0:
                logging.info("service docker start  -success. %s", out)
            else:
                logging.error("service docker start  -Failed. %s", err)
                print "service docker start failed. check log for details."
                return False
        except Exception as exp:
            logging.warning("Exception:service docker start  -Failed. %d : %s", exp.errno, exp.strerror)
            return False

        self.progressBar(18)
        try:
            # Sync Network Time
            cmd_ntpupdate = "ntpdate -b -u time.nist.gov"
            code, out, err = self.cmdExecute(cmd_ntpupdate)
            if code == 0:
                logging.info("ntp update  -success. %s", out)
            else:
                logging.info("ntp update  -Failed. %s", err)
        except Exception as exp:
            logging.warning("Exception: ntp update  -Failed. %d : %s", exp.errno, exp.strerror)
            return False

        #Setup IPTableRules
        cmd_iptablerule1 = "iptables -D INPUT -j REJECT --reject-with icmp-host-prohibited "
        cmd_iptablerule2 = "iptables -D  FORWARD -j REJECT --reject-with icmp-host-prohibited"
        cmd_iptablesaverule = "/sbin/service iptables save"

        try:
            code, out, err = self.cmdExecute(cmd_iptablerule1)
            if code == 0:
                logging.info("iptable rule1 - success %s", out)
            else:
                logging.warning("iptable rule1 - Failed %s", err)
        except Exception as exp:
            logging.warning("Exception:iptable rule1 - Failed.  %d : %s", exp.errno, exp.strerror)

        try:
            code, out, err = self.cmdExecute(cmd_iptablerule2)
            if code == 0:
                logging.info("iptable rule2 - success. %s", out)
            else:
                logging.warning("iptable rule2 - Failed. %s", err)
        except Exception as exp:
            logging.warning("Exception:iptable rule2 - Failed.  %d : %s", exp.errno, exp.strerror)

        try:
            code, out, err = self.cmdExecute(cmd_iptablesaverule)
            if code == 0:
                logging.info("iptable rules saved - success %s", out)
            else:
                logging.warning("iptable rules saved - Failed %s", err)
        except Exception as exp:
            logging.warning("Exception:iptable rules saved - Failed.  %d : %s", exp.errno, exp.strerror)

        if os.path.isfile('/usr/bin/firewall-cmd'):
            try:
                #  Enable the port used by Chef (permanent makes it persist after reboot
                #  Chef Port HardCoded
                cmd_firewall = "firewall-cmd --permanent --add-port=9443/tcp"
                code, out, err = self.cmdExecute(cmd_firewall)
                if code == 0:
                    logging.info("firewall rules saved - success %s", out)
                else:
                    logging.warning("firewall rules saved - Failed %s", err)
            except Exception as exp:
                logging.warning("Exception:firewall rules saved - Failed.  %d : %s", exp.errno, exp.strerror)

        self.progressBar(19)

        return True

