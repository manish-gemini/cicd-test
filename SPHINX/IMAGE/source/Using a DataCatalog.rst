**Using a Data Catalog**
------------------------

A data catalog is a cluster-specific repository that is used to store
one or more data templates. Each data catalog also defines the size of
the virtual store used by the data templates. The initial data catalog
is typically used to create a data store for a running application
similar to a gold backup version of the data.

Once you create the initial data store, you use data templates to
pre-populate multiple instances of the same application. You can create
one or more data templates for the same application, based on the number
of data nodes that have active volumes.

For clarification, the types of nodes for a cluster include the cluster
node, and a data node or an application and data node. When you use a
Data Catalog to create a data node, you can add additional volumes to
the data catalog location.

When you add volumes to the data catalog, you are creating virtual
storage from the host and attaching it to the data catalog and adding
the storage to the existing storage pool.

The appOrbit Platform allows you to:

-   Create a data catalog.

-   View data catalogs.

-   Add volumes to a data catalog

-   Remove a data catalog.

Each of these procedures is described in a separate topic.

### **To create a data catalog**

1.  Click **CLOUDS**.

2.  On the Clouds page, select a Cloud Name that contains one or
    > more clusters.

![](media/image35.jpg)

1.  On the CLUSTERS tab, locate the quick view for the active cluster
    > that is to contain the data catalog you want to create.

![](media/image27.png)

1.  On the selected quick view, click setup icon.

![](media/image39.jpg)

1.  On the OVERVIEW tab, click **DATA CATALOGS**.

![](media/image34.jpg)

1.  On the DATA CATALOGS tab, click **Create Data Catalog** to add a new
    > data catalog.

2.  ![](media/image29.jpg)

<!-- -->

1.  Enter the data catalog details.

2.  These include:

-   **Node**: Select the Node you want to use to create the
    > data catalog. The selection list shows only the host Nodes
    > (IP addresses) that are qualified to have data volumes. Only one
    > data catalog is allowed per node.

-   **Note**: When you select the Node for an active data catalog, the
    > Catalog Name displays. In this case, you are only allowed to
    > increase the size of the existing volume. For more information, go
    > to “To edit a data catalog”.

-   **Catalog Name**: Type the name you want to use to identify the
    > data catalog.

1.  Click **Add Volume** to create a data volume for the data catalog.

2.  **Note**: You can click Remove at any time to delete the data
    > volume details.

3.  Enter the details for the data volume you want to add.

4.  These include:

-   **Type**: Select the type of data volume you want to add based on
    > the type of cloud selected.

-   For example, when you are building a data catalog for an AWS cloud,
    > you are allowed to select these data types:

-   **Standard**: Standard magnetic storage

-   **Provisioned IOPS**: Solid State Drives (SSD)

-   **General Purpose**: Good quality magnetic disk

-   **Size (GB)**: Type the size in gigabytes of the data volume you
    > want to create such as 50.

1.  You can click Add Volume again and continue to add more data volumes
    > to the data catalog you want to create as needed.

2.  Click **Create**.

3.  A progress bar is displayed while the data catalog configuration is
    > being completed. When the data catalog is created, the data volume
    > for the data catalog is associated with the virtual machine
    > you selected.

4.  When the data catalog is ready, the Catalog Name, Node Name and
    > Size (GB) display at the bottom of the page.

### **To view data catalogs**

1.  Click **CLOUDS**.

2.  On the Clouds page, select a Cloud Name that contains one or
    > more clusters.

![](media/image24.jpg)

1.  On the CLUSTERS tab, the quick view provides the high level status
    > of each active cluster in the selected cloud. This includes the
    > resource usage for the virtual machines and other components of
    > each active cluster.

![](media/image19.png)

1.  On the quick view for each cluster, click setup icon to view the
    > details for the selected cluster.

2.  When the OVERVIEW tab displays, click **DATA CATALOGS**.

3.  The DATA CATALOGS tab displays each active data catalogs for a given
    > cluster, including:

-   **Catalog Name**: Name used to identity the data catalog.

-   **Node Name**: Nodes that are qualified to use data volumes.

-   **Size (GB)**: Total size in gigabytes of all data volumes contained
    > in each data catalog.

![](media/image25.jpg)

### **To add volumes to a data catalog**

1.  Click **CLOUDS**.

2.  On the Clouds page, select a Cloud Name that contains one or
    > more clusters.

![](media/image30.jpg)

1.  On the CLUSTERS tab, locate the quick view of the active cluster
    > that contains the data catalog you want to edit.

![](media/image33.png)

1.  On the quick view, click setup icon to view the details for the
    > selected cluster.

![](media/image22.jpg)

1.  When the OVERVIEW tab displays, click **DATA CATALOGS**.

![](media/image28.jpg)

1.  On the DATA CATALOGS tab, click **Create Data Catalog** to add
    > additional volumes to an active data catalog.

2.  ![](media/image07.jpg)

<!-- -->

1.  Enter the data catalog details.

2.  These include:

-   **Node**: Select the Node you want to use to create the
    > data catalog. The selection list shows only the host Nodes
    > (IP addresses) that are qualified to have data volumes. Only one
    > data catalog is allowed per node.

-   When you select the Node for an active data catalog, the Catalog
    > Name is displayed. In this case, you are only allowed to increase
    > the size of the existing volume.

-   **Catalog Name**: Displays the catalog name for the Node
    > you selected.

1.  Click **Add Volume** to add an additional data volume to the
    > data catalog.

2.  **Note**: You can click Remove at any time to delete the data
    > volume details.

3.  Enter the details for the data volume you want to add.

4.  These include:

-   **Type**: Select the type of data volume you want to add based on
    > the type of cloud selected.

-   **Size (GB)**: Type the size in gigabytes of data volume you want
    > to add.

1.  You can click Add Volume again and continue to add more data volumes
    > to the data catalog you want to create as needed.

![](media/image38.jpg)

1.  Click **Create** to add an additional data volume.

2.  A progress bar is displayed while the data catalog configuration is
    > being completed.

3.  When the data catalog is ready, the Catalog Name, Node Name and
    > combined total Size (GB) of all data volumes for the selected data
    > catalog display at the bottom of the page.

![](media/image23.jpg)

### **To remove a data catalog**

1.  Click **CLOUDS**.

2.  On the Clouds page, select a Cloud Name that contains one or
    > more clusters.

![](media/image26.jpg)

1.  On the CLUSTERS tab, locate the quick view of the active cluster
    > that contains the data catalog you want to remove.

![](media/image21.png)

1.  On the quick view, click setup icon to view the details for the
    > selected cluster.

![](media/image31.jpg)

1.  When the OVERVIEW tab displays, click **DATA CATALOGS**.

![](media/image37.jpg)

1.  On the DATA CATALOGS tab, click the checkbox for the data catalog
    > you want to remove.

2.  Click delete icon. A confirmation message is displayed.

3.  **IMPORTANT**: Remove a data catalog only when it is
    > entirely necessary. When you delete a data catalog, all of the
    > associated volumes and all data templates for the entire data
    > catalog are also permanently removed and unrecoverable. You cannot
    > delete separate volumes.

4.  Click **OK** to remove the data catalog.

5.  A progress bar is shown while the deletion is being completed. When
    > you delete a data catalog, all of the associated volumes and all
    > data templates for the entire data catalog are also permanently
    > removed and unrecoverable.

6.  ![](media/image36.jpg)
