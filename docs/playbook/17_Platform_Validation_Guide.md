# Platform Validation Guide

## Purpose

This guide explains how platform health is verified within the M-DevOps platform.

The objective is to provide a repeatable and deterministic validation process that confirms the operational readiness of the platform after deployment, maintenance activities, or recovery procedures.

Validation is a mandatory step of the platform lifecycle.

---

# Why Validation Matters

A successful deployment does not automatically mean a healthy platform.

Example:

```text id="r7n4cp"
Deployment Succeeded
        ↓
Pod Failed Later
```

Or:

```text id="c2m9vd"
ArgoCD Healthy
        ↓
Application Unavailable
```

Validation provides evidence that the platform is functioning as intended.

---

# Validation Philosophy

The platform follows the principle:

```text id="m3q7xf"
Trust
        ↓
Verify
```

Every significant change should be followed by validation.

Examples:

* Initial platform deployment
* Infrastructure changes
* Application releases
* Recovery procedures
* Troubleshooting activities

---

# Validation Architecture

Current validation implementation:

```text id="n4x8wu"
scripts/
│
├── verify_cluster.ps1
├── verify_gitops.ps1
├── verify_pods.ps1
└── verify_all.ps1
```

These scripts define the operational health standard of the platform.

---

# Validation Levels

The platform validates multiple layers.

```text id="w9k5yl"
Cluster
    ↓
GitOps
    ↓
Workloads
    ↓
Application Readiness
```

Each validation layer contributes to overall platform confidence.

---

# Cluster Validation

Script:

```text id="t7m2oq"
verify_cluster.ps1
```

Purpose:

Verify foundational platform components.

Validated checks include:

* Kubernetes cluster reachable
* ArgoCD namespace exists
* ApplicationSet CRD installed

Example output:

```text id="v8n6ep"
[PASS] Kubernetes cluster is reachable.

[PASS] Namespace 'argocd' exists.

[PASS] ApplicationSet CRD is installed.
```

These checks confirm platform infrastructure readiness.

---

# GitOps Validation

Script:

```text id="k6v4md"
verify_gitops.ps1
```

Purpose:

Verify GitOps deployment health.

Responsibilities:

* Synchronization status
* Application health
* Deployment readiness

This validation confirms the GitOps layer is operating correctly.

---

# Workload Validation

Script:

```text id="u5x9na"
verify_pods.ps1
```

Purpose:

Verify workload execution.

Responsibilities:

* Pod health
* Running state
* Container readiness

This confirms Kubernetes is executing workloads successfully.

---

# Full Platform Validation

Script:

```text id="o2j7gh"
verify_all.ps1
```

Purpose:

Execute all validation checks.

Typical execution:

```powershell id="z4w8me"
.\scripts\verify_all.ps1
```

Expected outcome:

```text id="f3n9kw"
[PASS] All validation checks completed successfully.
```

This represents the preferred validation method.

---

# Validation Workflow

Recommended sequence:

```text id="q7m2yc"
Platform Change
        ↓
Deployment
        ↓
verify_all.ps1
        ↓
Review Results
        ↓
Platform Accepted
```

Validation should become a routine operational habit.

---

# Understanding PASS Results

Example:

```text id="w8n6db"
[PASS]
```

Meaning:

* Validation executed
* Check succeeded
* No action required

PASS indicates expected platform behavior.

---

# Understanding Failure Results

Example:

```text id="n5v3oj"
[FAIL]
```

Meaning:

* Validation executed
* Problem detected
* Investigation required

A FAIL result should never be ignored.

---

# Validation During Rebuild Activities

Validation should be executed after:

* Kubernetes installation
* ArgoCD installation
* GitOps bootstrap
* Application deployment
* Recovery operations

This provides confidence that each stage completed successfully.

---

# Validation During Daily Operations

Validation should also be executed:

* Before major changes
* After major changes
* During troubleshooting
* After upgrades

Consistent validation reduces operational risk.

---

# Common Failure Patterns

## Cluster Unreachable

Symptoms:

```text id="u4m7gx"
Cluster validation failed
```

Possible causes:

* Kubernetes not running
* Context configuration issue
* Local cluster unavailable

Verify cluster status first.

---

## Missing ArgoCD Namespace

Symptoms:

```text id="m8k5vh"
Namespace validation failed
```

Possible causes:

* ArgoCD not installed
* Bootstrap incomplete
* Cluster reset

Verify namespace existence.

---

## ApplicationSet CRD Missing

Symptoms:

```text id="j9n4wy"
CRD validation failed
```

Possible causes:

* Incomplete ArgoCD installation
* Missing ApplicationSet component

Verify installation state.

---

## Pod Validation Failure

Symptoms:

```text id="x3v8bt"
Pod health validation failed
```

Possible causes:

* Image deployment failure
* Application startup issue
* Runtime error

Inspect workload state.

---

## GitOps Validation Failure

Symptoms:

```text id="v7q2dj"
Synchronization failed
```

Possible causes:

* ArgoCD issue
* Invalid manifests
* Repository configuration problem

Review GitOps health first.

---

# Validation as an Operational Standard

Validation is not merely a troubleshooting tool.

Validation is part of the platform operating model.

The preferred workflow is:

```text id="z8j4nk"
Build
        ↓
Deploy
        ↓
Validate
```

A deployment should not be considered complete until validation succeeds.

---

# Success Criteria

This guide is complete when the engineer understands:

* Validation philosophy
* Validation layers
* Available validation scripts
* PASS and FAIL interpretation
* Validation workflow
* Common failure patterns

The engineer should be capable of verifying platform health consistently and repeatably.
---

# Next Recommended Reading

Continue with:

- [Kubernetes Bootstrap Guide](18_Kubernetes_Bootstrap_Guide.md)

---

# Related Documents

- [Kubernetes Deployment and Runtime Guide](16_Kubernetes_Deployment_and_Runtime_Guide.md)
- [Validation and Health Checks](31_Validation_and_Health_Checks.md)
- [Platform Rebuild Checklist](20_Platform_Rebuild_Checklist.md)

---

Return to:

- [Engineering Playbook](README.md)
- [Engineering Documentation Portal](../README.md)
