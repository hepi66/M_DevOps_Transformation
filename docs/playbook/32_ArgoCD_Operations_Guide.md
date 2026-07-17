# ArgoCD Operations Guide

## Purpose

This guide explains how to operate, monitor, and maintain the ArgoCD GitOps layer during normal platform operations.

The objective is to enable engineers to identify synchronization issues, investigate deployment problems, and maintain confidence in the GitOps delivery process.

This guide focuses on operational activities after ArgoCD has already been installed and bootstrapped.

---

# Operational Role of ArgoCD

ArgoCD acts as the deployment controller of the platform.

Responsibilities:

```text id="y6m2rb"
Monitor Git Repository
        ↓
Detect Changes
        ↓
Synchronize Cluster
        ↓
Maintain Desired State
```

During daily operations ArgoCD becomes one of the most important platform health indicators.

---

# Daily ArgoCD Health Review

The primary operational questions are:

```text id="g7n4vk"
Is ArgoCD running?

Is synchronization working?

Are applications healthy?

Is GitOps functioning correctly?
```

If all answers are positive, the GitOps layer can generally be considered healthy.

---

# Core Health Indicators

ArgoCD health is evaluated using two primary states:

## Synchronization State

Examples:

```text id="x2m8py"
Synced

OutOfSync

Unknown
```

Desired state:

```text id="r5k1vt"
Synced
```

---

## Application Health State

Examples:

```text id="f4n7mz"
Healthy

Progressing

Degraded

Missing

Unknown
```

Desired state:

```text id="m8p2qw"
Healthy
```

---

# Desired Operational State

The preferred platform condition is:

```text id="j6v3xt"
Healthy
        +
Synced
```

This indicates:

* Desired state matches cluster state
* Resources deployed successfully
* No active synchronization issues

---

# Verify ArgoCD Components

Verify ArgoCD workloads:

```powershell id="u2q7nh"
kubectl get pods -n argocd
```

Review:

* Running status
* Restart counts
* Failed components

Typical components include:

```text id="k9m4wr"
argocd-server

argocd-repo-server

argocd-application-controller
```

Exact component names depend on the installed version.

---

# Verify Namespace

Execute:

```powershell id="w7x1pa"
kubectl get namespaces
```

Expected:

```text id="q8n3yc"
argocd
```

The namespace must exist for GitOps functionality.

---

# Verify ApplicationSet Support

Execute:

```powershell id="c4v8mt"
kubectl get crd | findstr applicationset
```

Expected:

```text id="b6q2dz"
applicationsets.argoproj.io
```

This confirms ApplicationSet capability remains available.

---

# Verify GitOps Validation

Execute:

```powershell id="t9r5ku"
.\scripts\verify_gitops.ps1
```

Expected:

```text id="a3m8xp"
PASS
```

This provides a repeatable operational verification.

---

# Understanding Synchronization

Normal synchronization lifecycle:

```text id="p4v6nw"
Git Commit
        ↓
Git Push
        ↓
Repository Updated
        ↓
ArgoCD Detects Change
        ↓
Synchronization
        ↓
Cluster Updated
```

This process should require no manual deployment actions.

---

# Understanding OutOfSync

State:

```text id="u8q1mb"
OutOfSync
```

Meaning:

The cluster does not match the desired state stored in Git.

Possible causes:

```text id="v2w9pk"
Recent repository changes

Synchronization failure

Manual cluster modification

Configuration drift
```

OutOfSync should always be investigated.

---

# Understanding Degraded

State:

```text id="n6m4zx"
Degraded
```

Meaning:

Resources exist but are not functioning correctly.

Possible causes:

```text id="f3v7qc"
Pod failures

Deployment failures

Service issues

Invalid manifests
```

Degraded status usually requires immediate investigation.

---

# Understanding Unknown

State:

```text id="k2x5yn"
Unknown
```

Meaning:

ArgoCD cannot determine application health.

Possible causes:

```text id="d8v3pt"
Communication issue

Missing resources

Controller issue
```

Further investigation is required.

---

# Drift Detection

One of ArgoCD's most valuable capabilities is drift detection.

Example:

```text id="m1q8vk"
Git Desired State
        ↓
Manual Cluster Change
        ↓
State Drift
        ↓
ArgoCD Detects Difference
```

This protects platform consistency.

---

# Self-Healing Concept

GitOps platforms attempt to maintain:

```text id="g4m7tb"
Git State
        =
Cluster State
```

When differences appear:

```text id="e7p2wd"
Drift Detected
        ↓
Synchronization
        ↓
State Restored
```

This behavior improves platform reliability.

---

# Investigating GitOps Problems

Recommended investigation order:

```text id="z8n5qu"
Repository
        ↓
ArgoCD
        ↓
Application Status
        ↓
Pods
        ↓
Services
```

Avoid starting troubleshooting at the lowest layer first.

---

# Operational Checklist

Daily review:

```text id="v9q2tr"
□ argocd namespace exists

□ ArgoCD Pods running

□ ApplicationSet available

□ Applications Healthy

□ Applications Synced

□ GitOps validation successful
```

This checklist provides a quick operational assessment.

---

# Common Operational Issues

## ArgoCD Pods Not Running

Verify:

```powershell id="m5v7qn"
kubectl get pods -n argocd
```

Investigate:

* Failed pods
* Restart loops
* Pending status

---

## Applications OutOfSync

Possible causes:

* Repository changes
* Synchronization issue
* Drift

Review application status before proceeding.

---

## Applications Degraded

Possible causes:

* Deployment issue
* Kubernetes issue
* Manifest issue

Investigate workload health.

---

## GitOps Validation Failure

Execute:

```powershell id="c6m4yx"
.\scripts\verify_gitops.ps1
```

Review reported failures carefully.

The validation output should guide the investigation.

---

# Operational Best Practices

Prefer:

```text id="t3w8vd"
Observe

Validate

Investigate

Correct

Validate Again
```

Avoid making multiple changes simultaneously during troubleshooting.

---

# Success Criteria

This guide is complete when the engineer understands:

* ArgoCD responsibilities
* Synchronization states
* Health states
* Drift detection
* Self-healing concepts
* Daily GitOps operations

The engineer should be capable of monitoring and maintaining the GitOps layer confidently.
---

# Next Recommended Reading

Continue with:

- [Kubernetes Operations Guide](33_Kubernetes_Operations_Guide.md)

---

# Related Documents

- [GitOps and ArgoCD Guide](15_GitOps_and_ArgoCD_Guide.md)
- [Validation and Health Checks](31_Validation_and_Health_Checks.md)
- [ArgoCD Troubleshooting](43_ArgoCD_Troubleshooting.md)

---

Return to:

- [Engineering Playbook](README.md)
- [Engineering Documentation Portal](../README.md)
