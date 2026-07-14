# Platform Recovery Guide

## Purpose

This guide describes how to recover the M-DevOps platform after failures, outages, configuration mistakes, or infrastructure disruptions.

The objective is to provide a structured recovery approach that minimizes downtime, reduces uncertainty, and restores the platform to a known-good operational state.

This guide focuses on platform recovery rather than routine troubleshooting.

---

# Recovery Philosophy

The platform follows a GitOps-based recovery model.

Core principle:

```text
Git is the source of truth.
```

Recovery should always aim to restore the platform to the desired state stored in Git.

Whenever possible:

```text
Git
    ↓
ArgoCD
    ↓
Kubernetes
```

should be used instead of manual cluster modifications.

---

# Recovery Objectives

A successful recovery restores:

```text
Source Control
        ✓

CI/CD
        ✓

Container Registry
        ✓

GitOps
        ✓

Kubernetes
        ✓

Application
        ✓
```

The platform is considered recovered only when all critical layers are operational.

---

# Recovery Levels

Not all incidents require the same response.

The platform defines four recovery levels:

```text
Level 1
Validation Failure

Level 2
Application Failure

Level 3
GitOps Failure

Level 4
Platform Failure
```

Always begin with the lowest appropriate level.

---

# Level 1 – Validation Failure

Symptoms:

```text
verify_cluster.ps1 fails

verify_gitops.ps1 fails

verify_pods.ps1 fails
```

Recovery workflow:

```text
Review Validation Output
        ↓
Identify Failed Component
        ↓
Investigate Root Cause
        ↓
Correct Issue
        ↓
Run Validation Again
```

Do not skip investigation.

Validation failures are indicators, not root causes.

---

# Level 2 – Application Failure

Symptoms:

```text
Application unavailable

Application errors

Failed functionality
```

Recovery workflow:

```text
Service Check
        ↓
Pod Check
        ↓
Pod Logs
        ↓
Deployment Review
        ↓
GitOps Status Review
```

Useful commands:

```powershell
kubectl get services

kubectl get pods

kubectl logs <pod-name>

kubectl describe deployment <deployment-name>
```

---

# Level 3 – GitOps Failure

Symptoms:

```text
OutOfSync

Degraded

Synchronization failures
```

Recovery workflow:

```text
Review Repository State
        ↓
Review ArgoCD State
        ↓
Review Kubernetes Resources
        ↓
Correct Configuration
        ↓
Revalidate
```

Useful checks:

```powershell
.\scripts\verify_gitops.ps1
```

Goal:

```text
Healthy
+
Synced
```

---

# Level 4 – Platform Failure

Symptoms:

```text
Cluster unavailable

ArgoCD unavailable

Major platform outage
```

Recovery workflow:

```text
Infrastructure
        ↓
Kubernetes
        ↓
ArgoCD
        ↓
GitOps
        ↓
Application
```

Recovery must proceed from the foundation upward.

---

# Recovery Decision Tree

Start with:

```text
What is broken?
```

Examples:

```text
Application only?
        ↓
Level 2

GitOps only?
        ↓
Level 3

Cluster unavailable?
        ↓
Level 4
```

Accurate classification reduces recovery time.

---

# Kubernetes Recovery

Verify:

```powershell
kubectl cluster-info
```

Expected:

```text
Cluster reachable
```

Then:

```powershell
kubectl get nodes
```

Expected:

```text
Ready
```

If Kubernetes is unavailable, restore cluster functionality before proceeding.

---

# ArgoCD Recovery

Verify:

```powershell
kubectl get pods -n argocd
```

Expected:

```text
ArgoCD components running
```

Verify namespace:

```powershell
kubectl get namespaces
```

Expected:

```text
argocd
```

If ArgoCD is unavailable, restore ArgoCD before investigating applications.

---

# Root Application Recovery

Validated artifact:

```text
k8s/apps/root-app.yml
```

If GitOps registration is lost:

```powershell
kubectl apply -f k8s/apps/root-app.yml
```

Purpose:

Restore GitOps bootstrap entry point.

---

# GitOps Recovery

Verify:

```powershell
.\scripts\verify_gitops.ps1
```

Review:

```text
Synchronization State

Application Health
```

Target:

```text
Healthy

Synced
```

GitOps should be restored before addressing workload-specific issues.

---

# Workload Recovery

Verify deployments:

```powershell
kubectl get deployments
```

Verify pods:

```powershell
kubectl get pods
```

Verify services:

```powershell
kubectl get services
```

Review any failed resources before proceeding.

---

# Full Platform Rebuild Scenario

If recovery cannot be achieved through operational procedures:

Use:

```text
20_Platform_Rebuild_Checklist.md
```

Purpose:

Reconstruct the platform from a known-good baseline.

The rebuild checklist is the final recovery mechanism.

---

# Recovery Validation

After any recovery action:

Execute:

```powershell
.\scripts\verify_cluster.ps1
```

```powershell
.\scripts\verify_gitops.ps1
```

```powershell
.\scripts\verify_pods.ps1
```

or:

```powershell
.\scripts\verify_all.ps1
```

Expected result:

```text
[PASS] All validation checks completed successfully.
```

Recovery is incomplete until validation succeeds.

---

# Recovery Documentation

Record:

```text
Incident Description

Root Cause

Corrective Action

Validation Result

Lessons Learned
```

Operational knowledge improves through documented recovery events.

---

# Recovery Anti-Patterns

Avoid:

```text
Making multiple changes simultaneously

Skipping validation

Applying fixes without evidence

Ignoring GitOps state

Manual cluster drift
```

These actions increase recovery risk.

---

# Recovery Checklist

```text
□ Incident classified

□ Root cause identified

□ Corrective action applied

□ Validation successful

□ Application available

□ GitOps healthy

□ Kubernetes healthy

□ Lessons learned documented
```

This checklist should be completed before closing an incident.

---

# Operational Rule

Recovery is not complete when:

```text
The error disappears.
```

Recovery is complete when:

```text
Root Cause Identified

AND

Validation Successful

AND

Application Operational
```

---

# Success Criteria

This guide is complete when the engineer understands:

* Recovery levels
* Recovery sequencing
* Recovery validation
* GitOps recovery principles
* Platform rebuild fallback procedures

The engineer should be capable of restoring platform functionality systematically and safely.

---

# Next Step

Continue with:

**Troubleshooting Knowledge Base**

This section contains symptom-driven troubleshooting procedures, lessons learned, and operational knowledge collected throughout the project lifecycle.
