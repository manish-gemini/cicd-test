**Command Line Interface**
==========================

The specification for the command-line interface (CLI) of the Gemini
Management platform is described below. The CLI provides a complete
interface via a command-shell to use with the Gemini Management platform
for web-scale applications.

The CLI specification is divided into two sections. The parameters to
start and control the Gemini Management Server and the ability to pass
commands to the Gemini Management Server.

**Downloading the Command Line Tool**
-------------------------------------

### **To download the command line tool **

To be added.

**Command Line Format**
-----------------------

### **Usage**

**apporbit \[OPTIONS\] COMMAND \[arg...\]**

**Note**: The term “apporbit” is all lowercase when used in the command
line interface.

### **Options**

-D,| --debug=false | Enable debug mode

Do we need an option for blocking v/s non-blocking operations? Print
version information and quit.

### **Commands**

For more information about a command:

**Run 'apporbit COMMAND**

  > **Apporbit command**              > **Definition**
  ----------------------------------- -----------------------------------------------------------------
  > search                            > Search for an object by name, tag, type or id.
  > tag                               > Tag an object.
  > props                             > Show properties including tags on an object.
  > version                           > Show the Apporbit version information.
  > info                              > Display system-wide information.
  > login                             > Register or log in to the Apporbit server.
  > logout                            > Log out from the Apporbit server.
  > **apporbit app**                  
  > clone                             > Clone an application.
  > snap                              > Snapshot an application.
  > restore                           > Restore an application from a snapshot.
  > promote                           > Promote an application to the next stage.
  > start                             > Start an application.
  > stop                              > Stop an application.
  > pause                             > Pause an application.
  > export                            > Stream the contents of a container as a tar archive.
  > history                           > Show the history of an application.
  > list                              > List applications.
  > enum                              > Enumerate list of containers for the application.
  > delete                            > Delete an application.
  > cost                              > Show the cost model for the app.
  > **apporbit blueprint**            
  > create                            > Create a new application blueprint.
  > diff                              > Inspect changes between two blueprints.
  > import                            > Import Application Blueprint file.
  > deploy                            > Deploy an application from a blueprint.
  > update                            > Update an existing application blueprint.
  > delete                            > Delete an application blueprint.
  > **apporbit monitor**              
  > events                            > Get real time events from the server.
  > inspect &lt;application\_id&gt;   > Return low-level information on an application.
  > logs                              > Fetch the logs of an application, container or VM.
  > **apporbit cloud**                
  > list                              > List clouds
  > create                            > Add a new cloud to manage.
  > update                            > Update an existing clouds properties.
  > delete                            > Delete an existing cloud.
  > **apporbit clusters**             
  > list                              > List clusters.
  > create                            > Create a cluster.
  > update                            > Update a cluster, add/delete VMs.
  > delete                            > Delete a cluster.
  > exec                              > Run a command on an individual node in the cluster.
  > lifecycle                         > Add 1 or more clusters to a lifecycle stage e.g. Development.
  > **apporbit system**               
  > directory                         > Add, edit the directory server info.
  > users                             
  > wait                              > Block until an app stops, then print its exit code ??

**Table x. Examples of appOrbit CLI commands and usage**

  ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  **Command**                                                                           **Usage**
  ------------------------------------------------------------------------------------- ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  **For Help**                                                                          Use –h
                                                                                        
                                                                                        For example:
                                                                                        
                                                                                        apporbit app status -h
                                                                                        
                                                                                        apporbit app deploy -h

  **First logon**                                                                       apporbit login -e &lt;email&gt; -p &lt;pswd&gt; -s http://&lt;ip address&gt;
                                                                                        
                                                                                        OR
                                                                                        
                                                                                        apporbit login (and specify input params when prompted for)

  **Get list of clouds**                                                                apporbit cloud list

  **Get list of clusters**                                                              apporbit cluster list
                                                                                        
                                                                                        ASSUME:
                                                                                        
                                                                                        · application ID is 1
                                                                                        
                                                                                        · target cluster ID is 1
                                                                                        
                                                                                        · snapshot ID is 1
                                                                                        
                                                                                        · repeat interval is 4 seconds
                                                                                        
                                                                                        Change them suitably as needed.

  **Deploy application on cluster and continuously watch its status**                   apporbit app deploy -i 1 -t 1
                                                                                        
                                                                                        apporbit app status -i 1 -a deploy -r 4

  **Get application details**                                                           apporbit app details -i 1
                                                                                        
                                                                                        **Note**: In the following, for Docker applications, the option target (-t) is optional and may be skipped. The application workflow needs to be executed on the deployed application.

  **Perform 'snap' workflow on an application and continuously watch its status**       apporbit app snap -i 1 -t 1
                                                                                        
                                                                                        apporbit app status -i 1 -a snap -r 4

  **Perform 'restore' workflow on an application and continuously watch its status**    apporbit app restore -i 1 -t 1 -s 1
                                                                                        
                                                                                        apporbit app status -i 1 -a restore -r 4

  **Perform 'clone' workflow on an application and continuously watch its status**      apporbit app clone -i 1 -t 1
                                                                                        
                                                                                        apporbit app status -i 1 -a clone -r 4

  **Perform 'undeploy' workflow on an application and continuously watch its status**   apporbit app undeploy -i 1 -t 1
                                                                                        
                                                                                        apporbit app status -i 1 -a undeploy -r 4

  **List blueprints**                                                                   apporbit blueprint list

  **Add a cluster**                                                                     apporbit cluster add
                                                                                        
                                                                                        Options include:
                                                                                        
                                                                                        · name, -n Cluster name
                                                                                        
                                                                                        · cloud, -I Cloud ID
                                                                                        
                                                                                        · data, -d Cluster data in JSON format or YML template that defines
                                                                                        
                                                                                        cluster data

  **Add (import) a blueprint**                                                          apporbit blueprint add
                                                                                        
                                                                                        Options include:
                                                                                        
                                                                                        · data, -d Blueprint data in JSON format or .YML template that
                                                                                        
                                                                                        defines blueprint data

  **Deploy a blueprint**                                                                apporbit blueprint deploy -i 1 -t 1 -n "MyCLINodeJSApp" -g 1
                                                                                        
  **(and create a new application)**                                                    Options include:
                                                                                        
                                                                                        · id, -I Blueprint ID
                                                                                        
                                                                                        · target, -t Target Cluster ID
                                                                                        
                                                                                        · name, -n Application Name
                                                                                        
                                                                                        · group, -g Group ID

  **Get a cluster overview**                                                            apporbit cluster overview -i 4

  **Create a data catalog in a cluster**                                                apporbit cluster dc-create -i 4 -c "catalog-1-rax-1" -n "&lt;node&gt;" -s '\["100"\]' -t '\["SATA"\]'
                                                                                        
                                                                                        For OpenStack:
                                                                                        
                                                                                        apporbit cluster dc-create -i 4 -c "catalog-1-rax-1" -n "&lt;node&gt;" -s '\["10"\]' -t '\[""\]'

  **List snapshots**                                                                    apporbit snapshot list

  **Create data template**                                                              apporbit data-template create -i 1 -b 2 --dc 4-209.205.211.79 -g 1 -n 'Template 1'

  **List data templates**                                                               apporbit data-template list
  ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
