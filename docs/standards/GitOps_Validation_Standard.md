---
title: "GitOps Validation Standard"
type: "Engineering Standard"
status: "Active"
version: "1.0"
owner: "Engineering"
last_updated: "2026-07-07"
related_epic: "E03"
---

# GitOps Validation Standard

## Purpose

This standard defines the mandatory validation approach for GitOps deployments within the M_DevOps_Transformation project.

The objective is to ensure that deployment issues are detected systematically and that troubleshooting follows a predictable engineering workflow.

---

# Validation Principles

Validation shall always proceed from lower-level infrastructure components to higher-level application components.

Validation must never begin at the application layer.

The following sequence is mandatory.

---

# Validation Sequence

## Step 1: Cluster Validation

Verify that the Kubernetes cluster is operational.

Validation includes:

- Cluster connectivity
- Node readiness
- Kubernetes API availability

Example:

```powershell
.\scripts\verify_cluster.ps1
```

Expected result:

```text
PASS Cluster is reachable
```

---

## Step 2: Platform Validation

Verify that platform services are operational.

Validation includes:

- ArgoCD namespace
- ArgoCD pods
- ArgoCD services
- ArgoCD CRDs

Example:

```powershell
.\scripts\verify_platform.ps1
```

Expected result:

```text
PASS Platform components operational
```

---

## Step 3: GitOps Validation

Verify that GitOps synchronization is functioning correctly.

Validation includes:

- Application registration
- Sync status
- Repository connectivity
- Health status

Example:

```powershell
.\scripts\verify_gitops.ps1
```

Expected result:

```text
PASS Applications synchronized
```

---

## Step 4: Application Validation

Verify that deployed workloads are healthy.

Validation includes:

- Pod status
- Service availability
- Deployment health
- Container readiness

Example:

```powershell
.\scripts\verify_applications.ps1
```

Expected result:

```text
PASS Applications healthy
```

---

# Validation Framework

Validation scripts shall follow a modular architecture.

Each script is responsible for one validation layer only.

Examples:

```text
verify_cluster.ps1
verify_platform.ps1
verify_gitops.ps1
verify_applications.ps1
```

A master script may orchestrate the complete validation process.

Example:

```text
verify_all.ps1
```

---

# PASS / FAIL Convention

Validation output shall be human-readable.

Examples:

```text
[PASS] Cluster validation succeeded.
```

```text
[FAIL] ArgoCD server pod not running.
```

---

# Exit Codes

Validation scripts shall return meaningful exit codes.

| Exit Code | Meaning |
|------------|----------|
| 0 | Success |
| 1 | Validation failed |

Non-zero exit codes must be treated as validation failures.

---

# Troubleshooting Principle

When validation fails:

1. Stop immediately.
2. Resolve the failure at the current layer.
3. Repeat validation.
4. Continue only after success.

Do not continue to higher validation layers while lower layers remain unresolved.

---

# Engineering Rationale

This approach provides:

- predictable troubleshooting
- reproducible validation
- reduced diagnosis time
- reusable verification scripts
- consistent engineering workflow

The validation sequence reflects the dependency chain of a GitOps-based platform.

Infrastructure must be healthy before GitOps can function.

GitOps must function before applications can be considered healthy.

---

# Compliance

All future deployment automation introduced into this repository shall follow this validation sequence.

Exceptions must be documented through an Architecture Decision Record (ADR).