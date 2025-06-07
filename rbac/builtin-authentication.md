# Kubeflow Authentication Setup

This README describes how to set up user authentication in Kubeflow using Dex with static passwords and user Profiles.

## Prerequisites

* Kubeflow installed and running
* `kubectl` configured to access your cluster
* Dex deployed in the `auth` namespace
* Python 3 and the `passlib` library installed (for generating bcrypt hashes)

## 1. Create a User Profile

Save the following YAML as `profile.yaml`, replacing the placeholders with your own values:

```yaml
apiVersion: kubeflow.org/v1beta1
kind: Profile
metadata:
  name: test-user-profile   # Replace with the desired profile name (this becomes the user's namespace)
spec:
  owner:
    kind: User
    name: test-user@kubeflow.org
  resourceQuotaSpec:    # Optional: restrict resource usage per user
    hard:
      cpu: "2"
      memory: 2Gi
      requests.nvidia.com/gpu: "1"
      persistentvolumeclaims: "1"
      requests.storage: "5Gi"
```

Apply it with:

```bash
kubectl apply -f profile.yaml
```

## 2. Generate bcrypt Passwords

Use the `gen-bcrypt.sh` script below to prompt for a password and output a bcrypt hash at cost factor 12 with the `$2y$` prefix.

```bash
#!/usr/bin/env bash
# gen-bcrypt.sh: generate bcrypt hash for Dex staticPasswords
read -s -p "Password: " pw && echo
python3 - <<PYCODE
from passlib.hash import bcrypt
print(bcrypt.using(rounds=12, ident="2y").hash("$pw"))
PYCODE
```

Make it executable and run:

```bash
chmod +x gen-bcrypt.sh
./gen-bcrypt.sh
```

Copy the resulting hash for inclusion in Dex.

## 3. Update the Dex ConfigMap

Edit the Dex ConfigMap (`dex`) in the `auth` namespace to include your users under `staticPasswords`. You can reference an environment variable (`hashFromEnv`) or paste the hash directly.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: dex
  namespace: auth
data:
  config.yaml: |-
    staticPasswords:
      - email: user@example.com
        hashFromEnv: DEX_USER_PASSWORD
        username: user
        userID: "15841185641784"
      - email: test-user@kubeflow.org
        username: test-user
        hash: $2y$12$umVt4J6/utjUwMXdIRpg3OnmdKps7jtznxUnirexZrN.rL529mdAK
```

After updating, restart the Dex deployment to pick up the changes:

```bash
kubectl -n auth rollout restart deployment dex
```

---

You now have a new user Profile and corresponding static password authentication configured in Kubeflow.
