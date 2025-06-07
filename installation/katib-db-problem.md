# Katib MySQL Data Dictionary Initialization Error

This README describes the error encountered with the Katib MySQL pod in the Kubeflow namespace and the steps taken to resolve it.

## Error Observed

When inspecting the logs of the MySQL container, the following error appeared:

```plain
2025-06-06T08:34:43.664623Z 1 [ERROR] [MY-011096] [Server] No data dictionary version number found.
2025-06-06T08:34:43.665012Z 0 [ERROR] [MY-010020] [Server] Data Dictionary initialization failed.
2025-06-06T08:34:43.665156Z 0 [ERROR] [MY-010119] [Server] Aborting
```

### Root Cause

The MySQL entrypoint script skips initialization if it detects any files or directories under `/var/lib/mysql`. A nested `datadir` folder was present on the PVC, so the system tables were never bootstrapped, leading to the missing data dictionary.

## Diagnosis Steps

1. **Check PVC status**

   ```bash
   kubectl describe pvc katib-mysql -n kubeflow
   ```
2. **Mount and inspect PVC contents**

   * Create a debug pod mounting the PVC:

     ```bash
     # debug-mysql.yaml
     apiVersion: v1
     kind: Pod
     metadata:
       name: katib-mysql-debug
       namespace: kubeflow
     spec:
       containers:
         - name: shell
           image: busybox
           command: ["sleep", "3600"]
           volumeMounts:
             - mountPath: /mnt/mysql-data
               name: mysql-pv
       volumes:
         - name: mysql-pv
           persistentVolumeClaim:
             claimName: katib-mysql
     ```
   * Inspect files:

     ```bash
     kubectl exec -it katib-mysql-debug -n kubeflow -- sh
     ls -l /mnt/mysql-data
     ```
3. **Identify nested `datadir`**

   ```bash
   /mnt/mysql-data# ls
   datadir/  mysql.sock -> /var/run/mysqld/mysqld.sock
   ```
4. **Inspect contents of `datadir`**

   ```bash
   cd /mnt/mysql-data/datadir
   ls
   # Files: ibdata1, ib_logfile*, mysql/, undo_00*
   ```

## Resolution Options

Two approaches can fix the issue: wiping and recreating the PVC, or relocating the contents within the existing PVC.

### Option A: Wipe & Recreate PVC (Destructive)

> **Warning:** This will destroy all existing MySQL data.

1. Delete the MySQL pod:

   ```bash
   kubectl delete pod katib-mysql-57f8b8d46f-s2qz7 -n kubeflow
   ```
2. Delete the PVC (and PV if it remains):

   ```bash
   kubectl delete pvc katib-mysql -n kubeflow
   kubectl delete pv pvc-7a7a13b2-0d49-4c4c-9b84-8553d7ac7966
   ```
3. Restart the StatefulSet/Deployment:

   ```bash
   kubectl rollout restart statefulset katib-mysql -n kubeflow
   # or deployment if applicable
   ```
4. Verify fresh initialization in logs:

   ```bash
   kubectl logs katib-mysql-0 -n kubeflow
   # Look for "Initializing database" and "ready for connections"
   ```

### Option B: Relocate Existing Files (Non-destructive)

1. In the debug pod, move files out of `datadir` into the root:

   ```bash
   kubectl exec -it katib-mysql-debug -n kubeflow -- sh
   mv /mnt/mysql-data/datadir/* /mnt/mysql-data/
   rmdir /mnt/mysql-data/datadir
   chown -R 999:999 /mnt/mysql-data
   chmod 700 /mnt/mysql-data
   exit
   ```
2. Delete the MySQL pod to trigger reinitialization:

   ```bash
   kubectl delete pod katib-mysql-57f8b8d46f-s2qz7 -n kubeflow
   ```
3. Check logs for a clean startup:

   ```bash
   kubectl logs <new-mysql-pod> -n kubeflow
   # Expect "Initializing database" and "ready for connections"
   ```

## Confirmation

After applying either option, the MySQL pod should start without the data dictionary error and display:

```plain
[Entrypoint] MySQL init process done. Ready for start up
[Server] /usr/sbin/mysqld: ready for connections.
```

At that point, Katib’s MySQL is fully operational. Feel free to delete the debug pod:

```bash
kubectl delete pod katib-mysql-debug -n kubeflow
```
