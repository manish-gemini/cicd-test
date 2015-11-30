**Supportability**
==================

Support Bundle is a utility that retrieves log information from the host
that is running the appOrbit containers and bundles it as an archive.
The Support Bundle script is provided with the Customer Deploy scripts.

When the Support Bundle script is run, log information is retrieved
from:

-   appOrbit Services container

-   appOrbit Controller container

-   appOrbit Database dumb

-   Logs of the host machine running appOrbit containers

-   Logs of the virtual machines created as a part of cluster creation
    > using the appOrbit Engine

The logs are collected and archived in the /opt directory. Each archive
uses the timestamp name to indicate when the log was generated.

### **To use Support Bundle**

1.  In the /Deploy Scripts directory, locate a file named,
    > apporbit-supportbundle.sh**.**

2.  Run the script with Root privileges:

3.  sh apporbit-supportbundle.sh

4.  The script collects and archives the logs described above and stores
    > the log bundle in the following file:

5.  /opt/var\_log\_apporbit06-08-11-16-2015.tar.gz
