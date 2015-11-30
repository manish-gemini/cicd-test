**Using an Application Blueprint**
----------------------------------

An application blueprint is a template that is infrastructure agnostic.
Each blueprint describes how an application consisting of multiple tiers
communicates between tiers and uses resources. Each blueprint maps to
the application binaries, configurations, and resource requirements.
Once an associated application catalog is created, you can expose the
service endpoints using a blueprint.

The appOrbit Platform allows you to:

-   Import a blueprint.

-   View a blueprint details.

-   View blueprints status.

-   Export a blueprint.

-   Remove a blueprint.

Each of these procedures is described in a separate topic.

### **To import a blueprint**

1.  Click **APPS**.

![](media/image17.jpg)

1.  On the BLUEPRINTS tab, click **Import App Blueprint** to select a
    > blueprint (.YML template).

2.  **Note**: You can upload a blueprint for a custom application using
    > a file or command line. For more information, go to
    > “Blueprints Reference”.

3.  Navigate to the folder that contains the application blueprints
    > (.YML templates) if needed.

4.  Select the application blueprint (.YML template) you want to upload.

5.  Click **Open** to import the blueprint.

![](media/image14.png)

1.  Once you select the blueprint you want to import, the .YML template
    > is uploaded and the blueprint name displaye on the BLUEPRINT tab.

![](media/image10.jpg)

### **To view blueprint details**

1.  Click **APPS**.

![](media/image21.jpg)

1.  On the BLUEPRINTS tab, click the **Blueprint Name** to select the
    > blueprint you want to view.

![](media/image20.jpg)

1.  The BLUEPRINTS page displays the details of the selected blueprint
    > including:

-   **Author**: Name of the person who created the blueprint.

-   **Version**: Version of the blueprint (.YML template).

-   **Date Imported**: Date when the blueprint was imported.

-   **Tier Startup Order**: Displays the start-up order for each of the
    > application tiers. Tiers are set up in the start-up order defined
    > in the .YML template. For example, a given .YML template might
    > only include an Application Tier and the Database Tier.

-   **Tier Summary**: Displays the details for the selected tier:

-   **Name**: Name used to identify the tier.

-   **Service**: Each tier can use either of the following types of
    > service:

-   **Internal** (the default): The service can only be used by other
    > tiers in the same application.

-   **External**: The service can be accessed outside of
    > the application. For example, when a user interface is accessed
    > from a browser, it is defined as an external service.

-   **Replicas**: Number of copies of the selected tier (the default
    > is 1). Each copy is stored as a stateless replica only. No volumes
    > are assigned for the tier. You can click pencil icon to change the
    > number of replicas.

-   **Tier Containers**: Displays the services and resources for the
    > selected tier:

-   **Image Name**: Image name of the container image in the
    > Docker Registry.

-   **Ports**: Ports used by the blueprint including the host port and
    > container port.

-   **Environment**: Environmental variables that are passed to
    > the instance.

-   **Volumes**: Stateful data that persists to the underlying storage
    > in the cluster.

-   **Resources**: CPU memory or disk resources. Displays either the
    > minimum requested or maximum limits.

### **To view blueprints status**

1.  Click **APPS**.

![](media/image15.jpg)

1.  The BLUEPRINTS tab displays each of the application blueprints that
    > are imported and active, including:

-   **Blueprint Name**: Name that identifies each blueprint.

-   **Version**: Version of the .YML file that is in use.

-   **Date**: Date the blueprint was imported.

![](media/image16.jpg)

### **To export a blueprint**

1.  Click **APPS**.

![](media/image19.jpg)

1.  On the BLUEPRINTS tab, click the checkbox to select the blueprint
    > (.YML template) you want to export.

2.  Click export icon.

3.  The .YML template for the selected blueprint is downloaded to the
    > local Download directory on your computer. You can use downloaded
    > file to review the contents of the .YML template. For example, to
    > compare a newer version of a blueprint to an older version.

4.  When you select the downloaded file, the .YML template for the
    > selected blueprint displays.

![](media/image01.jpg)

### **To remove a blueprint**

1.  Click **APPS**.

![](media/image11.jpg)

1.  On the BLUEPRINTS tab, select the blueprints you want to remove.

2.  **IMPORTANT**: You cannot remove a blueprint when one or more
    > application instances are already running, based on the
    > blueprint version. In this case, you first need to stop and remove
    > all of the associated application instances, or upgrade the
    > blueprint to enable the application to use a different
    > blueprint version. For more details, go to ‘To remove an
    > application instance”.

3.  Click delete icon. A confirmation message is displayed.

4.  **IMPORTANT**: When there are no application instances running, you
    > can remove a blueprint, but only when it is entirely necessary.
    > When you delete a blueprint, any data templates that were created
    > for the selected blueprint version become orphan data templates.

5.  Click **OK** to remove the blueprint.

6.  A progress bar is shown while the deletion is being completed. When
    > you delete a blueprint, all of any data templates that were
    > created for the selected blueprint version become orphan
    > data templates.

7.  ![](media/image18.jpg)
