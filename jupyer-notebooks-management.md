# Kubeflow Jupyter Notebooks

## Launching Jupyter Notebooks

You can launch Jupyter notebooks directly from the Kubeflow GUI by navigating to **Notebook Servers** and creating a new NotebookServer. You’ll need to provide a notebook image URL. Kubeflow includes some sample container images out‑of‑the‑box, but in most cases you’ll use private or custom images and may encounter errors related to `imagePullSecrets`.

## Attaching imagePullSecret to ServiceAccount

The Kubeflow GUI doesn’t let you supply a pull secret directly when creating notebooks. Notebook pods run under the `default-editor` ServiceAccount in your namespace, so you need to attach your registry secret there.

1. **Create the Docker registry secret** (if you haven’t already):

   ```bash
   kubectl create secret docker-registry my-registry-secret \
     --docker-server=<registry-url> \
     --docker-username=<username> \
     --docker-password=<password> \
     --docker-email=<email> \
     -n <namespace>
   ```

2. **Patch `default-editor` to reference the secret**:

   ```bash
   kubectl patch serviceaccount default-editor \
     -n <namespace> \
     --patch '{
       "imagePullSecrets": [
         {"name": "my-registry-secret"}
       ]
     }'
   ```

## Deploying a Jupyter Notebook

1. **Deploy the Notebook using the Kubeflow GUI**:

   Image: kubeflownotebookswg/jupyter-scipy:latest
   Minimum CPU: 0.5
   Minimum Memory: 0.5 Gi
   Volumes: Optional

2. **Install minio dependencies**

    Connect to the Jupyter Notebook terminal and run the following:
    ```bash
    pip3 install minio
    ```

3. **In the Notebook, run the following python code**:

   ```python
   import os
   from minio import Minio

   client = Minio(
     "minio-service.kubeflow.svc.cluster.local:9000",
     access_key="minio",
     secret_key="minio123",
     secure=False
     )

   print(client.list_buckets())

   ```
   

