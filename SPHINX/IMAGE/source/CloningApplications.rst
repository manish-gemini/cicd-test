**Cloning Applications**
------------------------

A clone is used to create a new copy of a running application instance.
You can create a clone of a running application instance and data either
using an existing snapshot. You can also create a clone using a new
snapshot of the running instance of an application and its data on the
fly at a point-in-time.

You can use a clone to:

-   Troubleshoot and resolve issues with the application in a new
    > environment, without disturbing the production instance.

-   Replace an application instance

-   Try out new test scenarios.

The appOrbit Platform allows you to:

-   Clone an application using a new snapshot.

-   Clone an application using an existing snapshot.

Each of these procedures is described in a separate topic.

### **To clone an application using a new snapshot**

1.  Click **APPS**.

2.  The **BLUEPRINTS** tab is displayed.

3.  Click **SNAPSHOTS**. The SNAPSHOTS tab displays a list of all of the
    > available snapshots.

4.  Select the snapshot you want to use.

5.  Click clone icon to create a clone of the selected snapshot.

6.  **Note**: When you click clone icon, the Clone popup displays from
    > the INSTANCES tab.

7.  On the Clone popup, type the **Clone Application Name** to identify
    > the clone.

8.  Click **OK**.

![](media/image06.jpg)

A progress bar is shown below the selected snapshot. In this process, a
second snapshot is created and that snapshot is used to create the
clone. Once created, the clone performs as a new application.

![](media/image02.jpg)

### **To clone an application using an existing snapshot**

1.  Click **APPS**.

2.  The **BLUEPRINTS** tab is displayed.

3.  Click **INSTANCES**. The INSTANCES tab displays a list of all
    > running and stopped applications.

4.  Select the snapshot you want to use.

5.  Click clone icon to create a clone of the selected snapshot.

6.  On the Clone popup, type the **Snapshot Name** to identify
    > the snapshot.

7.  Type the **Clone Application Name** to identify the clone.

8.  Click **OK**.

![](media/image05.jpg)

A progress bar is shown below the selected snapshot. In this process, a
second snapshot is created and that snapshot is used to create the
clone. Once created, the clone performs as a new application.

![](media/image07.jpg)
