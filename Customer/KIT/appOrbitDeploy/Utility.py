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
        return



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
                process = subprocess.Popen(subscription_cmd, shell=True, stdout=subprocess.PIPE, \
                                   stderr=subprocess.PIPE)
                out, err =  process.communicate()

                if process.returncode == 0:
                    # print out
                    logging.info("subscription manager version. %s", out)
                    if "currently not registered" in out:
                        logging.error("Red Hat Subscription : This system is not Registered. Register and retry installation.")
                        print "Red Hat is not having a valid subscription. Get a valid subscription and retry installation."
                        exit()

                else:
                    # print err
                    logging.error("Error in finding subscription details. %s", err)


            except Exception as exp:
                logging.error("subscription manager version command failed.")
                logging.error("Unable to find subscription details..")


        return


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
            process = subprocess.Popen(docker_cmd, shell=True, stdout=subprocess.PIPE, \
                                   stderr=subprocess.PIPE)

            out, err =  process.communicate()

            if process.returncode == 0:
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
            process = subprocess.Popen(ntp_cmd, shell=True, stdout=subprocess.PIPE, \
                                   stderr=subprocess.PIPE)

            out, err =  process.communicate()

            if process.returncode == 0:
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
            process = subprocess.Popen(wget_cmd, shell=True, stdout=subprocess.PIPE, \
                                   stderr=subprocess.PIPE)

            out, err =  process.communicate()

            if process.returncode == 0:
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
        if self.do_wgetinstall:
            cmd_wgetInstall = "yum install -y wget"

            process = subprocess.Popen(cmd_wgetInstall, shell=True, stdout=subprocess.PIPE, \
                                   stderr=subprocess.PIPE)

            out, err =  process.communicate()

            if process.returncode == 0:
                # print out
                logging.info("Install wget success. %s", out)

            else:
                logging.warning("Install wget failed. %s", err)
                print "Installing wget failed!. Check log for details."
                return False

        self.progressBar(12)
        if self.do_ntpinstall:
            cmd_ntpInstall = "yum install -y ntp"

            process = subprocess.Popen(cmd_ntpInstall, shell=True, stdout=subprocess.PIPE, \
                                   stderr=subprocess.PIPE)

            out, err =  process.communicate()

            if process.returncode == 0:
                logging.info("Install ntp success. %s", out)

            else:
                logging.warning("Install ntp failed. %s", err)
                print "Installing ntp failed!. check log for details."
                return False
        self.progressBar(14)

        if self.do_dockerinstall:
            cmd_dockerInstall = "yum install -y docker-1.7.1"

            process = subprocess.Popen(cmd_dockerInstall, shell=True, stdout=subprocess.PIPE, \
                                   stderr=subprocess.PIPE)

            out, err =  process.communicate()

            if process.returncode == 0:
                logging.info("Install docker success. %s", out)

            else:
                logging.warning("Install docker failed. %s", err)
                print "Installing docker failed!. check log for details."
                return False

        self.progressBar(16)
        if self.do_sesettings:
            # print ("Info: Setting SElinux status to permissive")
            cmd_sesettings = "setenforce 0"

            process = subprocess.Popen(cmd_sesettings, shell=True, stdout=subprocess.PIPE, \
                                   stderr=subprocess.PIPE)

            out, err =  process.communicate()

            if process.returncode == 0:
                logging.info("setting sestatus success. %s", out)

            else:
                logging.warning("setting sestatus Failed. %s", out)
                print "setting sestatus failed!. check log for details."
                return False
        self.progressBar(17)
        # Enable Docker Service
        cmd_dockerservice = "systemctl enable docker.service"
        process_doc = subprocess.Popen(cmd_dockerservice, shell=True, stdout=subprocess.PIPE, \
        stderr=subprocess.PIPE)
        out_doc, err_doc =  process_doc.communicate()
        if process_doc.returncode == 0:
            logging.info("service docker enabled on startup  -success. %s", out_doc)

        else:
            logging.warning("service docker enabled on startup - Failed. %s", err_doc)


        #Enable Docker service on restart
        cmd_dockerservice = "systemctl start docker.service"
        process_doc = subprocess.Popen(cmd_dockerservice, shell=True, stdout=subprocess.PIPE, \
                         stderr=subprocess.PIPE)

        out_doc, err_doc =  process_doc.communicate()
        if process_doc.returncode == 0:
            logging.info("service docker start  -success. %s", out_doc)

        else:
            logging.error("service docker start  -Failed. %s", err_doc)
            print "service docker start failed. check log for details."
            return False
        self.progressBar(18)
        # Sync Network Time
        cmd_ntpupdate = "ntpdate -b -u time.nist.gov"

        process = subprocess.Popen(cmd_ntpupdate, shell=True, stdout=subprocess.PIPE, \
                                   stderr=subprocess.PIPE)

        out, err =  process.communicate()

        if process.returncode == 0:
            logging.info("ntp update  -success. %s", out_doc)
        else:
            logging.info("ntp update  -Failed. %s", err_doc)


        #Setup IPTableRules
        cmd_iptablerule1 = "iptables -D INPUT -j REJECT --reject-with icmp-host-prohibited "
        cmd_iptablerule2 = "iptables -D  FORWARD -j REJECT --reject-with icmp-host-prohibited"
        cmd_iptablesaverule = "/sbin/service iptables save"

        process = subprocess.Popen(cmd_iptablerule1, shell=True, stdout=subprocess.PIPE, \
                                   stderr=subprocess.PIPE)

        out, err =  process.communicate()

        if process.returncode == 0:
            logging.info("iptable rule1 - success %s", out)
        else:
            logging.warning("iptable rule1 - Failed %s", err)


        process = subprocess.Popen(cmd_iptablerule2, shell=True, stdout=subprocess.PIPE, \
                                   stderr=subprocess.PIPE)

        out, err =  process.communicate()

        if process.returncode == 0:
            logging.info("iptable rule2 - success. %s", out)
        else:
            logging.warning("iptable rule2 - Failed. %s", err)


        process = subprocess.Popen(cmd_iptablesaverule, shell=True, stdout=subprocess.PIPE, \
                                   stderr=subprocess.PIPE)

        out, err =  process.communicate()

        if process.returncode == 0:

            logging.info("iptable rules saved - success %s", out)
        else:
            logging.warning("iptable rules saved - Failed %s", err)


        if os.path.isfile('/usr/bin/firewall-cmd'):
            #  Enable the port used by Chef (permanent makes it persist after reboot
            #  Chef Port HardCoded
            cmd_firewall = "firewall-cmd --permanent --add-port=9443/tcp"
            process = subprocess.Popen(cmd_firewall, shell=True, stdout=subprocess.PIPE, \
                                   stderr=subprocess.PIPE)

            out, err =  process.communicate()

            if process.returncode == 0:

                logging.info("firewall rules saved - success %s", out)
            else:
                logging.warning("firewall rules saved - Failed %s", err)

        self.progressBar(19)

        return True

