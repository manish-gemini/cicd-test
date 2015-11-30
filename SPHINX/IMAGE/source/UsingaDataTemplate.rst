**Using a Data Template**
-------------------------

A data template is a small data set that is used to pre-populate
multiple instances of the same application. You can create one or more
data templates for the same application, based on the number of data
nodes that have active volumes.

A data template is data catalog specific. The data catalog is used to
store data templates and to define the size of the virtual storage used
by the data templates.

In addition, you can promote snapshots to data templates. A data
template allows you to share snapshots with others, and to clone an
application from a snapshot, such as to debug an application with data
in a new environment. For more information, go to “Using Snapshots” and
“Cloning Applications”.

The appOrbit Platform allows you to:

-   Create a data template.

-   Import external data to a data template.

-   View a data template.

-   Remove a data template.

-   Copy a data template from one data catalog to another.

-   Refresh the data catalog to create another version of the data.

Each of these procedures is described in a separate topic.

### **To create a data template**

1.  Click **APPS**.

2.  On the BLUEPRINTS tab, click **DATA TEMPLATES**.

3.  On the DATA TEMPLATES tab, click **Create Data Templates**.

![](media/image14.jpg)

1.  On the Create Data Template page, enter the data template details.

2.  These include:

-   **Template Name**: Type the name used to identify the data template.

-   **Group**: Select the group to use the data template, including the
    > development, testing, staging and production environments.

-   **Blueprint Name**: Select the blueprint name and version.

-   **Data Catalog**: Select the data catalog location that is to
    > contain the data template.

-   **Choose Type**: Click **Snapshot** to create the data template from
    > a snapshot.

-   **Note**: You can also click Special Data Import. For more
    > information, see “To import external data into a data template”.

-   **Snapshot Name**: Select the snapshot name you want to use.

1.  Click **OK**.

2.  A progress bar is displayed while the data catalog configuration is
    > being completed. When the data catalog is created, the data volume
    > for the data catalog is associated with the virtual machine
    > you selected.

3.  When the data template is ready, the Data Template Name, Blueprint –
    > Version, Location, and Time Created display at the bottom of
    > the page.

### **To import external data to a data template**

1.  Click **APPS**.

2.  On the BLUEPRINTS tab, click **DATA TEMPLATES**.

![](media/image21.jpg)

1.  On the DATA TEMPLATES tab, click **Create Data Templates**.

![](media/image15.jpg)

1.  On the Create Data Template page, enter the data template details.

2.  These include:

-   **Template Name**: Type the name you want to use to identify the
    > data template.

-   **Group**: Select the group to use the data template, including the
    > development, testing, staging and production environments.

-   **Blueprint Name**: Select the blueprint name and version you want
    > to associate with this date template.

-   **Data Catalog**: Select the data catalog that is to contain the
    > data template.

-   **Choose Type**: Click **Special Data Import** to import data that
    > is external to the appOrbit Platform into a data template. The
    > directories for the external data source display at the bottom of
    > the page, based on the Blueprint Name you selected.

-   **Note**: You can also click Snapshot. For more information, see “To
    > create a data template”.

-   Enter the special data import details for the selected blueprint.

![](media/image22.jpg)

These include:

-   **Tier**: Displays the name of each tier that contains an image of
    > one or more volumes. The Tier name provides the path to each
    > volume that stores data for the data catalog.

-   **Note**: The tier is the parent of the image. Each tier is
    > associated with an image and each image is associated with the
    > volumes it contains.

-   **Container**: Displays the name of the image where the volume
    > exists, such as MySQL.

-   **Container Volume**: Displays the path where the volume is located.

-   **Source Path**: Type the directory location for each external
    > source data that is to be copied to the data template. The source
    > data is copied for use with the selected blueprint.

-   **Note**: You can select one or more directory locations for
    > external source data as needed.

-   **Source Info**: Select the host for each selected Source Path, and
    > type the credentials needed to access each host.

-   When you select **Add New**, the Source Information popup displays.
    > In this case, type the Source Information details including the
    > credentials needed to access the host.

-   **Note**: You can select a separate host for each Source Path when
    > multiple Source Paths are used, or use the same host for each
    > Source Path as needed.

-   These details include:

-   **Host Name/IP Address**: Type the Host Name or IP address of the
    > host where the external source data is stored.

-   **User Name**: Type the user name that is used to access the host.

-   **Password** or **SSH Private Key**: Type the Password or SSH
    > Private Key.

-   Click **OK**.

-   Once connected, the new host is displayed on the Source Info
    > selection list for each Tier. This allows you to select the same
    > host for more than one tier.

![](media/image13.jpg)

-   Click **Next** to verify the details for the Special Data Import.

-   **Note**: If an error message displays, click Previous to return to
    > the Create Data Template page and change the special data import
    > details as needed.

![](media/image10.jpg)

1.  When the special data import details are accepted, click **Begin
    > Import** to import the external source data from the selected
    > Source Path and Source Info to the data template you created.

2.  A progress bar is displayed while the external data import is
    > being completed. When the data catalog is created, the data volume
    > for the data catalog is associated with the virtual machine
    > you selected.

3.  **IMPORTANT**: When you are importing external data to a data
    > template, do not perform any other actions until the data import
    > process is completed.

4.  When the data catalog is ready, the Catalog Name, Node Name and
    > Size (GB) display at the bottom of the page.

![](media/image12.jpg)

1.  Click **Finish** when the import is successfully completed.

2.  Click **OK** to save the data template.

### **To view a data template**

1.  Click **APPS**.

2.  On the BLUEPRINTS tab, click **DATA TEMPLATES**.

![](media/image23.jpg)

1.  The DATA TEMPLATES tab displays each active data template for a
    > given data catalog, including:

-   **Data Template Name**: Name that identifies the data catalog.

-   **Blueprint - Version**: Blueprint name and version.

-   **Location**: Location of the data catalog location that is to
    > contain the data template.

-   **Time Created**: Date and time when the data template was created.

### **To remove a data template**

1.  Click **APPS**.

2.  On the BLUEPRINTS tab, click **DATA TEMPLATES**.

![](media/image17.jpg)

1.  On the DATA TEMPLATES tab, select the data template you want
    > to remove.

2.  Click delete icon. A confirmation message is displayed.

3.  **IMPORTANT**: Remove a data template only when it is
    > entirely necessary. When you delete a data template, the data
    > template and any associated data is permanently removed
    > and unrecoverable.

4.  Click **OK** to remove the data template.

5.  A progress bar is shown while the deletion is being completed. When
    > you remove a data template, the data template and any associated
    > data is also permanently removed and recoverable.

![](media/image20.jpg)

### **To copy a data template from one data catalog to another**

1.  Click **APPS**.

2.  On the BLUEPRINTS tab, click **DATA TEMPLATES**.

![](media/image03.jpg)

1.  On the DATA TEMPLATES tab, select the data template you want
    > to remove.

2.  Click clone icon.

### **To refresh the data template**

1.  Click **APPS**.

2.  On the BLUEPRINTS tab, click **DATA TEMPLATES**.

![](media/image16.jpg)

1.  On the DATA TEMPLATES tab, select the data template you want
    > to remove.

2.  Click refresh icon.
