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

4. **Next Steps**

* Configure ingress or port-forwarding to access the Kubeflow dashboard
* Set up authentication (e.g., Dex, OIDC)
* Install additional Kubeflow components or customize overlays

*End of install-kubeflow\.md*
