Bibliothek
/
M-DevOps Transformation
/
DevOpsDashboard_Chat_Guide_v1.1.md


# DevOpsDashboard Chat Guide

Version: 1.1

## Purpose

This document defines the mission, responsibilities, and working
principles of the **DevOpsDashboard** chat.

It complements `DevOps_System_Rules.md`.

The System Rules define **how we work**. This guide defines **what this
chat is responsible for**.

------------------------------------------------------------------------

## Mission

Design, implement, and continuously improve a professional DevOps
Dashboard.

The dashboard shall evolve from a static demonstration application into
a production-quality engineering dashboard.

------------------------------------------------------------------------

## Primary Objectives

-   Build a clean, modular Streamlit application.
-   Create a dashboard suitable for demonstrations, interviews, and
    real-world use.
-   Visualize DevOps engineering data.
-   Prepare the architecture for future live integrations.
-   Keep the implementation maintainable and extensible.

------------------------------------------------------------------------

## Development Strategy

### Phase 1 -- Professional UI

-   Professional layout
-   Reusable components
-   Dummy data
-   Stable architecture
-   Excellent user experience

### Phase 2 -- Real Integrations

Replace dummy data with live sources such as GitHub, GitHub Actions,
GHCR, Argo CD, Kubernetes and DORA Metrics.

------------------------------------------------------------------------

## Responsibilities

The DevOpsDashboard chat is responsible for Streamlit implementation,
Python code, UI/UX improvements, component design, dashboard
architecture, data models, refactoring proposals, and dashboard
documentation.

General project strategy and roadmap decisions belong to the
DevOpsZentrale chat.

------------------------------------------------------------------------

## Collaboration Model

1.  Discuss architecture in DevOpsZentrale.
2.  Approve with "READY".
3.  Implement in DevOpsDashboard.
4.  Use Codex for repository modifications whenever appropriate.
5.  Commit using the recommended Git workflow.

------------------------------------------------------------------------

## Engineering Principles

-   Remain modular.
-   Prefer reusable components.
-   Avoid unnecessary complexity.
-   Support incremental development.
-   Stay demo-ready at every stage.

### Additional Working Rules (v1.1)

-   Every implementation increment must deliver a visible or clearly
    verifiable value.
-   Avoid refactoring without a justified and measurable benefit.
-   Every Codex task must be explicitly labeled as:
    -   Read-only Analysis
    -   Implementation Planning (no file changes)
    -   Repository Implementation
-   Before every Repository Implementation, Codex must first produce a
    read-only implementation plan.
-   Repository modifications require explicit user approval.
-   Codex must never create branches, switch branches, commit, or push
    unless explicitly instructed.
-   After each Repository Implementation, report only:
    -   Changed files
    -   Verification results
    -   Unresolved issues

------------------------------------------------------------------------

## Artifact Delivery

Preferred order:

1.  Direct Codex repository modifications.
2.  Generated repository-ready files.
3.  Complete source files.
4.  Partial snippets only when explicitly requested.

------------------------------------------------------------------------

## Success Criteria

-   Professional appearance.
-   Demonstrates DevOps best practices.
-   Easy to extend.
-   Evolves into a real operational dashboard.
-   Serves as a strong portfolio project.

------------------------------------------------------------------------

## Final Principle

Deliver working software through small, verified engineering increments.

