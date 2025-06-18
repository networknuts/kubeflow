# `CD_REGISTRATION_FLOW` in Kubeflow Central Dashboard

The `CD_REGISTRATION_FLOW` environment variable controls the user registration behavior when new users access the Kubeflow Central Dashboard.

---

## 🔧 What is `CD_REGISTRATION_FLOW`?

The `CD_REGISTRATION_FLOW` environment variable is part of the `centraldashboard` Deployment and defines how user profiles are created when a new user signs in for the first time.

---

## 🧩 Supported Values

| Value           | Description                                                                 |
|----------------|-----------------------------------------------------------------------------|
| `true` (default) | Shows a **registration page** to the user to input username and namespace. |
| `false`         | **Skips the registration page** and directly uses the authenticated identity (e.g., email) to auto-provision profile and namespace. |

---

## ✍️ How to Set the Variable

1. Edit the centraldashboard deployment:

   ```bash
   kubectl edit deployment centraldashboard -n kubeflow
   ```

2. Locate the `env` section under the container spec and modify or add the variable:

   ```yaml
   env:
     - name: CD_REGISTRATION_FLOW
       value: "false"
   ```

3. Save and exit the editor.

4. Restart the deployment to apply changes:

   ```bash
   kubectl rollout restart deployment centraldashboard -n kubeflow
   ```

---

## ✅ Advantages and ❌ Disadvantages

### ✅ CD\_REGISTRATION\_FLOW = "false" (Automatic Registration)

* **Advantages:**

  * Fully automatic onboarding; no manual input required.
  * Seamless integration in enterprise SSO or OAuth setups.
  * Reduces confusion for non-technical users.

* **Disadvantages:**

  * Namespace names are derived from the identity provider (e.g., email) which may be long or contain special characters.
  * Less control over namespace naming conventions.
  * May require cleanup logic for inactive users.

---

### ✅ CD\_REGISTRATION\_FLOW = "true" (Manual Registration)

* **Advantages:**

  * Users can choose their namespace and username explicitly.
  * More control and transparency over resource allocation.
  * Suitable for environments with custom naming or quotas.

* **Disadvantages:**

  * Slower first-time login flow.
  * Can lead to user error if incorrect names are entered.
  * May confuse non-technical users.

---

## 🧪 When to Use What?

| Use Case                           | Recommended Setting |
| ---------------------------------- | ------------------- |
| Multi-user environment with SSO    | `false`             |
| Training or classroom environment  | `true`              |
| Open clusters with limited control | `true`              |
| Enterprise internal platform       | `false`             |
