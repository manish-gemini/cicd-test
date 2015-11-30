**Configuring appOrbit Platform**
=================================

The appOrbit Platform allows you to enable and update the system
settings for the platform.

The appOrbit Platform configuration settings allow you to:

-   Use appOrbit Chef settings.

-   Use Docker Registry settings.

-   Use Licensing details.

-   Use the Simple Mail Transfer Protocol (SMTP) settings.

Each of these procedures is described in a separate topic.

### **To use appOrbit Chef settings**

1.  Click settings icon to display the appOrbit Platform settings.

2.  The CHEF SETTINGS tab is displayed.

3.  **IMPORTANT**: Change the appOrbit Chef setting only when either of
    > the following conditions exists:

-   You are not using the default appOrbit Chef deployment.

-   The appOrbit Chef certificates have changed and the controller is
    > not communicating with appOrbit Chef Server.

![](media/image05.png)

The CHEF SETTINGS include:

-   **Chef URL**: Use one of the following:

-   URL of the appOrbit Chef Server (host IP 9443), when you installed
    > appOrbit Chef Server from HTTPS://&lt;*ip address*&gt;:9443/.

-   Correct URL when appOrbit Chef Server is deployed on a different
    > machine, and include any port numbers as needed.

-   **Organization name**: Organization name used to identify appOrbit
    > Chef Server.

-   The default name is Chef.

-   **Host key**: appOrbit Chef Server host key.

-   **Validation Key**: appOrbit Chef Server validation key.

-   **Username**: Name used to communicate with appOrbit Chef Server.

-   The default Username is admin.

1.  Click **Save** to store the settings.

### **To use Docker Registry settings**

1.  Click settings icon to display the appOrbit Platform settings.

![](media/image15.png)

1.  On the CHEF SETTINGS tab, click DOCKER REGISTRY.

![](media/image06.png)

1.  On the DOCKER REGISTRY tab, the Docker Registry setting includes:

-   **Docker Registry URL**: Specifies the internal Docker Registry from
    > which the Docker images are retrieved in the nodes. This global
    > default value is used when a new cluster is created.

-   **Note**: You are allowed to change the Docker Registry URL in the
    > cluster setup when you are using a private Docker registry to
    > retrieve the Docker images.

-   The Docker Registry URL setting is either:

-   Docker Registry URL (the default). In this case, the URL is applied
    > to all new cluster creations.

-   No default value. In this case, Docker Hub repository is used as the
    > source for all Docker images.

1.  Click **Save** to store the settings.

### **To use Licensing details**

1.  Click settings icon to display the appOrbit Platform settings.

![](media/image08.png)

1.  On the CHEF SETTINGS tab, click **LICENSING**.

![](media/image10.png)

1.  On the LICENSING tab, the Licensing Details setting includes:

-   **Enter License key:** Specifies the License key of the
    > appOrbit Platform.

-   To upgrade the license key, cut and paste the contents of
    > /tmp/GeminiPackages/100UserLicense.pdf in this field.

1.  Click **Save** to store the settings.

![](media/image09.png)

### **To use SMTP settings**

1.  Click settings icon to display the appOrbit Platform settings.

2.  **Note**: Use this procedure only after you receive an email to
    > reset your password.

![](media/image13.png)

1.  On the CHEF SETTINGS tab, click **MAIL**.

![](media/image14.png)

On the MAIL tab, the Simple Mail Transfer Protocol (SMTP) settings
include:

-   **Address**: IP address of the SMTP server.

-   **Port**: SMTP server port.

-   **UserName**: Optional username if the SMTP server needs
    > authentication

-   **Password**: Optional password if the SMTP server needs
    > authentication

-   **Authentication type**: Authentication types include an
    > Open (non-secured) or Secured connection.

-   **Enable STARTTLS**: STARTTLS is used encrypt plain text connections
    > using TLS (or SSL) rather than use a designated port for
    > encrypted emails.

1.  Click **Save** to store the settings.
