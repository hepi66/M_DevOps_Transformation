Title: Engineering Knowledge Base
Type: Handbook Index
Status: Living Document
Version: 2.0
Owner: Engineering
Last Updated: 2026-07-03

# Engineering Knowledge Base

Welcome to the Engineering Knowledge Base (EKB) of the **M_DevOps_Transformation** project.

The EKB is the single entry point for all engineering documentation, standards, reports, templates, prompts, cheat sheets, and reusable knowledge created throughout the project lifecycle.

The objective of the EKB is to ensure that engineering knowledge is captured once, maintained consistently, and remains reusable throughout the project's evolution.

---

# Getting Started

If you are new to this project, read the documents in the following order:

1. `handbook/00_Working_Principles.md`
2. `handbook/01_Documentation_Architecture.md`
3. This README
4. The latest Epic Transition Report

---

# Repository Structure

```
docs/
│
├── archive/
├── cheat_sheets/
├── decisions/
├── handbook/
├── prompts/
├── reports/
├── standards/
└── templates/
```

Each directory serves a specific purpose within the Engineering Knowledge Base.

---

# Handbook

Engineering concepts, documentation architecture and long-term project knowledge.

| Document | Description |
|----------|-------------|
| handbook/00_Working_Principles.md | Engineering principles and collaboration rules |
| handbook/01_Documentation_Architecture.md | Documentation architecture and knowledge management |

---

# Standards

Project-specific engineering standards.

| Document | Description |
|----------|-------------|
| ToolChain.md | DevOps toolchain overview |
| Container_Registry_Strategy.md | Container registry strategy |

> Additional engineering standards will be introduced as the project evolves.

---

# Cheat Sheets

Daily engineering reference documentation.

| Document | Description |
|----------|-------------|
| cheat_sheets/Git_Daily_Workflow.md | Daily Git and GitHub workflow |

---

# Reports

Permanent Epic summaries and engineering reports.

| Document | Description |
|----------|-------------|
| reports/E00_Transition_Report.md | Project foundation |
| reports/E01_Transition_Report.md | Local development environment |
| reports/E02_Transition_Report.md | CI/CD pipeline implementation |
| E01_Verification_Report.md | Local Docker verification report |

---

# Templates

Reusable documentation templates.

| Document | Description |
|----------|-------------|
| templates/Epic_Transition_Report_Template.md | Standard Epic handover template |

---

# Prompts

Reusable AI prompts supporting the engineering workflow.

| Document | Description |
|----------|-------------|
| prompts/Generate_Epic_Transition_Report.md | Generate an official Epic Transition Report |

---

# Architecture Decisions

Architectural decisions are maintained within the `decisions/` directory.

This section will grow as long-term architectural decisions are made.

---

# Archive

Historical documents that have been superseded but are retained for traceability are stored in the `archive/` directory.

Archived documents are not considered authoritative references.

---

# Engineering Principles

The Engineering Knowledge Base follows the principles defined in:

- `handbook/00_Working_Principles.md`
- `handbook/01_Documentation_Architecture.md`

The repository follows the guiding principle:

> **One Decision – One Standard – One Cheat Sheet**

Engineering knowledge shall have exactly one authoritative home.

---

# Status

**Version:** 2.0

**Status:** Living Document

The Engineering Knowledge Base evolves together with the project.

New engineering knowledge is continuously integrated through the established documentation workflow rather than creating isolated documents.