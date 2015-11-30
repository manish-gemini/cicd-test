**Deploying appOrbit Platform**
===============================

Use this topic to install and deploy appOrbit Platform including the
pre-requisite requirements, to verify the deployment in Docker PS, and
to change the default administrator password for appOrbit Platform.

### **Pre-requisite requirements**

Before you install and deploy appOrbit Platform, complete these
pre-requisite steps:

1.  Enter your License key (or Trial license provided on installation
    > for 60 days).

2.  Verify that you have your appOrbit Platform credentials on hand.
    > These credentials are provided by your appOrbit
    > Sales/Business representative. For example,
    > admin/&lt;*password*&gt;

Contact your Sales or Business representative if you have questions
about your appOrbit Platform credentials or require assistance.

### **To install appOrbit Platform**

1.  Verify that the firewall and cloud settings make ports 80, 443, 9443
    > and 8080 accessible from the internet.

2.  Run the following command to start the installation:

3.  **\# bash
    > &lt;(curl "http://repos.gsintlab.com/install/apporbit-curl.sh")**

4.  After the installation begins, the following prompt displays:

5.  Installing appOrbit Platform containers requires selinux to be
    > turned off.

6.  Do you want to continue (Y or N)?

7.  Type one of the following responses:

-   **Y** (Yes, the default) to disable selinux and continue with the
    > installation

-   **N** (No) to cancel the installation

-   A prompt for logon information about the appOrbit registry displays.

1.  Type your credentials (provided by your appOrbit Sales or
    > Business representative) to logon to appOrbit Docker Registry. The
    > logon credentials include the Username, Password and
    > Email address.

2.  Once you enter the logon information, the following prompts display:

3.  WARNING: login credentials saved in /root/.docker/config.json

4.  Logon Succeeded

5.  The following prompt displays:

6.  Enter the deployment scenario:

7.  Type Y (default) to install appOrbit Chef in the same machine as
    > appOrbit Platform.

8.  Type N to deploy appOrbit Chef to an external host.

9.  Type one the following responses:

-   **Y** (Yes, the default), when you want to deploy appOrbit Chef an
    > All in Private Network or All in Public Network deployment.

-   **N** (No), when you are using a Mixed Mode Deployment and want to
    > deploy appOrbit Chef to an external host in the public network.

The following prompt displays:

> Enter the appOrbit Chef installation type:

Type Y (default) to install appOrbit Chef.

Type N when appOrbit Chef is already deployed on a different machine.

1.  Type one of the following responses:

-   **Y** (Yes, the default) when you want to install appOrbit Chef on
    > the same machine as appOrbit Platform.

-   **N** (No) when appOrbit Chef is already deployed on a
    > different machine.

A confirmation message displays:

> Do you want to continue to deploy appOrbit Chef (Y or N)?

1.  Type one of the following responses:

-   **Y** (Yes, the default) to install appOrbit Chef from
    > Docker Registry.

-   **N** (No) to cancel the installation.

The following prompt displays:

> Enter the IP address for appOrbit Platform:

Type the Host IP (default is 52.11.51.251)

Type the IP that is used to access appOrbit Chef.

1.  Type one of the following responses:

-   Public IP address for the machine (the default is 52.11.51.251).

-   Public IP address that is used to access appOrbit Chef

When you install appOrbit Platform, the following prompt displays:

> Enter the deployment type:

Type 1 (default) to deploy from the Registry

Type 2 to deploy from the Tar file

1.  For the **Deployment Type**, type one of the following responses:

-   **1** (the default) to deploy appOrbit Platform from the Docker
    > Registry

-   **2** to deploy appOrbit Platform from a Tar file, when the internet
    > cannot be accessed

The next prompt is shown:

> Enter the Build ID (default is Latest):

1.  For the **Build ID**, type one of the following responses:

-   **Latest** (the default)

-   A specific version of the product

The following prompt displays:

> Do you want to clean up the setup (removes Database, RabbitMQ Data and
> so on)?

Type 1 (default) to clean the setup

Type 2 to retain the older entries

1.  Type one of the following responses:

-   **1** (the default) when you are installing appOrbit Platform for
    > the first time. This removes any older instances of
    > appOrbit Platform).

-   **2** to upgrade the setup and retain any older instances of
    > appOrbit Platform.

The next prompt displays:

> Mode of Operation:
>
> Type 1 (the default) for ON PREM MODE
>
> Type 2 for SAAS MODE

1.  For **Mode of Operation**, type one of the following responses:

-   **1** (ON PREM MODE, the default) when a single tenant is used

-   **2** (SaaS MODE) when a SaaS-based or multi-tenant setup is used

The next prompt is shown:

> Enter the Host IP (the default is 52.11.51.251):

1.  For the **Host IP**, type one of the following responses:

-   **52.11.51.251** (the default)

-   IP address of the host IP

1.  When the installation is complete, the Welcome to appOrbit
    > page displays.

2.  To logon to appOrbit Platform using the web interface, go to
    > “Logging On”.

### **To verify the deployment in Docker PS**

You can use Docker PS to verify that appOrbit Platform and all of the
containers in the machine are running properly.

To use Docker PS, type the following command at the Linux command
prompt:

**\# docker ps**

The output from this command is illustrated below.

![](media/image03.jpg)

**IMPORTANT**: When an error is encountered, and the appOrbit Platform
installation script is not completed correctly, you will need to
reinstall appOrbit Platform, or contact appOrbit Support for assistance.

### **To change the appOrbit Chef default password**

1.  Verify that the appOrbit Plaform is running properly.

2.  For details, go to “To verify the deployment in Docker PS”.

3.  Type **https://&lt;*IPaddress*&gt;:9443** to change your default
    > password using the appOrbit Chef Management user interface.

![](media/image02.jpg)

1.  On the Home page, type your credentials (provided by your appOrbit
    > Sales or Business representative):

-   **User Name**: appOrbit admin name (admin@geminisystems.net).

-   **Password**: Default password (admin1234).

Contact your Sales or Business representative if you have questions
about your appOrbit Platform credentials or require assistance.

1.  Click **login**.

![](media/image05.jpg)

1.  On the Edit user: admin page (Edit tab), type a new, secure
    > **Password** and **Password confirmation** for your appOrbit
    > admin account. Change the default password of the appOrbit Chef
    > Server from admin/p@ssw0rd1 to a new, secure password.

2.  **IMPORTANT**: Do not click the Regenerate Private Key checkbox.
    > Leave this field blank.

3.  Do not change appOrbit Platform certificates when you change
    > the password. Otherwise, the appOrbit Chef settings will require
    > updating, and the appOrbit Controller will not be able to
    > communicate with the appOrbit Chef Server.

4.  Click **Save User**.

5.  When complete, at the top, click **Logout admin** to exit appOrbit
    > Chef Management user interface.

6.  A confirmation displays.

7.  Click **OK**.

8.  The Home page of the appOrbit Chef Management user
    > interface displays.

9.  Close the user interface.
