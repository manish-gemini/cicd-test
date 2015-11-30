**Using Restore**
-----------------

You can restore a deployed application from an existing snapshot as an
“in place” restore. This is similar to the way in which an application
can be restored from a back-up. For example, suppose you create a
snapshot from your production environment and then make some changes to
the application instance. You can use Restore to restart the working
production application based on the snapshot version.

In contrast, you can also restore an application by creating a clone,
which creates a new copy of the application instance from the backup as
a new deployment. For more details, go to “To clone an application using
a new snapshot”.

The appOrbit Platform allows you to:

-   Restore a snapshot from an application.

-   Remove a snapshot.

Each of these procedures is described in a separate topic.

### **To restore a snapshot from an application**

1.  Click **APPS**.

2.  The **BLUEPRINTS** tab is displayed.

3.  Click **SNAPSHOTS**. The SNAPSHOTS tab displays a list of all of the
    > available snapshots.

4.  Select the snapshot you want to use.

5.  Click restore icon to restore a snapshot from an application. When
    > you click restore icon, the snapshot is restored from the
    > INSTANCES tab. A confirmation message displays.

6.  **IMPORTANT**: A snapshot cannot be restored if the application
    > instance is changed after the snapshot is taken. In addition, you
    > are not allowed to restore a snapshot when the snapshot has been
    > used to create one or more clones.

7.  On the confirmation message, click **OK**.

8.  On the INSTANCES tab, a progress bar is shown while the snapshot is
    > being restored. When the deployment is complete, the Application
    > shows a Status of Running.

![](media/image01.jpg)

### **To remove a snapshot**

1.  Click **APPS**.

2.  The **BLUEPRINTS** tab is displayed.

3.  Click **SNAPSHOTS**. The SNAPSHOTS tab displays a list of all of the
    > available snapshots.

4.  Select the snapshot you want to remove.

5.  **Note**: When one or more clones are created from the selected
    > snapshot, the snapshot cannot be removed.

6.  Click delete icon to remove the selected snapshot. A confirmation
    > box is displayed.

7.  **IMPORTANT**: When you delete an application instance, all of the
    > snapshots associated with an application instance are also
    > permanently removed.

8.  Click **OK**.

9.  A progress bar is shown below the selected snapshot while the
    > snapshot is being removed.
