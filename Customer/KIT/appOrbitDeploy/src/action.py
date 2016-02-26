#!/usr/bin/env python

import logging
import multiprocessing
import os
import re
import shutil
import time

import utility


class Action:

    def __init__(self):
        self.utilityobj = utility.Utility()
        return


    def deployRMQ(self, reg_url):
        if not reg_url:
            reg_url = "secure-registry.gsintlab.com"

        rmq_image_name = reg_url + "/apporbit/apporbit-rmq"

        cmd_deploy_rmq = "docker run -m 2g -d --hostname rmq --restart=always \
        --name apporbit-rmq -d " + rmq_image_name
        try:
            code, out, err = self.utilityobj.cmdExecute(cmd_deploy_rmq)
            if code == 0:
                logging.info(out)
                #Sleep Added for safe start of containers
                time.sleep(10)
            else:
                logging.warning(err)
                print "Deploy rmq  -[FAILED]. Check logs for details."
                exit()
        except Exception as exp:
            logging.warning("Exception:Deploy rmq  -[FAILED]. %d : %s", exp.errno, exp.strerror)
            exit()



    def deployDocs(self, reg_url):
        if not reg_url:
            reg_url = "secure-registry.gsintlab.com"

        rmq_image_name = reg_url + "/apporbit/apporbit-docs"

        cmd_deploy_docs = "docker run --name apporbit-docs --restart=always -p 9080:80 -d " + rmq_image_name
        try:
            code, out, err = self.utilityobj.cmdExecute(cmd_deploy_docs)
            if code == 0:
                logging.info(out)
            else:
                logging.error(err)
                print "Deploy docs container - [FAILED] Check logs for details. "
                exit()
        except Exception as exp:
            logging.warning("Exception:Deploy docs container - [FAILED]. %d : %s", exp.errno, exp.strerror)
            exit()

        return True

    def deployDB(self):
        cmd_deploy_db = "docker run --name db --restart=always -e MYSQL_ROOT_PASSWORD=admin \
        -e MYSQL_USER=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=apporbit_controller \
        -v /var/dbstore:/var/lib/mysql -d mysql:5.6.24"
        try:
            code, out, err = self.utilityobj.cmdExecute(cmd_deploy_db)
            if code == 0:
                logging.info(out)
                # sleep added for mysql container to get completed started
                self.utilityobj.progressBar(11)
                time.sleep(60)
            else:
                logging.error(err)
                print "Deploy db container - [FAILED] Check logs for details. "
                exit()
        except Exception as exp:
            logging.warning("Exception:Deploy db container - [FAILED]. %d : %s", exp.errno, exp.strerror)
            exit()

        return  True


    def deployChef(self, host_ip, reg_url = ""):
        if reg_url:
            chef_image_name = reg_url + '/apporbit/apporbit-chef:1.0'
        else:
            chef_image_name = 'apporbit/apporbit-chef'

        cmd_chefDeploy = "docker run -m 2g -it --restart=always -p 9443:9443  \
        -v /etc/chef-server/ --name apporbit-chef -h "+ host_ip + " -d " + chef_image_name

        try:
            code, out, err = self.utilityobj.cmdExecute(cmd_chefDeploy)
            if code == 0:
                logging.info(out)
                # sleep added for chef container to start completely before other containers
                time.sleep(120)
            else:
                logging.error(err)
                print "Deploy chef container -[FAILED] Check logs for details. "
                exit()
        except Exception as exp:
            logging.warning("Exception:Deploy chef container -[FAILED]. %d : %s", exp.errno, exp.strerror)
            exit()

        return True


    def deployServices(self, config_obj):

        internal_repo = config_obj.internal_repo
        host_ip = config_obj.hostip
        repo_str = config_obj.registry_url
        mode = config_obj.build_deploy_mode
        vol_mount = config_obj.volume_mount
        deploy_chef = config_obj.deploy_chef

        # Varaiable Declaration
        image_name = ""
        vol_mount_str = ""

        if repo_str:
            image_name = repo_str + "/apporbit/apporbit-services:" + config_obj.buildid
        else:
            image_name = "apporbit/apporbit-services"

        if mode == '2' or mode == '1':
            image_name = "apporbit/apporbit-services"

        if vol_mount:
            volonhost = vol_mount + "/Gemini-poc-stack"
            voloncontainer = "/home/apporbit/apporbit-services"
            vol_mount_str = " -v " + volonhost + ":" + voloncontainer
            logging.info("volume mount str" + vol_mount_str)


        cmd_deploy_services = "docker run -t --name apporbit-services --restart=always \
        -e GEMINI_INT_REPO=" + internal_repo
        if deploy_chef == "1":
            cmd_deploy_services = cmd_deploy_services + " -e CHEF_URL=https://" + host_ip +":9443 "

        cmd_deploy_services = cmd_deploy_services + " -e MYSQL_HOST=db \
        -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=apporbit_mist \
        -e GEMINI_STACK_IPANEMA=1 --link db:db --link apporbit-rmq:rmq \
        -v /var/lib/apporbit/sshKey_root:/root "

        if deploy_chef == "1":
            cmd_deploy_services = cmd_deploy_services + "--volumes-from apporbit-chef "

        cmd_deploy_services = cmd_deploy_services + " -v /var/log/apporbit/services:/var/log/apporbit" + vol_mount_str + " -d  \
        " + image_name

        try:
            code, out, err = self.utilityobj.cmdExecute(cmd_deploy_services)
            if code == 0:
                logging.info(out)
                #Sleep added for safe start of container process before next container start
                time.sleep(10)
            else:
                logging.error(err)
                logging.error(cmd_deploy_services)
                print "Deploy deploy services container - [FAILED] Check logs for details. "
                exit()
        except Exception as exp:
            logging.warning("Exception:Deploy deploy services container -[FAILED]. %d : %s", exp.errno, exp.strerror)
            exit()
        return True


    def calcMaxPhusionProcess(self):
        logging.info( 'Max Pool Size' )
        cpu_count = multiprocessing.cpu_count()
        meminfo = open('/proc/meminfo').read()
        matched = re.search(r'^MemTotal:\s+(\d+)', meminfo)
        ram_size = int(matched.groups()[0])

        B = 1024
        KB = B * B
        ram_size_gb = ( ram_size + (KB - 1)/KB )
        ram_per_process = ( ram_size_gb + (cpu_count - 1)/cpu_count )

        adjvar1=75
        adjvar2=100

        if ram_per_process == 0 :
            ram_per_process = 1

        max_app_process = (ram_size_gb * adjvar1 )/( ram_per_process * adjvar2 )

        if max_app_process == 0:
            max_app_process = 1

        return max_app_process


    def deployController (self, config_obj):

        onprem_emailID = config_obj.onprem_emailID
        hostip = config_obj.hostip
        deploy_mode = config_obj.deploy_mode
        theme_name = config_obj.theme_name
        api_version = config_obj.api_version
        registry_url = config_obj.registry_url
        build_deploy_mode = config_obj.build_deploy_mode
        vol_mount = config_obj.volume_mount
        deploy_chef = config_obj.deploy_chef


        log_level = 'DEBUG'
        onpremmode = 'true'
        cntrlimageName = ''
        vol_mount_str = ''

        max_phusion_process = self.calcMaxPhusionProcess()

        if deploy_mode == '1':
            onpremmode = 'true'
        else:
            onpremmode = 'false'

        if registry_url:
            cntrlimageName = registry_url + '/apporbit/apporbit-controller:' + config_obj.buildid
        else:
            cntrlimageName = 'apporbit/apporbit-controller'

        if build_deploy_mode == '2' or build_deploy_mode == '1':
            cntrlimageName = 'apporbit/apporbit-controller'

        if vol_mount:
            volonhost = vol_mount + "/Gemini-poc-mgnt"
            voloncontainer = "/home/apporbit/apporbit-controller"
            vol_mount_str = " -v " + volonhost + ":" + voloncontainer

        cmd_deploy_controller = "docker run -t --name apporbit-controller --restart=always \
        -p 80:80 -p 443:443 -e ONPREM_EMAIL_ID="+ onprem_emailID + " \
        -e LOG_LEVEL="+log_level + " -e MAX_POOL_SIZE=" + str(max_phusion_process)

        if deploy_chef == "1":
            cmd_deploy_controller = cmd_deploy_controller + " -e CHEF_URL=https://"+ hostip +":9443"

        cmd_deploy_controller = cmd_deploy_controller + " -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=apporbit_controller \
        -e ON_PREM_MODE=" + onpremmode + " -e THEME_NAME="+ theme_name + "\
        -e CURRENT_API_VERSION=" + api_version + " --link db:db --link apporbit-rmq:rmq "
        if deploy_chef == "1":
            cmd_deploy_controller = cmd_deploy_controller + "--volumes-from apporbit-chef "

        cmd_deploy_controller = cmd_deploy_controller + vol_mount_str + " -v /var/log/apporbit/controller:/var/log/apporbit \
        -v /var/lib/apporbit/sslkeystore/:/home/apporbit/apporbit-controller/sslkeystore \
        -d " + cntrlimageName

        try:
            code, out, err = self.utilityobj.cmdExecute(cmd_deploy_controller)
            if code == 0:
                logging.info(out)
                # print "Deploy Controller - SUCCESS"
            else:
                logging.error(err)
                print "Deploy controllers container - [FAILED] Check logs for details."
                exit()
        except Exception as exp:
            logging.warning("Exception:Deploy controllers container -[FAILED]. %d : %s", exp.errno, exp.strerror)
            exit()
        return True


    def createSelfSignedCert(self):
        #Generate SSL Certificate
        cmd_sslcert = 'openssl req -new -newkey rsa:4096 -days 365 -nodes -x509 \
        -subj "/C=US/ST=NY/L=appOrbit/O=Dis/CN=www.apporbit.com" \
        -keyout /var/lib/apporbit/sslkeystore/apporbitserver.key \
        -out /var/lib/apporbit/sslkeystore/apporbitserver.crt'
        try:
            code, out, err = self.utilityobj.cmdExecute(cmd_sslcert)
            if code == 0:
                logging.info("SSL Certificate Create - SUCCESS. %s", out)
            else:
                logging.warning("SSL Certificate Create - Failed. %s", err)
                print "SSL Certificate Create - [FAILED] Check logs for details. "
                exit()
        except Exception as exp:
            logging.warning("Exception:SSL Certificate Create -[FAILED]. %d : %s", exp.errno, exp.strerror)
            exit()

        return True

    def copySSLCertificate(self, dir):

        sslkeyfile = dir + "/apporbitserver.key"
        sslkeycrt = dir + "/apporbitserver.crt"

        if not os.path.isfile(sslkeyfile):
            logging.error('%s SSL key file does not exist.', sslkeyfile)
            print "SSL key file does not exist. Check logs for details."
            exit()

        if not os.path.isfile(sslkeycrt):
            logging.error('%s SSL certificate file does not exist.', sslkeycrt)
            print "SSL certificate file does not exist. Check logs for details."
            exit()

        cmd_cpysslkey = "cp -f " + dir +"/apporbitserver.key /var/lib/apporbit/sslkeystore/apporbitserver.key"
        cmd_cpysslcrt = "cp -f " + dir +"/apporbitserver.crt /var/lib/apporbit/sslkeystore/apporbitserver.crt"

        try:
            code, out, err = self.utilityobj.cmdExecute(cmd_cpysslkey)
            if code == 0:
                logging.info("SSL key copy  - SUCCESS. %s", out)
            else:
                logging.warning("SSL key copy  - Failed. %s", err)
                print "Copy SSL key - [FAILED] Check logs for details. "
                exit()
        except Exception as exp:
            logging.warning("Exception:SSL key copy -[FAILED]. %d : %s", exp.errno, exp.strerror)
            exit()

        try:
            code, out, err = self.utilityobj.cmdExecute(cmd_cpysslcrt)
            if code == 0:
                logging.info("SSL Certificate copy - SUCCESS. %s", out)
            else:
                logging.warning("SSL Certificate copy - Failed. %s", err)
                print "Copy SSL Certificate - [FAILED] Check logs for details. "
                exit()
        except Exception as exp:
            logging.warning("Exception:SSL Certificate copy -[FAILED]. %d : %s", exp.errno, exp.strerror)
            exit()

        return True


    def deployAppOrbit(self, config_obj):
        self.utilityobj.progressBar(1)
        self.removeRunningContainers(config_obj)
        self.utilityobj.progressBar(2)

        # CLEAN or RETAIN OLD ENTRIES
        if config_obj.clean_setup == '1':
             self.clearOldEntries()

        # SETUP or CREATE DIRECTORIES for VOL MOUNT
        self.setupDirectoriesForVolumeMount()

        if config_obj.self_signed_crt == '1':
            self.createSelfSignedCert()
        else:
            logging.info("Copying SSL Certificate from the dir %s", config_obj.self_signed_crt_dir)
            self.copySSLCertificate(config_obj.self_signed_crt_dir)

        self.utilityobj.progressBar(3)
        # LOGIN to DOCKER REGISTRY
        if config_obj.build_deploy_mode == '3' or config_obj.build_deploy_mode == '0':
            self.loginDockerRegistry(config_obj.docker_uname, config_obj.docker_passwd, config_obj.registry_url)

            self.pullImagesformRepos(config_obj.registry_url, config_obj.buildid)


        # DEPLOY CHEF CONTAINER
        if config_obj.clean_setup == '1':
            if config_obj.deploy_chef == '1' or config_obj.deploy_chef == '3':
                self.deployChef(config_obj.hostip, config_obj.registry_url) #CUSTOMER DEPLOYMENT or Master Deployment
            elif config_obj.deploy_chef == '0':
                self.deployChef(config_obj.hostip)                        #LOCAL DEPLOYMENT- LOCAL IMAGE
            else:
                logging.info("Chef is chosen to be deployed in a different machine.")
        
        self.utilityobj.progressBar(10)

        # DEPLOY DATABASE CONTAINER
        self.deployDB()
        self.utilityobj.progressBar(12)
        #DEPLOY DOCS CONTAINER
        self.deployDocs(config_obj.registry_url)
        self.utilityobj.progressBar(14)
        # DEPLOY RABBIT MQ
        self.deployRMQ(config_obj.registry_url)
        self.utilityobj.progressBar(15)
        # DEPLOY SERVICES

        self.deployServices(config_obj)

        self.utilityobj.progressBar(17)
        # DEPLOY PLATFORM
        self.deployController(config_obj)
        self.utilityobj.progressBar(19)
        return True



    def removeRunningContainers(self, config_obj):
        cmd_dockerps = "docker ps -a "
        try:
            code, out, err = self.utilityobj.cmdExecute(cmd_dockerps)
            if code == 0:
                if config_obj.clean_setup == '1':
                    if "apporbit-chef" in out:
                        logging.info( "apporbit-chef exist remove it")
                        cmd_chef_rm = "docker rm -f apporbit-chef"
                        try:
                            code, out, err = self.utilityobj.cmdExecute(cmd_chef_rm)
                            if code == 0:
                                logging.info("Successfully removed apporbit-chef")
                            else:
                                logging.warning(err)
                        except Exception as exp:
                            logging.warning("Exception: Clean up chef container -[FAILED]. %d : %s", exp.errno, exp.strerror)
                            print "Clean up chef container - [FAILED]. Check logs for details."
                            exit()

                if "apporbit-controller" in out:
                    logging.info("apporbit-controller exist remove it")
                    cmd_controller_rm = "docker rm -f apporbit-controller"
                    try:
                        code, out, err = self.utilityobj.cmdExecute(cmd_controller_rm)
                        if code == 0:
                            logging.info("Successfully removed apporbit-controller")
                        else:
                            logging.warning(err)
                    except Exception as exp:
                        logging.warning("Exception: Clean up controller container -[FAILED]. %d : %s", exp.errno, exp.strerror)
                        print "Clean up controller container - [FAILED]. Check logs for details."
                        exit()

                if "apporbit-services" in out:
                    logging.info( "apporbit-rmq-services exist remove it")
                    cmd_services_rm = "docker rm -f apporbit-services"
                    try:
                        code, out, err = self.utilityobj.cmdExecute(cmd_services_rm)
                        if code == 0:
                            logging.info("Successfully removed apporbit-services")
                        else:
                            logging.warning(err)
                    except Exception as exp:
                        logging.warning("Exception: Clean up services container -[FAILED]. %d : %s", exp.errno, exp.strerror)
                        print "Clean up services container - [FAILED]. Check logs for details."
                        exit()

                if  "db" in out:
                    logging.info( "db container exist remove it")
                    cmd_db_rm = "docker rm -f db"
                    try:
                        code, out, err = self.utilityobj.cmdExecute(cmd_db_rm)
                        if code == 0:
                            logging.info("Successfully removed apporbit-db")
                        else:
                            logging.warning(err)
                    except Exception as exp:
                        logging.warning("Exception: Clean up database container -[FAILED]. %d : %s", exp.errno, exp.strerror)
                        print "Clean up database container - [FAILED]. Check logs for details."
                        exit()

                if "apporbit-rmq" in out:
                    logging.info( "rmq container exist remove it")
                    cmd_rmq_rm = "docker rm -f apporbit-rmq"
                    try:
                        code, out, err = self.utilityobj.cmdExecute(cmd_rmq_rm)
                        if code == 0:
                            logging.info("Successfully removed apporbit-rmq")
                        else:
                            logging.warning(err)
                    except Exception as exp:
                        logging.warning("Exception: Clean up message container -[FAILED]. %d : %s", exp.errno, exp.strerror)
                        print "Clean up message container - [FAILED]. Check logs for details."
                        exit()

                if "apporbit-docs" in out:
                    cmd_docs_rm = "docker rm -f apporbit-docs"
                    try:
                        code, out, err = self.utilityobj.cmdExecute(cmd_docs_rm)
                        if code == 0:
                            logging.info("Successfully removed apporbit-docs")
                        else:
                            logging.warning(err)
                    except Exception as exp:
                        logging.warning("Exception: Clean up document container -[FAILED]. %d : %s", exp.errno, exp.strerror)
                        print "Clean up document container - [FAILED]. Check logs for details."
                        exit()


        except Exception as exp:
            logging.warning("Exception:DOCKER PS -[FAILED]. %d : %s", exp.errno, exp.strerror)
            print "Getting Docker Running Process failed. Check log for more information."
            exit()

        return True

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

        try:
            code, out, err = self.utilityobj.cmdExecute(cmd_db_dir)
            if code == 0:
                logging.info( out)
            else:
                logging.error(err)

            code, out, err = self.utilityobj.cmdExecute(cmd_sshkey)
            if code == 0:
                logging.info( out)
            else:
                logging.error(err)

            code, out, err = self.utilityobj.cmdExecute(cmd_sslkey)
            if code == 0:
                logging.info( out)
            else:
                logging.error(err)

            code, out, err = self.utilityobj.cmdExecute(cmd_services)
            if code == 0:
                logging.info( out)
            else:
                logging.error(err)

            code, out, err = self.utilityobj.cmdExecute(cmd_controller)
            if code == 0:
                logging.info( out)
            else:
                logging.error(err)

        except Exception as exp:
            logging.warning("Exception: Setting folder permission -[FAILED]. %d : %s", exp.errno, exp.strerror)

        return True


    def loginDockerRegistry(self, uname, passwd, repo_str = "secure-registry.gsintlab.com" ):
        # print "Login to Docker Registry " + repo_str
        if passwd:
            cmd_str = 'docker login -e=admin@apporbit.com -u=' + uname + ' -p=' + passwd +' '+ repo_str
            code, out, err = self.utilityobj.cmdExecute(cmd_str)
            if code == 0:
                logging.info("Docker Login Success ")
                pass
            else:
                logging.error("Docker Login Failed ")
                print 'Docker login -[Failed]'
                exit()
        else:
            logging.error("Docker Login Failed ")
            print 'Docker login -[Failed!]'
            exit()

        return True


    def pullImagesformRepos(self, repo_str, build_id):
        controller_image = repo_str + '/apporbit/apporbit-controller:' + build_id
        services_image = repo_str + '/apporbit/apporbit-services:' + build_id
        message_queue_image = repo_str + '/apporbit/apporbit-rmq'
        docs_image = repo_str + '/apporbit/apporbit-docs'
        database_image = 'mysql:5.6.24'

        cmd_ctrl_image = 'docker pull ' + controller_image
        cmd_srvc_image = 'docker pull ' + services_image
        cmd_msg_image = 'docker pull ' + message_queue_image
        cmd_docs_image = 'docker pull ' + docs_image
        cmd_dbs_image = 'docker pull ' + database_image


        try:
            code, out, err = self.utilityobj.cmdExecute(cmd_ctrl_image)
            if code == 0:
                logging.info(out)
            else:
                logging.warning(err)
                print "Getting images for repo  - [Failed]. Check log for details"
                exit()

            self.utilityobj.progressBar(4)

            code, out, err = self.utilityobj.cmdExecute(cmd_srvc_image)
            if code == 0:
                logging.info(out)
            else:
                logging.warning(err)
                print "Getting images for repo  - [Failed]. Check log for details"
                exit()

            self.utilityobj.progressBar(5)

            code, out, err = self.utilityobj.cmdExecute(cmd_msg_image)
            if code == 0:
                logging.info(out)
            else:
                logging.warning(err)
                print "Getting images for repo  - [Failed]. Check log for details"
                exit()

            self.utilityobj.progressBar(6)

            code, out, err = self.utilityobj.cmdExecute(cmd_docs_image)
            if code == 0:
                logging.info(out)
            else:
                logging.warning(err)
                print "Getting images for repo  - [Failed]. Check log for details"
                exit()

            self.utilityobj.progressBar(7)

            code, out, err = self.utilityobj.cmdExecute(cmd_dbs_image)
            if code == 0:
                logging.info(out)
            else:
                logging.warning(err)
                print "Getting images for repo  - [Failed]. Check log for details"
                exit()

        except Exception as exp:
            logging.warning("Exception: Getting images for repo  -[FAILED]. %d : %s", exp.errno, exp.strerror)
            print "Getting images for repo  - Failed!. Check log for details."
            exit()