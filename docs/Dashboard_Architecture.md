# DevOps Dashboard Architecture

## Purpose

This document defines the durable product and technical boundaries of the DevOps Dashboard. It records architecture principles and responsibilities independently of implementation workflow, temporary project status, and operational procedures.

The repository contains two distinct Streamlit application roles. This document establishes how those roles remain separate while sharing appropriate repository-level capabilities.

## Product Context

The DevOps Dashboard is the primary product of the repository. It is intended to provide a professional, extensible, demonstration-ready, and portfolio-quality dashboard experience.

The dashboard is developed in parallel with an existing lifecycle demonstrator. The two applications serve complementary purposes but remain separate products at runtime.

## Application Roles

### DevOps Lifecycle Demonstrator

`app.py` remains the independent DevOps lifecycle demonstrator. It validates and showcases the DevOps delivery platform used to build and deliver repository applications.

The demonstrator must remain fully functional and isolated. It must not be renamed, converted into the dashboard, made a dashboard page, or used as the dashboard data source.

### DevOps Dashboard

`dashboard_app.py` is the future entry point of the DevOps Dashboard. The dashboard will use a dedicated modular dashboard package that is separate from the lifecycle demonstrator.

The dashboard package will own dashboard presentation, navigation, styling, reusable UI elements, and dashboard data responsibilities introduced within the approved phase scope.

## Application Boundaries

The lifecycle demonstrator and the dashboard may share repository-level tooling, dependencies, continuous integration, and delivery infrastructure. They must not share runtime responsibilities.

Each application must remain independently runnable and independently verifiable. Future dashboard data providers must remain independent from the lifecycle demonstrator.

## Incremental Architecture Principles

Dashboard modules must be introduced only when they have an immediate responsibility. Empty or speculative folder structures must not be created in advance.

Initial reusable component concepts should remain simple:

- Layout
- Navigation
- Cards
- Sections

Models, utilities, charts, integrations, and additional abstractions must be added only when justified by implemented behavior.

This document defines architecture principles and boundaries rather than a speculative complete directory tree.

## Phase 1 Scope

### Included

Phase 1 includes:

- Professional UI and UX
- Dashboard navigation
- Page layout
- Reusable UI components
- Centralized styling
- Realistic, deterministic dummy data
- Demonstration quality
- Portfolio quality

### Excluded

Phase 1 excludes:

- Credentials
- Network clients
- Production control functions
- Live GitHub integration
- Live GitHub Actions integration
- Live GHCR integration
- Live Argo CD integration
- Live Kubernetes integration
- Live DORA data integration

Later-phase technologies may appear during Phase 1 as realistic demonstration data without becoming runtime dependencies.

## Future Evolution

Live providers may be introduced in later phases behind dashboard-owned boundaries. They must remain independent from the lifecycle demonstrator and must not change the demonstrator into a dashboard dependency.

Models, utilities, charts, integrations, and other abstractions should evolve only in response to implemented and verifiable needs.

Usage and run instructions belong in the root `README.md` once `dashboard_app.py` exists. Installation, deployment, validation, and operational procedures belong in the playbooks.

## Architecture Authority

`docs/Dashboard_Architecture.md` is the authoritative source for the DevOps Dashboard product boundary. Other documentation may reference this decision but should not duplicate its detailed architectural rationale.
