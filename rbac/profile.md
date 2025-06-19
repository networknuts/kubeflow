# Kubeflow Profile: What Gets Created and Why

When a **Kubeflow Profile** is created, a dedicated Kubernetes namespace is provisioned for the user. This setup includes service accounts and pods that are essential for managing and visualizing machine learning pipelines. Below is a detailed explanation of each component.

---

## 📂 Namespace

Each user profile in Kubeflow results in the creation of a unique Kubernetes **namespace**.

### Purpose:
- Provides **isolation** for each user's resources.
- Ensures that notebooks, pipelines, models, secrets, and other components do not interfere with those of other users.

---

## 👤 Service Accounts

Two ServiceAccounts (SAs) are created in each namespace to manage access permissions:

### 1. `default-editor`
- Has **edit** privileges.
- Used by components like Jupyter Notebooks and Pipelines to **create, update, or delete resources**.

### 2. `default-viewer`
- Has **read-only** privileges.
- Used when **viewing or listing** resources, such as pipeline runs and logs.

---

## 🚀 Pods Deployed

Two key pods are deployed automatically in the new namespace to support pipeline artifact viewing and visualization.

### 1. `ml-pipeline-ui-artifact`
- **Containers**: Usually runs 2 containers — one for the service and another for Istio sidecar (if Istio is used).
- **Function**: Serves pipeline output artifacts like files, logs, and metrics through the Kubeflow UI.
- **Use Case**: When a pipeline run completes, this service renders output files and links in the UI.

### 2. `ml-pipeline-visualizationserver`
- **Function**: Generates charts and visualizations such as:
  - ROC curves
  - Confusion matrices
  - Scalar metrics graphs
- **Use Case**: Helps in visually interpreting the model's performance directly in the pipeline output UI.

---

## ✅ Summary Table

| Component                             | Description                                                            |
|--------------------------------------|------------------------------------------------------------------------|
| **Namespace**                        | Isolated Kubernetes environment per user                              |
| `default-editor` SA                  | Allows modifying resources within the namespace                       |
| `default-viewer` SA                  | Allows read-only access to resources                                  |
| `ml-pipeline-ui-artifact` Pod        | Renders pipeline artifacts for display in the UI                      |
| `ml-pipeline-visualizationserver` Pod| Produces visualizations of pipeline outputs (e.g., metrics, graphs)   |
