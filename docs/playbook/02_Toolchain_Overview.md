# Toolchain Overview

## Purpose

This document provides an overview of the tools that form the M-DevOps platform.

Its purpose is to explain the role of each tool within the delivery pipeline and how the tools interact to support development, automation, deployment, validation, and operations.

This document focuses on responsibilities and relationships rather than installation procedures.

---

# Toolchain Summary

The platform is built using the following core technologies:

| Category                | Tool                                 |
| ----------------------- | ------------------------------------ |
| Operating System        | Windows 11                           |
| Development Environment | Visual Studio Code                   |
| Scripting               | PowerShell                           |
| Programming Language    | Python                               |
| Runtime Isolation       | Python Virtual Environment (venv)    |
| Source Control          | Git                                  |
| Repository Hosting      | GitHub                               |
| Continuous Integration  | GitHub Actions                       |
| Containerization        | Docker Desktop                       |
| Container Registry      | GitHub Container Registry (GHCR)     |
| GitOps                  | ArgoCD                               |
| Container Orchestration | Kubernetes                           |
| Validation              | Custom PowerShell Validation Scripts |

---

# Development Layer

## Windows 11

Purpose:

* Primary workstation operating system
* Local development environment
* Platform administration

The project assumes a Windows-based development workflow.

---

## Visual Studio Code

Purpose:

* Primary integrated development environment (IDE)

Responsibilities:

* Source code editing
* Repository management
* Terminal access
* Extension integration

Visual Studio Code serves as the primary engineering workspace.

---

## PowerShell

Purpose:

* Command-line interface
* Automation scripting
* Platform validation

Responsibilities:

* Execute validation scripts
* Perform administrative tasks
* Support development workflows

PowerShell is the primary automation interface used throughout the project.

---

## Python

Purpose:

* Application development

Responsibilities:

* Execute the Streamlit application
* Run automated tests
* Support local development

Python is the primary application runtime.

---

## Python Virtual Environment (venv)

Purpose:

* Dependency isolation

Benefits:

* Consistent local development environment
* Dependency version control
* Reduced workstation conflicts

Each engineer should work inside a dedicated virtual environment.

---

# Source Control Layer

## Git

Purpose:

* Version control

Responsibilities:

* Track changes
* Support branching workflows
* Enable reproducible development

Git is the foundation of all engineering activities.

---

## GitHub

Purpose:

* Repository hosting
* Collaboration platform

Responsibilities:

* Source code storage
* Pull request workflow
* Change history
* Project management integration

GitHub acts as the authoritative source of platform configuration.

---

# Automation Layer

## GitHub Actions

Purpose:

* Continuous Integration

Responsibilities:

* Linting
* Security scanning
* Automated testing
* Container image creation
* Registry publication

GitHub Actions automatically validates and packages application changes.

---

# Containerization Layer

## Docker Desktop

Purpose:

* Local container runtime

Responsibilities:

* Build Docker images
* Execute containers locally
* Support deployment validation

Docker Desktop provides a consistent container environment for development and testing.

---

## Docker

Purpose:

* Application packaging

Responsibilities:

* Bundle application code
* Bundle runtime dependencies
* Produce deployable software artifacts

Docker images become the deployment unit consumed by Kubernetes.

---

# Registry Layer

## GitHub Container Registry (GHCR)

Purpose:

* Container image storage

Responsibilities:

* Store published images
* Distribute deployment artifacts
* Provide immutable deployment targets

GHCR separates software creation from software execution.

---

# GitOps Layer

## ArgoCD

Purpose:

* Continuous deployment through GitOps

Responsibilities:

* Monitor repository state
* Detect configuration changes
* Synchronize Kubernetes resources
* Self-heal drift

ArgoCD continuously aligns cluster state with repository state.

---

# Runtime Layer

## Kubernetes

Purpose:

* Application execution platform

Responsibilities:

* Schedule workloads
* Manage containers
* Provide runtime services
* Maintain platform stability

Kubernetes hosts the running application environment.

---

# Validation Layer

## Validation Scripts

Current scripts:

* verify_cluster.ps1
* verify_gitops.ps1
* verify_pods.ps1
* verify_all.ps1

Purpose:

* Platform health verification

Responsibilities:

* Validate infrastructure readiness
* Validate GitOps synchronization
* Validate workload health
* Provide deterministic operational checks

The validation layer defines the platform's operational health standard.

---

# Toolchain Interaction

The tools operate together in the following sequence:

Developer Workstation

→ Git

→ GitHub

→ GitHub Actions

→ Docker

→ GHCR

→ ArgoCD

→ Kubernetes

→ Validation

This sequence represents the validated platform delivery chain.

---

# Design Principles

The toolchain was selected according to the following principles:

* Reproducibility
* Automation
* Low operational overhead
* Open standards
* Industry relevance
* GitOps compatibility
* Learning value

The resulting platform provides a complete DevOps learning and operational environment using widely adopted industry tools.

---

# Relationship to Other Playbook Documents

This document explains the tools used by the platform.

For architectural relationships, see:

* Architecture Overview

For workflow execution, see:

* Golden Path End-to-End

For implementation details, see:

* Rebuild Guides

For daily operation, see:

* Operations Guides
---

# Next Recommended Reading

Continue with:

- [Golden Path End-to-End](03_Golden_Path_End_to_End.md)

---

# Related Documents

- [Architecture Overview](01_Architecture_Overview.md)
- [Platform Component Map](04_Platform_Component_Map.md)
- [Glossary](05_Glossary.md)

---

Return to:

- [Engineering Playbook](README.md)
- [Engineering Documentation Portal](../README.md)
