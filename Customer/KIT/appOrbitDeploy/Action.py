import os
import logging
import subprocess
import time
import shutil
import multiprocessing
import re

import Config


class Action:

    def __init__(self):
        return

        # self.removeRunningContainers()
        #
        # if clean_setup == '1':
        #     self.clearOldEntries()
        #
        # self.setupDirectoriesForVolumeMount()
        #
        # if repo_str:
        #     self.loginDockerRegistry(uname, passwd, repo_str)
        #     self.pullImagesformRepos(repo_str)
        #
        # self.deployAppOrbit(deploy_mode, email_id, theme_name, host_ip, repo_str, cfg_mgr)


    def deployRMQ(self, reg_url):
        if not reg_url:
            reg_url = "secure-registry.gsintlab.com"

        rmq_image_name = reg_url + "/apporbit/apporbit-rmq"

        cmd_deploy_rmq = "docker run -m 2g -d --hostname rmq --restart=always \
        --name apporbit-rmq -d " + rmq_image_name
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


    def deployDocs(self):
        if not reg_url:
            reg_url = "secure-registry.gsintlab.com"

        rmq_image_name = reg_url + "/apporbit/apporbit-docs"

        cmd_image_pull = "docker pull " + rmq_image_name

        process = subprocess.Popen(cmd_image_pull, shell=True, stdout=subprocess.PIPE, \
                                   stderr=subprocess.PIPE)

        out, err =  process.communicate()

        if process.returncode == 0:
            logging.info(out)
        else:
            logging.error(err)
            print "pull docs image from repo. Check Logs for details - FAILED"
            exit()

        cmd_deploy_docs = "docker run --name apporbit-docs --restart=always -p 9080:80 -d " + rmq_image_name

        process = subprocess.Popen(cmd_deploy_docs, shell=True, stdout=subprocess.PIPE, \
                                   stderr=subprocess.PIPE)

        out, err =  process.communicate()

        if process.returncode == 0:
            logging.info(out)
        else:
            logging.error(err)
            print "pull docs image from repo. Check Logs for details - FAILED"
            exit()

        return

    def deployDB(self):
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


    def deployChef(self, host_ip, reg_url = ""):
        if reg_url:
            chef_image_name = reg_url + '/apporbit/apporbit-chef:1.0'
        else:
            chef_image_name = 'apporbit/apporbit-chef'

        cmd_chefDeploy = "docker run -m 2g -it --restart=always -p 9443:9443  \
        -v /etc/chef-server/ --name apporbit-chef -h "+ host_ip + " -d " + chef_image_name

        process = subprocess.Popen(cmd_chefDeploy, shell=True, stdout=subprocess.PIPE, \
                            stderr=subprocess.PIPE)

        out, err =  process.communicate()
        if process.returncode == 0:
            logging.info(out)
            print "Deploy Chef - SUCCESS"
            print "Deploy in progress ..."
            time.sleep(120)
        else:
            logging.error(err)
            print "Deploy Chef - FAILED"
            exit()

        return


    def deployServices(self, internal_repo, host_ip, repo_str, mode, vol_mount=''):
        # Varaiable Declaration
        image_name = ""
        vol_mount_str = ""

        if repo_str:
            image_name = repo_str + "/apporbit/apporbit-services"
        else:
            image_name = "apporbit/apporbit-services"

        if mode == '2' or '1':
            image_name = "apporbit/apporbit-services"

        if vol_mount:
            volonhost = vol_mount + "/Gemini-poc-stack"
            voloncontainer = "/home/apporbit/apporbit-services"
            vol_mount_str = " -v " + volonhost + ":" + voloncontainer


        cmd_deploy_services = "docker run -t --name apporbit-services --restart=always \
        -e GEMINI_INT_REPO=" + internal_repo + " -e CHEF_URL=https://" + host_ip +":9443 -e MYSQL_HOST=db \
        -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=apporbit_mist \
        -e GEMINI_STACK_IPANEMA=1 --link db:db --link apporbit-rmq:rmq \
        -v /var/lib/apporbit/sshKey_root:/root --volumes-from apporbit-chef \
        -v /var/log/apporbit/services:/var/log/apporbit" + vol_mount_str + " -d  \
        " + image_name

        # print cmd_deploy_services

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
        return


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


    def deployController (self, onprem_emailID, hostip,\
                              deploy_mode, theme_name,\
                              api_version, registry_url,\
                              build_deploy_mode, vol_mount = ""):

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
            cntrlimageName = registry_url + '/apporbit/apporbit-controller'
        else:
            cntrlimageName = 'apporbit/apporbit-controller'

        if build_deploy_mode == '2' or '1':
            cntrlimageName = 'apporbit/apporbit-controller'

        if vol_mount:
            volonhost = vol_mount + "/Gemini-poc-mgnt"
            voloncontainer = "/home/apporbit/apporbit-controller"
            vol_mount_str = " -v " + volonhost + ":" + voloncontainer

        cmd_deploy_controller = "docker run -t --name apporbit-controller --restart=always \
        -p 80:80 -p 443:443 -e ONPREM_EMAIL_ID="+ onprem_emailID + " \
        -e LOG_LEVEL="+log_level + " -e MAX_POOL_SIZE=" + str(max_phusion_process) +" \
        -e CHEF_URL=https://"+ hostip +":9443 \
        -e MYSQL_USERNAME=root -e MYSQL_PASSWORD=admin -e MYSQL_DATABASE=apporbit_controller \
        -e ON_PREM_MODE=" + onpremmode + " -e THEME_NAME="+ theme_name + "\
        -e CURRENT_API_VERSION=" + api_version + " --link db:db --link apporbit-rmq:rmq \
        --volumes-from apporbit-chef" + vol_mount_str + " -v /var/log/apporbit/controller:/var/log/apporbit \
        -v /var/lib/apporbit/sslkeystore/:/home/apporbit/apporbit-controller/sslkeystore \
        -d " + cntrlimageName

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

        return


    def createSelfSignedCert(self):
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

        return


    def deployAppOrbit(self, config_obj):
        print "Deploy in progress ..."
        # Remove Running Containers
        # If Clean Setup is 1 , It will remove chef as well other wise will retain chef server
        self.removeRunningContainers()

        # CLEAN or RETAIN OLD ENTRIES
        if config_obj.clean_setup == '1':
             self.clearOldEntries()

        # SETUP or CREATE DIRECTORIES for VOL MOUNT
        self.setupDirectoriesForVolumeMount()

        if config_obj.self_signed_crt == '1':
            self.createSelfSignedCert()


        # LOGIN to DOCKER REGISTRY
        if config_obj.build_deploy_mode == '3' or config_obj.build_deploy_mode == '0':
            self.loginDockerRegistry(config_obj.docker_uname, config_obj.docker_passwd, config_obj.registry_url)
            self.pullImagesformRepos(config_obj.registry_url)


        # DEPLOY CHEF CONTAINER
        if config_obj.deploy_chef == '1' or '3':
            self.deployChef(config_obj.hostip, config_obj.registry_url) #CUSTOMER DEPLOYMENT or Master Deployment
        elif config_obj.deploy_chef == '2':
            self.deployChef(config_obj.hostip)                        #LOCAL DEPLOYMENT- LOCAL IMAGE
        else:
            logging.info("Chef is chosen to be deployed in a different machine.")

        # DEPLOY DATABASE CONTAINER
        self.deployDB()

        #DEPLOY DOCS CONTAINER
        self.deployDocs()

        # DEPLOY RABBIT MQ
        self.deployRMQ(config_obj.registry_url)

        # DEPLOY SERVICES

        self.deployServices(config_obj.internal_repo, config_obj.hostip,\
                            config_obj.registry_url, config_obj.build_deploy_mode, config_obj.volume_mount)


        # DEPLOY PLATFORM
        self.deployController(config_obj.onprem_emailID, config_obj.hostip,\
                              config_obj.deploy_mode, config_obj.theme_name,\
                              config_obj.api_version, config_obj.registry_url,\
                              config_obj.build_deploy_mode, config_obj.volume_mount)

        print "Please change your chef password by logging into the UI."
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
        print "Login to Docker Registry " + repo_str
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
