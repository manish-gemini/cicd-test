#!/usr/bin/env python


import logging
import os
import sys
import shutil
import argparse
import datetime
import time
# Project Modules
import config, utility, action, userinteract


def main():
    CONF_FILE='setup.conf'
    if os.geteuid() != 0:
        sys.exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")

    if not os.path.exists("/var/log/apporbit"):
       os.makedirs("/var/log/apporbit")

    logging.basicConfig(filename='/var/log/apporbit/apporbit-server.log', level=logging.DEBUG,
                         format='[ %(asctime)s  %(levelname)s ] %(message)s', datefmt='%Y-%m-%dT%H:%M:%S')

    # arguments parser
    parser = argparse.ArgumentParser(description='apporbit-server to manage apporbit server')
    parser.add_argument("-d","--deploychef",action='store_true', help='Deploy chef enable flag')
    parser.add_argument("-c","--consul", action='store_true', help='Deploy consul')
    parser.add_argument("--setuponly", action='store_true', help='Setup appOrbit Server')
    parser.add_argument("--start", action='store_true', help='Start appOrbit Server')
    parser.add_argument("--stop", action='store_true', help='Stop appOrbit Server')
    parser.add_argument("--kill", action='store_true', help='Forcefully stop appOrbit Server')
    parser.add_argument("--restart", action='store_true', help='Restart appOrbit Server')
    parser.add_argument("--pullimages", action='store_true', help='Pull new versions of appOrbit Server images')
    parser.add_argument("--removedata", action='store_true', help='Remove Data in appOrbit Server')
    parser.add_argument("--removeconfig", action='store_true', help='Remove Config in appOrbit Server')
    parser.add_argument("--status", action='store_true', help='Show status of appOrbit Server')
    parser.add_argument("list",  nargs='*', help='List of components')
    args = parser.parse_args()
    if args.deploychef:
        chef_dep_obj = action.DeployChef()
        chef_dep_obj.deploy_chef()
        print "Chef Deployed"
        sys.exit(0)
    if args.consul:
        consul_obj = action.DeployConsul()
        consul_obj.deploy_consul()
        print "Consul Deployed"
        sys.exit(0)

    config_obj = config.Config()
    userinteract_obj = userinteract.UserInteract()
    utility_obj = utility.Utility()
    action_obj = action.Action()

    setupDone = False
    try:
      if (os.path.isfile(config_obj.apporbit_serverconf) 
           and os.path.isfile(config_obj.composeFile)
           and utility_obj.isPreviousInstallSuccess()
           ):
          setupRequired = False
          logging.info("Setup not required. Loading existing setup config")
          config_obj.loadConfig(config_obj.apporbit_serverconf)
      else:
          # This is the only visual clue that the product is not installed.
          print ("appOrbit server is not installed.")
          setupRequired = True
    except:
          #setupRequired = True
          raise
    skipSetup = False
    if not args.setuponly and (args.stop or args.kill or args.status or args.removedata or args.removeconfig):
       skipSetup = True

    if  args.setuponly or (setupRequired and not skipSetup):
        print ("This installer will install the appOrbit server in this machine")
        print ("Installation log will be in : /var/log/apporbit/apporbit-server.log")
        logging.info("Starting appOrbit Installation")

        # Will check all the System Requirements
        # Fail and exit if Not fixable Requirements like
        # Hardware Requirements are not satisfied
        # Fail but not exit with Fixable Reqruiements
        utility_obj.loadTempFile(config_obj)
        if not config_obj.systemreqs:
            print "Verifying system information."
            with utility.DotProgress("Verify"):
                utility_obj.progressBar(0)
                utility_obj.preSysRequirements(config_obj)
                utility_obj.verifySystemInfo()
                logging.info("System info verification is completed!")

                # Will Fix all the Fixable Software Requriements
                # Will Fix Docker startup and
                # Seliux settings.
                if not utility_obj.fixSysRequirements():
                    logging.error("Unable to auto fix System Requirements.")
                    print "Unable to auto fix system Requirements. Check Log for details and fix it"
                    sys.exit(1)
                utility_obj.progressBar(20)
            logging.info("fix System Requirements is completed!")
            config_obj.systemreqs = True
            print "   -- [Done]"
            utility_obj.createTempFile(config_obj)


        # If CONF_FILE file is available will proceed for Local Deployment
        # else will proceed with the Customer Deployment.
        # In Regular customer Deployment case we will not provide any config file.

        if os.path.isfile(CONF_FILE):
            logging.info('Using ' + CONF_FILE + ' file for deployment')
            config_obj.loadConfig(CONF_FILE)
        else:
            logging.info("Starting to get user configuration.")
            # Get User Configuration for Customer Deployment
            # and write to a config file apporbit_deploy.conf
            userinteract_obj.getUserConfigInfo(config_obj, utility_obj)
            utility_obj.createTempFile(config_obj)

        # Validate that the apporbit_host chosen during configuration belongs to the current host machine.
        if not utility_obj.validateHostIP(config_obj.apporbit_host):
            print "WARNING: Given Name/IP is not accessible publicly or on private network"
            if os.path.isfile(CONF_FILE):
                print "The install will proceed in 5 seconds with that Name/IP.. Break CTRL-C to stop"
                time.sleep(5)
            else:
                user_input = raw_input("Do you want to Abort(a) or continue(c) installation[c]:") or 'c'
                if user_input == "a" or user_input != "c":
                    sys.exit(1)
            print "Continuing .."

        # Setup configuration files
        print "\nConfiguring appOrbit setup"
        config_obj.setupConfig(utility_obj)

        print "Preparing and removing old containers for appOrbit server."
        with utility.DotProgress("Prepare"):
            utility_obj.progressBar(0)
            action_obj.predeployAppOrbit(config_obj)
            utility_obj.progressBar(20)
        print "   -- [Done]"

        if config_obj.remove_data:
            logging.warning("Removing old data")
            print "Removing old data for appOrbit server."
            action_obj.removeData(config_obj)

        if os.listdir(config_obj.APPORBIT_DATA):
            config_obj.initial_install = True

        if args.setuponly:
            utility_obj.removeTempFile()
            print "Requested setup only."
            print "Use apporbit-server --pullimages to pull images."
            print "Then use  apporbit-server --start to start appOrbit server."
            return

        print "Download  appOrbit Server container images"
        logging.info("Updating Images")
        with utility.DotProgress("Pull"):
            utility_obj.progressBar(0)
            action_obj.pullImages(config_obj)
            utility_obj.progressBar(20)
        print "   -- [Done]"


        print "Deploying appOrbit server."
        with utility.DotProgress("Deploy"):
            utility_obj.progressBar(0)
            action_obj.deployAppOrbitCompose(config_obj)
            utility_obj.progressBar(20)
	    utility_obj.removeTempFile()
        print "   -- [Done]"


        print "Now login to the appOrbit server using"
        print "https://" + config_obj.apporbit_host 
        print "Login: " + config_obj.apporbit_loginid 
        print "and default password 'admin1234'"
        logging.info("END OF DEPLOYMENT")

        logtimestamp = str(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
        shutil.move('/var/log/apporbit/apporbit-server.log', '/var/log/apporbit/apporbit-server-' + logtimestamp + '.log')
        print "Server logs moved to /var/log/apporbit/apporbit-server-" + logtimestamp + '.log'

    elif args.pullimages:
        print "Update  appOrbit Server images"
        logging.info("Updating Images")
        with utility.DotProgress("Pull"):
            utility_obj.progressBar(0)
            action_obj.pullImages(config_obj)
            utility_obj.progressBar(100)
        print "   -- [Done]"
    elif args.start: 
        print "Start appOrbit Server containers"
        logging.info("Starting Server")
        action_obj.deployAppOrbitCompose(config_obj, show=True)
        print " [Done]"
        print "Now login to the appOrbit server using"
        print "https://" + config_obj.apporbit_host 
    elif args.stop:
        print "Stop appOrbit Server containers"
        logging.info("Stopping Server")
        action_obj.removeCompose(config_obj, show=True)
        logging.info("Stopped Server")
        print " [Done]"
    elif args.kill:
        print "Stop and kill appOrbit Server containers"
        logging.info("Stopping and killing Server")
        action_obj.removeRunningContainers(config_obj, show=True)
        logging.info("Killed appOrbit Server")
        print "   -- [Done]"
    elif args.restart:
        complist = ' '.join(args.list)
        print "Restart appOrbit Server components:", complist
        logging.info("Restarting appOrbit Server components: %s" %complist)
        action_obj.restartAppOrbitCompose(config_obj, complist, show=True)
        logging.info("Restarted appOrbit Server")
        print " [Done]"
    elif args.removedata:
        logging.info("Requesting to remove data")
        if action_obj.showStatus(config_obj,show=False):
            print "Run apporbit-server --stop to stop containers before deleting data."
            logging.error("appOrbit server is running. Cannot delete data")
            return False
        else:
            logging.warning("REMOVING appOrbit server Volume data.")
            action_obj.removeData(config_obj)
            print "Removing appOrbit server data."
    elif args.removeconfig:
        logging.info("Requesting to remove setup configuration")
        if action_obj.showStatus(config_obj,show=False):
            print "Run apporbit-server --stop to stop containers before deleting setup configuration."
            logging.error("appOrbit server is running. Cannot delete setup configuration")
            return False
        else:
            logging.warning("REMOVING appOrbit server setup configuration.")
            action_obj.removeSetupConfig(config_obj)
            print "Removing appOrbit server setup configuration."
    elif args.status:
        # If product is not installed it will show above that it is not installed.
        # If it is installed then the next block will show the status of containers
        if os.path.isfile(config_obj.apporbit_serverconf):
            print "Showing status of appOrbit Server"
            action_obj.showStatus(config_obj, show=True)
    elif args.list:
        # if I am here I have not given any valid option but did enter a list argument
        complist = ' '.join(args.list)
        print 'Invalid arguments: ' + complist + '\n\n'
        parser.print_help()
    else:
        # No options and no list and product is already installed. Just show the status and help command
        print "appOrbit Server is already configured\n"
        action_obj.showStatus(config_obj,show=True)
        print ""
        parser.print_help()

    return

if __name__ == "__main__":
    main()

