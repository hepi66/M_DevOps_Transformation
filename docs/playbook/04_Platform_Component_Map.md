# Platform Component Map

## Purpose

This document provides the architectural map of the M-DevOps platform.

Its goal is to help engineers quickly understand:

* Platform structure
* Component relationships
* Deployment flow
* Ownership boundaries
* Troubleshooting starting points

This document should be read before performing major platform changes, rebuild activities, or troubleshooting.

---

# Platform Overview

The platform implements a complete DevOps delivery pipeline using:

```text
Python Application
        ↓
Docker
        ↓
GitHub
        ↓
GitHub Actions
        ↓
GHCR
        ↓
ArgoCD
        ↓
Kubernetes
        ↓
Validation
```

Each component has a clearly defined responsibility.

---

# High-Level Architecture

```text
┌──────────────────────┐
│      Developer       │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│       GitHub         │
│  Source Repository   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   GitHub Actions     │
│       CI/CD          │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│        GHCR          │
│ Container Registry   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│       ArgoCD         │
│       GitOps         │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│     Kubernetes       │
│      Runtime         │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│     Application      │
└──────────────────────┘
```

---

# Component Responsibilities

## Developer

Responsible for:

```text
Source Code Changes

Testing

Commits

Pull Requests

Validation
```

Primary Location:

```text
app.py
tests/
```

---

## GitHub Repository

Responsible for:

```text
Version Control

Source Management

Platform Documentation

GitOps Definitions
```

Primary Locations:

```text
.github/

docs/

k8s/

scripts/

tests/
```

---

## GitHub Actions

Responsible for:

```text
CI/CD Automation

Quality Gates

Container Build

Artifact Publication
```

Primary Location:

```text
.github/workflows/ci.yml
```

Pipeline Stages:

```text
Ruff
↓
Bandit
↓
pytest
↓
Docker Build
↓
GHCR Publish
```

---

## Docker

Responsible for:

```text
Application Packaging

Runtime Consistency

Deployment Artifact Creation
```

Primary Files:

```text
Dockerfile

requirements.txt
```

Output:

```text
Container Image
```

---

## GitHub Container Registry (GHCR)

Responsible for:

```text
Container Storage

Artifact Distribution
```

Example:

```text
ghcr.io/<owner>/m-devops-transformation
```

Consumers:

```text
Kubernetes

ArgoCD
```

---

## ArgoCD

Responsible for:

```text
GitOps

Deployment Automation

Desired State Management
```

Role:

```text
Git State
        ↓
Cluster State
```

Synchronization Engine:

```text
ArgoCD
```

---

## Root Application

Primary GitOps Entry Point:

```text
k8s/apps/root-app.yml
```

Purpose:

```text
Bootstrap GitOps

Register Platform Applications

Control Deployment Hierarchy
```

---

## ApplicationSet

Purpose:

```text
Application Management

GitOps Scalability

Deployment Automation
```

Validation Evidence:

```text
ApplicationSet CRD Installed
```

ApplicationSet support is part of the validated platform architecture.

---

## Kubernetes

Responsible for:

```text
Container Orchestration

Workload Execution

Service Exposure

Runtime Operations
```

Primary Areas:

```text
Deployments

Pods

Services

Namespaces
```

---

## Validation Layer

Responsible for:

```text
Platform Verification

Operational Health

Deployment Validation
```

Primary Scripts:

```text
verify_cluster.ps1

verify_gitops.ps1

verify_pods.ps1

verify_all.ps1
```

---

# Repository Component Map

```text
Repository Root
│
├── app.py
│
├── Dockerfile
│
├── requirements.txt
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── docs/
│
├── k8s/
│   ├── apps/
│   │   └── root-app.yml
│   │
│   ├── base/
│   │
│   └── overlays/
│
├── scripts/
│
└── tests/
```

---

# Deployment Artifact Flow

The application artifact moves through the platform as follows:

```text
app.py
        ↓
Docker Build
        ↓
Container Image
        ↓
GHCR
        ↓
ArgoCD
        ↓
Kubernetes Deployment
        ↓
Running Pod
```

This is the primary software delivery path.

---

# Golden Path Flow

Validated delivery workflow:

```text
Developer Change
        ↓
Git Commit
        ↓
Git Push
        ↓
GitHub Actions
        ↓
Quality Checks
        ↓
Docker Build
        ↓
GHCR Publication
        ↓
ArgoCD Sync
        ↓
Kubernetes Deployment
        ↓
Validation
```

This is the platform's Golden Path.

---

# Troubleshooting Ownership Map

When a problem occurs:

| Symptom                 | Start Here         |
| ----------------------- | ------------------ |
| Commit / Push Issue     | Git & GitHub       |
| Pipeline Failure        | GitHub Actions     |
| Container Build Failure | Docker             |
| Missing Image           | GHCR               |
| Sync Failure            | ArgoCD             |
| Pod Failure             | Kubernetes         |
| Runtime Failure         | Application        |
| Unknown Issue           | Validation Scripts |

---

# Platform Recovery Sequence

When rebuilding or recovering the platform:

```text
Workstation
        ↓
Repository
        ↓
Docker
        ↓
GitHub
        ↓
GHCR
        ↓
Kubernetes
        ↓
ArgoCD
        ↓
Validation
```

Recovery should follow this order.

---

# Most Important Files

The following files are considered platform-critical:

```text
app.py

Dockerfile

requirements.txt

.github/workflows/ci.yml

k8s/apps/root-app.yml

verify_all.ps1
```

Changes to these files should be reviewed carefully.

---

# Relationship To Other Playbook Documents

For detailed architecture:

```text
01_Architecture_Overview.md
```

For toolchain details:

```text
02_Toolchain_Overview.md
```

For deployment flow:

```text
03_Golden_Path_End_to_End.md
```

For rebuild activities:

```text
10-20 Series
```

For operations:

```text
30-35 Series
```

For troubleshooting:

```text
40-45 Series
```

---

# Success Criteria

This document is complete when an engineer can answer:

* What components exist?
* What does each component do?
* How do components interact?
* Where should troubleshooting start?
* How does software move through the platform?
* Which files are most important?

The engineer should be capable of understanding the complete platform architecture within a few minutes.
---

# Next Recommended Reading

Continue with:

- [Glossary](05_Glossary.md)

---

# Related Documents

- [Architecture Overview](01_Architecture_Overview.md)
- [Toolchain Overview](02_Toolchain_Overview.md)
- [Golden Path End-to-End](03_Golden_Path_End_to_End.md)

---

Return to:

- [Engineering Playbook](README.md)
- [Engineering Documentation Portal](../README.md)
