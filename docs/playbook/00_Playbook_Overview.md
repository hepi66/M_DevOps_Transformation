# M-DevOps Platform Playbook

## Purpose

The M-DevOps Platform Playbook is the authoritative engineering guide for rebuilding, operating, validating, and maintaining the M-DevOps platform.

The Playbook is intended to enable future engineers to understand the platform architecture, reproduce the complete environment from scratch, operate the platform safely, and troubleshoot common issues without relying on historical project conversations.

The Playbook serves as the primary operational knowledge source for the project.

---

# Objectives

This Playbook provides:

* Platform architecture documentation
* Toolchain documentation
* End-to-end delivery workflow documentation
* Platform rebuild procedures
* Validation procedures
* Operational guidance
* Troubleshooting knowledge
* Lessons learned from implementation

The Playbook is designed to support long-term maintainability and engineering knowledge transfer.

---

# Target Audience

This Playbook is intended for:

* DevOps Engineers
* Platform Engineers
* Software Engineers
* Technical Leads
* Engineering Managers
* Future maintainers of the platform

The reader is expected to have basic familiarity with Git, Docker, Kubernetes, and software development practices.

---

# Scope

The Playbook covers the complete validated platform delivery chain:

Developer Workstation

→ Source Control

→ Continuous Integration

→ Container Build

→ Container Registry

→ GitOps

→ Kubernetes

→ Validation

→ Operations

The Playbook focuses on the final validated implementation.

Rejected implementation attempts, temporary experiments, and obsolete approaches are intentionally excluded unless they provide valuable troubleshooting knowledge.

---

# Engineering Principles

The platform follows the following engineering principles:

* Git as the single source of truth
* Infrastructure and deployment managed declaratively
* Automated validation wherever possible
* Small and verifiable changes
* Reproducible engineering workflows
* Continuous improvement through documented lessons learned

---

# Platform Overview

The platform consists of the following major components:

| Component          | Purpose                               |
| ------------------ | ------------------------------------- |
| GitHub             | Source control and collaboration      |
| GitHub Actions     | Continuous integration and automation |
| Docker             | Application packaging                 |
| GHCR               | Container image storage               |
| ArgoCD             | GitOps deployment controller          |
| Kubernetes         | Application runtime platform          |
| Validation Scripts | Platform health verification          |

Together these components form a complete DevOps delivery pipeline from source code change to running application.

---

# Playbook Structure

The Playbook is organized into the following sections:

## Foundation

Platform concepts, architecture, and toolchain overview.

## Golden Path

The validated end-to-end delivery workflow.

## Rebuild Guides

Procedures for rebuilding the platform from scratch.

## Operations

Operational procedures, validation, and platform management.

## Troubleshooting

Known issues, diagnostics, and recovery procedures.

---

# Definition of Success

A platform engineer should be able to use this Playbook to:

1. Prepare a new workstation.
2. Clone the repository.
3. Rebuild the platform.
4. Deploy application changes.
5. Validate platform health.
6. Operate the environment.
7. Troubleshoot common failures.
8. Recover the platform if required.

If these objectives can be achieved without relying on undocumented knowledge, the Playbook is considered successful.

---

# Document Status

Status: Active

This document serves as the entry point for the M-DevOps Platform Playbook and should be read before consulting any other Playbook section.
