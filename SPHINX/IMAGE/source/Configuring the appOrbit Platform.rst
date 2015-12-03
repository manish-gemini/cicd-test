**Configuring the appOrbit Platform**
=====================================

The appOrbit Platform can be used to enable and update the configuration
settings.

The appOrbit Platform configuration settings allow you to:

-   Use appOrbit Chef settings.

-   Use Docker Registry settings.

-   Use Licensing details.

-   Use the Simple Mail Transfer Protocol (SMTP) settings.

Each of these procedures is described in a separate topic.

### **To use appOrbit Chef settings**

1.  Click ![](media/image04.png) to display the appOrbit
    > Platform settings.

> The CHEF SETTINGS tab is displayed.
>
> **IMPORTANT**: Change the appOrbit Chef setting only when either of
> the following conditions exists:

-   You are not using the default appOrbit Chef deployment.

> For more information, go to “appOrbit Deployment Scenarios”.

-   The appOrbit Chef certificates have changed and the appOrbit
    > Controller is not communicating with appOrbit Chef Server.

> For more information, go to “To change the appOrbit Chef default
> password”.
>
> The CHEF SETTINGS include:

-   **Chef URL**: Use one of the following:

-   URL of the appOrbit Chef Server (host IP 9443), when you installed
    > appOrbit Chef Server from HTTPS://&lt;*ip address*&gt;:9443/.

-   Correct URL when appOrbit Chef Server is deployed on a different
    > machine, and any port numbers when needed.

-   **Organization name**: Organization name used to identify appOrbit
    > Chef Server.

> The default name is Chef.

-   **Host key**: appOrbit Chef Server host key.

-   **Validation Key**: appOrbit Chef Server validation key.

-   **Username**: Name used to communicate with appOrbit Chef Server.

> The default Username is admin.

1.  Click **Save** to store the settings.

### **To use Docker Registry settings**

1.  Click ![](media/image02.png) to display the appOrbit
    > Platform settings.

2.  On the CHEF SETTINGS tab, click **DOCKER REGISTRY**.

3.  On the DOCKER REGISTRY tab, the Docker Registry setting includes:

-   **Docker Registry URL**: Specifies the default Docker Registry you
    > want to use as the source of all container images each time a new
    > cluster is created.

> Choose one of the following responses:

-   Type the **Docker Registry URL** of the private Docker Registry you
    > want to use as the default registry.

-   Leave this field blank. In this case, the public Docker Hub Registry
    > is used as the default registry.

> **Note**: You are allowed to change the Docker Registry URL each time
> you create a new cluster, such as when you want to use a different
> private Docker registry to retrieve the Docker images.

1.  Click **Save** to store the settings.

### **To use Licensing details**

1.  Click ![](media/image03.png) to display the appOrbit
    > Platform settings.

2.  On the CHEF SETTINGS tab, click **LICENSING**.

3.  On the LICENSING tab, the Licensing Details setting includes:

-   **Enter License key:** Specifies the License key of the
    > appOrbit Platform.

> To upgrade the license key, cut and paste the contents of
> /tmp/GeminiPackages/100UserLicense.pdf in this field.

1.  Click **Save** to store the settings.

### **To use SMTP settings**

1.  Click ![](media/image01.png) to display the appOrbit
    > Platform settings.

> **IMPORTANT**: Use this procedure only after you receive an email to
> reset your password.

1.  On the CHEF SETTINGS tab, click **MAIL**.

> On the MAIL tab, the Simple Mail Transfer Protocol (SMTP) settings
> include:

-   **Address**: IP address of the SMTP server.

-   **Port**: SMTP server port.

-   **UserName**: Optional username if the SMTP server needs
    > authentication

-   **Password**: Optional password if the SMTP server needs
    > authentication

-   **Authentication type**: Authentication types include an
    > Open (non-secured) or Secured connection.

-   **Enable STARTTLS**: STARTTLS is used encrypt plain text connections
    > using Transport Layer Security (TLS), or its predecessor Secure
    > Sockets Layer (SSL), rather than use a designated port for
    > encrypted emails.

1.  Click **Save** to store the settings.
