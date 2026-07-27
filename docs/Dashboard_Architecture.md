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

`dashboard_app.py` is the entry point of the DevOps Dashboard. The dashboard uses a dedicated modular dashboard package that is separate from the lifecycle demonstrator.

The dashboard package will own dashboard presentation, navigation, styling, reusable UI elements, and dashboard data responsibilities introduced within the approved phase scope.

## Application Boundaries

The lifecycle demonstrator and the dashboard may share repository-level tooling, dependencies, continuous integration, and delivery infrastructure. They must not share runtime responsibilities.

Each application must remain independently runnable and independently verifiable. Future dashboard data providers must remain independent from the lifecycle demonstrator.

## Live Data Lifecycle Foundation

One Streamlit rerun creates one authoritative cached runtime snapshot. The
dashboard lifecycle aggregation service normalizes that snapshot and produces
exactly one immutable `PipelineRun` observation for downstream pipeline
consumers.

```text
Existing provider retrieval
        ↓
Authoritative runtime snapshot
        ↓
Provider normalization
        ↓
Identifier correlation
        ↓
PipelineRun
        ↓
Deterministic pipeline-stage mapping
```

`PipelineRun` records the delivery identifiers and state shared across
providers: commit SHA, workflow run ID, branch, workflow state, image
coordinates, deployment revision and namespace, Pod observations, lifecycle
timestamps, duration, and refresh metadata. The model also retains normalized
GitHub, GHCR, Argo CD, and Kubernetes observations without exposing their raw
provider dictionaries to pipeline presentation code.

The current retrieval layer populates GitHub, GitHub Actions, Docker Build,
and GHCR data. Argo CD and Kubernetes normalization is available as a stable
boundary, but remains `unknown` until live dashboard providers supply those
observations. Static Argo CD and Kubernetes pipeline presentation therefore
remains unchanged.

### Correlation Strategy

Correlation is evidence-based:

1. Commit SHA is the primary lifecycle identity.
2. Workflow run ID identifies the observed CI execution.
3. An image tag may connect GHCR to the commit only when it equals the full
   commit SHA or an unambiguous SHA prefix.
4. Deployment and runtime observations are attached only when their revisions
   or image tags match already-correlated identifiers.

Missing or conflicting identifiers produce an `unknown` or `partial`
correlation result. The aggregator never guesses a relationship from timing,
names, or ordering alone.

### Refresh Foundation

The lifecycle model contains the last refresh time, refresh status, configured
refresh interval, and calculated next refresh time. These values describe the
current retrieval observation only. No timer, polling, countdown, fragment
refresh, or background refresh behavior is implemented.

## Incremental Architecture Principles

Dashboard modules must be introduced only when they have an immediate responsibility. Empty or speculative folder structures must not be created in advance.

Initial reusable component concepts should remain simple:

- Layout
- Navigation
- Cards
- Sections

Models, utilities, charts, integrations, and additional abstractions must be added only when justified by implemented behavior.

This document defines architecture principles and boundaries rather than a speculative complete directory tree.

## Operational UI Design Rules

- Operational states use one shared semantic icon and color mapping; individual components must reuse rather than redefine it.
- Icons are the primary fast-recognition signal in compact operational rows. Long repeated state labels must not dominate them.
- Status legends belong in shared secondary UI, not inside individual panels; operational dashboard space must not be sacrificed for explanatory legends.
- Every event in a timeline uses the same compact, human-readable local timestamp format instead of raw machine timestamps.
- Logs, timelines, and event feeds use compact rows and always have a bounded visible height with overflow scrolling inside the component.
- Dynamic operational content must not expand indefinitely or destabilize the surrounding dashboard layout.

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
- Live Argo CD integration
- Live Kubernetes integration
- Live DORA data integration
- Automatic or background refresh

Later-phase technologies may appear during Phase 1 as realistic demonstration data without becoming runtime dependencies.

## Future Evolution

Additional live providers may be introduced behind the normalized lifecycle
boundary. They must remain independent from the lifecycle demonstrator and
must not change the demonstrator into a dashboard dependency.

Models, utilities, charts, integrations, and other abstractions should evolve only in response to implemented and verifiable needs.

Usage and run instructions belong in the root `README.md` once `dashboard_app.py` exists. Installation, deployment, validation, and operational procedures belong in the playbooks.

## Architecture Authority

`docs/Dashboard_Architecture.md` is the authoritative source for the DevOps Dashboard product boundary. Other documentation may reference this decision but should not duplicate its detailed architectural rationale.
