# Adding External Links to Kubeflow Central Dashboard

This guide explains how to add custom external links (such as documentation pages, company websites, or internal tools) to the Kubeflow Central Dashboard by editing the `centraldashboard-config` ConfigMap.

---

## 🛠️ Step 1: Edit the `centraldashboard-config` ConfigMap

1. Open a terminal and run the following command to edit the ConfigMap:

   ```bash
   kubectl edit configmap centraldashboard-config -n kubeflow
   ```

2. Locate or add the `externalLinks` section in the JSON configuration. Insert your desired link(s).
   Example:

   ```json
   "externalLinks": [
     {
       "type": "item",
       "iframe": false,
       "text": "Network Nuts Website",
       "link": "https://networknuts.net/",
       "icon": "launch"
     }
   ]
   ```

3. Save and exit the editor.

---

## 🔁 Step 2: Restart the Central Dashboard Deployment

Changes to the ConfigMap will not take effect until the Central Dashboard pod is restarted.

1. Run the following command to restart the deployment:

   ```bash
   kubectl rollout restart deployment centraldashboard -n kubeflow
   ```

2. Verify that the new link appears in the Central Dashboard UI after a few seconds.

---

## ✅ Result

The external link (`Network Nuts Website`) should now be visible in the Central Dashboard menu with a "launch" icon.

---

## 🔍 Notes

* The `icon` field refers to a Material Design icon. Common options include `launch`, `help`, `link`, etc.

