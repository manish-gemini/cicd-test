
#!/usr/bin/python
import UserInteract
import Utility
import logging
import os

def main():
    logging.basicConfig(filename='appOrbitInstall.log', level=logging.DEBUG,
                        format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

    logging.info("Starting appOrbit Installation")
    logging.info("Verifying for pre-existing installation")

    userinteractObj = UserInteract.UserInteract()
    utilityObj = Utility.Utility()
    utilityObj.verifySystemInfo()
    logging.info("System info verification is completed!")

    utilityObj.fixSysRequirements()

    logging.info("fix System Requirements is completed!")

    if os.path.isfile('local.conf'):
        logging.info('Using local.conf file for deployment')
        userinteractObj.showConfigInfo('local.conf')
        utilityObj.deployFromFile('local.conf')
    else:
        logging.info("Starting to get user configuration.")
        userinteractObj.getUserConfigInfo()
        if not os.path.isfile('appobit_deploy.conf'):
            logging.error("ERROR: Deployment Configuration file not found!")
            print "Config file is missing! check log for more details."
            exit()

        utilityObj.deployFromFile('appobit_deploy.conf')

    return

if __name__ == "__main__":
    main()