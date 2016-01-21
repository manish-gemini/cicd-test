
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
import time

class Utility:

    def __init__(self):
        self.do_dockerinstall = 0
        self.do_ntpinstall = 0
        self.do_wgetinstall = 0
        self.do_sesettings = 0
        return


    # Check for System Information if it satisfy all Pre Deploy Requirements
    # If not fixable errors found exit the process and log the errors.
    def verifySystemInfo(self):
        logging.info("Hardware Requirement Check   -STARTED")
        print "Hardware Requirement Check  - STARTED"
        if not self.verifyHardwareRequirement():
            logging.error("Hardware requirements are not satisfied !")
            print ("ERROR : Hardware requirement check failed! \
            Check log for details.")
            exit()
        logging.info("Hardware Requirement Check   -COMPLETED")
        print "Hardware Requirement Check  - COMPLETED"

        print "Software Requirement Check  - STARTED"
        logging.info("Software Requirement Check   -STARTED")
        if not self.verifySoftwareRequirement():
            logging.error("Software requirements are not satisfied !")
            print ("ERROR : Software requirement check failed! \
            Check log for details.")
            exit()
        logging.info("Software Requirement Check   -COMPLETED")
        print "Software Requirement Check  - COMPLETED"

        print "Security Requirement Check  - STARTED"
        logging.info("Security Requirement Check   -STARTED")
        if not self.verifySecuirtyIssues():
            logging.error('security requirements not satisfied')
            print "ERROR: Security Requirements not satified."
            exit()
        logging.info("Security Requirement Check   -COMPLETED")
        print "Security Requirement Check  - COMPLETED"

        print "Repo Connectivity Requirement Check  - STARTED"
        logging.info("Repo Connectivity Requirement Check   -STARTED")
        if not self.verifyRepoConnection():
            logging.error("Network requirement not satisfied !")
            print " ERROR: Network requirement not satisfied !"
            exit()
        logging.info("Repo Connectivity Requirement Check   -COMPLETED")
        print "Repo Connectivity Requirement Check  - COMPLETED"

        return

    # Check for cpu count
    # Check for RAM Size
    def verifyHardwareRequirement(self):
        logging.info("No of cpu is %d", multiprocessing.cpu_count())
        if multiprocessing.cpu_count() < 2:
            logging.error("No of cpu is expected to be atleast two.\
                          Increase your system cpu count and try again.")
            print "ERROR: Number of processor is expected to be alteast two"
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
            print "ERROR: System Memory is expected to be alteast 4GB"
            return False

        logging.info("Hardware requirement verified successfully")
        return True


    # Check - apporbit.repo file
    # Check - docker, ntp, wget
    def verifySoftwareRequirement(self):
        logging.info("started verifying software requirements")
        if os.path.isfile('apporbit.repo'):
            logging.info('copying apporbit.repo to yum.repos.d directory.')
            shutil.copyfile('apporbit.repo', '/etc/yum.repos.d/apporbit.repo')
        else:
            logging.error('apporbit.repo file is missing in the package.\
                          check with appOrbit Business contact.')
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
            logging.error("ntp needs to be installed! %d : %s", exp.errno, exp.strerror)
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
        host = "repos.gsintlab.com"
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
                print ("Unable to connect to repository. \
                Check Network settings and Enable connection to http://repos.gsintlab.com ")
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

        if self.do_ntpinstall:
            cmd_ntpInstall = "yum install -y ntp"

            process = subprocess.Popen(cmd_ntpInstall, shell=True, stdout=subprocess.PIPE, \
                                   stderr=subprocess.PIPE)

            out, err =  process.communicate()

            if process.returncode == 0:
                logging.info("Install ntp success. %s", out)
            else:
                logging.warning("Install ntp failed. %s", err)
                print ("NTP Install - FAILED")
                return False


        if self.do_dockerinstall:
            cmd_dockerInstall = "yum install -y docker-1.7.1"

            process = subprocess.Popen(cmd_dockerInstall, shell=True, stdout=subprocess.PIPE, \
                                   stderr=subprocess.PIPE)

            out, err =  process.communicate()

            if process.returncode == 0:
                logging.info("Install docker success. %s", out)
            else:
                logging.error("Install docker failed. %s", err)
                print ("docker Install - Failed")
                return False

        if self.do_sesettings:
            cmd_sesettings = "setenforce 0"

            process = subprocess.Popen(cmd_sesettings, shell=True, stdout=subprocess.PIPE, \
                                   stderr=subprocess.PIPE)

            out, err =  process.communicate()

            if process.returncode == 0:
                logging.info("setting sestatus success. %s", out)
            else:
                logging.warning("setting sestatus Failed. %s", out)
                return False

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
            return False

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

        #Generate SSL Certificate
        cmd_sslcert = 'openssl req -new -newkey rsa:4096 -days 365 -nodes -x509 \
        -subj "/C=US/ST=NY/L=appOrbit/O=Dis/CN=www.apporbit.com" \
        -keyout /var/lib/apporbit/sslkeystore/apporbitserver.key \
        -out /var/lib/apporbit/sslkeystore/apporbitserver.crt'

        process = subprocess.Popen(cmd_sslcert, shell=True, stdout=subprocess.PIPE, \
                                   stderr=subprocess.PIPE)

        out, err =  process.communicate()

        if process.returncode == 0:
            logging.info("SSL Certificate Create - SUCCESS. %s", out)
        else:
            logging.warning("SSL Certificate Create - Failed. %s", err)


        return True


    def deployFromFile(self, fname = 'local.conf'):
        repo_str = ""
        config = ConfigParser.ConfigParser()
        fp = open(fname, 'r')
        config.readfp(fp)

        try:
            uname = config.get('Docker Login', 'username')
        except ConfigParser.NoOptionError:
            uname = ''
        except ConfigParser.NoSectionError:
            uname = ''

        try:
            passwd = config.get('Docker Login', 'password')
        except ConfigParser.NoOptionError:
            passwd = ''
        except ConfigParser.NoSectionError:
            passwd = ''

        try:
            buildID = config.get('User Config', 'build_id')
        except ConfigParser.NoOptionError:
            buildID = 'latest'
        except ConfigParser.NoSectionError:
            buildID = 'latest'

        try:
            repo_str = config.get('User Config', 'repo_str')
        except ConfigParser.NoOptionError:
            repo_str = ''
        except ConfigParser.NoSectionError:
            repo_str = ''

        if not repo_str:
            if not fname == 'local.conf':
                repo_str = "registry.apporbit.com"


        if fname == 'local.conf':
            try:
                dev_mode = config.get('User Config', 'dev_mode')
            except ConfigParser.NoOptionError:
                dev_mode = 0
            except ConfigParser.NoSectionError:
                dev_mode = 0


        try:
            clean_setup = config.get('User Config', 'clean_setup')
        except ConfigParser.NoOptionError:
            clean_setup = 2
        except ConfigParser.NoSectionError:
            clean_setup = 2

        try:
            cfg_mgr =  config.get('User Config', 'cfg_mgr')
        except ConfigParser.NoOptionError:
            cfg_mgr = 'y'
        except ConfigParser.NoSectionError:
            cfg_mgr = 'y'

        try:
            deploy_mode = config.get('User Config', 'deploy_mode')
        except ConfigParser.NoOptionError:
            deploy_mode = '1'
        except ConfigParser.NoSectionError:
            deploy_mode = '1'

        try:
            email_id = config.get('User Config', 'on_prem_emailid')
        except ConfigParser.NoOptionError:
            email_id = 'admin@apporbit.com'
        except ConfigParser.NoSectionError:
            email_id = 'admin@apporbit.com'

        try:
            theme_name = config.get('User Config', 'themeName')
        except ConfigParser.NoOptionError:
            theme_name = 'apporbit-v2'
        except ConfigParser.NoSectionError:
            theme_name = 'apporbit-v2'


        try:
            host_ip = config.get('User Config', 'hostIP')
        except ConfigParser.NoOptionError:
            host_ip = ''
        #     TODO EXIT or ASSIGN PUBLIC IP
        except ConfigParser.NoSectionError:
            host_ip = ''
        #     TODO EXIT or ASSIGN PUBLIC IP


        self.removeRunningContainers()

        if clean_setup == '1':
            self.clearOldEntries()

        self.setupDirectoriesForVolumeMount()

        if repo_str:
            self.loginDockerRegistry(uname, passwd, repo_str)
            self.pullImagesformRepos(repo_str)

        self.deployAppOrbit(deploy_mode, email_id, theme_name, host_ip, repo_str, cfg_mgr)

        return



    def deployAppOrbit(self, deploy_mode, email_id, theme_name, host_ip, repo_str, config_mgr = 'y'):
        if config_mgr == 'y':
            cmd_chefDeploy = "docker run -m 2g -it --restart=always -p 9443:9443  \
            -v /etc/chef-server/ --name apporbit-chef -h "+ host_ip + " -d \
            "+ repo_str +"/apporbit/apporbit-chef:1.0"

            process = subprocess.Popen(cmd_chefDeploy, shell=True, stdout=subprocess.PIPE, \
                                   stderr=subprocess.PIPE)

            out, err =  process.communicate()

            if process.returncode == 0:
                logging.info(out)
                print "Deploy Chef - SUCCESS"
                print "Deploy in progress ..."
                time.sleep(180)
            else:
                logging.error(err)
                print "Deploy Chef - FAILED"
                exit()

        else:
            # TODO HANDLE
            logging.error("Chef not chosen for deploy. exit")
            print "CHEF NOT CHOSEN FOR DEPLOY."
            exit()


        cmd_deploy_db = "docker run --name db --restart=always -e MYSQL_ROOT_PASSWORD=admin \
        -e MYSQL_USER=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=apporbit_controller \
        -v /var/dbstore:/var/lib/mysql -d mysql:5.6.24"

        process = subprocess.Popen(cmd_deploy_db, shell=True, stdout=subprocess.PIPE, \
                                   stderr=subprocess.PIPE)

        out, err =  process.communicate()

        if process.returncode == 0:
            logging.info(out)
            print "Deploy db  -SUCCESS"
            print "Deploy in progress ..."
            time.sleep(60)
        else:
            logging.error(err)
            print "Deploy db - FAILED"
            exit()


        cmd_deploy_rmq = "docker run -m 2g -d --hostname rmq --restart=always \
        --name apporbit-rmq -d " + repo_str + "/apporbit/apporbit-rmq"

        process = subprocess.Popen(cmd_deploy_rmq, shell=True, stdout=subprocess.PIPE, \
                                   stderr=subprocess.PIPE)

        out, err =  process.communicate()

        if process.returncode == 0:
            logging.info(out)
            print "Deploy rmq - SUCCESS"
            print "Deploy in progress ..."
            time.sleep(20)
        else:
            logging.warning(err)
            print "Deploy rmq - FAILED"
            exit()

        internal_repo = "http://repos.gsintlab.com/repos/"
        cmd_deploy_services = "docker run -t --name apporbit-services --restart=always \
        -e GEMINI_INT_REPO=" + internal_repo + " -e CHEF_URL=https://" + host_ip +":9443 -e MYSQL_HOST=db \
        -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=apporbit_mist \
        -e GEMINI_STACK_IPANEMA=1 --link db:db --link apporbit-rmq:rmq \
        -v /var/lib/apporbit/sshKey_root:/root --volumes-from apporbit-chef \
        -v /var/log/apporbit/services:/var/log/apporbit -d  \
        "+ repo_str +"/apporbit/apporbit-services"


        process = subprocess.Popen(cmd_deploy_services, shell=True, stdout=subprocess.PIPE, \
                                   stderr=subprocess.PIPE)

        out, err =  process.communicate()

        if process.returncode == 0:
            logging.info(out)
            print "Deploy services - SUCCESS"
            print "Deploy in progress ..."
            time.sleep(20)
        else:
            logging.error(err)
            print "Deploy services - FAILED"
            exit()

        log_level = 'DEBUG'
        max_app_processes =1
        deploy_mode=1
        onpremmode = 'true'
        apiversion = 'v2'

        cmd_deploy_controller = "docker run -t --name apporbit-controller --restart=always \
        -p 80:80 -p 443:443 -e ONPREM_EMAIL_ID="+ email_id + " \
        -e LOG_LEVEL="+log_level + " -e MAX_POOL_SIZE=1 -e CHEF_URL=https://"+ host_ip +":9443 \
        -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=apporbit_controller \
        -e ON_PREM_MODE=" + onpremmode + " -e THEME_NAME="+ theme_name + "\
        -e CURRENT_API_VERSION=" + apiversion + " --link db:db --link apporbit-rmq:rmq \
        --volumes-from apporbit-chef -v /var/log/apporbit/controller:/var/log/apporbit \
        -v /var/lib/apporbit/sslkeystore/:/home/apporbit/apporbit-controller/sslkeystore \
        -d " + repo_str + "/apporbit/apporbit-controller"

        # print cmd_deploy_controller
        process = subprocess.Popen(cmd_deploy_controller, shell=True, stdout=subprocess.PIPE, \
                                   stderr=subprocess.PIPE)

        out, err =  process.communicate()

        if process.returncode == 0:
            logging.info(out)
            print "Deploy Controller - SUCCESS"
        else:
            logging.error(err)
            print "Deploy Controller - FAILED"
            exit()

        print "Apporbit Deploy completed - SUCCESS!"
        return True

    def removeRunningContainers(self):
        process = subprocess.Popen("docker ps -a ", shell=True, stdout=subprocess.PIPE, \
                                   stderr=subprocess.PIPE)
        out, err =  process.communicate()
        if process.returncode == 0:
            if "apporbit-chef" in out:
                logging.info( "apporbit-chef exist remove it")
                rmvprocess = subprocess.Popen("docker rm -f apporbit-chef", shell=True,\
                                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                rmvout, rmverr = rmvprocess.communicate()
                if rmvprocess.returncode == 0:
                    logging.info("Successfully removed apporbit-controller")
                else:
                    logging.warning(rmverr)

            if "apporbit-controller" in out:
                logging.info("apporbit-controller exist remove it")
                rmvprocess = subprocess.Popen("docker rm -f apporbit-controller", shell=True,\
                                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                rmvout, rmverr = rmvprocess.communicate()
                if rmvprocess.returncode == 0:
                    logging.info("Successfully removed apporbit-controller")
                else:
                    logging.warning(rmverr)

            if "apporbit-services" in out:
                logging.info( "apporapporbit-rmqbit-services exist remove it")
                rmvprocess = subprocess.Popen("docker rm -f apporbit-services", shell=True,\
                                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                rmvout, rmverr = rmvprocess.communicate()
                if rmvprocess.returncode == 0:
                    logging.info("Successfully removed apporbit-services")
                else:
                    logging.warning(rmverr)

            if  "db" in out:
                logging.info( "db container exist remove it")
                rmvprocess = subprocess.Popen("docker rm -f db", shell=True,\
                                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                rmvout, rmverr = rmvprocess.communicate()
                if rmvprocess.returncode == 0:
                    logging.info("Successfully removed apporbit-db")
                else:
                    logging.warning(rmverr)
            if "apporbit-rmq" in out:
                logging.info( "rmq container exist remove it")
                rmvprocess = subprocess.Popen("docker rm -f apporbit-rmq", shell=True,\
                                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                rmvout, rmverr = rmvprocess.communicate()
                if rmvprocess.returncode == 0:
                    logging.info("Successfully removed apporbit-rmq")
                else:
                    logging.warning(rmverr)
            if "apporbit-docs" in out:
                rmvprocess = subprocess.Popen("docker rm -f apporbit-docs", shell=True,\
                                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                rmvout, rmverr = rmvprocess.communicate()
                if rmvprocess.returncode == 0:
                    logging.info("Successfully removed apporbit-docs")
                else:
                    logging.warning(rmverr)

        return



    def clearOldEntries(self):
        logging.info("clean old entries to create freash setup STARTED!!!")
        try:
            shutil.rmtree('/var/dbstore', ignore_errors = True)
            shutil.rmtree('/var/lib/apporbit/', ignore_errors = True)
            shutil.rmtree('/var/log/apporbit/', ignore_errors = True)
        except OSError as e:
            logging.warning("Failed to clean old Entries : " + e.strerror)

        logging.info("Clean old entries COMPLETED !!!")
        return


    def setupDirectoriesForVolumeMount(self):
        logging.info("Setting up Directories for Volume Mount location  STARTED!!!")
        try:
            os.mkdir("/var/dbstore")
            os.mkdir("/var/log/apporbit")
            os.mkdir("/var/lib/apporbit")
            os.mkdir("/var/log/apporbit/controller")
            os.mkdir("/var/log/apporbit/services")
            os.mkdir("/var/lib/apporbit/sshKey_root")
            os.mkdir("/var/lib/apporbit/sslkeystore")
        except OSError as ose:
            logging.warning("could not create all the required directories" \
                             + ose.strerror)

        cmd_db_dir = "chcon -Rt svirt_sandbox_file_t /var/dbstore"
        cmd_sshkey = "chcon -Rt svirt_sandbox_file_t /var/lib/apporbit/sshKey_root"
        cmd_sslkey = "chcon -Rt svirt_sandbox_file_t /var/lib/apporbit/sslkeystore"
        cmd_services = "chcon -Rt svirt_sandbox_file_t /var/log/apporbit/services"
        cmd_controller = "chcon -Rt svirt_sandbox_file_t /var/log/apporbit/controller"

        process = subprocess.Popen(cmd_db_dir, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        if(process.returncode==0):
            # print out
            logging.info( out)
        else:
            logging.error(err)

        process = subprocess.Popen(cmd_sshkey, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        if(process.returncode==0):
            # print out
            logging.info(out)
        else:
            logging.error(err)

        process = subprocess.Popen(cmd_sslkey, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        if(process.returncode==0):
            # print out
            logging.info(out)
        else:
            logging.error(err)


        process = subprocess.Popen(cmd_services, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        if(process.returncode==0):
            # print out
            logging.info(out)
        else:
            logging.error(err)

        process = subprocess.Popen(cmd_controller, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        if(process.returncode==0):
            # print out
            logging.info(out)
        else:
            logging.error(err)


    def loginDockerRegistry(self, uname, passwd, repo_str = "secure-registry.gsintlab.com" ):
        print ("Login to Docker Registry ", repo_str)
        cmd_str = 'docker login -e='' -u=' + uname + ' -p=' + passwd +' '+ repo_str
        process = subprocess.Popen(cmd_str, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        if(process.returncode==0):
            print out
            print ("Login Success!")
        else:
            print err
            print ("Login Failed!")
            exit()
        return


    def pullImagesformRepos(self, repo_str):
        print repo_str
        controller_image = repo_str + '/apporbit/apporbit-controller'
        services_image = repo_str + '/apporbit/apporbit-services'
        message_queue_image = repo_str + '/apporbit/apporbit-rmq'
        docs_image = repo_str + '/apporbit/apporbit-docs'
        database_image = 'mysql:5.6.24'

        cmd_ctrl_image = 'docker pull ' + controller_image
        cmd_srvc_image = 'docker pull ' + services_image
        cmd_msgq_image = 'docker pull ' + message_queue_image
        cmd_docs_image = 'docker pull ' + docs_image
        cmd_dbs_image = 'docker pull ' + database_image

        process = subprocess.Popen(cmd_ctrl_image, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        if(process.returncode==0):
            # print out
            logging.info(out)

        else:
            logging.warning(err)
            print ("Getting Image Failed. Check log for details")
            exit()

        process = subprocess.Popen(cmd_srvc_image, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        if(process.returncode==0):
            # print out
            logging.info(out)

        else:
            logging.warning(err)
            print ("Getting Image Failed. Check log for details")
            exit()

        process = subprocess.Popen(cmd_msgq_image, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        if(process.returncode==0):
            # print out
            logging.info(out)

        else:
            logging.warning(err)
            print ("Getting Image Failed. Check log for details")
            exit()

        process = subprocess.Popen(cmd_docs_image, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        if(process.returncode==0):
            # print out
            logging.info(out)

        else:
            logging.warning(err)
            print ("Getting Image Failed. Check log for details")
            exit()

        process = subprocess.Popen(cmd_dbs_image, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        if(process.returncode==0):
            # print out
            logging.info(out)

        else:
            logging.warning(err)
            print ("Getting Image Failed. Check log for details")
            exit()
