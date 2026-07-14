# Validation and Health Checks Guide

## Purpose

This guide defines how platform health is evaluated, monitored, and interpreted within the M-DevOps platform.

The objective is to establish a consistent operational health model that enables engineers to detect issues early, validate platform stability, and maintain confidence in the delivery pipeline.

This guide expands on the Platform Validation Guide and focuses on operational interpretation rather than validation execution.

---

# Health Monitoring Philosophy

The platform follows a simple principle:

```text
Healthy systems are verified continuously.
```

Health should never be assumed.

Health should be demonstrated through observable evidence.

---

# What Defines a Healthy Platform?

A healthy platform satisfies the following conditions:

```text
Source Control Healthy
        ✓

CI/CD Healthy
        ✓

Container Registry Healthy
        ✓

GitOps Healthy
        ✓

Kubernetes Healthy
        ✓

Application Healthy
        ✓
```

Platform health is therefore evaluated across multiple layers.

---

# Health Layers

The platform health model consists of:

```text
Repository Layer
        ↓
CI/CD Layer
        ↓
Artifact Layer
        ↓
GitOps Layer
        ↓
Kubernetes Layer
        ↓
Application Layer
```

Each layer contributes to overall platform stability.

---

# Repository Health

Indicators:

```text
Repository accessible

No unresolved merge conflicts

Clean working tree

Expected branch state
```

Verification:

```powershell
git status
```

Expected result:

```text
working tree clean
```

---

# CI/CD Health

Indicators:

```text
Successful workflow runs

No recurring failures

Build completion

Image publication successful
```

Review:

```text
GitHub Actions
```

Expected state:

```text
Latest pipeline successful
```

Repeated failures should trigger investigation.

---

# Artifact Health

The deployment chain depends on container image availability.

Indicators:

```text
Image exists

Latest image available

Expected tag present
```

Target location:

```text
GitHub Container Registry (GHCR)
```

A missing image blocks deployment.

---

# GitOps Health

GitOps health is measured through synchronization and application status.

Desired state:

```text
Healthy

Synced
```

Indicators requiring investigation:

```text
OutOfSync

Degraded

Unknown
```

GitOps health represents deployment reliability.

---

# Kubernetes Health

Kubernetes health focuses on workload execution.

Verification:

```powershell
kubectl get nodes
```

Expected:

```text
Ready
```

Additional verification:

```powershell
kubectl get pods --all-namespaces
```

Review:

* Failed Pods
* Pending Pods
* Restart loops
* Resource availability

---

# Pod Health

Healthy Pods typically exhibit:

```text
Running

Ready

Low restart count
```

Warning indicators:

```text
CrashLoopBackOff

ImagePullBackOff

Error

Pending
```

These states require investigation.

---

# Deployment Health

Verification:

```powershell
kubectl get deployments
```

Healthy deployment indicators:

```text
Desired replicas available

Ready replicas available

No rollout failures
```

Deployments should remain stable after synchronization.

---

# Service Health

Verification:

```powershell
kubectl get services
```

Healthy indicators:

```text
Service exists

Expected ports exposed

Application reachable
```

Services provide workload accessibility.

---

# Application Health

Ultimately, platform success is measured at the application layer.

Indicators:

```text
Application accessible

Expected functionality available

No visible runtime failures
```

Even if infrastructure appears healthy, application availability must still be verified.

---

# Validation Scripts as Health Controls

The platform implements automated health controls through:

```text
verify_cluster.ps1

verify_gitops.ps1

verify_pods.ps1

verify_all.ps1
```

These scripts define the platform's operational health baseline.

---

# Recommended Health Check Sequence

Preferred workflow:

```text
Repository
        ↓
CI/CD
        ↓
GitOps
        ↓
Kubernetes
        ↓
Validation Scripts
        ↓
Application
```

This sequence progresses from upstream causes to downstream effects.

---

# Health Check Frequency

Recommended cadence:

## Daily

```text
Validation

GitOps review

Pod review
```

---

## After Changes

```text
Deployment

Configuration update

Infrastructure modification
```

Execute:

```powershell
.\scripts\verify_all.ps1
```

---

## Before Major Activities

Examples:

```text
Platform upgrade

Recovery exercise

Large deployment
```

Health should be confirmed before proceeding.

---

# Common Warning Signals

## Repeated Pipeline Failures

Possible causes:

* Source code defects
* Test failures
* Registry publication issues

---

## Repeated Pod Restarts

Possible causes:

* Application startup failures
* Runtime defects
* Resource constraints

---

## OutOfSync Applications

Possible causes:

* Repository changes pending
* Synchronization issues
* Configuration drift

---

## Validation Failures

Possible causes:

* Infrastructure issues
* Deployment issues
* GitOps issues

Validation failures should always be investigated.

---

# Health Dashboard Concept

Engineers should be able to answer the following questions quickly:

```text
Is Git healthy?

Is CI/CD healthy?

Is GHCR healthy?

Is GitOps healthy?

Is Kubernetes healthy?

Is the application healthy?
```

If all answers are positive, platform confidence is high.

---

# Operational Rule

The platform should be considered healthy only when:

```text
Validation Successful

AND

GitOps Healthy

AND

Kubernetes Healthy

AND

Application Available
```

Partial success is not sufficient.

---

# Success Criteria

This guide is complete when the engineer understands:

* Platform health layers
* Health indicators
* Validation interpretation
* Warning signals
* Recommended monitoring workflow

The engineer should be capable of evaluating overall platform health consistently and systematically.

---

# Next Step

Continue with:

**ArgoCD Operations Guide**

This guide explains how to operate, monitor, and troubleshoot the GitOps layer during daily platform operations.
