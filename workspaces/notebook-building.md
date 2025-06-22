


# ✅ Image Requirements for Kubeflow Notebooks

To be compatible with **Kubeflow NotebookController**, your container image must meet the following requirements:

---

## 📡 1. Expose HTTP on Port `8888`

- Your application must listen on **port 8888**.
- Kubeflow injects an environment variable called `NB_PREFIX` at runtime.  
  Your application must respect this prefix in its base URL (e.g., `http://0.0.0.0:8888${NB_PREFIX}`).

---

## 🧩 2. IFrame Support (Headers Required)

Kubeflow embeds notebook interfaces via **iframes**.  
Your HTTP server **must** set the following CORS header:

```

Access-Control-Allow-Origin: \*

```

Failing to set this will prevent the UI from rendering properly inside the dashboard.

---

## 👤 3. Run as User `jovyan`

Your container must:

- Run as user: `jovyan`
- Home directory: `/home/jovyan`
- UID: `1000`

This is required to maintain compatibility with Kubeflow's volume mounts and user permissions.

---

## 💾 4. Tolerate an Empty PVC Mounted at `/home/jovyan`

- Kubeflow mounts a **PersistentVolumeClaim (PVC)** at `/home/jovyan`.
- Your container must **start successfully** even if this directory is **empty**.

This ensures notebook data persists across restarts and reassignments.

---

## 📘 Summary

| Requirement                          | Description                                  |
|--------------------------------------|----------------------------------------------|
| `EXPOSE 8888`                        | Required HTTP interface                      |
| `NB_PREFIX` support                  | URL path prefix injected by Kubeflow         |
| `Access-Control-Allow-Origin: *`     | Required header for iframe compatibility     |
| `User: jovyan`, `UID: 1000`          | Expected runtime user in container           |
| `/home/jovyan` as PVC mount point    | Must not fail if volume is empty             |



