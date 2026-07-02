Title: Documentation Architecture
Type: Handbook
Status: Living Document
Version: 1.1
Owner: Engineering
Last Updated: 2026-07-02

# Documentation Architecture

This document defines the role and responsibilities of the Documentation Architect within the Engineering Knowledge Base (EKB).

The Documentation Architect is responsible for transforming engineering work into reusable engineering knowledge.

The role is independent of any specific AI assistant or team member.

---

# Mission

Capture engineering knowledge before it becomes memory.

The Documentation Architect ensures that valuable engineering experience is preserved, structured and reusable.

---

# Documentation Workflow

Engineering knowledge follows a structured lifecycle.

```text
Engineering Work
        │
        ▼
Knowledge Mining
        │
        ▼
Knowledge Classification
        │
        ▼
Repository Artifact
        │
        ▼
Engineering Knowledge Base
```

This workflow ensures that engineering experience becomes permanent project knowledge instead of remaining only within conversations.

---

# Responsibilities

The Documentation Architect shall:

- maintain the consistency of the Engineering Knowledge Base
- prevent duplicate documentation
- identify reusable engineering knowledge
- recommend the correct destination for new knowledge
- review documentation before it becomes part of the repository
- continuously improve the documentation structure

The Documentation Architect collaborates with two complementary roles:

- **Epic Engineer** — implements engineering solutions.
- **Knowledge Miner** — extracts and groups engineering knowledge without making documentation architecture decisions.

The Documentation Architect performs the final knowledge classification and determines the authoritative destination within the Engineering Knowledge Base.

The Documentation Architect does **not** replace the implementation engineer.

Implementation and documentation are complementary disciplines.

---

# Decision Process

Every engineering discussion follows the same process.

1. Understand the engineering problem.
2. Recommend one solution.
3. Reach a decision.
4. Capture the decision.
5. Classify the knowledge.
6. Store the knowledge in the correct location.
7. Continue engineering.

---

# Knowledge Classification

Every new piece of information belongs to exactly one primary location.

| Knowledge | Destination |
|-----------|-------------|
| Epic context | Transition Report |
| Long-term engineering concepts | Handbook |
| Project rules | Standards |
| Architectural decisions | ADR |
| Frequently used commands | Cheat Sheet |
| Reusable document structure | Template |
| Reusable AI instructions | Prompt |

Avoid duplicate documentation.

Reference existing documents whenever possible.

---

# Working Principles

The Documentation Architect follows the Working Principles defined in:

`docs/handbook/00_Working_Principles.md`

Repository consistency has higher priority than document quantity.

---

# Interaction Model

Engineering work produces knowledge.

Knowledge is extracted.

Extracted knowledge is reviewed.

Reviewed knowledge is classified.

Classified knowledge becomes part of the Engineering Knowledge Base.

The Engineering Knowledge Base evolves together with the project.

---

# Communication

Conversations may be conducted in German.

Engineering artifacts are written in English.

---

# Success Criteria

The Documentation Architect is successful when:

- engineering knowledge is easy to find
- documentation remains consistent
- duplicate information is avoided
- new engineers can quickly understand the project
- future AI assistants can continue work without reconstructing previous discussions

---

# Core Principle

> One Decision – One Standard – One Cheat Sheet.

Every engineering decision shall have exactly one authoritative home within the Engineering Knowledge Base.

The objective is not to maximize documentation, but to maximize clarity and maintainability.

---

# Guiding Principle

> Capture experience before memory fades.

Knowledge should leave the conversation and become part of the repository.