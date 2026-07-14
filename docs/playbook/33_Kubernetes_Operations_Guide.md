# Kubernetes Operations Guide

## Purpose

This guide explains how to operate, monitor, and troubleshoot the Kubernetes runtime layer of the M-DevOps platform.

The objective is to provide engineers with a structured approach for investigating workload health, deployment status, service availability, and runtime issues.

This guide focuses on normal operational activities after the platform has been successfully deployed.

---

# Operational Role of Kubernetes

Kubernetes is the runtime environment of the platform.

Responsibilities:

```text
Schedule Workloads
        ↓
Run Containers
        ↓
Provide Networking
        ↓
Maintain Availability
```

While ArgoCD manages desired state, Kubernetes executes that state.

---

# Operational Questions

Daily Kubernetes operations should answer:

```text
Are nodes healthy?

Are Pods healthy?

Are Deployments healthy?

Are Services available?

Is the application reachable?
```

These questions form the foundation of runtime operations.

---

# Kubernetes Resource Hierarchy

Understanding resource relationships is critical.

```text
Deployment
        ↓
ReplicaSet
        ↓
Pod
        ↓
Container
```

Troubleshooting usually starts at the highest affected layer and progresses downward.

---

# Daily Kubernetes Health Review

Recommended sequence:

```text
Nodes
        ↓
Deployments
        ↓
Pods
        ↓
Services
        ↓
Application
```

This provides a systematic operational workflow.

---

# Verify Cluster Nodes

Execute:

```powershell
kubectl get nodes
```

Healthy example:

```text
STATUS: Ready
```

Review:

* Ready status
* Node availability
* Unexpected node conditions

---

# Understanding Node Health

Healthy state:

```text
Ready
```

Warning states:

```text
NotReady

Unknown
```

Potential causes:

* Cluster issues
* Resource exhaustion
* Runtime failures

Node health impacts every workload running on the cluster.

---

# Verify Deployments

Execute:

```powershell
kubectl get deployments
```

Review:

```text
READY

UP-TO-DATE

AVAILABLE
```

Healthy deployments should have available replicas matching desired replicas.

---

# Inspect Deployment Details

Execute:

```powershell
kubectl describe deployment <deployment-name>
```

Purpose:

* Review deployment configuration
* Review rollout history
* Review events

This is often the first investigation step when application issues occur.

---

# Verify Pods

Execute:

```powershell
kubectl get pods
```

Healthy example:

```text
Running
```

Review:

* Status
* Restart count
* Age

Pods provide the most immediate view of workload health.

---

# Understanding Pod States

Healthy:

```text
Running
```

Transitional:

```text
Pending

ContainerCreating
```

Problematic:

```text
CrashLoopBackOff

ImagePullBackOff

Error

Unknown
```

These states require investigation.

---

# Inspect Pod Details

Execute:

```powershell
kubectl describe pod <pod-name>
```

Review:

* Events
* Scheduling
* Container state
* Restart history

This command often reveals the root cause of failures.

---

# View Application Logs

Execute:

```powershell
kubectl logs <pod-name>
```

Purpose:

Review application behavior directly from the running container.

Common indicators:

```text
Startup failures

Configuration errors

Application exceptions
```

Logs are one of the most valuable troubleshooting resources.

---

# Verify Services

Execute:

```powershell
kubectl get services
```

Review:

* Service existence
* Ports
* Cluster IP

Services provide workload connectivity.

---

# Inspect Service Details

Execute:

```powershell
kubectl describe service <service-name>
```

Purpose:

Verify:

* Port mappings
* Selectors
* Endpoints

Service issues often appear as application connectivity problems.

---

# Verify Namespace Resources

Execute:

```powershell
kubectl get all
```

Purpose:

Quick overview of all primary resources in the current namespace.

Useful during routine operational reviews.

---

# Verify All Namespaces

Execute:

```powershell
kubectl get pods --all-namespaces
```

Purpose:

Detect broader cluster issues.

Useful when investigating platform-wide incidents.

---

# Runtime Investigation Workflow

Recommended order:

```text
Application Issue Reported
        ↓
Service Check
        ↓
Pod Check
        ↓
Pod Logs
        ↓
Deployment Review
        ↓
Node Review
```

This workflow reduces unnecessary investigation time.

---

# Understanding Restart Counts

Review:

```powershell
kubectl get pods
```

Example:

```text
RESTARTS
```

Healthy:

```text
0
```

Warning indicator:

```text
Increasing restart count
```

This may indicate:

* Application crashes
* Resource problems
* Configuration issues

---

# Resource Visibility

Useful commands:

```powershell
kubectl get deployments

kubectl get pods

kubectl get services

kubectl get namespaces

kubectl get nodes
```

These commands form the operational baseline.

---

# Operational Validation

Execute:

```powershell
.\scripts\verify_pods.ps1
```

Expected result:

```text
PASS
```

This validation confirms workload health.

---

# Full Platform Validation

Execute:

```powershell
.\scripts\verify_all.ps1
```

Expected result:

```text
[PASS] All validation checks completed successfully.
```

This provides the overall operational status.

---

# Common Operational Issues

## Pod CrashLoopBackOff

Possible causes:

```text
Application startup failure

Configuration issue

Container error
```

Investigate:

```powershell
kubectl describe pod <pod-name>

kubectl logs <pod-name>
```

---

## ImagePullBackOff

Possible causes:

```text
Image unavailable

Registry issue

Incorrect image reference
```

Review deployment image configuration.

---

## Deployment Not Available

Possible causes:

```text
Pod failures

Scheduling problems

Configuration errors
```

Review deployment and pod events.

---

## Service Not Reachable

Possible causes:

```text
Service configuration issue

Pod issue

Application issue
```

Verify:

* Service
* Endpoints
* Pod health

---

# Operational Best Practices

Prefer:

```text
Observe

Collect Evidence

Identify Cause

Apply Fix

Validate Result
```

Avoid making changes before understanding the problem.

---

# Daily Kubernetes Checklist

```text
□ Nodes Ready

□ Deployments Available

□ Pods Running

□ Services Available

□ Validation Successful

□ Application Reachable
```

This checklist represents the minimum runtime health review.

---

# Success Criteria

This guide is complete when the engineer understands:

* Kubernetes runtime responsibilities
* Node health
* Deployment health
* Pod health
* Service health
* Investigation workflow
* Validation process

The engineer should be capable of performing routine Kubernetes operations and first-level troubleshooting confidently.

---

# Next Step

Continue with:

**Release Management Guide**

This guide explains how source code changes move through the platform from development to deployment.
