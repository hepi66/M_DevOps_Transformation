# Release Management Guide

## Purpose

This guide describes how source code changes move through the M-DevOps platform from development to deployment.

The objective is to provide a clear understanding of the release flow, validation controls, deployment automation, and delivery responsibilities.

This guide focuses on the validated end-to-end release process implemented within the platform.

---

# Release Philosophy

The platform follows a GitOps-based release model.

Core principle:

```text
Git is the source of truth.
```

All platform changes originate from source control and progress through automated validation and deployment stages.

---

# End-to-End Release Flow

Validated platform flow:

```text
Developer Change
        ↓
Local Validation
        ↓
Git Commit
        ↓
Git Push
        ↓
GitHub Repository
        ↓
GitHub Actions
        ↓
Container Build
        ↓
GHCR Publication
        ↓
ArgoCD Synchronization
        ↓
Kubernetes Deployment
        ↓
Application Validation
```

This sequence represents the Golden Path release process.

---

# Release Lifecycle

A release consists of five major phases:

```text
Development
        ↓
Validation
        ↓
Build
        ↓
Deployment
        ↓
Verification
```

Each phase contributes to platform reliability.

---

# Phase 1 – Development

Changes begin within the local development environment.

Typical activities:

```text
Feature implementation

Bug fixes

Documentation updates

Configuration changes
```

Engineers should validate changes locally before committing.

---

# Local Validation

Recommended validation activities:

```powershell
pytest
```

```powershell
streamlit run app.py
```

```powershell
docker build -t m-devops-transformation .
```

Goal:

```text
Verify before committing.
```

Early validation reduces pipeline failures.

---

# Phase 2 – Source Control

Changes are recorded through Git.

Typical workflow:

```powershell
git status

git add .

git commit -m "description"

git push
```

The push event triggers the automated delivery process.

---

# Source Control Responsibilities

Engineers should ensure:

```text
Meaningful commit messages

Validated code

No unintended changes

Clean repository state
```

Source control quality directly impacts delivery quality.

---

# Phase 3 – Continuous Integration

GitHub Actions performs automated validation.

Validated pipeline components:

```text
Ruff

Bandit

pytest

Docker Build
```

These controls protect platform quality.

---

# Linting Stage

Purpose:

```text
Code quality verification
```

Tool:

```text
Ruff
```

Benefits:

* Detect style issues
* Improve consistency
* Reduce maintainability risks

---

# Security Validation Stage

Purpose:

```text
Basic security review
```

Tool:

```text
Bandit
```

Benefits:

* Detect common security concerns
* Improve engineering discipline

---

# Test Stage

Purpose:

```text
Functional verification
```

Tool:

```text
pytest
```

Benefits:

* Detect regressions
* Verify expected behavior

Failed tests block release progression.

---

# Container Build Stage

Purpose:

```text
Produce deployable artifact
```

Tool:

```text
Docker
```

Output:

```text
Container Image
```

This image becomes the deployment artifact.

---

# Phase 4 – Artifact Publication

Container images are published to:

```text
GitHub Container Registry (GHCR)
```

Purpose:

```text
Central artifact storage
```

The registry becomes the source for Kubernetes deployments.

---

# Artifact Flow

```text
Docker Build
        ↓
Container Image
        ↓
GHCR
        ↓
Kubernetes Pull
```

No deployment can occur without a valid artifact.

---

# Phase 5 – GitOps Deployment

Deployment responsibility transfers to ArgoCD.

Flow:

```text
Git Repository
        ↓
ArgoCD
        ↓
Kubernetes
```

ArgoCD continuously compares:

```text
Desired State

vs

Actual State
```

and performs synchronization when required.

---

# Synchronization Process

Typical flow:

```text
Repository Change
        ↓
ArgoCD Detects Change
        ↓
Synchronization
        ↓
Deployment Update
```

This removes the need for manual deployment commands.

---

# Kubernetes Deployment

Kubernetes performs runtime execution.

Responsibilities:

```text
Create Pods

Schedule Workloads

Manage Services

Maintain Availability
```

At this stage the new release becomes active.

---

# Release Verification

After deployment verify:

```text
Application healthy

Pods healthy

Services available

GitOps synchronized
```

Verification is mandatory.

Deployment completion alone is not sufficient.

---

# Recommended Validation Sequence

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

---

# Release Success Criteria

A release is successful when:

```text
CI/CD successful

Image published

GitOps synchronized

Pods healthy

Application available

Validation successful
```

All criteria must be satisfied.

---

# Failed Release Indicators

Examples:

```text
Pipeline failure

Image publication failure

OutOfSync status

Degraded application

Validation failure
```

These conditions require investigation before considering the release complete.

---

# Release Ownership

Engineering responsibilities:

## Developer

Responsible for:

```text
Code quality

Local validation

Commit quality
```

---

## CI/CD

Responsible for:

```text
Automated validation

Artifact creation
```

---

## GHCR

Responsible for:

```text
Artifact storage
```

---

## ArgoCD

Responsible for:

```text
Deployment automation

Desired state reconciliation
```

---

## Kubernetes

Responsible for:

```text
Runtime execution
```

---

# Release Audit Trail

Every release should be traceable through:

```text
Git Commit
        ↓
GitHub Actions Run
        ↓
Container Image
        ↓
ArgoCD Synchronization
        ↓
Kubernetes Deployment
```

This traceability supports troubleshooting and operational reviews.

---

# Operational Rule

Never assume a release is successful because deployment completed.

A release is successful only when:

```text
Deployment Completed

AND

Validation Successful

AND

Application Available
```

---

# Success Criteria

This guide is complete when the engineer understands:

* Release lifecycle
* CI/CD responsibilities
* Artifact flow
* GitOps deployment model
* Validation requirements
* Release success criteria

The engineer should be capable of explaining and operating the complete delivery chain from source code change to running application.

---

# Next Step

Continue with:

**Platform Recovery Guide**

This guide explains how to restore platform functionality after failures, outages, or recovery exercises.
