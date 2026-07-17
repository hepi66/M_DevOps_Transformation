# GitOps and ArgoCD Guide

## Purpose

This guide explains how the M-DevOps platform deploys applications using GitOps principles and ArgoCD.

The objective is to understand how repository state is transformed into a running Kubernetes deployment without executing manual deployment commands.

This guide bridges the gap between deployment artifacts stored in GHCR and running workloads inside Kubernetes.

---

# What is GitOps?

GitOps is an operational model where Git becomes the authoritative source of truth for platform configuration.

Instead of deploying software manually:

```text id="p6k2rz"
Engineer
    ↓
kubectl apply
```

the platform follows:

```text id="e4h7qw"
Git Change
    ↓
ArgoCD
    ↓
Kubernetes
```

The desired platform state is stored in Git.

---

# Core GitOps Principle

The platform continuously compares:

```text id="a2m8xf"
Desired State
        vs
Actual State
```

Desired State:

* Stored in Git

Actual State:

* Running inside Kubernetes

ArgoCD continuously attempts to make both states identical.

---

# What is ArgoCD?

ArgoCD is a GitOps deployment controller for Kubernetes.

Responsibilities:

* Monitor Git repositories
* Detect configuration changes
* Synchronize cluster state
* Report deployment health
* Self-heal configuration drift

ArgoCD acts as the automation engine between Git and Kubernetes.

---

# Position in the Delivery Chain

ArgoCD occupies the following position:

```text id="j7p3yk"
Git Repository
        ↓
ArgoCD
        ↓
Kubernetes
        ↓
Running Application
```

ArgoCD does not build software.

ArgoCD deploys configuration.

---

# Platform GitOps Architecture

Validated architecture:

```text id="v4d8hs"
Git Repository
        ↓
root-app.yml
        ↓
ArgoCD
        ↓
Application Resources
        ↓
Kubernetes
```

The repository contains the deployment definitions.

ArgoCD continuously evaluates those definitions.

---

# Root Application Pattern

Validated repository artifact:

```text id="u5c7wj"
k8s/apps/root-app.yml
```

Purpose:

* Bootstrap GitOps configuration
* Register application definitions
* Serve as GitOps entry point

The Root Application pattern allows ArgoCD to manage multiple applications through a single entry point.

---

# Application Definitions

ArgoCD manages Kubernetes resources through application definitions.

Typical responsibilities include:

* Repository registration
* Deployment synchronization
* Health monitoring
* State reconciliation

The exact application structure should be verified against the repository.

---

# ApplicationSet Support

Validated:

```text id="k1r5gp"
ApplicationSet CRD installed
```

Validation output confirmed:

```text id="f9q2zs"
[PASS] ApplicationSet CRD is installed.
```

Purpose of ApplicationSets:

* Manage multiple applications
* Generate application definitions dynamically
* Simplify large-scale GitOps management

Current implementation may use ApplicationSets directly or may be prepared for future expansion.

---

# Synchronization Process

Deployment lifecycle:

```text id="c3w6nb"
Git Repository
        ↓
Manifest Change
        ↓
ArgoCD Detects Change
        ↓
Synchronization
        ↓
Kubernetes Updated
```

No direct deployment command is required.

---

# Self-Healing

A key GitOps capability is self-healing.

Example:

```text id="h8x4tf"
Manual Cluster Change
        ↓
State Drift
        ↓
ArgoCD Detects Drift
        ↓
Desired State Restored
```

This helps maintain platform consistency.

---

# Health Status

ArgoCD tracks application status.

Typical states include:

```text id="m7d3qy"
Healthy
Progressing
Degraded
Missing
Unknown
```

Healthy indicates that the deployed resources match the desired state and are functioning correctly.

---

# Synchronization Status

Typical synchronization states:

```text id="r4j8ko"
Synced
OutOfSync
Unknown
```

A healthy deployment should report:

```text id="q2w9pl"
Healthy
Synced
```

---

# Relationship to GHCR

ArgoCD does not store images.

ArgoCD deploys manifests that reference images.

Example:

```yaml id="z6k1tr"
image: ghcr.io/<owner>/m-devops-transformation:latest
```

Deployment flow:

```text id="n8m4dy"
Manifest
        ↓
Image Reference
        ↓
GHCR
        ↓
Kubernetes
```

---

# Relationship to Kubernetes

ArgoCD manages desired state.

Kubernetes executes workloads.

Relationship:

```text id="b4p7nw"
ArgoCD
        ↓
Creates Resources
        ↓
Kubernetes
        ↓
Runs Workloads
```

Both components are required.

---

# Common Troubleshooting

## OutOfSync

Symptoms:

```text id="s5r9cm"
Application OutOfSync
```

Possible causes:

* Repository changes pending
* Synchronization failure
* Cluster state drift

Review ArgoCD synchronization details.

---

## Degraded Application

Symptoms:

```text id="f2m7kv"
Application Degraded
```

Possible causes:

* Pod failures
* Service failures
* Invalid manifests

Review workload health.

---

## Missing Resources

Symptoms:

```text id="x1q8wt"
Expected resources not created
```

Possible causes:

* Invalid manifest configuration
* Repository path issues
* Synchronization errors

Verify application definitions.

---

# Current Documentation Gap

The following areas require additional reconstruction:

* Detailed application manifests
* Detailed ApplicationSet configuration
* Full bootstrap workflow
* Cluster recovery workflow

These items were identified during Playbook analysis and will be addressed as knowledge becomes available.

---

# Success Criteria

This guide is complete when the engineer understands:

* GitOps principles
* ArgoCD responsibilities
* Root Application pattern
* Synchronization lifecycle
* Health and sync states
* Relationship between Git, GHCR, ArgoCD, and Kubernetes

The engineer should be able to explain how a Git change eventually becomes a running deployment.
---

# Next Recommended Reading

Continue with:

- [Kubernetes Deployment and Runtime Guide](16_Kubernetes_Deployment_and_Runtime_Guide.md)

---

# Related Documents

- [GHCR Guide](14_GHCR_Guide.md)
- [Kubernetes Deployment and Runtime Guide](16_Kubernetes_Deployment_and_Runtime_Guide.md)
- [ArgoCD Troubleshooting](43_ArgoCD_Troubleshooting.md)

---

Return to:

- [Engineering Playbook](README.md)
- [Engineering Documentation Portal](../README.md)
