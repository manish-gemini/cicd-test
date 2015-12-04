**Using an Application Blueprint**
----------------------------------

An application blueprint is a YAML template that is infrastructure
agnostic. Each blueprint describes how an application consisting of
multiple tiers communicates between each tier and how it uses resources.
Each blueprint maps to the application binaries, configurations, and
resource requirements. Once an associated application catalog is
created, you can expose the service endpoints using a blueprint.

For more information, go to “appOrbit Blueprints Reference” to review an
example YAML template.

The appOrbit Platform allows you to:

-   Import a blueprint.

-   View blueprint details.

-   View blueprints status.

-   Export a blueprint.

-   Remove a blueprint.

Each of these procedures is described in a separate topic.

### **To import a blueprint**

1.  Click **APPS**.

2.  On the BLUEPRINTS tab, click **Import App Blueprint** to select an
    > application blueprint (YAML template).

> **Note**: You can upload a blueprint for a custom application using a
> file or command line. For more information, go to “appOrbit Command
> Line Interface”.

1.  Navigate to the folder that contains the application blueprints
    > if needed.

2.  Select the application blueprint you want to upload.

3.  Click **Open** to import the blueprint.

4.  Once you select the blueprint you want to import, the Blueprint name
    > is shown on the BLUEPRINT tab.

> **Note**: The Blueprint name is the app\_id defined in the YAML
> template. For more information, go to “appOrbit Blueprints Reference”
> to review an example YAML template.

### **To view blueprint details**

1.  Click **APPS**.

> **Note**: For more information, go to “appOrbit Blueprints Reference”
> to review an example YAML template.

1.  On the BLUEPRINTS tab, click the **Blueprint Name** to select the
    > blueprint you want to view.

2.  The BLUEPRINTS page displays the details of the selected blueprint
    > including:

-   **Author**: Name of the person who created the blueprint.

-   **Version**: Version of the blueprint (YAML template).

-   **Date Imported**: Date when the blueprint was imported.

-   **Tier Startup Order**: Displays the start-up order for each of the
    > application tiers. Tiers are set up in the start-up order defined
    > in the YAML template. For example, a given YAML template might
    > only include a Database Tier and then an Application Tier.

-   **Tier Summary**: Displays the details for the selected tier:

-   **Name**: Name used to identify the tier.

-   **Service**: Service is shown in the TIER CONTAINER tab. Each tier
    > can use either of the following types of service:

-   **Internal** (the default): The service can only be used by other
    > tiers in the same application.

-   **External**: The service can be accessed outside of
    > the application. For example, when a user interface is accessed
    > from a browser, it is defined as an external service.

-   **Replicas**: Number of copies of the selected tier (the default
    > is 1). Each copy is stored as a stateless replica only. No volumes
    > are assigned to the tier. You can click ![](media/image01.png) to
    > change the number of replicas.

-   **Tier Containers**: Displays the services and resources for the
    > selected tier:

-   **Image Name**: Image name of the container image in the
    > Docker Registry.

-   **Ports**: Ports used by the blueprint including the host port and
    > container port.

-   **Environment**: Environment variables that are passed to
    > the instance.

-   **Volumes**: Stateful data that persists to the underlying storage
    > in the cluster.

-   **Resources**: CPU memory or disk resources. Displays either the
    > minimum requested or maximum limits.

### **To view blueprints status**

1.  Click **APPS**.

2.  The BLUEPRINTS tab displays each of the application blueprints that
    > are imported and active, including:

-   **Blueprint Name**: Name that identifies each blueprint.

-   **Version**: Version of the YAML template that is in use.

-   **Date**: Date the blueprint was imported.

### **To export a blueprint**

1.  Click **APPS**.

2.  On the BLUEPRINTS tab, click the checkbox to select the blueprint
    > (YAML template) you want to export.

3.  Click ![](media/image03.png).

> The YAML template for the selected blueprint is downloaded to the
> local Download directory on your computer. The downloaded file
> contains the YAML template for your review, such as to compare a newer
> version of a blueprint to an older version.

1.  When you select the downloaded file, the YAML template for the
    > selected blueprint displays.

### **To remove a blueprint**

1.  Click **APPS**.

2.  On the BLUEPRINTS tab, select the blueprints you want to remove.

> **IMPORTANT**: You cannot remove a blueprint when one or more
> application instances are already running, based on the blueprint
> version. In this case, you first need to stop and remove all of the
> running application instances, or upgrade the blueprint to a different
> blueprint version. For more details, go to ”To remove an application
> instance”.

1.  Click ![](media/image05.png). A confirmation message displays.

> **IMPORTANT**: When there are no application instances running, you
> can remove a blueprint, but only when it is entirely necessary. When
> you delete a blueprint, any data templates that were created for the
> selected blueprint version become orphan data templates.

1.  Click **OK** to remove the blueprint.

> A progress bar is shown while the deletion is being completed. When
> you delete a blueprint, all of any data templates that were created
> for the selected blueprint version become orphan data templates.
