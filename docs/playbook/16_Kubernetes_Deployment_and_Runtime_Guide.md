# Kubernetes Deployment and Runtime Guide

## Purpose

This guide explains how Kubernetes executes, manages, and maintains the workloads deployed through the GitOps delivery process.

The objective is to understand how deployment definitions become running containers and how Kubernetes maintains application availability.

This guide builds upon the GitOps and ArgoCD Guide.

---

# M-DevOps Dashboard Deployment Contract

The portfolio-facing workload deploys `dashboard_app.py` from:

```text
ghcr.io/hepi66/m_devops_transformation:9715faa3d0fc7c7a545ffaec5817adbac0592e91
```

The CI workflow publishes an immutable full commit-SHA tag for every image.
The workload is pinned to the verified dashboard image instead of relying on
the mutable `latest` tag. No automated image updater is part of this
increment.

The package is public, so the current workload needs no image-pull Secret.
Never commit GHCR credentials, GitHub tokens, kubeconfig data, or Argo CD
credentials. If package visibility changes, create an out-of-repository
Kubernetes image-pull Secret and reference it from the Pod specification.

## Repository Resources

```text
k8s/
├── apps/
│   ├── root-app.yml
│   └── m-devops-dashboard.yaml
└── workloads/
    └── m-devops-dashboard/
        ├── namespace.yaml
        ├── deployment.yaml
        ├── service.yaml
        └── kustomization.yaml
```

The workload uses:

- Namespace `m-devops-dashboard`
- Dedicated ServiceAccount `m-devops-dashboard`
- One replica with a rolling update strategy
- ClusterIP Service `m-devops-dashboard` on port `8501`
- Conservative CPU and memory requests and limits for a small demonstration
  workload
- Streamlit `/_stcore/health` readiness and liveness checks
- Namespace-scoped, read-only access to its Deployment, ReplicaSets, and Pods
- Resource-name-scoped, read-only access to the
  `m-devops-dashboard` Argo CD Application

Readiness starts after 10 seconds and checks every 10 seconds so traffic is
sent only when Streamlit is ready. Liveness starts after 30 seconds and checks
every 20 seconds to avoid restart loops during normal startup.

## Argo CD Management

`k8s/apps/root-app.yml` discovers the child Application
`k8s/apps/m-devops-dashboard.yaml` from the `main` branch. The child
Application renders the Kustomize workload path and targets the
`m-devops-dashboard` namespace.

The root Application remains automated and discovers the child Application.
The child Application intentionally uses manual synchronization for the
bootstrap. This prevents Argo CD from deploying the previous `latest` image
before CI has published the dashboard container. After the workload is pinned
to the new immutable commit-SHA tag, synchronize it explicitly. Automated
pruning and self-healing can then be enabled in a separate, reviewable change.
`CreateNamespace=true` permits initial namespace creation; the Namespace
manifest also keeps namespace labels under GitOps control.

## Static Validation

From the repository root:

```powershell
kubectl kustomize k8s/workloads/m-devops-dashboard
kubectl apply --dry-run=client -k k8s/workloads/m-devops-dashboard
kubectl apply --dry-run=client -f k8s/apps/m-devops-dashboard.yaml
```

## Runtime Verification

After the repository change is available on `main` and CI has published the
dashboard image:

```powershell
kubectl config current-context
kubectl get application m-devops-dashboard -n argocd
kubectl patch application m-devops-dashboard -n argocd --type merge -p '{"operation":{"sync":{}}}'
kubectl get deployment,replicaset,pods,service -n m-devops-dashboard
.\scripts\verify_dashboard.ps1
kubectl port-forward service/m-devops-dashboard 8501:8501 -n m-devops-dashboard
```

In a second terminal:

```powershell
Invoke-WebRequest http://127.0.0.1:8501/_stcore/health
```

The expected health response has HTTP status `200`. Stop port-forwarding with
`Ctrl+C` after verification.

The dashboard can start without GitHub or GHCR credentials. Providers that
cannot authenticate retain their established unavailable or demonstration
behavior. Argo CD and Kubernetes observations use in-cluster ServiceAccount
authentication automatically. Local execution requires no kubeconfig and
returns a safe unavailable state for those providers.

## Live Observation Permissions

The dashboard ServiceAccount has only:

- `get` and `list` for Deployments and ReplicaSets in
  `m-devops-dashboard`
- `get` and `list` for Pods in `m-devops-dashboard`
- `get` for the named Argo CD Application `m-devops-dashboard` in `argocd`

No ClusterRole, cluster-admin permission, Secret read permission, or write
verb is granted.

GitHub authentication remains optional and uses the existing GitHub CLI
mechanism where that CLI is available. `gh` recognizes `GH_TOKEN`, so an
environment-specific deployment may source that variable from a Kubernetes
Secret managed outside this repository. The current slim dashboard image does
not install the GitHub CLI; its in-cluster lifecycle reconstruction therefore
uses Argo CD and Kubernetes evidence when GitHub retrieval is unavailable.
Never store token values in this repository.

## Fragment Refresh Verification

The Delivery Pipeline and Operational Detail Viewer use Streamlit-native
fragments. To verify:

1. Open the dashboard and select a non-default Operational Viewer filter.
2. Observe the live countdown changing once per second.
3. Confirm provider data changes only when the displayed next-refresh time is
   reached.
4. Select `Refresh now` and confirm the monitoring area refreshes immediately.
5. Confirm the selected viewer filter remains unchanged.
6. Confirm static summary, deployment, environment, and lower platform cards
   are not periodically recreated.

The adaptive defaults are 7 seconds for active work, 20 seconds for partial or
unavailable retrieval, and 45 seconds while idle. The implementation contains
no global recurring `st.rerun()`, background thread, or simulated pipeline
transition.

## Verified Initial Deployment

The initial GitOps deployment was verified on 27 July 2026 against the local
Docker Desktop Kubernetes cluster:

- Kubernetes context: `docker-desktop`
- Argo CD Applications: `root-app` and `m-devops-dashboard` both `Synced` and
  `Healthy`
- Deployment: one desired and one available replica
- Pod: `Running`, ready, with zero restarts
- Service: `m-devops-dashboard` (`ClusterIP`) with a ready endpoint on port
  `8501`
- Pulled image digest:
  `sha256:1e389cd00eb2ebe995493e73c51fce904d124b2bfe70752722dd9c8b4f28a4dd`
- Streamlit health endpoint: HTTP `200` with response `ok`
- Browser verification: the deployed application rendered
  `M-DevOps Dashboard` without browser-console warnings or errors

The complete repository verification can be repeated with:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\verify_all.ps1
```

The execution-policy change is limited to the current PowerShell process.
The child Application intentionally retains manual synchronization.

---

# What is Kubernetes?

Kubernetes is a container orchestration platform.

Purpose:

* Run containerized applications
* Manage workloads
* Maintain desired availability
* Provide service discovery
* Support automated recovery

Kubernetes is the runtime platform of the M-DevOps environment.

---

# Position in the Delivery Chain

Kubernetes occupies the following position:

```text
Git Repository
        ↓
ArgoCD
        ↓
Kubernetes
        ↓
Running Application
```

ArgoCD defines what should run.

Kubernetes is responsible for running it.

---

# Desired State Model

Kubernetes operates using a desired state model.

Example:

```text
Desired Replicas = 1
```

If the running container stops unexpectedly:

```text
Container Stops
        ↓
Kubernetes Detects Failure
        ↓
Replacement Container Created
```

The platform continuously attempts to maintain the declared state.

---

# Core Kubernetes Resources

The validated platform architecture includes the following resource types.

---

## Namespace

Purpose:

Provide logical separation of resources.

Validated namespace:

```text
argocd
```

The namespace contains ArgoCD resources and supporting deployment components.

---

## Deployment

Purpose:

Manage application workloads.

Responsibilities:

* Define container image
* Define replica count
* Define container configuration
* Manage rollout behavior

Typical deployment lifecycle:

```text
Deployment
        ↓
ReplicaSet
        ↓
Pod
```

Deployments represent the desired application state.

---

## Pod

Purpose:

Run containers.

A Pod is the smallest deployable Kubernetes unit.

Responsibilities:

* Host application containers
* Execute workloads
* Provide runtime environment

The application ultimately executes inside Pods.

---

## Service

Purpose:

Provide stable network access.

Responsibilities:

* Route traffic
* Abstract Pod lifecycle
* Maintain connectivity

Without Services, clients would need to track changing Pod addresses.

---

# Container Image Deployment

Kubernetes does not deploy source code.

Kubernetes deploys container images.

Example:

```yaml
image: ghcr.io/<owner>/m-devops-transformation:latest
```

Deployment process:

```text
Deployment Resource
        ↓
Image Reference
        ↓
GHCR
        ↓
Image Download
        ↓
Container Startup
```

---

# Workload Lifecycle

A typical workload lifecycle:

```text
Deployment Created
        ↓
Pod Scheduled
        ↓
Image Pulled
        ↓
Container Started
        ↓
Application Available
```

Each step must succeed for the application to become operational.

---

# Kubernetes Health Model

Kubernetes continuously evaluates workload health.

Typical indicators include:

* Pod status
* Container status
* Restart count
* Resource availability

Healthy workloads should remain stable without frequent restarts.

---

# Runtime Verification

Useful commands:

View Pods:

```powershell
kubectl get pods
```

View Services:

```powershell
kubectl get services
```

View Namespaces:

```powershell
kubectl get namespaces
```

View Deployments:

```powershell
kubectl get deployments
```

These commands provide visibility into platform state.

---

# Relationship to ArgoCD

Responsibilities are separated:

```text
ArgoCD
        ↓
Manages Desired State

Kubernetes
        ↓
Runs Desired State
```

ArgoCD deploys.

Kubernetes executes.

---

# Relationship to GHCR

Kubernetes retrieves deployment artifacts from GHCR.

Flow:

```text
GHCR
        ↓
Image Download
        ↓
Pod Startup
```

If the image cannot be downloaded, the workload cannot start.

---

# Common Troubleshooting

## Pod Not Running

Symptoms:

```text
CrashLoopBackOff
```

Possible causes:

* Application startup failure
* Configuration error
* Runtime dependency issue

Inspect Pod logs.

---

## Image Pull Failure

Symptoms:

```text
ImagePullBackOff
```

Possible causes:

* Image missing from GHCR
* Incorrect image reference
* Authentication issue

Verify image availability.

---

## Deployment Not Created

Possible causes:

* ArgoCD synchronization issue
* Invalid manifest configuration
* Repository path problem

Verify GitOps synchronization status.

---

## Service Unreachable

Possible causes:

* Pod unavailable
* Service misconfiguration
* Port mismatch

Verify:

```powershell
kubectl get services
kubectl get pods
```

---

# Current Platform Knowledge Gaps

The following areas require additional verification:

* Final deployment manifest structure
* Service manifest details
* ApplicationSet deployment relationships
* Full bootstrap procedure

These gaps were identified during Playbook reconstruction and should be addressed as additional validated information becomes available.

---

# Success Criteria

This guide is complete when the engineer understands:

* Kubernetes responsibilities
* Deployments
* Pods
* Services
* Image deployment flow
* Runtime lifecycle
* Basic troubleshooting workflow

The engineer should be able to explain how Kubernetes transforms deployment definitions into running application workloads.
---

# Next Recommended Reading

Continue with:

- [Platform Validation Guide](17_Platform_Validation_Guide.md)

---

# Related Documents

- [GitOps and ArgoCD Guide](15_GitOps_and_ArgoCD_Guide.md)
- [Platform Validation Guide](17_Platform_Validation_Guide.md)
- [Kubernetes Troubleshooting](44_Kubernetes_Troubleshooting.md)

---

Return to:

- [Engineering Playbook](README.md)
- [Engineering Documentation Portal](../README.md)
