# ArgoCD Troubleshooting Guide

## Purpose

This guide documents common ArgoCD and GitOps issues encountered during development and operation of the M-DevOps platform.

The objective is to provide structured troubleshooting procedures for synchronization failures, degraded applications, bootstrap problems, GitOps drift, and repository-to-cluster reconciliation issues.

This guide is particularly important because GitOps became one of the most complex implementation areas during Epics E03 and E04.

---

# ArgoCD Architecture Overview

Validated platform architecture:

```text id="f4q8wd"
Git Repository
        ↓
Root Application
        ↓
ArgoCD
        ↓
Kubernetes
        ↓
Application
```

ArgoCD continuously compares:

```text id="m2v7pk"
Desired State (Git)

vs

Actual State (Cluster)
```

and attempts to reconcile differences.

---

# Troubleshooting Philosophy

Before changing anything:

Determine:

```text id="q8m3vx"
Is the problem:

Git?

ArgoCD?

Kubernetes?

Application?
```

Many GitOps issues appear to be ArgoCD issues but originate elsewhere.

---

# Investigation Workflow

Recommended order:

```text id="p6w4tr"
Validation
        ↓
ArgoCD Health
        ↓
Application Status
        ↓
Kubernetes Resources
        ↓
Repository Structure
```

Avoid jumping directly into Kubernetes troubleshooting.

---

# First Validation Step

Execute:

```powershell id="n4v7pk"
.\scripts\verify_gitops.ps1
```

Expected:

```text id="t8m2qw"
PASS
```

If validation fails, use the reported failure as the investigation starting point.

---

# Issue: ArgoCD Namespace Missing

## Symptom

```powershell id="w5r8mx"
kubectl get namespaces
```

does not show:

```text id="y9m1pk"
argocd
```

---

## Impact

GitOps functionality unavailable.

---

## Investigation

Verify cluster state:

```powershell id="a7q4vd"
kubectl get namespaces
```

---

## Resolution

Restore ArgoCD installation according to:

```text id="s2v9pk"
19_ArgoCD_Bootstrap_Guide.md
```

Validate after restoration.

---

# Issue: ArgoCD Pods Not Running

## Symptom

```powershell id="m6w2qx"
kubectl get pods -n argocd
```

returns failed, pending, or missing workloads.

---

## Investigation

Review:

```powershell id="d4v8tp"
kubectl get pods -n argocd
```

and:

```powershell id="r7m3qy"
kubectl describe pod <pod-name> -n argocd
```

---

## Resolution

Identify infrastructure or workload issue before continuing.

ArgoCD must be healthy before application troubleshooting begins.

---

# Issue: Application OutOfSync

## Symptom

Application status:

```text id="k8w5pr"
OutOfSync
```

---

## Meaning

Cluster state differs from Git state.

---

## Possible Causes

```text id="z4m7vd"
Recent repository change

Synchronization failure

Manual cluster modification

Configuration drift
```

---

## Investigation

Review:

```text id="c5v2qx"
Recent commits

Application status

Synchronization details
```

Determine why desired and actual states differ.

---

## Resolution

Restore alignment between:

```text id="q7w9mk"
Git

and

Cluster
```

Validate synchronization afterward.

---

# Issue: Application Degraded

## Symptom

Application status:

```text id="v2m4tr"
Degraded
```

---

## Meaning

Resources exist but are unhealthy.

---

## Investigation

Review:

```powershell id="x9q3wd"
kubectl get deployments

kubectl get pods
```

Then inspect failed resources.

---

## Common Causes

```text id="j4m8pk"
Pod failures

Image issues

Deployment issues

Manifest problems
```

---

## Resolution

Correct underlying Kubernetes issue.

ArgoCD health normally recovers automatically after workload recovery.

---

# Issue: Application Unknown

## Symptom

Status:

```text id="n6v2qx"
Unknown
```

---

## Meaning

ArgoCD cannot determine application health.

---

## Investigation

Review:

```text id="d3m7pr"
Application resources

Controller health

Cluster connectivity
```

---

## Resolution

Restore visibility between ArgoCD and managed resources.

---

# Issue: Root Application Missing

## Symptom

GitOps structure appears incomplete.

Applications fail to appear.

---

## Investigation

Verify existence of:

```text id="t9m4qw"
k8s/apps/root-app.yml
```

This is the validated GitOps entry point.

---

## Resolution

Reapply:

```powershell id="b5v7pk"
kubectl apply -f k8s/apps/root-app.yml
```

Validate GitOps state afterward.

---

# Issue: Repository Structure Does Not Match Expectations

## Symptom

ArgoCD cannot locate expected manifests.

Applications fail to deploy.

---

## Project Observation

During the project lifecycle, repository structure changed multiple times.

Several deployment artifacts required reconstruction.

---

## Investigation

Verify:

```text id="f7q2mx"
Current Repository Structure

Manifest Locations

GitOps References
```

Never assume documentation reflects the final repository state.

---

## Resolution

Validate all GitOps paths explicitly.

---

# Issue: ApplicationSet Validation Failure

## Symptom

Validation reports:

```text id="r2m9wd"
ApplicationSet CRD missing
```

---

## Investigation

Execute:

```powershell id="k5v3pr"
kubectl get crd | findstr applicationset
```

Expected:

```text id="u7m8qx"
applicationsets.argoproj.io
```

---

## Resolution

Restore ApplicationSet support according to platform bootstrap procedures.

---

# Issue: GitOps Validation Failure

## Symptom

```powershell id="v4q7tp"
.\scripts\verify_gitops.ps1
```

fails.

---

## Investigation

Review reported failure.

Classify issue:

```text id="n9m4pk"
Namespace

ApplicationSet

Synchronization

Health
```

Use the failing validation step as the investigation starting point.

---

# Issue: Drift Detected

## Symptom

Cluster differs from repository state.

---

## Meaning

Configuration drift occurred.

---

## Possible Causes

```text id="x3v8mq"
Manual kubectl changes

Temporary modifications

Partial recovery actions
```

---

## Resolution

Restore Git as the source of truth.

Avoid maintaining long-term manual cluster modifications.

---

# Project Lesson Learned: Architecture Documentation Is Critical

## Observation

The implementation became reproducible before the architecture became fully documented.

---

## Impact

Later reconstruction required significant investigation.

Questions included:

```text id="q8r5vn"
Where are the manifests?

What manages what?

What is the root entry point?
```

---

## Final Practice

Always document:

```text id="s5v9px"
Architecture

Ownership

Resource Relationships
```

explicitly.

---

# Project Lesson Learned: GitOps Structure Must Be Visible

## Observation

The platform eventually validated successfully.

However, parts of the GitOps architecture required reconstruction from reports and repository artifacts.

---

## Impact

Operational understanding became harder than implementation itself.

---

## Final Practice

Maintain clear documentation for:

```text id="w2m6tr"
Root Application

ApplicationSet

Manifest Structure

Bootstrap Process
```

---

# Project Lesson Learned: Validation Scripts Provide Fast Triage

## Observation

The validation scripts consistently identified the affected layer quickly.

---

## Final Practice

Always begin with:

```powershell id="g4v8pk"
.\scripts\verify_gitops.ps1
```

before deeper investigation.

---

# ArgoCD Troubleshooting Checklist

```text id="m7q2wd"
□ argocd namespace exists

□ ArgoCD Pods running

□ Root Application exists

□ ApplicationSet available

□ Applications Healthy

□ Applications Synced

□ GitOps validation successful
```

This checklist resolves the majority of GitOps incidents.

---

# Success Criteria

This guide is complete when the engineer understands:

* ArgoCD health states
* Synchronization failures
* Drift detection
* Root Application issues
* ApplicationSet issues
* GitOps validation workflow
* Project-specific lessons learned

The engineer should be capable of diagnosing and resolving routine GitOps and ArgoCD issues independently.

---

# Next Step

Continue with:

**Kubernetes Troubleshooting Guide**

This guide covers Pods, Deployments, Services, runtime failures, and workload recovery procedures.
