# Granting Kubeflow Admin Access to a Contributor

## 🎯 Objective

Provide `aryan@networknuts.net` with **admin-level access** to the Kubeflow namespace `kubeflow-user-example-com`, allowing them to:

- View and interact with resources (e.g., Notebooks, Pipelines)
- Be listed as a **Contributor** in the Kubeflow UI
- **Add or remove other contributors** through the "Manage Contributors" interface

---

## 📁 Namespace Involved

- **Target Profile/Namespace**: `kubeflow-user-example-com`
- **User to be Granted Access**: `aryan@networknuts.net`

---

## ✅ Step 1: Create RoleBinding with Admin Role

RoleBinding structure for Kubeflow:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: user-<SAFE_USER_EMAIL>-clusterrole-<USER_ROLE>
  namespace: <PROFILE_NAME>
  annotations:
    role: <USER_ROLE>
    user: <RAW_USER_EMAIL>
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: kubeflow-<USER_ROLE>
subjects:
  - apiGroup: rbac.authorization.k8s.io
    kind: User
    name: <RAW_USER_EMAIL>
```

Apply the following Kubernetes `RoleBinding` manifest to give Aryan `kubeflow-admin` permissions within the target namespace:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: user-aryan-networknuts-net-clusterrole-admin
  namespace: kubeflow-user-example-com
  annotations:
    role: admin
    user: aryan@networknuts.net
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: kubeflow-admin
subjects:
  - apiGroup: rbac.authorization.k8s.io
    kind: User
    name: aryan@networknuts.net
```

* `kubeflow-admin` gives full permissions to manage all Kubeflow resources, including `RoleBindings`.

---

## ✅ Step 2: Ensure Contributor UI Visibility

To allow Aryan to appear as a **Contributor** in the dashboard UI, and access via Istio:

### Apply `AuthorizationPolicy` (if not already present):

```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: user-aryan-networknuts-net-clusterrole-edit
  namespace: kubeflow-user-example-com
  annotations:
    role: edit
    user: aryan@networknuts.net
spec:
  rules:
    - from:
        - source:
            principals:
              - "cluster.local/ns/istio-system/sa/istio-ingressgateway-service-account"
              - "cluster.local/ns/kubeflow/sa/ml-pipeline-ui"
      when:
        - key: request.headers[kubeflow-userid]
          values:
            - aryan@networknuts.net
```

> Even though Aryan has `admin` in RBAC, the `AuthorizationPolicy` is required for visibility in the GUI and routing access.

---

## 🧪 Final Validation

After applying the above:

* Login as `aryan@networknuts.net` to the Kubeflow dashboard
* Go to **"Manage Contributors"**
* Confirm:

  * `kubeflow-user-example-com` is listed under **Profile Memberships**
  * Aryan can **add/remove contributors**

---

## 📌 Notes

* Kubeflow does not natively support multiple owners per Profile.
* This approach simulates multiple owners using `kubeflow-admin` role + contributor UI integration.
* Always match **OIDC email case and exact string** when applying RBAC or Istio policies.
