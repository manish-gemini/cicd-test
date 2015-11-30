**Deploying the Application**
-----------------------------

When an application is deployed, a given blueprint is used to create a
running instance of an application.

The appOrbit Platform allows you to:

-   Deploy an application with a fresh volume.

-   Deploy an application using a data template.

-   View application instances.

-   Launch an application instance.

-   Remove an application instance.

Each of these procedures is described in a separate topic.

### **To deploy an application with a fresh volume**

1.  Click **APPS**.

2.  On the **BLUEPRINTS** tab, select the application blueprint you want
    > to deploy.

![](media/image16.jpg)

1.  Click deploy Start icon to deploy the application with a
    > fresh volume.

2.  On the Deploy Application popup, enter the application
    > deployment details.

![](media/image18.jpg)

To deploy an application blueprint with fresh data, enter the
application details.

These include:

-   **Application Name**: Type the name you want to use to identify
    > the application.

-   **Destination Cluster**: Select the active cluster on which you want
    > to run the application.

-   **Note**: The selection does not list clusters that are in a
    > maintenance mode.

-   **Group**: Select the group that is to use the application,
    > including the development, testing, staging and
    > production environments.

-   **Source Data Template from Data Catalog**: Leave the checkbox blank
    > to deploy the application blueprint with fresh data.

1.  Click **OK**.

2.  On the INSTANCES tab, a progress bar is shown while the application
    > deployment is being completed. When the deployment is complete,
    > the Application shows a Status of Running.

![](media/image15.jpg)

### **To deploy an application using a data template**

1.  Click **APPS**.

2.  On the **BLUEPRINTS** tab, select the application blueprint you want
    > to deploy.

![](media/image11.jpg)

1.  Click deploy Start icon to deploy the application with a
    > data template.

2.  On the Deploy Application popup, enter the application
    > deployment details.

When a data template has been created for a given blueprint, you can use
the data template to deploy an application. In this case, the data
template is displayed in the Data Template selection list.

![](media/image13.jpg)

To deploy an application blueprint with a data template, enter the
application details.

These include:

-   **Application Name**: Type the name you want to use to identify
    > the application.

-   **Destination Cluster**: Select the active cluster on which you want
    > to run the application.

-   **Note**: The selection does not list clusters that are in a
    > maintenance mode.

-   **Group**: Select the group that is to use the application,
    > including the development, testing, staging and
    > production environments.

-   **Source Data Template from Data Catalog**: Click to select the data
    > catalog and data template you want to use as the source data for
    > this application blueprint.

-   The data template details include:

-   **Data Catalog**: Select the data catalog you want to use. When you
    > select a data catalog that is associated with one or more data
    > templates, the Data Template selection list displays the data
    > template names.

-   **Data Template**: Select the data template you want to use from the
    > data catalog you selected.

-   **Note**: These selections are only shown when active data catalogs
    > and data templates are available for this application.

1.  Click **OK**.

2.  On the INSTANCES tab, a progress bar is shown while the application
    > deployment is being completed. When the deployment is complete,
    > the Application shows a Status of Running.

![](media/image19.jpg)

### **To view application instances**

1.  Click **APPS**.

2.  The **BLUEPRINTS** tab is displayed.

3.  Click **INSTANCES**. The INSTANCES tab displays all running and
    > stopped applications.

4.  This includes:

-   **Application**: Name that identifies each application.

-   **Blueprint – Version**: Blueprint image (.YML template) name
    > and version.

-   **Cluster**: Cluster associated with this application

-   **Status**: Current status of the application, such as Stopped,
    > Running and Failed.

![](media/image14.jpg)

You can click the checkbox under Application to select the application
instance you want to use. Then click any of the icons at the top to
perform actions on the selected application instance.

These actions include:

-   **Start**: Start the selected application instance.

-   **Stop**: Stop the selected application instance.

-   **Delete**: Remove the selected application instance.

-   **Take Snapshot**: Take a snapshot of the selected
    > application instance.

-   **Clone**: Create a clone from a snapshot of the
    > application instance.

-   **Share**: Share the selected application instance with a
    > different user.

-   **Blueprint Update**: Perform a rolling update of the blueprint
    > (.YML template) for the selected application instance, such as to
    > update the blueprint version.

### **To launch an application instance**

1.  Click **APPS**.

2.  The **BLUEPRINTS** tab is displayed.

3.  Click **INSTANCES**. The INSTANCES tab displays a list of all
    > running and stopped applications.

4.  On the INSTANCES tab, locate the running application instance that
    > you want to launch.

5.  Click launchapp icon to display one or more URLs that open running
    > application instances for each blueprint.

![](media/image12.jpg)

1.  Click to select the URL for the application instance you want
    > to open.

2.  **Note**: You can also hover over the term, LAUNCHAPP, to view the
    > URL for the selected application.

![](media/image03.jpg)

1.  The customer-provided application is launched in a separate window.

### **To remove an application instance**

1.  Click **APPS**.

2.  The **BLUEPRINTS** tab is displayed.

3.  Click **INSTANCES**. The INSTANCES tab displays a list of all
    > running and stopped applications.

![](media/image17.jpg)

1.  Click the checkbox next to the Application instance you want
    > to remove.

2.  Click stop application icon to stop the running
    > application instance.

3.  **IMPORTANT**: You are required to stop and remove all running
    > application instances before you can delete a blueprint based on
    > the blueprint version, or upgrade the blueprint to enable the
    > application to use a different blueprint version. For more
    > details, go to ‘To remove a blueprint”.

4.  A confirmation message displays.

5.  Click **OK**.

6.  A progress bar is shown while the application instance is
    > being stopped. When complete, the Application shows a Status
    > of Stopped.

7.  Click delete icon to remove the selected application instance. A
    > confirmation box is displayed.

8.  **IMPORTANT**: Remove an application instance only when it is
    > entirely necessary. When you delete an application instance, all
    > of the snapshots associated with an application instance are also
    > permanently removed.

<!-- -->

1.  Click **OK** to remove the application instance.

2.  A progress bar is shown while the deletion is being completed. When
    > you delete an application instance, all of the snapshots
    > associated with an application instance are also
    > permanently removed.
