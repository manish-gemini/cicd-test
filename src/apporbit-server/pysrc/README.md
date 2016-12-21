## AppOrbit Installer

The installer is created using pyInstaller. The installer **apporbit-server** is used to install the apporbit server on the host. The installer can be used to install the apporbit on online machine or an offline machine.

## Options in the installer ( use --help)

Below options can be used to install the apporbit server.

positional arguments:
  list              List of components

optional arguments:
  -h, --help        show this help message and exit
  -d, --deploychef  Deploy chef enable flag
  -c, --consul      Deploy consul
  --setuponly       Setup appOrbit Server
  --start           Start appOrbit Server
  --stop            Stop appOrbit Server
  --kill            Forcefully stop appOrbit Server
  --restart         Restart appOrbit Server
  --pullimages      Pull new versions of appOrbit Server images
  --removedata      Remove Data in appOrbit Server
  --removeconfig    Remove Config in appOrbit Server
  --removeall       Remove Data, Config and Keys in appOrbit Server
  --upgrade         Upgrade Setup
  --buildpackages   Fetch resources for offline installation
  --setupprovider   Set up provider machine for offline installation
  --deployoffline   Deploy apporbit on an offline host
  --offline         Install apporbit host offline (guided)
  --status          Show status of appOrbit Server


Of these options, **buildpackages**, **setupprovider**, **deployoffline** and **offline** are used to install apporbit server in offline mode.

## Offline Installation

To start with, use option --offline for guided installation. The installer will guide to use other option to complete the installation.

Or

One can use options to :
buildpackages  :-  [to be run on Online machine]
    to download the resources and packages that will be needed during the offline deployment
setupprovider  :-  [to be run on an offline machine called provider host]
    to set the offline docker registry and offline-repo on the setup in the same network on which the appOrbit host is to be deployed
deployoffline  :-  [to be run on an offline machine in the same local network as provider host]
    to deploy the apporbit server on the offline machine. Make sure to run installer with option --setupprovider on the provider host

Note :- The provider host and appOrbit host can be same
 

## Design and Changes

Four pyhton files are added to handle offline installation

1) docker.py           - to handle the basic docker operations like pull, tag, push, save, load etc.
2) resourcefetcher.py  - to fetch the resources and packages (appOrbit images) and created two compressed file appOrbitResources.tar and appOrbitPackages.tar.gz for provider and apporbit host respectively.
3) provider.py         - to do operations to set up the local docker registry and yum repository which will be needed for deploying apporbit server
4) offlinedeploy.py    - to deploy the apporbit server using the registries and repositories offline
