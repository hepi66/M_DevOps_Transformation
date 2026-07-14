# ArgoCD Bootstrap Guide

## Purpose

This guide describes how the GitOps layer is established within the M-DevOps platform.

The objective is to install ArgoCD, prepare GitOps functionality, and bootstrap repository-driven deployments.

This guide follows the Kubernetes Bootstrap Guide.

---

# Scope

This guide covers:

* ArgoCD installation
* Namespace verification
* Root Application pattern
* GitOps bootstrap process
* Initial validation

This guide does not cover:

* Daily operations
* Troubleshooting procedures
* Platform recovery

These topics are addressed in later Playbook sections.

---

# Bootstrap Goal

Successful completion results in:

```text id="j8r5fw"
Kubernetes
        ✓

ArgoCD Installed
        ✓

Git Repository Registered
        ✓

GitOps Active
        ✓
```

At this point the platform becomes self-managing through GitOps.

---

# What is Being Installed?

ArgoCD is the GitOps controller of the platform.

Responsibilities:

* Monitor Git repositories
* Detect configuration changes
* Synchronize cluster state
* Track deployment health
* Reconcile configuration drift

ArgoCD becomes the deployment authority of the platform.

---

# Validated Platform Components

The following components were validated during project execution:

```text id="k4u7nx"
argocd namespace

root-app.yml

ApplicationSet CRD

GitOps validation scripts
```

These artifacts form the foundation of the GitOps architecture.

---

# Install ArgoCD

Install ArgoCD using the project's validated installation procedure.

After installation verify:

```powershell id="m1x7rb"
kubectl get namespaces
```

Expected result:

```text id="n5v3jq"
argocd
```

The namespace should now exist.

---

# Verify ArgoCD Pods

Run:

```powershell id="f9k2wu"
kubectl get pods -n argocd
```

Expected result:

Multiple ArgoCD components should be running.

Typical components include:

```text id="y2m8sp"
argocd-server

argocd-repo-server

argocd-application-controller
```

Exact component names may vary by version.

---

# Verify ApplicationSet Support

Validated project output confirmed:

```text id="b8t6dn"
[PASS] ApplicationSet CRD is installed.
```

Verify manually:

```powershell id="r4q7vk"
kubectl get crd | findstr applicationset
```

Expected result:

```text id="c7n1mx"
applicationsets.argoproj.io
```

This confirms ApplicationSet functionality.

---

# Root Application Pattern

Validated repository artifact:

```text id="s6j3wf"
k8s/apps/root-app.yml
```

Purpose:

* Bootstrap GitOps
* Register repository resources
* Deploy managed applications

The Root Application serves as the GitOps entry point.

---

# Bootstrap Process

Validated high-level architecture:

```text id="p3m7zu"
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

The Root Application connects repository state to cluster state.

---

# Apply Root Application

Validated repository entry point:

```text id="a2w9rh"
k8s/apps/root-app.yml
```

Apply:

```powershell id="h5n4xt"
kubectl apply -f k8s/apps/root-app.yml
```

Purpose:

Register the Root Application with ArgoCD.

This step activates GitOps management.

---

# Synchronization

After registration:

```text id="z8q6pb"
ArgoCD
        ↓
Reads Repository
        ↓
Detects Resources
        ↓
Synchronizes Cluster
```

The cluster begins moving toward the desired state stored in Git.

---

# Verify Synchronization

Review ArgoCD status.

Healthy target state:

```text id="m4v8jk"
Healthy

Synced
```

These states indicate:

* Resources deployed
* Desired state achieved
* No active drift detected

---

# Validate GitOps Layer

Run:

```powershell id="t7w3ny"
.\scripts\verify_gitops.ps1
```

Expected outcome:

GitOps validation succeeds.

---

# Verify Cluster Validation

Run:

```powershell id="q9k2cs"
.\scripts\verify_cluster.ps1
```

Expected output:

```text id="u3m8rv"
[PASS] Kubernetes cluster is reachable.

[PASS] Namespace 'argocd' exists.

[PASS] ApplicationSet CRD is installed.
```

This confirms successful bootstrap.

---

# Reconstructed Areas

The following elements are known to exist but require future verification:

```text id="x5j7qp"
root-app.yml contents

ApplicationSet implementation details

Child application definitions

Manifest hierarchy
```

These components should be validated during the next full platform rebuild.

---

# Common Troubleshooting

## Namespace Missing

Symptoms:

```text id="y8m4dn"
argocd namespace not found
```

Possible causes:

* Installation incomplete
* Cluster reset
* Bootstrap interrupted

Verify installation process.

---

## ApplicationSet CRD Missing

Symptoms:

```text id="v1q7zk"
ApplicationSet validation failed
```

Possible causes:

* Incomplete installation
* Missing ArgoCD components

Verify CRD availability.

---

## Root Application Not Created

Symptoms:

```text id="n2w5rc"
GitOps bootstrap incomplete
```

Possible causes:

* Invalid path
* Missing file
* Repository structure issue

Verify:

```text id="e4m8xt"
k8s/apps/root-app.yml
```

exists and is accessible.

---

## Synchronization Failure

Symptoms:

```text id="b7r3vk"
OutOfSync

Degraded
```

Possible causes:

* Invalid manifests
* Repository configuration issues
* Resource definition errors

Review ArgoCD synchronization details.

---

# Success Criteria

This guide is complete when:

* ArgoCD installed successfully
* argocd namespace exists
* ApplicationSet CRD available
* Root Application applied
* GitOps synchronization operational
* Validation scripts succeed

The platform is now operating under GitOps control.

---

# Next Step

Continue with:

**Platform Rebuild Checklist**

This checklist provides a complete end-to-end procedure for rebuilding the entire platform from scratch.
