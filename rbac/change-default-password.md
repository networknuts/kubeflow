
# 🔐 Change Default Kubeflow Password (Using dex-passwords Secret)

This guide explains how to **safely update the default user's password** in a Kubeflow environment where Dex reads password hashes from a Kubernetes Secret named `dex-passwords`.

---

## 📌 Assumptions

- Dex is deployed in the `auth` namespace.
- Dex is configured to read user credentials from the `dex-passwords` Secret.
- You have `kubectl` access to your cluster.

---

## 🛠️ Steps to Change Password

### 1. Generate a Bcrypt Password Hash

Dex requires a bcrypt hash. You can generate one using `htpasswd` or Python.

#### ✅ Option A: `htpasswd` (recommended)

```bash
sudo apt install apache2-utils  # Skip if already installed

htpasswd -bnBC 10 "" newpassword | tr -d ':\n'
```

#### ✅ Option B: Python

```python
import bcrypt
print(bcrypt.hashpw(b"newpassword", bcrypt.gensalt()).decode())
```

Copy the output — this will be your new password hash.

---

### 2. Delete the Existing Secret

```bash
kubectl delete secret dex-passwords -n auth
```

---

### 3. Create the New Secret with Updated Hash

Replace `REPLACE_WITH_HASH` with the actual bcrypt hash from step 1:

```bash
kubectl create secret generic dex-passwords \
  --from-literal=DEX_USER_PASSWORD='REPLACE_WITH_HASH' \
  -n auth
```

---

### 4. Restart the Dex Pod

To apply the new password, restart Dex:

```bash
kubectl delete pods --all -n auth
```

---

### 5. Log In

Go to your Kubeflow URL and try logging in using:

* **Username/Email:** as originally configured (e.g., `admin@example.com`)
* **Password:** the new password you just set

---

## ✅ Verification

You can inspect the new secret:

```bash
kubectl get secret dex-passwords -n auth -o yaml
```

Check Dex logs if login fails:

```bash
kubectl logs -l app=dex -n auth
```

---

## 🔒 Best Practices

* Keep password hashes secure — do not commit them to version control.
* Always regenerate the hash for new passwords — do **not** paste plain text.
