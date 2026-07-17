# Kubernetes Troubleshooting Guide

## Purpose

This guide documents common Kubernetes runtime issues encountered during development and operation of the M-DevOps platform.

The objective is to provide structured troubleshooting procedures for Pods, Deployments, Services, workload availability, and runtime failures.

This guide focuses on problems occurring after Kubernetes resources have been deployed.

---

# Kubernetes Runtime Overview

Validated runtime architecture:

```text
Deployment
        ↓
ReplicaSet
        ↓
Pod
        ↓
Container
        ↓
Application
```

Most Kubernetes incidents occur within this execution chain.

---

# Troubleshooting Philosophy

Do not begin by changing resources.

First determine:

```text
What failed?

Where did it fail?

Why did it fail?
```

Always collect evidence before applying corrective actions.

---

# Investigation Workflow

Recommended investigation sequence:

```text
Deployment
        ↓
Pods
        ↓
Pod Details
        ↓
Logs
        ↓
Services
        ↓
Application
```

This sequence aligns with Kubernetes resource dependencies.

---

# First Validation Step

Execute:

```powershell
.\scripts\verify_pods.ps1
```

Expected:

```text
PASS
```

Validation results should guide the investigation.

---

# Issue: Pod Not Running

## Symptom

```powershell
kubectl get pods
```

returns:

```text
Pending

Error

CrashLoopBackOff

ImagePullBackOff
```

instead of:

```text
Running
```

---

## Investigation

Review Pod details:

```powershell
kubectl describe pod <pod-name>
```

Then review logs:

```powershell
kubectl logs <pod-name>
```

---

## Resolution

Identify the specific failure reason before making changes.

---

# Issue: CrashLoopBackOff

## Symptom

Pod repeatedly restarts.

Example:

```text
CrashLoopBackOff
```

---

## Meaning

The container starts but exits repeatedly.

---

## Investigation

Execute:

```powershell
kubectl logs <pod-name>
```

and:

```powershell
kubectl describe pod <pod-name>
```

Review:

```text
Application startup

Exceptions

Configuration issues
```

---

## Common Causes

```text
Application error

Missing dependency

Startup failure

Invalid configuration
```

---

## Resolution

Correct the underlying application or configuration issue.

Redeploy and validate.

---

# Issue: ImagePullBackOff

## Symptom

Pod cannot retrieve container image.

---

## Meaning

Kubernetes cannot pull the referenced image.

---

## Investigation

Review:

```powershell
kubectl describe pod <pod-name>
```

Verify:

```text
Image Reference

Registry Availability

Image Tag
```

---

## Common Causes

```text
Image not published

Incorrect tag

Registry access issue
```

---

## Resolution

Verify GHCR image availability and deployment configuration.

---

# Issue: Pod Running But Application Not Working

## Symptom

Pod status:

```text
Running
```

but application unavailable.

---

## Investigation

Review:

```powershell
kubectl logs <pod-name>
```

Verify:

```text
Application startup

Runtime exceptions

Expected service behavior
```

---

## Resolution

Correct application-level issue.

Pod health alone does not guarantee application health.

---

# Issue: Deployment Not Available

## Symptom

```powershell
kubectl get deployments
```

shows:

```text
AVAILABLE = 0
```

or desired replicas are not available.

---

## Investigation

Review deployment:

```powershell
kubectl describe deployment <deployment-name>
```

Review associated Pods.

---

## Common Causes

```text
Pod failures

Image failures

Scheduling issues
```

---

## Resolution

Resolve underlying Pod or scheduling issue.

---

# Issue: Deployment Rollout Failure

## Symptom

Deployment update does not complete successfully.

---

## Investigation

Review:

```powershell
kubectl describe deployment <deployment-name>
```

Focus on:

```text
Events

Replica creation

Pod status
```

---

## Resolution

Correct the resource causing rollout failure.

---

# Issue: Service Exists But Application Not Reachable

## Symptom

Service appears healthy.

Application unavailable.

---

## Investigation

Review:

```powershell
kubectl get services
```

and:

```powershell
kubectl describe service <service-name>
```

Verify:

```text
Selectors

Endpoints

Ports
```

---

## Common Causes

```text
Service selector mismatch

Application failure

Pod failure
```

---

## Resolution

Ensure Service targets healthy Pods.

---

# Issue: Pods Restart Repeatedly

## Symptom

Increasing restart count.

Review:

```powershell
kubectl get pods
```

Column:

```text
RESTARTS
```

---

## Meaning

Workload instability exists.

---

## Investigation

Review:

```powershell
kubectl logs <pod-name>
```

and:

```powershell
kubectl describe pod <pod-name>
```

---

## Resolution

Identify root cause before attempting recovery.

---

# Issue: Namespace Resources Missing

## Symptom

Expected resources cannot be found.

---

## Investigation

Verify namespace:

```powershell
kubectl get namespaces
```

Review current context:

```powershell
kubectl get all
```

---

## Resolution

Confirm correct namespace and deployment state.

---

# Issue: Cluster Appears Unhealthy

## Symptom

Multiple workloads affected simultaneously.

---

## Investigation

Execute:

```powershell
kubectl get nodes
```

Expected:

```text
Ready
```

Review:

```powershell
kubectl cluster-info
```

---

## Resolution

Restore cluster health before investigating application workloads.

---

# Issue: Validation Failure

## Symptom

```powershell
.\scripts\verify_pods.ps1
```

fails.

---

## Investigation

Review failed validation step.

Classify issue:

```text
Deployment

Pod

Service

Runtime
```

Use validation output as the starting point.

---

# Project Lesson Learned: Pod Status Is Not Application Health

## Observation

A Pod may be:

```text
Running
```

while the application itself is not functioning correctly.

---

## Final Practice

Always verify:

```text
Pod

AND

Application
```

Never assume one implies the other.

---

# Project Lesson Learned: Logs Are Usually The Fastest Path

## Observation

Many runtime issues become obvious when reviewing container logs.

---

## Final Practice

Prefer:

```powershell
kubectl logs <pod-name>
```

early in the investigation process.

---

# Project Lesson Learned: Validation Scripts Accelerate Diagnosis

## Observation

The platform validation scripts consistently reduced troubleshooting effort.

---

## Final Practice

Begin with:

```powershell
.\scripts\verify_pods.ps1
```

before manually inspecting resources.

---

# Project Lesson Learned: Follow Resource Hierarchy

## Observation

Troubleshooting becomes significantly easier when following Kubernetes resource relationships.

---

## Preferred Sequence

```text
Deployment
        ↓
Pod
        ↓
Logs
        ↓
Service
        ↓
Application
```

Avoid random investigation paths.

---

# Kubernetes Troubleshooting Checklist

```text
□ Nodes Ready

□ Deployments Available

□ Pods Running

□ Restart Count Acceptable

□ Logs Reviewed

□ Services Available

□ Validation Successful

□ Application Reachable
```

This checklist resolves the majority of Kubernetes runtime incidents.

---

# Success Criteria

This guide is complete when the engineer understands:

* Pod failures
* Deployment failures
* Service issues
* Runtime diagnostics
* Log analysis workflow
* Validation-based troubleshooting
* Project-specific lessons learned

The engineer should be capable of diagnosing and resolving routine Kubernetes runtime issues independently.
---

# Next Recommended Reading

Continue with:

- [Lessons Learned Knowledge Base](45_Lessons_Learned_Knowledge_Base.md)

---

# Related Documents

- [Kubernetes Deployment and Runtime Guide](16_Kubernetes_Deployment_and_Runtime_Guide.md)
- [Kubernetes Operations Guide](33_Kubernetes_Operations_Guide.md)
- [Troubleshooting Overview](40_Troubleshooting_Overview.md)

---

Return to:

- [Engineering Playbook](README.md)
- [Engineering Documentation Portal](../README.md)
