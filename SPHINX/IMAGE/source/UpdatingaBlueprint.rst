**Updating a Blueprint**
------------------------

When the version of an application blueprint changes, you can perform a
rolling update of the blueprint (.YML template), such as to deploy a new
version of the .YML template for a given application blueprint. Each
application blueprint is identified in the .YML template both by the
blueprint name and the version.

The appOrbit Platform allows you to:

-   Update a blueprint to a later version.

Each of these procedures is described in a separate topic.

### **To update a blueprint to a later version**

1.  Click **APPS**.

2.  The **BLUEPRINTS** tab is displayed.

![](media/image06.jpg)

1.  4Click **INSTANCES**. The INSTANCES tab displays a list of all
    > running and stopped applications.

![](media/image07.jpg)

1.  Select an application instance and cClick Blueprint Update to update
    > the application instanceblueprint (.YML template) to a
    > selected version.

2.  On the Blueprint Update popup, select the new bluprint versionenter
    > the application blueprint details.

![](media/image05.jpg)

These details include:

-   **Application Name**: Displays the application name you selected.

-   **Blueprint Name**: Displays the associated blueprint name.

-   **Current Version**: Displays the current version of the blueprint
    > that is being used with the application.

-   **New Version**: Select the new version of the application blueprint
    > (.YML template) that you want to use for the update.

-   **Note**: The blueprint update can be performed only when there are
    > multiple version of the same .YML template.

1.  Click **OK**.

2.  The Blueprint Difference list displays a comparison of each
    > Parameter for the Current and New versions of the blueprint
    > (.YML template).

![](media/image08.jpg)

1.  Click **OK** after you review the changes in the updated version of
    > the blueprint (.YML template).

![](media/image09.jpg)

A progress bar is shown below the selected application instance. In this
process, a rolling update of the blueprint version is performed. Once
completed, the application instance is upgraded to the new version of
the blueprint (.YML template).

When you perform rolling update of an app instancecreate a new, updated
version of the blueprint, it create an instance of the newer version,
points all new application service requests from each running
application that is associated with the older instanceblueprint to the
new version of the blueprint, and then removes the older prior version
of the instanceeach running application.
