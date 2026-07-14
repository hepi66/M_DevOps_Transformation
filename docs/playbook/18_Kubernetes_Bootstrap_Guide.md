# Kubernetes Bootstrap Guide

## Purpose

This guide describes how to bootstrap the Kubernetes foundation required by the M-DevOps platform.

The objective is to prepare a Kubernetes environment that can host ArgoCD, GitOps resources, and application workloads.

This guide focuses on the validated platform path and should be completed before installing ArgoCD.

---

# Scope

This guide covers:

* Kubernetes preparation
* Cluster verification
* Namespace verification
* Readiness validation

This guide does not cover:

* ArgoCD installation
* GitOps bootstrap
* Application deployment

These topics are addressed in subsequent guides.

---

# Prerequisites

Before starting, verify:

* Workstation Setup Guide completed
* Docker Desktop installed
* WSL2 operational
* kubectl available
* Repository cloned

---

# Bootstrap Goal

Successful completion of this guide results in:

```text id="y9m6vc"
Kubernetes Running
        ↓
Cluster Reachable
        ↓
kubectl Operational
        ↓
Ready For ArgoCD Installation
```

---

# Platform Architecture Context

Within the platform architecture:

```text id="v2t7fq"
Workstation
        ↓
Docker Desktop
        ↓
Local Kubernetes Cluster
        ↓
ArgoCD
        ↓
GitOps
        ↓
Application
```

Kubernetes acts as the runtime foundation for all higher platform layers.

---

# Verify kubectl

Open PowerShell:

```powershell id="m5h8dx"
kubectl version --client
```

Expected result:

```text id="r4j1nw"
Client Version displayed
```

This confirms kubectl availability.

---

# Start Kubernetes Environment

The project uses a local Kubernetes environment for learning and validation.

Verify that the Kubernetes environment is running.

Example validation:

```powershell id="a8p2my"
kubectl cluster-info
```

Expected result:

```text id="c7k5ub"
Cluster information displayed
```

The exact output depends on the local Kubernetes implementation.

---

# Verify Cluster Connectivity

Run:

```powershell id="u6v3rq"
kubectl get nodes
```

Expected result:

```text id="d3x7lm"
One or more nodes displayed
```

This confirms communication with the cluster.

---

# Verify Kubernetes Context

Display active context:

```powershell id="f8n2wd"
kubectl config current-context
```

Expected result:

```text id="t5j9qe"
Current context displayed
```

Verify that the correct cluster context is active.

---

# Verify Namespace Visibility

Run:

```powershell id="k1u7pm"
kubectl get namespaces
```

Expected result:

List of available namespaces displayed.

At this stage the ArgoCD namespace may not yet exist.

That is expected.

---

# Verify API Access

Run:

```powershell id="p9r4hx"
kubectl api-resources
```

Purpose:

Confirm API communication and resource discovery.

Successful execution confirms cluster responsiveness.

---

# Cluster Health Verification

Run:

```powershell id="v7y1kd"
kubectl get pods --all-namespaces
```

Purpose:

Identify obvious cluster issues before continuing.

Review:

* Failed Pods
* Pending Pods
* CrashLoopBackOff conditions

The cluster should appear healthy before proceeding.

---

# Bootstrap Validation

Run:

```powershell id="w3q6tb"
.\scripts\verify_cluster.ps1
```

Expected output:

```text id="n2k8fa"
[PASS] Kubernetes cluster is reachable.
```

Additional checks may fail at this stage because ArgoCD has not yet been installed.

That is expected.

---

# Understanding What Has Been Achieved

After completing this guide:

```text id="b5m1zg"
Docker Runtime
        ✓

Kubernetes Cluster
        ✓

kubectl Access
        ✓

Cluster Connectivity
        ✓
```

The platform foundation is now operational.

---

# Common Troubleshooting

## Cluster Not Reachable

Symptoms:

```text id="j4q7nv"
Unable to connect to server
```

Possible causes:

* Kubernetes not running
* Incorrect context
* Docker Desktop not healthy

Verify Docker Desktop first.

---

## No Nodes Available

Symptoms:

```text id="m8t3wk"
No resources found
```

Possible causes:

* Cluster startup incomplete
* Kubernetes disabled
* Runtime initialization still in progress

Wait and retry.

---

## kubectl Not Found

Symptoms:

```text id="u1r6xz"
kubectl is not recognized
```

Possible causes:

* kubectl not installed
* PATH configuration issue

Verify Kubernetes tooling installation.

---

## Incorrect Context

Symptoms:

```text id="s6n4cp"
Commands target wrong cluster
```

Verify:

```powershell id="q7m9vj"
kubectl config get-contexts
```

Switch to the intended context if required.

---

# Success Criteria

This guide is complete when:

* Kubernetes is running
* kubectl is operational
* Cluster connectivity verified
* Nodes visible
* API access functional
* Cluster validation succeeds

The platform is now ready for ArgoCD installation and GitOps bootstrap.

---

# Next Step

Continue with:

**ArgoCD Bootstrap Guide**

This guide installs the GitOps layer and establishes the connection between Git and Kubernetes.
