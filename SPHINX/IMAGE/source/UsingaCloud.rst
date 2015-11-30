**Using a Cloud**
-----------------

Use the appOrbit Platform Cloud feature to register and connect to
generic collections related to each cloud provider you want to use with
specific user credentials, or to register a private cloud.

appOrbit Platform supports the following cloud providers:

-   Amazon Web Services

-   Microsoft Azure

-   Rackspace

-   OpenStack including the Havana (and later versions), Nova, Neutron,
    > Cinder and Glance with Keystone v2 or v3 modules are used in any
    > OpenStack deployment.

The appOrbit Platform also allows you to register custom cloud to
register a private cloud using the access credentials of the physical
hosts.

The appOrbit Platform cloud feature allows you to:

-   Register each type of public cloud provider that you want to use.

-   Register a custom cloud when you are using a private cloud.

-   View cloud details.

-   Edit cloud details.

-   Remove a cloud.

-   Setup cloud permissions to delegate access to a selected cloud.

Each of these procedures is described in a separate topic.

### **To register a cloud provider**

1.  Click **CLOUDS**.

2.  Click **Add Cloud** to register one or more clouds by the
    > cloud type.

**Note**: You can create multiple clouds of the same type as needed,
such as to support different environments. In this case, each cloud
needs to be registered with a unique name.

![](media/image22.jpg)

1.  On the initial Add Cloud popup, select the Cloud Type that you want
    > to register.

2.  Click **OK**.

3.  **Note**: Both the OpenStack and the Custom Cloud types can be used
    > to create a private cloud.

4.  ![](media/image25.png)

<!-- -->

1.  On the next Add Cloud popup, enter the details for the Cloud Type
    > you selected.

2.  Click **OK**. Once each cloud is setup, it is displayed on the
    > Clouds page.

3.  The cloud details shown depend on the type of cloud you select, as
    > described below.

4.  **For AWS (Amazon Web Services)**

![](media/image06.jpg)

The cloud details include:

-   **Cloud Type**: Displays AWS.

-   **Cloud Name**: Type the name you want to use to identify the
    > AWS cloud.

-   **API Key**: Type the reference key for user access to the
    > AWS cloud.

-   **Secret Key**: Type the reference credentials for the AWS cloud.

-   **appOrbit Appliance IP**: Type the IP address that allows appOrbit
    > Platform to connect to the cloud.

**For Microsoft Azure**

![](media/image27.jpg)

The cloud details include:

-   **Cloud Type**: Displays Azure.

-   **Cloud Name**: Type the name you want to use to identify the
    > Azure cloud.

-   **Azure URL**: Displays the URL for the Azure cloud. You can change
    > the URL by typing another address as needed.

-   **Subscription ID**: Type the subscription ID for the Azure cloud.

-   **JKS Certificate**: Type the location of the Java Key Store (JKS)
    > certificate for the Azure cloud, or click Browse to select
    > the location.

-   **JKS Password**: Type the JKZ password.

-   **appOrbit Appliance IP**: Type the IP address that allows the
    > appOrbit Platform to connect to the cloud.

**For OpenStack**

![](media/image19.jpg)

The cloud details include:

-   **Cloud Type**: Displays OpenStack.

-   **Cloud Name**: Type the name you want to use to identify the
    > OpenStack cloud.

-   **KeyStone API URL**: Type the URL of the Keystone identity service
    > for the OpenStack cloud.

-   **User Name**: Type the username.

-   **Password**: Type the password.

-   **Domain Name**: Use the default domain name or type a domain name
    > for the OpenStack cloud.

-   **Project Name**: Type the project name.

**For Rackspace**

![](media/image20.jpg)

The cloud details include:

-   **Cloud Type**: Displays Rackspace.

-   **Cloud Name**: Type the name you want to use to identify the
    > Rackspace cloud.

-   **Username**: Type the username.

-   **API Key**: Type the API key for the Rackspace cloud.

-   **appOrbit Appliance IP**: Type the IP address that allows the
    > appOrbit Platform to connect to the cloud.

1.  Click **Next** to register the cloud. A progress bar is shown while
    > the cloud configuration is being completed.

### **To register a custom cloud**

1.  Click **CLOUDS**.

<!-- -->

1.  Click **Add Cloud**. On the initial Add Cloud popup, click
    > **Custom**.

2.  **Note**: The Custom Cloud type can be used to register a
    > private cloud.

3.  Click **OK**.

4.  

![](media/image18.jpg)

1.  On the Add Cloud popup for a custom cloud, type the **Cloud Name**
    > you want to use to identify the custom cloud. Click **Add Cloud**.
    > The custom cloud you registered is shown on the Clouds page.

![](media/image21.jpg)

### **To view registered clouds**

1.  Click **CLOUDS**. The Clouds page displays a high level status of
    > each of the registered clouds.

<!-- -->

1.  Once each cloud is set up, it is displayed on the Clouds page.

2.  **Note**: When you initially set up a cloud, the Cluster field
    > is blank.

![](media/image23.jpg)

The cloud details include:

-   **Type**: Displays the type of cloud.

-   **Name**: Displays the identity of the cloud. You can click the
    > cloud name to view the details of the clusters in each cloud. For
    > more information, go to “Creating Clusters”.

-   **Clusters**: Displays the number of clusters in the cloud.

-   **Actions**: Displays the actions you can perform based on
    > your permissions. For more information, go to “To set
    > up permissions”.

-   You can use Actions to:

-   Click pencil icon to edit the cloud details, including updating the
    > cloud credentials.

-   Click trash icon to permanently remove a registered cloud.

-   Each of these procedures is described in a separate topic.

### **\[JJ1\] To edit cloud details**

1.  Click **CLOUDS**. The Clouds page displays a high level status of
    > each of the registered clouds.

![](media/image05.jpg)

1.  Under Actions, click pencil icon next to the cloud you want to edit.
    > You can edit the cloud details and update the cloud credentials.

-   **Actions**: Allows you to select the pencil icon and trash icon
    > actions based on your permissions. For more information, go to “To
    > set up cloud permissions”.

1.  On Edit Cloud page, you can update the cloud credentials for the
    > selected Cloud Type when these settings have changed, such as the
    > API Key and Secret Key in the sample below.

2.  **Note**: The entries for the cloud details vary depending on the
    > type of cloud selected. For more information, go to “To register
    > a cloud”.

3.  Click **Next**.

![](media/image07.jpg)

A progress bar is shown while the cloud configuration is being
completed.

### **To remove a cloud**

1.  Click **CLOUDS**. The Clouds page displays a high level status of
    > each of the registered clouds.

2.  Under Actions, click trash icon next to the registered cloud you
    > want to remove.

-   **Actions**: Allows you to select the pencil icon and trash icon
    > actions based on your permissions. For more information, go to “To
    > set up cloud permissions”.

**IMPORTANT**: Before you can remove a registered cloud, you need to
delete all of the clusters that are associated with the selected cloud.

1.  Click **Next**. A confirmation message is displayed.

2.  **IMPORTANT**: Remove a cluster only when it is entirely necessary.
    > When you delete a cloud, it is permanently removed
    > and unrecoverable.

![](media/image28.jpg)

1.  Click **OK** to remove the cloud.

2.  A progress bar is shown while the deletion is being completed. When
    > you delete a cloud, it is permanently removed and unrecoverable.

### **To set up cloud permissions**

1.  Click **CLOUDS**.

2.  On the Clouds page, select the Name of the cloud you want to use.

3.  **Note**: Before you can set up cloud permissions, the cloud needs
    > to contain one or more clusters.

![](media/image08.jpg)

1.  On the CLUSTERS tab, click **PERMISSIONS**.

![](media/image17.png)

1.  On the PERMISSIONS tab, click the appropriate checkbox to grant
    > access to view, edit, delete and scan information for the
    > selected cloud.

2.  You can select all of the permission levels to grant the user full
    > admin access.

3.  The administrator permissions levels include these roles:

-   **Administrator**: Allows the admin permission to perform both the
    > Application Developer and Applications Admin roles.

-   **Application Developer**: Allows the admin permission to perform
    > application-related operations.

-   **Operations Admin**: Allows the admin permission to edit, create
    > and update clouds, clusters and data catalogs.

![](media/image29.jpg)

1.  Click **Save** to return to the appOrbit Platform dashboard.
