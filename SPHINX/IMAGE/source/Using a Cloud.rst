**Using a Cloud**
-----------------

The appOrbit Platform Cloud feature is used to register and connect to
generic collections related to each cloud provider with specific user
credentials, or to register a private cloud.

The appOrbit Platform supports the following public and private cloud
providers:

-   Amazon Web Services

-   Microsoft Azure

-   Rackspace

-   OpenStack including the Havana (and later versions), Nova, Neutron,
    > Cinder and Glance with Keystone v2 or v3 modules are used in any
    > OpenStack deployment.

The appOrbit Platform also allows you to register a private cloud using
the access credentials of the physical hosts.

The appOrbit Platform cloud feature allows you to:

-   Register a cloud provider.

-   Register a custom cloud.

-   View cloud details.

-   Edit cloud details.

-   Remove a cloud.

-   Setup cloud permissions to delegate access to a selected cloud.

Each of these procedures is described in a separate topic.

### **To register a cloud provider**

1.  Click **CLOUDS**.

2.  Click **Add Cloud** to register one or more clouds by the
    > cloud type.

> **Note**: You can add multiple clouds of the same type as needed. For
> example, you can register a number of AWS clouds to support different
> environments, such as the development, testing, staging and production
> environments. In this case, you need to register each cloud with a
> unique name.

3.  On the initial Add Cloud popup, select the Cloud Type that you want
    > to register.

4.  Click **OK**.

> **Note**: Both the OpenStack and the Custom Cloud types can be used to
> create a private cloud.

5.  On the next Add Cloud popup, enter the details for the Cloud Type
    > you selected.

6.  Click **OK**. Once each cloud is setup, it is displayed on the
    > Clouds page.

> The cloud details shown depend on the type of cloud you select, as
> described below.
>
> **For AWS (Amazon Web Services)**
>
> The cloud details include:

-   **Cloud Type**: Displays AWS.

-   **Cloud Name**: Type the name you want to use to identify the
    > AWS cloud.

-   **API Key**: Type the reference key for user access to the
    > AWS cloud.

-   **Secret Key**: Type the reference credentials for the AWS cloud.

-   **appOrbit Appliance IP**: Type the IP address that allows the
    > appOrbit Platform to connect to the cloud.

> **For Microsoft Azure**
>
> The cloud details include:

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

> **For OpenStack**
>
> The cloud details include:

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

> **For Rackspace**
>
> The cloud details include:

-   **Cloud Type**: Displays Rackspace.

-   **Cloud Name**: Type the name you want to use to identify the
    > Rackspace cloud.

-   **Username**: Type the username.

-   **API Key**: Type the API key for the Rackspace cloud.

-   **appOrbit Appliance IP**: Type the IP address that allows the
    > appOrbit Platform to connect to the cloud.

1.  Click **OK** to register the cloud. A progress bar is shown while
    > the cloud configuration is being completed.

### **To register a custom cloud**

1.  Click **CLOUDS**.

<!-- -->

2.  Click **Add Cloud**.

3.  On the initial Add Cloud popup, click **Custom**.

> **Note**: The Custom Cloud type is used to register a private cloud.

2.  Click **OK**.

3.  On the Add Cloud popup for a custom cloud, the cloud details
    > include:

-   **Cloud Type**: Displays Custom.

-   **Cloud Name**: Type the name you want to use to identify the
    > custom cloud.

2.  Click **Add Cloud**. The custom cloud you registered is shown on the
    > Clouds page.

### **To view registered clouds**

1.  Click **CLOUDS**. The Clouds page displays a high level status of
    > each of the registered clouds.

2.  Once each cloud is set up, it is displayed on the Clouds page.

> **Note**: When you initially set up a cloud, the Cluster field is
> blank.
>
> The cloud details include:

-   **Type**: Displays the type of cloud.

-   **Name**: Displays the identity of the cloud. You can click the
    > cloud name to view the details of the clusters in each cloud. For
    > more information, go to “Using a Cluster”.

-   **Clusters**: Displays the number of clusters in the cloud.

-   **Actions**: Displays the actions you can perform based on
    > your permissions. For more information, go to “To set up
    > cloud permissions”.

> You can use Actions to:

-   Click ![](media/image08.png) to edit the cloud details, including
    > updating the cloud credentials.

-   Click ![](media/image03.png) to permanently remove a
    > registered cloud.

> Each of these procedures is described in a separate topic.

### **To edit cloud details**

1.  Click **CLOUDS**. The Clouds page displays a high level status of
    > each of the registered clouds.

<!-- -->

2.  Under Actions, click ![](media/image06.png) next to the cloud you
    > want to edit. You can edit the cloud details and update the
    > cloud credentials.

-   **Actions**: Allows you to select ![](media/image09.png) and
    > ![](media/image05.png) based on your permissions. For more
    > information, go to “To set up cloud permissions”.

2.  On Edit Cloud page, you can update the cloud credentials for the
    > selected Cloud Type when these settings have changed, such as the
    > API Key and Secret Key in the sample below.

> **Note**: The entries for the cloud details vary depending on the type
> of cloud selected. For more information, go to “To register a cloud
> provider”.

2.  Click **Next**.

> A progress bar is shown while the cloud configuration is being
> completed.

### **To remove a cloud**

1.  Click **CLOUDS**. The Clouds page displays a high level status of
    > each of the registered clouds.

2.  Under Actions, click ![](media/image02.png) next to the registered
    > cloud you want to remove.

-   **Actions**: Allows you to select ![](media/image07.png) and
    > ![](media/image04.png) based on your permissions. For more
    > information, go to “To set up cloud permissions”.

> **IMPORTANT**: Before you can remove a registered cloud, you need to
> delete all of the clusters that are associated with the selected
> cloud.

1.  Click **Next**. A confirmation message displays.

> **IMPORTANT**: Remove a cluster only when it is entirely necessary.
> When you delete a cloud, it is permanently removed and unrecoverable.

1.  Click **OK** to remove the cloud.

> A progress bar is shown while the deletion is being completed. When
> you delete a cloud, it is permanently removed and unrecoverable.

### **To set up cloud permissions**

1.  Click **CLOUDS**.

2.  On the Clouds page, select the Name of the cloud you want to use.

> **Note**: Before you can set up cloud permissions, the cloud needs to
> contain one or more clusters.

1.  On the CLUSTERS tab, click **PERMISSIONS**.

2.  On the PERMISSIONS tab, click the appropriate checkbox to grant
    > access to view, edit and delete information for the
    > selected cloud.

> You can select all of the permission levels to grant the user full
> administrator access.
>
> The administrator permissions levels include these roles:

-   **Administrator**: Allows the admin permission to perform both the
    > Application Developer and Applications Admin roles.

-   **Application Developer**: Allows the admin permission to perform
    > application-related operations.

-   **Operations Admin**: Allows the admin permission to edit, create
    > and update clouds, clusters and data catalogs.

1.  Click **Save** to return to the appOrbit Platform dashboard.
