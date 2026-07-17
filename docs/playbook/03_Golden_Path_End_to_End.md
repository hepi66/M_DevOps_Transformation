# Golden Path End-to-End

## Purpose

This document describes the validated end-to-end delivery workflow of the M-DevOps platform.

The Golden Path represents the preferred and supported workflow for implementing, validating, building, deploying, and operating application changes.

All platform procedures should align with this workflow whenever possible.

---

# Overview

The platform follows a Git-centric DevOps and GitOps delivery model.

Every application change follows the same lifecycle:

Developer Change

→ Local Validation

→ Git Commit

→ GitHub Actions

→ Docker Build

→ GHCR Publication

→ ArgoCD Synchronization

→ Kubernetes Deployment

→ Platform Validation

→ Running Application

This workflow represents the authoritative deployment path.

---

# Stage 1 – Local Development

## Objective

Implement and verify application changes before publishing them.

### Activities

* Create or update application code
* Update tests if required
* Execute local validation
* Verify application behavior

### Typical Components

* Visual Studio Code
* Python
* Virtual Environment (venv)
* PowerShell

### Expected Result

The application functions correctly in the local environment.

---

# Stage 2 – Source Control

## Objective

Record the engineering change in Git.

### Activities

* Review modified files
* Create a commit
* Push changes to GitHub

### Responsibilities

Git provides:

* Change history
* Traceability
* Reproducibility
* Collaboration support

### Expected Result

The change is stored in the repository and becomes available to automation workflows.

---

# Stage 3 – Continuous Integration

## Objective

Validate the engineering change automatically.

### Trigger

Git push event.

### GitHub Actions Responsibilities

* Execute linting
* Execute security scanning
* Execute automated testing
* Build container image

### Quality Gates

The pipeline must pass all validation stages before image publication.

### Expected Result

The change is considered deployable.

---

# Stage 4 – Container Build

## Objective

Create a deployable software artifact.

### Responsibilities

Docker:

* Packages application code
* Packages dependencies
* Creates a reproducible runtime environment

### Output

Docker Image

Example:

```text
ghcr.io/<owner>/m-devops-transformation:<tag>
```

### Expected Result

A portable deployment artifact exists.

---

# Stage 5 – Container Registry Publication

## Objective

Store the deployable artifact.

### Responsibilities

GitHub Container Registry (GHCR):

* Store container images
* Provide deployment artifacts
* Maintain image history

### Expected Result

The application image is available for deployment.

---

# Stage 6 – GitOps Synchronization

## Objective

Align cluster state with repository state.

### Responsibilities

ArgoCD:

* Monitor repository state
* Detect changes
* Synchronize Kubernetes resources
* Self-heal configuration drift

### Important Principle

Git is the source of truth.

ArgoCD continuously attempts to make the cluster match the desired Git state.

### Expected Result

Deployment instructions are applied to Kubernetes.

---

# Stage 7 – Kubernetes Deployment

## Objective

Run the application.

### Responsibilities

Kubernetes:

* Pull container images
* Create workloads
* Maintain application availability
* Manage runtime resources

### Runtime Components

Validated architecture includes:

* Kubernetes Cluster
* ArgoCD Namespace
* Application Workloads
* Supporting Services

### Expected Result

Updated application containers are running.

---

# Stage 8 – Platform Validation

## Objective

Verify operational health.

### Validation Scripts

#### verify_cluster.ps1

Validates:

* Cluster availability
* ArgoCD namespace
* ApplicationSet CRD

---

#### verify_gitops.ps1

Validates:

* GitOps synchronization
* Application health

---

#### verify_pods.ps1

Validates:

* Pod health
* Container readiness

---

#### verify_all.ps1

Executes:

* Cluster validation
* Pod validation
* GitOps validation

### Expected Result

The platform is confirmed healthy.

---

# Golden Path Flow Diagram

```text
Developer
    │
    ▼
Local Validation
    │
    ▼
Git Commit
    │
    ▼
GitHub Repository
    │
    ▼
GitHub Actions
    │
    ├── Ruff
    ├── Bandit
    └── pytest
    │
    ▼
Docker Build
    │
    ▼
GHCR
    │
    ▼
ArgoCD
    │
    ▼
Kubernetes
    │
    ▼
Validation Scripts
    │
    ▼
Healthy Platform
```

---

# Success Criteria

A change has successfully completed the Golden Path when:

* Source code changes are committed
* CI validation succeeds
* Container image is published
* GitOps synchronization succeeds
* Kubernetes workloads are healthy
* Validation scripts pass
* Application functionality is confirmed

---

# Known Gaps

The following areas require additional reconstruction and documentation:

* Detailed Kubernetes deployment manifests
* Complete cluster bootstrap procedure
* Complete disaster recovery procedure

These topics are addressed in later Playbook sections.

---

# Relationship to Other Playbook Documents

This document describes the complete delivery workflow.

For architectural understanding, see:

* Playbook Overview
* Architecture Overview
* Toolchain Overview

For implementation procedures, continue with:

* Rebuild Guides

For platform operation, continue with:

* Operations Guides

For incident handling, continue with:

* Troubleshooting Guides
---

# Next Recommended Reading

Continue with:

- [Platform Component Map](04_Platform_Component_Map.md)

---

# Related Documents

- [Architecture Overview](01_Architecture_Overview.md)
- [CI/CD and GitHub Actions Guide](13_CICD_and_GitHub_Actions_Guide.md)
- [GitOps and ArgoCD Guide](15_GitOps_and_ArgoCD_Guide.md)

---

Return to:

- [Engineering Playbook](README.md)
- [Engineering Documentation Portal](../README.md)
