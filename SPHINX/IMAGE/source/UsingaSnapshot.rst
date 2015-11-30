**Using a Snapshot**
--------------------

Once you have deployed an application, you can create a snapshot to
capture the state of an entire application environment. The snapshot for
an application captures the binaries, metadata and persistent data for
an application. Snapshots are very efficient. You can take multiple
snapshots for an application with minimal resource usage. You can also
restore the application and data from the snapshot.

The appOrbit Platform allows you to:

-   Take a snapshot.

-   View snapshots.

-   Share a snapshot with another user.

-   Promote a snapshot to a data template.

Each of these procedures is described in a separate topic.

### **To take a snapshot**

1.  Click **APPS**.

2.  The **BLUEPRINTS** tab is displayed.

3.  Click **INSTANCES**. The SNAPSHOTS tab displays a list of all of the
    > available snapshots.

4.  On the INSTANCES tab, click the checkbox to select the application
    > instance you want to use.

![](media/image13.png)

1.  Click Take Snapshot icon to take a snapshot of the selected
    > application instance.

![](media/image10.jpg)

1.  On the Snapshot popup, type the **Snapshot Name** to identify
    > the snapshot.

2.  Choose one of the following responses:

-   Click the **Consistent Snapshot** checkbox to freeze a point-in-time
    > consistently across each tier of the application instance. This
    > provides a more accurate snapshot.

-   When you click Consistent Snapshot, a confirmation message is
    > displayed to warn you that the application will pause for
    > a moment.

-   **IMPORTANT**: Using Consistent Snapshot might take a longer time to
    > process and it is more resource intensive. Do not take a
    > Consistent Snapshot when there is a heavy load on an application.

-   Leave the Consistent Snapshot checkbox blank (the default). In this
    > case, a rolling snapshot is taken of each subsequent tier in the
    > application instance.

1.  Click **OK**.

2.  For a consistent snapshot, a warning message displays indicating
    > that the application will pause while the snapshot is taken. Click
    > **OK** to continue.

![](media/image08.jpg)

1.  The snapshot progress is shown below the application instance while
    > the snapshot is being created.

![](media/image06.jpg)

### **To view snapshots**

1.  Click **APPS**.

2.  The **BLUEPRINTS** tab is displayed.

3.  Click **SNAPSHOTS**. The SNAPSHOTS tab displays a list of all of the
    > available snapshots.

4.  This includes:

-   **Snapshot**: Name that identifies each snapshot.

-   **Application**: The application instance that the snapshot
    > is using.

-   **Blueprint – Version**: Blueprint image (.YML template) name
    > and version.

-   **Date/Time Taken**: Date and time when the snapshot was taken.

![](media/image09.jpg)

You can select a snapshot and then click any of the icons at the top to
perform actions on the selected snapshot.

These actions include:

-   **Clone**: Create a clone from a snapshot.

-   **Share**: Share a snapshot with a different user.

-   **Restore**: Restore a snapshot from an application.

-   **Delete**: Remove the selected snapshot.

-   **Promote**: Promote a snapshot from a data template.

### **To share a snapshot with another user**

**IMPORTANT**: Before you can share a snapshot, you need set up the SMTP
settings in the appOrbit Platform settings. The SMTP settings allow the
users to be listed. For more details, go to ‘To use the SMTP settings”.

1.  Click **APPS**.

2.  The **BLUEPRINTS** tab is displayed.

3.  Click **SNAPSHOTS**. The SNAPSHOTS tab displays a list of all of the
    > available snapshots.

4.  Click the checkbox for the snapshot you want to use.

5.  Click share icon to share the selected snapshot with another user.

6.  On the Share Snapshot popup, on the **Users** box, select the name
    > of one or more users with whom you want to share the snapshot.

7.  Click the checkboxes below **Specify Snapshot Permissions** to
    > indicate which permissions you want to give to each user including
    > **View**, **Clone** and **Share** permissions.

8.  Click **OK**.

![](media/image11.jpg)

### **To promote a snapshot to a data template**

1.  Click **APPS**.

2.  The **BLUEPRINTS** tab is displayed.

3.  Click **SNAPSHOTS**. The SNAPSHOTS tab displays a list of all of the
    > available snapshots.

4.  Click the checkbox to select the snapshot you want to promote.

5.  Click promote icon to promote a snapshot to a data template.

6.  **Note**: A snapshot can be promoted to data template only once. You
    > are not allowed to make additional data templates from the
    > same snapshot.

![](media/image07.jpg)

1.  On the Promote Snapshot popup, type the **Data Template Name** to
    > identify the data template.

2.  Select the **Data Catalog** where you want to store the
    > data template.

3.  Click **OK**.

4.  A progress bar is shown below the selected snapshot while it is
    > being copied to a data template in the selected data catalog.
