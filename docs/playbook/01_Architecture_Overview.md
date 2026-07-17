# Platform Architecture Overview

## Purpose

This document provides a high-level architectural overview of the M-DevOps platform.

Its purpose is to help engineers understand how the platform components interact before studying implementation details, operational procedures, or troubleshooting guides.

This document intentionally focuses on architecture and responsibilities rather than implementation steps.

---

# Architecture Goals

The platform was designed to achieve the following objectives:

* Automated software delivery
* Reproducible deployments
* Git-based change management
* Containerized application execution
* Automated validation
* Simplified operational management
* Continuous synchronization between desired and actual system state

The architecture follows modern DevOps and GitOps principles.

---

# High-Level Architecture

The platform consists of the following major layers:

```text
Developer
    │
    ▼
GitHub Repository
    │
    ▼
GitHub Actions
    │
    ▼
Docker Image Build
    │
    ▼
GitHub Container Registry (GHCR)
    │
    ▼
ArgoCD
    │
    ▼
Kubernetes
    │
    ▼
Running Application
```

Each layer has a clearly defined responsibility.

---

# Component Responsibilities

## Developer Workstation

Purpose:

* Application development
* Local testing
* Source code management
* Validation before commit

Primary Tools:

* Visual Studio Code
* Python
* PowerShell
* Docker Desktop
* Git

---

## GitHub Repository

Purpose:

* Single source of truth
* Version control
* Collaboration
* Storage of platform configuration

The repository stores:

* Application source code
* CI/CD configuration
* Kubernetes manifests
* Documentation
* Validation scripts

---

## GitHub Actions

Purpose:

* Continuous Integration
* Automated quality validation
* Automated container build
* Automated container publication

Key Responsibilities:

* Linting
* Security scanning
* Automated testing
* Docker image build
* Container registry publication

---

## Docker

Purpose:

* Package the application and its dependencies
* Create a reproducible runtime environment

Benefits:

* Consistent execution environment
* Simplified deployment
* Environment portability

The Docker image becomes the deployable software artifact.

---

## GitHub Container Registry (GHCR)

Purpose:

* Central storage for container images

Responsibilities:

* Store versioned application images
* Provide images to Kubernetes deployments
* Maintain deployment artifacts independent of source code execution

GHCR acts as the software distribution layer of the platform.

---

## ArgoCD

Purpose:

* GitOps deployment controller

Responsibilities:

* Monitor Git repositories
* Detect configuration changes
* Synchronize desired and actual state
* Self-heal configuration drift

ArgoCD continuously ensures that the cluster reflects the state declared in Git.

---

## Kubernetes

Purpose:

* Application runtime platform

Responsibilities:

* Container scheduling
* Application execution
* Service management
* Resource orchestration
* Platform resilience

Kubernetes executes the workloads defined by the deployment configuration.

---

## Validation Layer

Purpose:

* Verify platform health

Responsibilities:

* Infrastructure validation
* GitOps validation
* Workload validation
* Operational readiness checks

Validation scripts provide a consistent definition of platform health.

---

# Architectural Principles

## Git as Source of Truth

All platform configuration should originate from version-controlled repositories.

Manual configuration changes should be avoided.

---

## Declarative Configuration

Desired platform state is described declaratively.

The platform continuously attempts to converge toward the declared state.

---

## GitOps Deployment Model

Deployment is initiated by changes committed to Git.

No direct production deployment actions are required.

The deployment process is driven entirely by repository state.

---

## Immutable Deployment Artifacts

Application images are built once and deployed repeatedly.

Deployments should consume pre-built container images rather than rebuilding software inside the cluster.

---

## Continuous Validation

Platform health should be continuously verifiable through automated checks.

Validation results must be deterministic and repeatable.

---

# Deployment Flow Overview

The deployment lifecycle follows the sequence below:

1. Developer changes application code.
2. Changes are committed to Git.
3. GitHub Actions validates the change.
4. A Docker image is built.
5. The image is published to GHCR.
6. ArgoCD detects repository state.
7. Kubernetes receives updated deployment instructions.
8. Containers are started or updated.
9. Validation scripts confirm platform health.

---

# Known Architecture Gaps

The following areas require further verification or reconstruction:

* Kubernetes application deployment manifests
* Detailed cluster bootstrap procedure
* Detailed ArgoCD bootstrap procedure
* Disaster recovery workflow

These gaps were identified during PLAYBOOK-01 analysis and will be addressed in subsequent Playbook sections.

---

# Relationship to Other Playbook Documents

This document explains the architecture at a conceptual level.

For implementation details, continue with:

* Toolchain Overview
* Golden Path End-to-End
* Rebuild Guides
* Operations Guides
* Troubleshooting Guides

These documents build upon the architectural concepts introduced here.
---

# Next Recommended Reading

Continue with:

- [Toolchain Overview](02_Toolchain_Overview.md)

---

# Related Documents

- [Playbook Overview](00_Playbook_Overview.md)
- [Platform Component Map](04_Platform_Component_Map.md)
- [Architecture Decisions and Rationale](06_Architecture_Decisions_and_Rationale.md)

---

Return to:

- [Engineering Playbook](README.md)
- [Engineering Documentation Portal](../README.md)
