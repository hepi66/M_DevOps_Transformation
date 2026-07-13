# Kubernetes Deployment and Runtime Guide

## Purpose

This guide explains how Kubernetes executes, manages, and maintains the workloads deployed through the GitOps delivery process.

The objective is to understand how deployment definitions become running containers and how Kubernetes maintains application availability.

This guide builds upon the GitOps and ArgoCD Guide.

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

# Next Step

Continue with:

**Platform Validation Guide**

This guide explains how platform health is verified using the project's validation framework.
