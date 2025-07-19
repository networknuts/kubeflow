# KServe InferenceService Services Overview

This document explains the various Kubernetes `Service` objects created by KServe (on Knative) for an `InferenceService`, their purposes, and how to interact with them.

---

## 1. ExternalName Services

KServe creates DNS aliases that point into the Knative/istio gateway, allowing cluster‑local access via simple service names.

* **`<isvc-name>`** (`ExternalName`)

  * **Description**: The top‑level alias for the InferenceService.
  * **Target**: `knative-local-gateway.istio-system.svc.cluster.local`

* **`<isvc-name>-predictor`** (`ExternalName`)

  * **Description**: Alias specifically for the *predictor* component (e.g., sklearnserver).
  * **Target**: Same gateway as above.

These services do **not** select pods directly; they route through the Knative ingress and VirtualService layer.

---

## 2. ClusterIP Services

For each predictor revision, KServe creates two **ClusterIP** services:

| Service Name                          | Type      | Ports                                                                        | Selector | Purpose                                                                               |
| ------------------------------------- | --------- | ---------------------------------------------------------------------------- | -------- | ------------------------------------------------------------------------------------- |
| `<isvc>-predictor-<revision>`         | ClusterIP | 80/TCP, 443/TCP                                                              | None     | Public face of the Knative revision; fronts the VirtualService, does not select pods. |
| `<isvc>-predictor-<revision>-private` | ClusterIP | 80/TCP, 443/TCP, 8012/TCP, 8022/TCP, 9090/TCP (metrics), 9091/TCP (liveness) | Yes      | Selects the actual model pods; exposes inference and admin/health endpoints.          |

* **Public ClusterIP**: Represents the revision in Istio, but cannot be port‑forwarded since it has *no* pod selector.
* **Private ClusterIP**: The *real* service pointing at your pods; use this for direct testing, metrics, and health checks.

## 3. Why Use the *Private* Service for Port‑Forwarding 

* **Selector**: Only the `-private` service has a selector matching model pods.
* **Direct Pod Access**: Port‑forwarding to it (`kubectl port-forward svc/<isvc>-predictor-<rev>-private ...`) binds to real container ports (e.g., 80 or 8012 for inference).

---

## 4. Traffic Flow

1. **Client** queries `http://<isvc>.<namespace>.svc.cluster.local` (ExternalName)
2. Routed into the **Knative/istio gateway**
3. Knative **RoutingTable** sends to the specific revision
4. Hits the **public** ClusterIP (`<isvc>-predictor-<rev>`)
5. Proxied through Istio to the **private** ClusterIP
6. Load‑balanced to your model **pod(s)** running the sklearnserver

---

## 5. Example: Port‑Forwarding

```bash
kubectl port-forward \
  svc/iriskserve-predictor-00001-private \
  8080:80 \
  -n kubeflow-user-example-com
```

Then access:

```bash
curl -X POST http://localhost:8080/v1/models/1:predict \
     -H "Content-Type: application/json" \
     -d @iris-input.json
```
