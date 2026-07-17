# Document Roadmap

> **Overview of the Engineering Playbook structure**

This roadmap explains how the Engineering Playbook is organized, how the documents relate to each other, and which reading sequence is recommended for different engineering tasks.

> **Tip**
>
> To keep this roadmap open while reading, open document links in a new browser tab (Ctrl + Click or middle mouse button).

---

# Engineering Lifecycle

The Engineering Playbook follows the complete lifecycle of the platform.

```text
Learn
   ↓
Develop
   ↓
Build
   ↓
Validate
   ↓
Deploy
   ↓
Operate
   ↓
Troubleshoot
   ↓
Recover
```

Each phase is covered by a dedicated set of documents.

---

# Foundation (00–06)

These documents explain the platform architecture and engineering concepts.

## Recommended Reading

1. [00_Playbook_Overview.md](00_Playbook_Overview.md)
2. [01_Architecture_Overview.md](01_Architecture_Overview.md)
3. [02_Toolchain_Overview.md](02_Toolchain_Overview.md)
4. [03_Golden_Path_End_to_End.md](03_Golden_Path_End_to_End.md)
5. [04_Platform_Component_Map.md](04_Platform_Component_Map.md)
6. [05_Glossary.md](05_Glossary.md)
7. [06_Architecture_Decisions_and_Rationale.md](06_Architecture_Decisions_and_Rationale.md)

Recommended for:

- New engineers
- Technical onboarding
- Architecture reviews

---

# Development & Platform Build (10–20)

These documents describe how to build the platform from an empty workstation to a fully operational Kubernetes environment.

## Recommended Reading

1. [10_Workstation_Setup_Guide.md](10_Workstation_Setup_Guide.md)
2. [11_Repository_and_Development_Guide.md](11_Repository_and_Development_Guide.md)
3. [12_Container_Build_and_Validation_Guide.md](12_Container_Build_and_Validation_Guide.md)
4. [13_CICD_and_GitHub_Actions_Guide.md](13_CICD_and_GitHub_Actions_Guide.md)
5. [14_GHCR_Guide.md](14_GHCR_Guide.md)
6. [15_GitOps_and_ArgoCD_Guide.md](15_GitOps_and_ArgoCD_Guide.md)
7. [16_Kubernetes_Deployment_and_Runtime_Guide.md](16_Kubernetes_Deployment_and_Runtime_Guide.md)
8. [17_Platform_Validation_Guide.md](17_Platform_Validation_Guide.md)
9. [18_Kubernetes_Bootstrap_Guide.md](18_Kubernetes_Bootstrap_Guide.md)
10. [19_ArgoCD_Bootstrap_Guide.md](19_ArgoCD_Bootstrap_Guide.md)
11. [20_Platform_Rebuild_Checklist.md](20_Platform_Rebuild_Checklist.md)

Recommended for:

- Developers
- Platform Engineers
- Complete platform rebuild

---

# Daily Operations (30–35)

These documents support the daily operation of the running platform.

## Recommended Reading

1. [30_Daily_Operations_Guide.md](30_Daily_Operations_Guide.md)
2. [31_Validation_and_Health_Checks.md](31_Validation_and_Health_Checks.md)
3. [32_ArgoCD_Operations_Guide.md](32_ArgoCD_Operations_Guide.md)
4. [33_Kubernetes_Operations_Guide.md](33_Kubernetes_Operations_Guide.md)
5. [34_Release_Management_Guide.md](34_Release_Management_Guide.md)
6. [35_Platform_Recovery_Guide.md](35_Platform_Recovery_Guide.md)

Recommended for:

- Platform Operators
- Daily engineering work
- Health checks
- Release activities

---

# Troubleshooting (40–45)

Always begin with the overview before opening a technology-specific troubleshooting guide.

## Recommended Reading

1. [40_Troubleshooting_Overview.md](40_Troubleshooting_Overview.md)
2. [41_Git_and_GitHub_Troubleshooting.md](41_Git_and_GitHub_Troubleshooting.md)
3. [42_CICD_and_GHCR_Troubleshooting.md](42_CICD_and_GHCR_Troubleshooting.md)
4. [43_ArgoCD_Troubleshooting.md](43_ArgoCD_Troubleshooting.md)
5. [44_Kubernetes_Troubleshooting.md](44_Kubernetes_Troubleshooting.md)
6. [45_Lessons_Learned_Knowledge_Base.md](45_Lessons_Learned_Knowledge_Base.md)

Recommended for:

- Incident response
- Root cause analysis
- Platform debugging

---

# Recommended Learning Paths

## I am new to the project

1. [00_Playbook_Overview.md](00_Playbook_Overview.md)
2. [01_Architecture_Overview.md](01_Architecture_Overview.md)
3. [02_Toolchain_Overview.md](02_Toolchain_Overview.md)
4. [03_Golden_Path_End_to_End.md](03_Golden_Path_End_to_End.md)

---

## I am an Application Developer

1. [10_Workstation_Setup_Guide.md](10_Workstation_Setup_Guide.md)
2. [11_Repository_and_Development_Guide.md](11_Repository_and_Development_Guide.md)
3. [12_Container_Build_and_Validation_Guide.md](12_Container_Build_and_Validation_Guide.md)
4. [13_CICD_and_GitHub_Actions_Guide.md](13_CICD_and_GitHub_Actions_Guide.md)

---

## I am a Platform Engineer

1. [14_GHCR_Guide.md](14_GHCR_Guide.md)
2. [15_GitOps_and_ArgoCD_Guide.md](15_GitOps_and_ArgoCD_Guide.md)
3. [16_Kubernetes_Deployment_and_Runtime_Guide.md](16_Kubernetes_Deployment_and_Runtime_Guide.md)
4. [17_Platform_Validation_Guide.md](17_Platform_Validation_Guide.md)
5. [18_Kubernetes_Bootstrap_Guide.md](18_Kubernetes_Bootstrap_Guide.md)
6. [19_ArgoCD_Bootstrap_Guide.md](19_ArgoCD_Bootstrap_Guide.md)
7. [20_Platform_Rebuild_Checklist.md](20_Platform_Rebuild_Checklist.md)

---

## I am operating the platform

1. [30_Daily_Operations_Guide.md](30_Daily_Operations_Guide.md)
2. [31_Validation_and_Health_Checks.md](31_Validation_and_Health_Checks.md)
3. [32_ArgoCD_Operations_Guide.md](32_ArgoCD_Operations_Guide.md)
4. [33_Kubernetes_Operations_Guide.md](33_Kubernetes_Operations_Guide.md)
5. [34_Release_Management_Guide.md](34_Release_Management_Guide.md)
6. [35_Platform_Recovery_Guide.md](35_Platform_Recovery_Guide.md)

---

## I want to troubleshoot a problem

1. [40_Troubleshooting_Overview.md](40_Troubleshooting_Overview.md)
2. Continue with the technology-specific troubleshooting guide.

---

# Navigation Aids

Need a quick entry point?

➡ [Quick Start Guide](Quick_Start_Guide.md)

Need documentation based on a question?

➡ [Documentation Navigator](Playbook_Navigation_Guide.md)

---

# Related Documents

- [Quick Start Guide](Quick_Start_Guide.md)
- [Documentation Navigator](Playbook_Navigation_Guide.md)
- [Engineering Playbook](README.md)

---

Return to:

- [Engineering Playbook](README.md)
- [Engineering Documentation Portal](../README.md)

---

## Navigation Tip

Use **Ctrl + Click** or the middle mouse button to open linked documents in a new browser tab while keeping the current navigation page open.
