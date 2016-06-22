#!/usr/bin/env python


import logging
import os
import sys
# Project Modules
import config, utility, action, userinteract


def main():
    if not os.path.exists("/var/log/apporbit"):
       os.makedirs("/var/log/apporbit")

    logging.basicConfig(filename='/var/log/apporbit/Install.log', level=logging.DEBUG,
                         format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

    if len(sys.argv) > 1:
        if sys.argv[1] == "deploychef":
            chef_dep_obj = action.DeployChef()
            chef_dep_obj.deploy_chef()
            sys.exit(1)

    print ("This installer will install the appOrbit management server in this machine")
    logging.info("Starting appOrbit Installation")

    config_obj = config.Config()
    userinteract_obj = userinteract.UserInteract()
    utility_obj = utility.Utility()
    action_obj = action.Action()
    # Will check all the System Requirements
    # Fail and exit if Not fixable Requirements like
    # Hardware Requirements are not satisfied
    # Fail but not exit with Fixable Reqruiements
    print "Verifying system information."
    with utility.DotProgress("Verify"):
        utility_obj.progressBar(0)
        utility_obj.verifySystemInfo()
        logging.info("System info verification is completed!")

        # Will Fix all the Fixable Software Requriements
        # Will Fix Docker startup and
        # Seliux settings.
        if not utility_obj.fixSysRequirements():
            logging.error("Unable to auto fix System Requirments.")
            print "Unable to auto fix system Requirements. Check Log for details and fix it"
            sys.exit(1)
        utility_obj.progressBar(20)
    print "   -- [Done]"

    logging.info("fix System Requirements is completed!")

    # If local.conf file is available will proceed for Local Deployement
    # else will proceed with the Customer Deployment.
    # In Regular customer Deployment case we will not provide any config file.
    if os.path.isfile('local.conf'):
        logging.info('Using local.conf file for deployment')
        config_obj.loadConfig('local.conf')
    else:
        logging.info("Starting to get user configuration.")
        # Get User Configuration for Customer Deployment
        # and write to a config file apporbit_deploy.conf
        if utility_obj.isPreviousInstallSuccess():
            userinteract_obj.getUserConfigInfo(config_obj)
            utility_obj.createTempFile()
        else:
            previous_install = userinteract_obj.proceedWithPreviousInstall()
            if previous_install == "1":
                userinteract_obj.getUserConfigInfo(config_obj)
                utility_obj.createTempFile()

        # The User config file is read and processed, if not avilable exit
        if not os.path.isfile('apporbit_deploy.conf'):
            logging.error("ERROR: Deployment Configuration file not found!")
            # print "Config file is missing! check log for more details."
            sys.exit(1)
        config_obj.loadConfig('apporbit_deploy.conf')
        logging.info("user configuration is recived SUCCESS.")

    # Validate that the Hostip chosen during configuration belongs to the current host machine.
    if not utility_obj.validateHostIP(config_obj.hostip):
            print "ERROR: Host-IP or Host-Name entered is not valid. Check log for details."
            sys.exit(1)

    print "Deploying appOrbit management server."
    with utility.DotProgress("Deploy"):
        utility_obj.progressBar(0)
        action_obj.deployAppOrbit(config_obj)
	utility_obj.removeTempFile()
        utility_obj.progressBar(20)
    print "   -- [Done]"

    print "Now login to the appOrbit management server using https://" + config_obj.hostip + " with the default password 'admin1234'"
    logging.info("END OF DEPLOYMENT")

    return

if __name__ == "__main__":
    main()

