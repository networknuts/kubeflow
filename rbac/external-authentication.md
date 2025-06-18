# 🔐 Enabling GitHub Login in Kubeflow using Dex

Kubeflow supports external authentication providers like GitHub through **Dex**, which acts as an OpenID Connect (OIDC) identity provider.

This guide explains how to configure GitHub as an auth provider in Dex so users can log in to Kubeflow using their GitHub credentials.

---

## 📝 Prerequisites

- A running Kubeflow instance with Dex installed (usually part of default manifests).
- GitHub account.
- Access to edit the `dex` configuration (typically via `config-map` or static Dex manifest).
- A registered GitHub OAuth App.

---

## 🔧 Step 1: Register a GitHub OAuth App

1. Visit: [GitHub Developer Settings → OAuth Apps](https://github.com/settings/developers)
2. Click **New OAuth App**.
3. Fill out the details:

   | Field            | Value                                           |
   |------------------|-------------------------------------------------|
   | Application name | Kubeflow Dex                                    |
   | Homepage URL     | `https://<your-kubeflow-domain>`                |
   | Authorization callback URL | `https://<your-kubeflow-domain>/dex/callback` |

4. After creating, GitHub will show:
   - **Client ID**
   - **Client Secret**

---

## ✍️ Step 2: Update Dex ConfigMap

1. Edit the Dex config map:

   ```bash
   kubectl edit configmap dex -n auth
   ```

2. Add GitHub as a connector inside the `connectors:` section:

   ```yaml
   connectors:
   - type: github
     id: github
     name: GitHub
     config:
       clientID: YOUR_CLIENT_ID
       clientSecret: YOUR_CLIENT_SECRET
       redirectURI: https://<your-kubeflow-domain>/dex/callback
       orgs:
       - name: YOUR_ORG_NAME  # optional: restrict access to a specific org
   ```

   > 💡 Tip: You can remove `orgs` section to allow login from any GitHub account.

3. Save and exit.

---

## 🔁 Step 3: Restart Dex Deployment

Apply the changes by restarting the Dex deployment:

```bash
kubectl rollout restart deployment dex -n auth
```

---

## 🧪 Step 4: Test Login

1. Open your Kubeflow URL in a browser.
2. Click **"GitHub"** on the login screen.
3. You should be redirected to GitHub to authorize.
4. Once authenticated, you’ll be logged into Kubeflow.

---

## ✅ Optional: Customize Dex Login UI

To only show GitHub login (and hide password option), adjust `dex.config.yaml` under the `staticClients` section (if applicable), or UI config settings.

---

## 📌 Notes

* Ensure the **GitHub OAuth App** and **Dex redirect URI** use HTTPS and match exactly.
* Make sure DNS and Ingress (Istio, NGINX, etc.) are configured to route `/dex/callback` correctly.
* You can add more providers (Google, LDAP, etc.) by adding additional entries under `connectors`.

---

## 🔐 Security

* Do **not** commit your `clientSecret` to version control.
* Use Kubernetes secrets to store credentials securely (optional advanced config).

---

## 📚 References

* [Dex GitHub Connector Docs](https://dexidp.io/docs/connectors/github/)
* [Kubeflow Authentication Overview](https://www.kubeflow.org/docs/components/auth/)
