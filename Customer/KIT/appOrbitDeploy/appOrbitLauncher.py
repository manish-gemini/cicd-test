#!/usr/bin/env python


import os
import logging
# Project Modules
import UserInteract
import Utility
import Config
import Action

def main():
    logging.basicConfig(filename='appOrbitInstall.log', level=logging.DEBUG,
                        format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

    logging.info("Starting appOrbit Installation")
    logging.info("Verifying for pre-existing installation")

    config_obj = Config.Config()
    userinteractObj = UserInteract.UserInteract()
    utilityObj = Utility.Utility()
    actionObj = Action.Action()

    # Will check all the System Requirements
    # Fail and exit if Not fixable Requirements like
    # Hardware Requirements are not satisfied
    # Fail but not exit with Fixable Reqruiements
    utilityObj.verifySystemInfo()
    logging.info("System info verification is completed!")

    # Will Fix all the Fixable Software Requriements
    # Will Fix Docker startup and
    # Seliux settings.
    if not utilityObj.fixSysRequirements():
        logging.error("Unable to auto fix System Requirments.")
        print ("Unable to auto fix systeme Requirements.\
         Check Log for details and fix it")
        exit()

    logging.info("fix System Requirements is completed!")

    # If local.conf file is available will proceed for Local Deployement
    # else will proceed with the Customer Deployment.
    # In Regular customer Deployment case we will not provide any config file.
    if os.path.isfile('local.conf'):
        logging.info('Using local.conf file for deployment')
        config_obj.loadConfig('local.conf')
        actionObj.deployAppOrbit(config_obj)
        # utilityObj.deployFromFile('local.conf')
        logging.info("END OF DEPLOYMENT")
    else:
        logging.info("Starting to get user configuration.")
        # Get User Configuration for Customer Deployment
        # and write to a config file apporit_deploy.conf
        userinteractObj.getUserConfigInfo(config_obj)
        config_obj.loadConfig('appobit_deploy.conf')
        logging.info("user configuration is recived SUCCESS.")

        # The User config file is read and processed, if not avilable exit
        if not os.path.isfile('appobit_deploy.conf'):
            logging.error("ERROR: Deployment Configuration file not found!")
            print "Config file is missing! check log for more details."
            exit()
        actionObj.deployAppOrbit(config_obj)
        # utilityObj.deployFromFile('appobit_deploy.conf')

        logging.info("END OF DEPLOYMENT")

    return

if __name__ == "__main__":
    main()