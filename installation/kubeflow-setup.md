# Install Kubeflow Manifests

This guide describes how to deploy Kubeflow using the official manifests repository.

## Prerequisites

* `git`, `kubectl`, `kustomize` installed on your control workstation
* Cluster up and running with admin access
* `KUBECONFIG` environment variable pointing to your cluster config

## Steps

1. **Clone the Kubeflow Manifests Repository**

   ```bash
   git clone https://github.com/kubeflow/manifests.git
   cd manifests
   ```

2. **Apply Manifests with Retry Loop**

   Use the following loop to apply all resources under the `example` overlay. The loop retries on failure, waiting 20 seconds between attempts.

   ```bash
   while ! kustomize build example | kubectl apply --server-side --force-conflicts -f -; do
     echo "Retrying to apply resources"
     sleep 20
   done
   ```

3. **Allow Privileged Pod Security**

```bash
#!/usr/bin/env bash
set -euo pipefail

# Find all namespaces with Istio injection enabled
namespaces=$(kubectl get ns \
  -l istio-injection=enabled \
  -o jsonpath='{.items[*].metadata.name}')

if [[ -z "$namespaces" ]]; then
  echo "No namespaces found with istio-injection=enabled"
  exit 1
fi

for ns in $namespaces; do
  echo "→ Updating PodSecurity on namespace \"$ns\""
  kubectl label namespace "$ns" \
    pod-security.kubernetes.io/enforce=privileged \
    pod-security.kubernetes.io/enforce-version=latest \
    --overwrite

  echo "→ Restarting all deployments in \"$ns\""
  kubectl rollout restart deployment -n "$ns" 
done

echo "✅ Done."
```

4. **Fix Image Pull Issues**

   Since the container images used here are being downloaded from Docker Hub, you can run into Pull Rate limit errors, use the below script to apply an imagePullSecret on all the deployments of any project:

```bash
#!/usr/bin/env bash
set -eo pipefail

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <namespace> <imagePullSecret>"
  exit 1
fi

NS="$1"
SECRET="$2"

echo "⏳ Patching every Deployment in namespace '$NS' to add imagePullSecret '$SECRET'..."

# Fetch deployment names, one per line
kubectl get deployments -n "$NS" -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}' \
| while read -r DEP; do
    echo "→ Patching Deployment/$DEP"
    kubectl patch deployment "$DEP" -n "$NS" --type=merge --patch "
{
  \"spec\": {
    \"template\": {
      \"spec\": {
        \"imagePullSecrets\": [
          { \"name\": \"$SECRET\" }
        ]
      }
    }
  }
}"
done

echo "✅ Done."
```

Usage Syntax:

```bash
./patch-all-pullsecrets.sh <namespace> <imagePullSecret>
```

5. **Setup Ingress for Kubeflow**

Kubeflow cannot work on HTTP since it requires JSON Web Tokens (JWT) to prevent Cross-Site Request Forgery (CSRF). Due to this nature of Kubeflow, we have to configure HTTPS ingress. Kubeflow uses the primary service of `istio-ingressgateway` in the `istio-system` project.

   5.1 Deploy Metal LB to get a Public IP for your Kubeflow service

   ```bash
   kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.13.11/config/manifests/metallb-native.yaml
   ```

   5.2 Create YAML for Metal LB Address Pool & Layer 2 ARP 

   ```yaml
   apiVersion: metallb.io/v1beta1
   kind: IPAddressPool
   metadata:
      name: default-pool
      namespace: metallb-system
   spec:
     addresses:
     - 192.168.1.91-192.168.1.92
   ---
   apiVersion: metallb.io/v1beta1
   kind: L2Advertisement
   metadata:
     name: default-l2
     namespace: metallb-system
   spec:
     ipAddressPools:
     - default-pool
   ```

   5.3 Patch Kubeflow service to get Metal LB external LP

   ```bash
   kubectl patch svc istio-ingressgateway \
     -n istio-system \
     --type merge \
     -p '{"spec":{"type":"LoadBalancer"}}'
   ```
Wait until `kubectl get svc -n istio-system istio-ingressgateway` shows an EXTERNAL-IP

   5.4 Issue a TLS Certificate via Kubeflow Built-in Issuer

   ```yaml
   apiVersion: cert-manager.io/v1
   kind: Certificate
   metadata:
     name: kubeflow-ingressgateway-tls
     namespace: istio-system
   spec:
     secretName: kubeflow-ingressgateway-certs
     dnsNames:
       - your.kubeflow.domain.com      # ← replace with your host
     issuerRef:
       name: kubeflow-issuer
       kind: Issuer
       group: cert-manager.io

   ```

   5.5 Enable HTTPS on the Kubeflow Gateway

   ```bash
   kubectl edit gateway kubeflow-gateway -n kubeflow
   ```
   Under `specs.servers`, modify the following:
   ```yaml
     # HTTP → HTTPS redirect
     - port:
         number: 80
         name: http
         protocol: HTTP
       tls:
         httpsRedirect: true
       hosts:
         - "*"
   
     # HTTPS listener
     - port:
         number: 443
         name: https
         protocol: HTTPS
       tls:
         mode: SIMPLE
         credentialName: kubeflow-ingressgateway-certs
       hosts:
         - "*"
   ```

   5.6 Configure DNS   

Point your DNS (e.g. your.kubeflow.domain.com) at the LoadBalancer IP.

6. **Troubleshooting Namespaces**

Kubeflow uses istio injected workloads as privileged pods which Kubernetes may not allow unless specified otherwise:

   ```bash
   # replace <your-ns> with the namespace (e.g. kubeflow, sample, default…)
   NS=<your-ns>
   
   kubectl label ns $NS \
     pod-security.kubernetes.io/enforce=privileged \
     pod-security.kubernetes.io/audit=privileged \
     pod-security.kubernetes.io/warn=privileged \
     --overwrite

   ```

### Kubeflow Deployment Purpose Table

| Deployment | Purpose |
|------------|---------|
| `dex` | OIDC identity provider used for authentication (e.g., GitHub, LDAP, Google). |
| `oauth2-proxy` | Acts as a reverse proxy, handling OAuth2-based login and token exchange for web UIs. |
| `cert-manager` | Manages TLS certificates (e.g., from Let's Encrypt) for secure ingress. |
| `cert-manager-cainjector` | Injects CA data into webhook configurations automatically. |
| `cert-manager-webhook` | Handles dynamic admission control for cert-manager resources. |
| `nfs-provisioner-nfs-subdir-external-provisioner` | Dynamic NFS-based storage provisioning using sub-directories. |
| `minio` | S3-compatible object store used to store pipeline artifacts, models, etc. |
| `mysql` | Relational DB backend used by Katib for experiment metadata. |
| `cluster-local-gateway` | Istio gateway for internal-only traffic between services. |
| `istio-ingressgateway` | External-facing Istio gateway handling ingress traffic. |
| `istiod` | Istio control plane: manages sidecars, traffic rules, certificates. |
| `net-istio-controller` | Integrates Knative networking with Istio for traffic routing. |
| `net-istio-webhook` | Admission webhook for validating Istio networking resources. |
| `coredns` | Internal DNS server for Kubernetes service discovery. |
| `centraldashboard` | The main UI for accessing Kubeflow features. |
| `jupyter-web-app-deployment` | UI for managing and spawning Jupyter notebooks. |
| `notebook-controller-deployment` | Controller for managing notebook CRDs (spawns pods). |
| `profiles-deployment` | Manages user profiles, namespaces, and isolation. |
| `kubeflow-pipelines-profile-controller` | Ties pipelines with user profiles and RBAC. |
| `pvcviewer-controller-manager` | Renders UI to view contents of PVCs in the dashboard. |
| `volumes-web-app-deployment` | Web UI to manage PVCs in the user's namespace. |
| `ml-pipeline` | Orchestrates pipeline execution and lifecycle. |
| `ml-pipeline-ui` | Web UI to browse and run ML pipelines. |
| `ml-pipeline-ui-artifact` | UI to view pipeline artifacts. |
| `ml-pipeline-viewer-crd` | Manages CRD for artifact viewer and rendering logic. |
| `ml-pipeline-visualizationserver` | Renders charts/visuals of metrics during pipeline run. |
| `ml-pipeline-persistenceagent` | Persists pipeline runs and metadata to DB. |
| `ml-pipeline-scheduledworkflow` | Handles scheduled/cron-based pipeline runs. |
| `cache-server` | Caches pipeline steps to avoid redundant executions. |
| `workflow-controller` | Argo controller that runs workflows in Kubernetes. |
| `metadata-grpc-deployment` | gRPC API server for metadata tracking. |
| `metadata-envoy-deployment` | Sidecar proxy for metadata API. |
| `metadata-writer` | Writes pipeline metadata for lineage tracking. |
| `katib-controller` | Manages experiment lifecycle. |
| `katib-db-manager` | Seeds Katib DB schema and manages connections. |
| `katib-mysql` | MySQL database to store experiments and trials. |
| `katib-ui` | Web UI to launch and view Katib experiments. |
| `kserve-controller-manager` | Main controller for managing InferenceService CRDs. |
| `kserve-localmodel-controller-manager` | For serving models from local storage. |
| `kserve-models-web-app` | Web UI to manage deployed models. |
| `tensorboard-controller-deployment` | Manages tensorboard instances tied to experiments. |
| `tensorboards-web-app-deployment` | UI for launching and browsing tensorboards. |
| `training-operator` | Custom controller for training jobs (TFJob, PyTorchJob, etc.). |
| `activator` | Buffers requests for scale-to-zero services until pods are ready. |
| `autoscaler` | Monitors traffic and scales Knative services up/down. |
| `controller` (Knative) | Reconciles Knative Serving CRDs like Revision, Service. |
| `webhook` (Knative) | Validates and mutates Knative resources at creation. |
| `admission-webhook-deployment` | Validates resources like notebooks before they're created. |
