# Engineering Playbook

> **Operational Guide for the M-DevOps Transformation Platform**

---

The Engineering Playbook contains the validated engineering knowledge required to understand, rebuild, operate, recover, and troubleshoot the M-DevOps Transformation platform.

It complements the Engineering Knowledge Base by focusing on operational procedures and reproducible workflows.

---

# Start Here

Choose the entry point that best matches your current task.

| I want to... | Open |
|---|---|
| 🚀 Get productive quickly | [Quick Start Guide](Quick_Start_Guide.md) |
| ❓ Find documentation by question | [Documentation Navigator](Playbook_Navigation_Guide.md) |
| 🗺 Understand the Playbook structure | [Document Roadmap](Document_Roadmap.md) |
| 🏠 Return to the portal | [Engineering Documentation Portal](../README.md) |

---

# Learn the Platform

Foundation documents introducing the platform architecture and engineering concepts.

| Document | Purpose |
|---|---|
| [Playbook Overview](00_Playbook_Overview.md) | Purpose, scope, and target audience |
| [Architecture Overview](01_Architecture_Overview.md) | High-level platform architecture |
| [Toolchain Overview](02_Toolchain_Overview.md) | Tools and their responsibilities |
| [Golden Path End-to-End](03_Golden_Path_End_to_End.md) | Complete delivery workflow |
| [Platform Component Map](04_Platform_Component_Map.md) | Components, relationships, and ownership |
| [Glossary](05_Glossary.md) | Engineering terminology |
| [Architecture Decisions and Rationale](06_Architecture_Decisions_and_Rationale.md) | Why the platform was designed this way |

---

# Build and Rebuild

Follow the validated implementation path.

| Document | Purpose |
|---|---|
| [Workstation Setup Guide](10_Workstation_Setup_Guide.md) | Prepare a Windows 11 workstation |
| [Repository and Development Guide](11_Repository_and_Development_Guide.md) | Prepare the local project environment |
| [Container Build and Validation Guide](12_Container_Build_and_Validation_Guide.md) | Build and validate the Docker image |
| [CI/CD and GitHub Actions Guide](13_CICD_and_GitHub_Actions_Guide.md) | Understand the automated pipeline |
| [GHCR Guide](14_GHCR_Guide.md) | Store and distribute container images |
| [GitOps and ArgoCD Guide](15_GitOps_and_ArgoCD_Guide.md) | Understand GitOps deployment |
| [Kubernetes Deployment and Runtime Guide](16_Kubernetes_Deployment_and_Runtime_Guide.md) | Understand workload execution |
| [Platform Validation Guide](17_Platform_Validation_Guide.md) | Verify platform health |
| [Kubernetes Bootstrap Guide](18_Kubernetes_Bootstrap_Guide.md) | Prepare the Kubernetes foundation |
| [ArgoCD Bootstrap Guide](19_ArgoCD_Bootstrap_Guide.md) | Establish the GitOps layer |
| [Platform Rebuild Checklist](20_Platform_Rebuild_Checklist.md) | Execute a complete platform rebuild |

---

# Daily Operations

Use these documents to operate and maintain the running platform.

| Document | Purpose |
|---|---|
| [Daily Operations Guide](30_Daily_Operations_Guide.md) | Perform the routine platform health review |
| [Validation and Health Checks](31_Validation_and_Health_Checks.md) | Interpret health indicators |
| [ArgoCD Operations Guide](32_ArgoCD_Operations_Guide.md) | Operate the GitOps layer |
| [Kubernetes Operations Guide](33_Kubernetes_Operations_Guide.md) | Inspect workloads, Pods, Deployments, and Services |
| [Release Management Guide](34_Release_Management_Guide.md) | Manage the release flow |
| [Platform Recovery Guide](35_Platform_Recovery_Guide.md) | Restore platform functionality |

---

# Troubleshooting

Use symptom-driven guidance to investigate failures systematically.

| Document | Purpose |
|---|---|
| [Troubleshooting Overview](40_Troubleshooting_Overview.md) | Investigation method and starting point |
| [Git and GitHub Troubleshooting](41_Git_and_GitHub_Troubleshooting.md) | Source-control and repository issues |
| [CI/CD and GHCR Troubleshooting](42_CICD_and_GHCR_Troubleshooting.md) | Pipeline, Docker-build, and registry issues |
| [ArgoCD Troubleshooting](43_ArgoCD_Troubleshooting.md) | GitOps synchronization and health issues |
| [Kubernetes Troubleshooting](44_Kubernetes_Troubleshooting.md) | Deployment, Pod, Service, and runtime issues |
| [Lessons Learned Knowledge Base](45_Lessons_Learned_Knowledge_Base.md) | Reusable project and engineering lessons |

---

# Recommended Paths

## New to the platform

```text
Overview
   ↓
Architecture
   ↓
Toolchain
   ↓
Golden Path
   ↓
Component Map
   ↓
Glossary
```

## Daily work

```text
Daily Operations
   ↓
Health Checks
   ↓
ArgoCD Operations
   ↓
Kubernetes Operations
```

## Something is broken

```text
Troubleshooting Overview
   ↓
Affected Component Guide
   ↓
Platform Validation
```

## Complete rebuild

```text
Workstation Setup
   ↓
Local Development
   ↓
Docker
   ↓
CI/CD and GHCR
   ↓
Kubernetes and ArgoCD Bootstrap
   ↓
Platform Rebuild Checklist
```

---

# Engineering Principles

The Engineering Playbook is based on five principles:

- Understandable
- Repeatable
- Recoverable
- Operational
- Maintainable

---

# Related Resources

- [Documentation Navigator](Playbook_Navigation_Guide.md)
- [Quick Start Guide](Quick_Start_Guide.md)
- [Document Roadmap](Document_Roadmap.md)
- [Engineering Documentation Portal](../README.md)

---

© 2026 M-DevOps Transformation

**Engineering Playbook**