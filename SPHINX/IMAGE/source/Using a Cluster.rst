**Using a Cluster**
-------------------

Once you set up a cloud, the cloud can support one or more clusters,
such as to enable applications and data for different user groups. A
cluster is a collection of resources, also called a resource pool, for a
given cloud that is used to manage the applications and data
requirements. A cluster is also used to create the virtual machines for
the hosts that are used in a given cloud. The appOrbit Platform uses the
settings for each of the virtual hosts and other components to configure
and deploy applications and data.

The appOrbit Platform allows you to:

-   Create a cluster.

-   View cluster details.

-   Remove a cluster.

Each of these procedures is described in a separate topic.

### **To create a cluster**

1.  Click **CLOUDS**.

2.  On the Clouds page, select the Name of the cloud you want to use.

![](media/image10.jpg)

1.  One the Clusters tab, click **Create Cluster**. When you initially
    > set up a cloud, the Cluster tab is blank.

![](media/image17.jpg)

1.  Enter the cluster details.

2.  The cloud details shown for the cluster setup depend on the type of
    > cloud you select, as described below.

**For Microsoft Azure**

NEED A SCREEN SAMPLE HERE.

The cluster details include:

-   

**For AWS (Amazon Web Services)**

![](media/image18.jpg)

The cluster details include:

-   **Cluster Name**: Type the name you want to use to identify
    > the cluster.

-   **Group**: Select the group that is to use the cluster, including
    > the development, testing, staging and production environments.

-   **Deployment Spec**: Choose one of the following responses to select
    > the source you want to use for the deployment specification for
    > the selected cloud:

-   Click the checkbox (the default) to use the default deployment
    > specification, such as when you are setting up a new cloud.

-   Click to unmark the checkbox. Click **Browse** to select the
    > location of the deployment specification you want to use, for
    > example, when you are using an existing cloud setup.

-   **Region**: Select the region from which you want to create a
    > virtual machine.

-   **vPC**: For the region, select the virtual private cloud (vPC)
    > network definitions you want to use.

-   **Subnet**: For the vPC, select the subnet that you want to use.

-   **Registry**: If you are using a private Docker registry to retrieve
    > the Docker images, type the location for the registry. A private
    > Docker registry is used to supplement the public Docker registry.
    > If you do not enter a Registry location, the default Registry
    > setting is used.

-   **Note**: When the Registry/URL is blank, the global default value
    > is used when a new cluster is created to specify the internal
    > Docker Registry from which the Docker images are retrieved in
    > the nodes.

-   **Specify cluster resource properties**: Enter the details for each
    > resource that is used to create the cluster for a data node or a
    > compute only node.

-   **Note**: Each cluster setup requires at least one master pool.
    > appOrbit Platform uses the Master pool as a controller to
    > coordinate all of the other pools you define. The master pool is a
    > compute node that does not contain storage. The user admin is not
    > allowed to use the master pool.

-   Cluster resource properties include:

-   **Pool Name**: Type the name you want to use to identify the pool,
    > such as Master.

-   **Count**: Select the number of virtual machines in the cluster.

-   **Flavor**: Select the flavor of the virtual machines, such as
    > Small, Medium or Large.

-   Click **Add** to continue to enter properties when there is more
    > than one resource.

-   **Add Volume**: When you add more than one resource, click **Add
    > Volume** to add disk for to each of the virtual machines in
    > the cluster. When you select Add Volume, the following fields
    > are shown.

-   **Type**: Select the type of disk you want to use, such as Standard.

-   **Size (GB)**: Type the size of the disk in gigabytes.

-   You can click Remove at any time to delete your entries.

**For OpenStack**

NEED A SCREEN SAMPLE HERE.

The cluster details include:

-   

**For Rackspace**

![](media/image19.jpg)

The cluster details include:

-   **Cluster Name:** Type the name you want to use to identify
    > the cluster.

-   **Group:** Select the group that is to use the cluster, including
    > the development, testing, staging and production environments.

-   **Region**: Select the region from which you want to create a
    > virtual machine.

-   **Registry**: If you are using a private Docker registry to retrieve
    > the Docker images, type the location for the registry. A private
    > Docker registry is used to supplement the public Docker registry.

-   **Note**: When the Registry/URL is blank, the global default value
    > is used when a new cluster is created to specify the internal
    > Docker Registry from which the Docker images are retrieved in
    > the nodes.

-   **Specify cluster resource properties**: Enter the details for each
    > resource that is used to create the cluster for a data node or a
    > compute only node.

-   **Note**: Each cluster setup requires at least one master pool.
    > appOrbit Platform uses the Master pool as a controller to
    > coordinate all of the other pools you define. The master pool is a
    > compute node that does not contain storage. The user admin is not
    > allowed to use the master pool.

-   Cluster resource properties include:

-   **Pool Name**: Type the name you want to use to identify the pool,
    > such as Master.

-   **Count**: Select the number of virtual machines in the cluster.

-   **Flavor**: Select the flavor of the virtual machines, such as
    > Small, Medium or Large.

-   Click **Add** to continue to enter properties when there is more
    > than one resource.

-   **Add Volume**: When you add more than one resource, click **Add
    > Volume** to add disk for to each of the virtual machines in
    > the cluster. When you select Add Volume, the following fields
    > are shown.

-   **Type**: Select the type of disk you want to use, such as Standard.

-   **Size (GB)**: Type the size of the disk in gigabytes.

-   You can click Remove at any time to delete your entries.

**For Custom Cloud**

![](media/image21.jpg)

The cluster details include:

-   **Cluster Name**: Type the name you want to use to identify
    > the cluster.

-   **Registry/URL**: If you are using a private Docker registry to
    > retrieve the Docker images, type the location for the registry. A
    > private Docker is used to supplement the public Docker registry.

-   **Note**: When the Registry/URL is blank, the global default value
    > is used when a new cluster is created to specify the internal
    > Docker Registry from which the Docker images are retrieved in
    > the nodes.

-   **Group**: Select the group that is to use the cluster, including
    > the development, testing, staging and production environments.

-   **Specify cluster resource properties**: Enter the details for each
    > resource that is used to create the cluster for a data node or a
    > compute only node.

-   **Note**: Each cluster setup requires at least one Master pool.
    > appOrbit Platform uses the master pool as a controller to
    > coordinate all of the other pools you define. The master pool is a
    > compute node that does not contain storage. The user admin is not
    > allowed to use the master pool.

-   Cluster resource properties include:

-   **Name**: Type the name you want to use to identify the pool, such
    > as Master.

-   **IP**:

-   **User Name**:

-   **Authentication**:

-   **SSH Key**:

-   **Add**: When needed, click **Add** to add pools for to each of the
    > virtual machines in the cluster.

-   Click **Next.**

-   **Add**: When needed, click **Add** to add disk for to each of the
    > virtual machines in the cluster. When you select Add Volume, the
    > following fields are shown.

-   You can click Remove at any time to delete your entries.

-   **Type**: Select the type of disk you want to use, such as Standard.

-   **Size (GB)**: Type the size of the disk in gigabytes.

1.  Click **OK** to configure the virtual machines you defined.

2.  A progress bar is shown while the cluster configuration is
    > being completed.

3.  When complete, a confirmation is displayed showing the status of the
    > cluster deployment, including a listing of each Pool, IP Address
    > and Volume you created.

4.  Click **Done**.

![](media/image16.png)

### **To view cluster details**

1.  Click **CLOUDS**.

2.  On the Clouds page, select a Cloud Name that contains one or
    > more clusters.

![](media/image12.jpg)

1.  On the CLUSTERS tab, each quick view provides the high level status
    > of each active cluster in the selected cloud. This includes the
    > resource usage for the virtual machines and other components of
    > each active cluster.

![](media/image14.png)

The quick view for each cluster displays:

-   **Active**: The top section of each quick view displays a
    > color-coded status of the cluster:

-   **Green**: Indicates that adequate cluster resources are available
    > to perform all application operations.

-   **Yellow**: Warns that some cluster resources are in short supply.

-   **IMPORTANT**: When the quick view status is Yellow, you are not
    > allowed to deploy an application until you resolve the issue.

-   When you receive a Yellow status, hover over the term, Active, to
    > view the warning message, such as Disk Overload 83%. Click either
    > MEMORY, CPU or STORAGE to confirm which resource is in
    > short supply. To correct the shortage, you can either add resource
    > capacity, or reduce your usage of the existing resource. For
    > example, you might add nodes to the cluster to increase the
    > storage capacity.

-   **Red**: Resources are unavailable, such as when a node fails.

-   **IMPORTANT**: When the quick view status is Red, you are not
    > allowed to perform any application operations.

-   **Application**: Number of applications instances deployed.

-   **Snapshots**: Number of snapshots stored.

-   **Servers**: Number of server nodes.

You can either click MEMORY, CPU or STORAGE to display:

-   **MEMORY**: Percent of memory used.

-   **CPU**: Percent of CPU used.

-   **STORAGE**: Percent of storage used.

When you click MEMORY, CPU or STORAGE, these values display:

-   **Available**: Number of gigabytes (GBs) available. For CPU, this is
    > the percent used.

-   **Used (GB)**: Number of gigabytes used. For CPU, this is the
    > percent used.

-   **Total (GB)**: Total number of gigabytes (Available and Used). For
    > CPU, this is 100 %.

1.  On the selected quick view, click overview to view the details for
    > the selected cluster.

2.  The OVERVIEW tab displays the status of MEMORY, CPU and STORAGE, and
    > the resources that are currently available or in-use.

3.  **Note**: From the OVERVIEW tab, you can click DATA CATALOGS to
    > create or view a data catalog. For more information, go to “Using
    > a Data Catalog”.

4.  ![](media/image15.jpg)

### **To remove a cluster**

1.  Click **CLOUDS**.

2.  On the Clouds page, select a Cloud Name that contains one or
    > more clusters.

![](media/image11.jpg)

1.  On the CLUSTERS tab, locate the quick view of the active cluster
    > that you want to remove.

![](media/image09.png)

1.  On the selected quick view, click delete icon. A confirmation
    > message is displayed.

2.  **IMPORTANT**: Remove a cluster only when it is entirely necessary.
    > When you delete a cluster, all of the data catalogs, data
    > templates and deployed applications that use the cluster are also
    > permanently removed and unrecoverable.

3.  Click **OK**.

4.  A progress bar is shown while the deletion is being completed. When
    > you delete a cluster, all of the data catalogs, data templates and
    > deployed applications that use the cluster are also permanently
    > removed and unrecoverable.
