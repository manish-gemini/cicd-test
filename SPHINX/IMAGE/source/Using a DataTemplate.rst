**Using a Data Template**
-------------------------

A data template is a data set that can be used to pre-populate multiple
instances of the same application. You can create one or more data
templates for the same application. Each data template is stored in a
specific data catalog.

In addition, you can promote snapshots to data templates. A data
template allows you to share snapshots with others, and to clone an
application from a snapshot, such as to debug an application with data
in a new environment. For more information, go to “Using Snapshots” and
“Cloning Applications”.

The appOrbit Platform allows you to:

-   Create a data template.

-   Import external data to a data template.

-   Refresh a data template using Special Data Import.

-   View a data template.

-   Copy a data template from one data catalog to another.

-   Remove a data template.

Each of these procedures is described in a separate topic.

### **To create a data template**

1.  Click **APPS**.

2.  Click the **DATA TEMPLATES** tab.

3.  On the DATA TEMPLATES tab, click **Create Data Template**.

4.  On the Create Data Template page, enter the data template details.

> These include:

-   **Template Name**: Type the name used to identify the data template.

-   **Group**: Select the group for the data template, including the
    > development, testing, staging and production environments.

-   **Blueprint Name**: Select the blueprint name and version you want
    > use with the data template.

-   **Data Catalog**: Select the name and node location of the data
    > catalog that is to contain the data template.

-   **Choose Type**: Click **Snapshot** (the default) to create the data
    > template from a snapshot.

> **Note**: You can also click Special Data Import. For more
> information, see “To import external data into a data template”.

-   **Snapshot Name**: Select the snapshot name you want to use.

1.  Click **OK**.

> A progress bar is shown while the data template is being created.
>
> When the data template is ready, the Data Template Name, Blueprint –
> Version, Location, Time Created and Status are shown at the bottom of
> the page.

### **To import external data to a data template**

1.  Click **APPS**.

2.  Click the **DATA TEMPLATES** tab.

3.  On the DATA TEMPLATES tab, click **Create Data Templates**.

4.  On the Create Data Template page, enter the data template details.

> These include:

-   **Template Name**: Type the name you want to use to identify the
    > data template.

-   **Group**: Select the group for the data template, including the
    > development, testing, staging and production environments.

-   **Blueprint Name**: Select the blueprint name and version you want
    > use with the date template.

-   **Data Catalog**: Select the name and node location of the data
    > catalog that is to contain the data template.

-   **Choose Type**: Click **Special Data Import** to import data that
    > is external to the appOrbit Platform into the data template. The
    > directories for the external data source display at the bottom of
    > the page, based on the Blueprint Name you selected.

> **Note**: You can also click Snapshot (the default). For more
> information, see “To create a data template”.

-   Enter the special data import details for the selected blueprint.

> The details include:

-   **Tier**: Displays the name of each tier that contains an image with
    > one or more volumes. The Tier name provides the path to each
    > volume that stores data for the data catalog.

-   **Container**: Displays the name of the image where the volume
    > exists, such as MySQL.

-   **Container Volume**: Displays the path where the volume is mounted
    > in the container.

-   **Source Path**: Type the directory location for each external
    > source data that is to be copied to the data template. The
    > external source data is copied for use with the
    > selected blueprint.

> **Note**: You can select one or more directory locations for external
> source data as needed.

-   **Source Info**: Select the host for each selected Source Path, and
    > type the credentials needed to access each host.

> When you select **Add New**, the Source Information popup displays. In
> this case, type the Source Information details including the
> credentials needed to access the host.
>
> **Note**: You can select a separate host for each Source Path when
> multiple Source Paths are used, or use the same host for each Source
> Path as needed.
>
> These include:

-   **Host Name/IP Address**: Type the Host Name or host IP Address
    > where the external source data is stored.

-   **User Name**: Type the user name that is to access the host.

-   **Password** or **SSH Private Key**: Type either the Password or an
    > SSH Private Key. The SSH key provides access a trusted virtual
    > machine or physical server, without requiring a password.

-   Click **OK**.

> Once connected, the new host is displayed on the Source Info selection
> list for each Tier. This allows you to select the same host for more
> than one tier.

-   Click **Next** to verify the details for the Special Data Import
    > including the connection and the volume size.

> **Note**: If an error message displays, click Previous to return to
> the Create Data Template page and change the special data import
> details as needed.

1.  When the special data import details are accepted, click **Begin
    > Import** to import the external source data from the selected
    > Source Path and Source Info to the data template you created.

> A progress bar is shown while the external data import is being
> completed.
>
> **IMPORTANT**: When you are importing external data to a data
> template, do not perform any other actions until the data import
> process is complete. The time it takes to complete the import is
> proportional to the amount of data that is being imported.
>
> When the data template is ready, the Data Template Name, Blueprint –
> Version, Location, Time Created and Status are shown at the bottom of
> the page.

### **To refresh a data template using Special Data Import**

1.  Click **APPS**.

2.  Click the **DATA TEMPLATES** tab.

3.  On the DATA TEMPLATES tab, select the data template you want
    > to refresh.

4.  Click ![](media/image05.png). The Refresh Data Template page shows
    > the current fields for the external data import for the selected
    > data template.

5.  On the Refresh Data Template page, use the steps described in “To
    > import external data to a data template” to verify the special
    > data import details and to refresh the data for the special
    > data import.

### **To view a data template**

1.  Click **APPS**.

2.  Click the **DATA TEMPLATES** tab.

3.  The DATA TEMPLATES tab displays each active data template for a
    > given data catalog, including:

-   **Data Template Name**: Name that identifies the data catalog.

-   **Blueprint - Version**: Blueprint name and version.

-   **Location**: Location of the data catalog that is to contain the
    > data template.

-   **Time Created**: Date and time when the data template was created.

-   **Status**: Current working status of the data template, such
    > as Active.

### **To copy a data template from one data catalog to another**

1.  Click **APPS**.

2.  Click the **DATA TEMPLATES** tab.

3.  On the DATA TEMPLATES tab, select the data template you want
    > to clone.

4.  Click ![](media/image01.png).

5.  On the Clone popup, type the details for the copy.

> These include:

-   **Target Template Name**: Type the new name you want to use to
    > identify the copy of the data template.

-   **Select Data Catalog**: Select the data catalog to which the data
    > template is copied.

> A progress bar is shown while the new data template is being copied to
> the selected data catalog.

### **To remove a data template**

1.  Click **APPS**.

2.  Click the **DATA TEMPLATES** tab.

3.  On the DATA TEMPLATES tab, select the data template you want
    > to remove.

4.  Click ![](media/image03.png). A confirmation message displays.

> **IMPORTANT**: Remove a data template only when it is entirely
> necessary. When you delete a data template, the data template and any
> associated data is permanently removed and unrecoverable.

1.  Click **OK** to remove the data template.

> A progress bar is shown while the deletion is being completed. When
> you remove a data template, the data template and any associated data
> is permanently removed and recoverable.
