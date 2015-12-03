**Using a Cluster**
-------------------

Once you set up a specified cloud, you can create one or more clusters
and deploy applications in those clusters for different groups. A
cluster is a collection of resources, also called a resource pool, for a
given cloud that is used to manage the applications and data
requirements. A cluster contains a number of virtual machines for a
given cloud that are called cluster hosts. The appOrbit Platform uses
the settings for each of the virtual machines and other components to
configure and deploy applications and data.

The appOrbit Platform allows you to:

-   Create a cluster.

-   View cluster details.

-   Remove a cluster.

Each of these procedures is described in a separate topic.

### **To create a cluster**

1.  Click **CLOUDS**.

2.  On the Clouds page, select the Name of the cloud you want to use.

<!-- -->

3.  On the Clusters tab, click **Create Cluster**. When you initially
    > set up a cloud, the Cluster tab is blank.

<!-- -->

4.  Enter the cluster details.

> The cloud details shown for the cluster setup depend on the type of
> cloud you select, as described below.
>
> **For Microsoft Azure**
>
> The cluster details include:

-   **Cluster Name**: Type the name you want to use to identify
    > the cluster.

-   **Group**: Select the group that is to use the cluster, including
    > the development, testing, staging and production environments.

-   **Deployment Spec**: Choose one of the following responses to
    > describe how you want to set up the selected cloud:

-   Select **Default** to use the default deployment specification.

-   Select **File** to use a predefined deployment specification, such
    > as when you initially create a cloud account. Then click
    > **Browse** to select the location of the deployment specification.

-   Select **Cloud** to create custom setups for the cloud.

-   **Region**: Select the region from which you want to create a
    > virtual machine.

-   **Network**: For the region, select the network you want to use.
    > When you select Default or File, the network is pre-filled based
    > on the deployment specification you select.

-   **Container Registry**: Choose one of the following responses to
    > name the Docker Registry you want to use to retrieve Docker
    > images:

-   Leave Registry blank to use the default public Docker Hub Registry.
    > The Docker Hub Registry location is used as the default when a new
    > cluster is created, unless you override the default with the URL
    > of a private Docker registry.

-   When you want to use a private Docker registry, type the
    > location (URL) of the registry. A private Docker registry can be
    > used when the cluster is created to specify the internal Docker
    > Registry from which the Docker images are retrieved in the node.

-   **Specify cluster resource properties**: Enter the details for each
    > resource that is used to create the cluster for a data node or a
    > compute only node.

> **Note**: Each cluster setup requires one Master as the first resource
> pool. The appOrbit Platform uses the master pool as a controller to
> coordinate all of the other pools you define. The master pool is a
> compute node that does not contain storage. The user admin is not
> allowed to use the master pool.
>
> Cluster resource properties include:

-   **Pool Name**: Type the name you want to use to identify the pool.
    > Master is the default name for the first resource pool.

-   **Count**: Select the number of virtual machines in the cluster.

-   **Flavor**: Select the flavor of the virtual machines, such as
    > Small, Medium or Large. Flavor describes the configuration of the
    > virtual machine that is created in the cloud including CPU
    > and memory.

-   Click **Add** to continue to enter properties when there is more
    > than one resource.

-   **Add Volume**: When you add more than one resource, click **Add
    > Volume** to add disk for to each of the virtual machines in
    > the cluster. When you select Add Volume, the following fields
    > are shown.

-   **Type**: Select the type of disk you want to use, such as Standard.

-   **Size (GB)**: Type the size of the disk in gigabytes.

> You can click Remove at any time to delete your entries.
>
> **For AWS (Amazon Web Services)**
>
> The cluster details include:

-   **Cluster Name**: Type the name you want to use to identify
    > the cluster.

-   **Group**: Select the group that is to use the cluster, including
    > the development, testing, staging and production environments.

-   **Deployment Spec**: Choose one of the following responses to
    > describe how you want to set up the selected cloud:

-   Select **Default** to use the default deployment specification.

-   Select **File** to use a predefined deployment specification, such
    > as when you initially create a cloud account. Then click
    > **Browse** to select the location of the deployment specification.

-   Select **Cloud** to create custom setups for the cloud.

-   **Region**: Select the region from which you want to create a
    > virtual machine.

-   **vPC**: For the region, select the virtual private cloud (vPC)
    > network definitions you want to use.

-   **Subnet**: For the vPC, select the subnet that you want to use.

-   **Container Registry**: Choose one of the following responses to
    > name the Docker Registry you want to use to retrieve Docker
    > images:

-   Leave Registry blank to use the default public Docker Hub Registry.
    > The Docker Hub Registry location is used as the default when a new
    > cluster is created, unless you override the default with the URL
    > of a private Docker registry.

-   When you want to use a private Docker registry, type the
    > location (URL) of the registry. A private Docker registry can be
    > used when the cluster is created to specify the internal Docker
    > Registry from which the Docker images are retrieved in the node.

-   **Specify cluster resource properties**: Enter the details for each
    > resource that is used to create the cluster for a data node or a
    > compute only node.

> **Note**: Each cluster setup requires one Master as the first resource
> pool. The appOrbit Platform uses the master pool as a controller to
> coordinate all of the other pools you define. The master pool is a
> compute node that does not contain storage. The user admin is not
> allowed to use the master pool.
>
> Cluster resource properties include:

-   **Pool Name**: Type the name you want to use to identify the pool.
    > Master is the default name for the first resource pool.

-   **Count**: Select the number of virtual machines in the cluster.

-   **Flavor**: Select the flavor of the virtual machines, such as
    > Small, Medium or Large. Flavor describes the configuration of the
    > virtual machine that is created in the cloud including CPU
    > and memory.

-   Click **Add** to continue to enter properties when there is more
    > than one resource.

-   **Add Volume**: When you add more than one resource, click **Add
    > Volume** to add disk for to each of the virtual machines in
    > the cluster. When you select Add Volume, the following fields
    > are shown.

-   **Type**: Select the type of disk you want to use, such as Standard.

-   **Size (GB)**: Type the size of the disk in gigabytes.

> You can click Remove at any time to delete your entries.
>
> **For OpenStack**
>
> The cluster details include:

-   **Cluster Name**: Type the name you want to use to identify
    > the cluster.

-   **Group**: Select the group that is to use the cluster, including
    > the development, testing, staging and production environments.

-   **Deployment Spec**: Choose one of the following responses to
    > describe how you want to set up the selected cloud:

-   Select **Default** to use the default deployment specification.

-   Select **File** to use a predefined deployment specification, such
    > as when you initially create a cloud account. Then click
    > **Browse** to select the location of the deployment specification.

-   Select **Cloud** to create custom setups for the cloud.

-   **Region**: Select the region from which you want to create a
    > virtual machine.

-   **Network**: For the region, select the network you want to use.
    > When you select Default or File, the network is pre-filled based
    > on the deployment specification you select.

-   **Container Registry**: Choose one of the following responses to
    > name the Docker Registry you want to use to retrieve Docker
    > images:

-   Leave Registry blank to use the default public Docker Hub Registry.
    > The Docker Hub Registry location is used as the default when a new
    > cluster is created, unless you override the default with the URL
    > of a private Docker registry.

-   When you want to use a private Docker registry, type the
    > location (URL) of the registry. A private Docker registry can be
    > used when the cluster is created to specify the internal Docker
    > Registry from which the Docker images are retrieved in the node.

-   **Specify cluster resource properties**: Enter the details for each
    > resource that is used to create the cluster for a data node or a
    > compute only node.

> **Note**: Each cluster setup requires one Master as the first resource
> pool. The appOrbit Platform uses the master pool as a controller to
> coordinate all of the other pools you define. The master pool is a
> compute node that does not contain storage. The user admin is not
> allowed to use the master pool.
>
> Cluster resource properties include:

-   **Pool Name**: Type the name you want to use to identify the pool.
    > Master is the default name for the first resource pool.

-   **Count**: Select the number of virtual machines in the cluster.

-   **Flavor**: Select the flavor of the virtual machines, such as
    > Small, Medium or Large. Flavor describes the configuration of the
    > virtual machine that is created in the cloud including CPU
    > and memory.

-   Click **Add** to continue to enter properties when there is more
    > than one resource.

-   **Add Volume**: When you add more than one resource, click **Add
    > Volume** to add disk for to each of the virtual machines in
    > the cluster. When you select Add Volume, the following fields
    > are shown.

-   **Type**: Select the type of disk you want to use, such as Standard.

-   **Size (GB)**: Type the size of the disk in gigabytes.

> You can click Remove at any time to delete your entries.
>
> **For Rackspace**
>
> The cluster details include:

-   **Cluster Name:** Type the name you want to use to identify
    > the cluster.

-   **Group:** Select the group that is to use the cluster, including
    > the development, testing, staging and production environments.

-   **Region**: Select the region from which you want to create a
    > virtual machine.

-   **Container Registry**: Choose one of the following responses to
    > name the Docker Registry you want to use to retrieve Docker
    > images:

-   Leave Registry blank to use the default public Docker Hub Registry.
    > The Docker Hub Registry location is used as the default when a new
    > cluster is created, unless you override the default with the URL
    > of a private Docker registry.

-   When you want to use a private Docker registry, type the
    > location (URL) of the registry. A private Docker registry can be
    > used when the cluster is created to specify the internal Docker
    > Registry from which the Docker images are retrieved in the node.

-   **Specify cluster resource properties**: Enter the details for each
    > resource that is used to create the cluster for a data node or a
    > compute only node.

> **Note**: Each cluster setup requires one Master as the first resource
> pool. The appOrbit Platform uses the master pool as a controller to
> coordinate all of the other pools you define. The master pool is a
> compute node that does not contain storage. The user admin is not
> allowed to use the master pool.
>
> Cluster resource properties include:

-   **Pool Name**: Type the name you want to use to identify the pool.
    > Master is the default name for the first resource pool.

-   **Count**: Select the number of virtual machines in the cluster.

-   **Flavor**: Select the flavor of the virtual machines, such as
    > Small, Medium or Large. Flavor describes the configuration of the
    > virtual machine that is created in the cloud including CPU
    > and memory.

-   Click **Add** to continue to enter properties when there is more
    > than one resource.

-   **Add Volume**: When you add more than one resource, click **Add
    > Volume** to add disk for to each of the virtual machines in
    > the cluster. When you select Add Volume, the following fields
    > are shown.

-   **Type**: Select the type of disk you want to use, such as Standard.

-   **Size (GB)**: Type the size of the disk in gigabytes.

> You can click Remove at any time to delete your entries.
>
> **For Custom Cloud**
>
> The cluster details include:

-   **Cluster Name**: Type the name you want to use to identify
    > the cluster.

-   **Container Registry**: Choose one of the following responses to
    > name the Docker Registry you want to use to retrieve Docker
    > images:

-   Leave Registry blank to use the default public Docker Hub Registry.
    > The Docker Hub Registry location is used as the default when a new
    > cluster is created, unless you override the default with the URL
    > of a private Docker registry.

-   When you want to use a private Docker registry, type the
    > location (URL) of the registry. A private Docker registry can be
    > used when the cluster is created to specify the internal Docker
    > Registry from which the Docker images are retrieved in the node.

-   **Group**: Select the group that is to use the cluster, including
    > the development, testing, staging and production environments.

-   **Specify cluster resource properties**: Enter the details for each
    > resource that is used to create the cluster for a data node or a
    > compute only node.

> **Note**: For a custom cloud, the virtual machines are not created in
> the appOrbit Platform. In this case, the virtual machines are assumed
> to have already been created, or the custom cloud might also be using
> physical machines.
>
> **Note**: Each cluster setup requires one Master as the first resource
> pool. The appOrbit Platform uses the master pool as a controller to
> coordinate all of the other pools you define. The master pool is a
> compute node that does not contain storage. The user admin is not
> allowed to use the master pool.
>
> Cluster resource properties include:

-   **Name**: Type the name you want to use to identify the pool. Master
    > is the default name for the first resource pool.

-   **IP**: Type the IP address of each virtual machine or
    > physical server.

-   **User Name**: Type the user name for the virtual machine or
    > physical server.

-   **Authentication**: Select SSH Key or Password.

-   **SSH Key**: When Authentication is SSH Key, type the SSH key you
    > want to use to identify a trusted virtual machine or physical
    > server, without requiring a password.

-   **Add**: Click **Add** to add each additional virtual machine or
    > physical server used in the cluster.

-   When complete, click **Next**.

-   **Add Volume**: When needed, click **Add** to add disk for to each
    > of the virtual machines in the cluster. When you select Add
    > Volume, the following fields are shown.

> **Note**: You can click Remove at any time to delete your entries.
>
> Enter a value for each field:

-   **Type**: Select the type of disk you want to use, such as Standard.

-   **Size (GB)**: Type the size of the disk in gigabytes.

4.  Click **OK** to configure the virtual machines you defined.

> A progress bar is shown while the cluster configuration is being
> completed.

4.  When complete, a confirmation is displayed showing the status of the
    > cluster deployment, including a listing of each Pool, IP Address
    > and Volume you created.

5.  Click **Done**.

### **To view cluster details**

1.  Click **CLOUDS**.

2.  On the Clouds page, select a Cloud Name that contains one or
    > more clusters.

3.  On the CLUSTERS tab, each quick view provides the high level status
    > of each cluster in the selected cloud. This includes the resource
    > usage for the virtual machines and other components of
    > each cluster.

> The quick view for each cluster displays:

-   **Active**: The top section of each quick view displays a
    > color-coded status of the cluster:

-   **Green**: Indicates that adequate cluster resources are available
    > to perform all application operations.

-   **Yellow**: Warns that some cluster resources are in short supply.

> **IMPORTANT**: When the quick view status is Yellow, you are not
> allowed to deploy an application until you resolve the issue.
>
> When you receive a Yellow status, you can move the cursor over the
> term, Active, to view the warning message, such as Disk Overload 83%.
> Click either MEMORY, CPU or STORAGE to confirm which resource is in
> short supply. To correct the shortage, you can either add resource
> capacity, or reduce your usage of the existing resource. For example,
> you might add nodes to the cluster to increase the storage capacity.

-   **Red**: Resources are unavailable, such as when a node fails.

> **IMPORTANT**: When the quick view status is Red, you are not allowed
> to perform any application operations.

-   **Application**: Number of applications instances deployed.

-   **Snapshots**: Number of snapshots stored.

-   **Servers**: Number of server nodes.

> You can either click MEMORY, CPU or STORAGE to display:

-   **MEMORY**: Percent of memory used.

-   **CPU**: Percent of CPU used.

-   **STORAGE**: Percent of storage used.

> When you click MEMORY, CPU or STORAGE, these values display:

-   **Available**: Number of gigabytes (GBs) available. For CPU, this is
    > the percent used.

-   **Used (GB)**: Number of gigabytes used. For CPU, this is the
    > percent used.

-   **Total (GB)**: Total number of gigabytes (Available and Used). For
    > CPU, this is 100 %.

1.  On the selected quick view, click ![](media/image03.png) to view the
    > details for the selected cluster.

> The OVERVIEW tab displays the status of MEMORY, CPU and STORAGE, and
> the resources that are currently available or in-use.
>
> **Note**: From the OVERVIEW tab, you can click DATA CATALOGS to create
> or view a data catalog. For more information, go to “Using a Data
> Catalog”.

### **To remove a cluster**

1.  Click **CLOUDS**.

2.  On the Clouds page, select a Cloud Name that contains one or
    > more clusters.

3.  On the CLUSTERS tab, locate the quick view of the active cluster
    > that you want to remove.

4.  On the selected quick view, click ![](media/image02.png). A
    > confirmation message displays.

> **IMPORTANT**: Remove a cluster only when it is entirely necessary.
> When you delete a cluster, all of the data catalogs, data templates
> and deployed applications that use the cluster are also permanently
> removed and unrecoverable.

1.  Click **OK**.

> A progress bar is shown while the deletion is being completed. When
> you delete a cluster, all of the data catalogs, data templates and
> deployed applications that use the cluster are also permanently
> removed and unrecoverable.
