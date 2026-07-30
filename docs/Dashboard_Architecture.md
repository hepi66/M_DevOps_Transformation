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

The retrieval layer populates GitHub, GitHub Actions, Docker Build, and GHCR
data. When the dashboard runs in Kubernetes, read-only providers additionally
observe the dashboard Argo CD Application and its Kubernetes Deployment,
ReplicaSets, and Pods. Local execution does not require cluster credentials;
the cluster observations return an explicit unavailable state.

The cluster providers use the automatically mounted Pod ServiceAccount token
and cluster certificate. They do not invoke `kubectl` or the `argocd` CLI,
embed credentials, or request write access.

### Correlation Strategy

Correlation is evidence-based:

1. Commit SHA is the primary lifecycle identity.
2. Workflow run ID identifies the observed CI execution.
3. An image tag may connect GHCR to the commit only when it equals the full
   commit SHA or an unambiguous SHA prefix.
4. Deployment and runtime observations are attached only when their revisions
   or image tags match already-correlated identifiers.

After a dashboard Pod restart, the currently deployed immutable image tag can
act as the commit anchor even when GitHub retrieval is temporarily
unavailable. This permits reconstruction of independently verified runtime
state without relying on transient Streamlit session state.

Missing or conflicting identifiers produce an `unknown` or `partial`
correlation result. The aggregator never guesses a relationship from timing,
names, or ordering alone.

### Pipeline Status and Operational Sources

Pipeline tiles use one evidence-based status vocabulary: `COMPLETED`,
`RUNNING`, `FAILED`, `UNKNOWN`, and `UNAVAILABLE`. `UNKNOWN` means that
lifecycle evidence is missing, conflicting, or cannot be correlated.
`UNAVAILABLE` means that the responsible provider cannot currently be
observed. During local execution, Argo CD and Kubernetes therefore report
`UNAVAILABLE` with the concise context `Unavailable locally`; this does not
imply a failed deployment.

Operational Events use one authoritative source vocabulary:

- `GI` — Git / local repository
- `GH` — GitHub
- `CI` — GitHub Actions / CI
- `DB` — Docker Build
- `CR` — GitHub Container Registry
- `CD` — Argo CD
- `K8` — Kubernetes

The same definitions drive Viewer filtering, event labels and colors,
pipeline context highlighting, deterministic ordering, and the footer legend.
The `All` view is the unfiltered event collection.

GHCR tile state and GHCR Operational Events are projected from the same
correlated `PipelineRun`. Publication is completed only when the image tag
matches the run commit, or when a digest match is anchored by a matching
runtime image tag. A successful but unrelated CI run or a stale package alone
does not mark GHCR completed.

### Targeted Live Monitoring

Streamlit fragments refresh only the Delivery Pipeline, refresh indicator,
countdown, manual refresh control, and Operational Detail Viewer. There is no
periodic complete-page rerun.

Two fragments share one session-scoped monitoring state. When a refresh is
due, the first fragment retrieves all providers and creates exactly one
authoritative `PipelineRun`; the other fragment reuses it. One-second fragment
ticks update the lightweight countdown, but provider calls occur only at the
scheduled interval or after `Refresh now`.

The deterministic defaults are:

- 7 seconds for a queued or active run
- 20 seconds after unavailable or partial retrieval
- 45 seconds while the latest known run is idle

Manual refresh marks the same shared observation immediately due and performs
one complete dashboard rerun so every monitoring consumer observes the new
cycle. Viewer filter and selected pipeline context remain in Streamlit session
state and are not reset by automatic refresh.

Refresh scheduling is presentation state and never creates Operational
Events. Pipeline stages change only from provider evidence; no simulated
progression, artificial delay, or animation exists.

When a retrieval attempt raises an error, the last successful observation is
retained with its timestamp and the monitoring status reports the retry
schedule. Provider failures remain isolated from the complete dashboard.

### Development Refresh Mode and Viewer Synchronization

The global `Live Refresh` control changes scheduling only:

- **ON** preserves adaptive provider polling, the countdown, and periodic
  fragment reruns.
- **OFF** removes periodic fragment scheduling and ignores elapsed refresh
  deadlines during ordinary UI reruns. The current snapshot remains visible.
  `Refresh now` still requests exactly one complete monitoring cycle.

`PipelineRun.current_stage` is the authoritative Active Pipeline Stage. While
the Viewer is in live-follow mode, this stage updates the existing
`operational_detail_source` selection; Operational Events are not inspected to
infer activity.

Every pipeline tile writes to that same selection. Clicking a tile or choosing
an individual Viewer source enables a small manual-override flag, preventing
later monitoring refreshes from replacing the user's choice. `All` means
**Return to Live**: its Viewer callback clears the override and immediately
resolves the selection from the current shared `PipelineRun.current_stage`.
The next Viewer render therefore resumes automatic following without waiting
for another provider refresh. The internal pipeline context and the Streamlit
selectbox use separate session keys so automatic synchronization never mutates
an already-instantiated widget.

The selected tile and Operational Detail Viewer use the contextual accent
defined for that stage in the authoritative operational-source vocabulary.
The same centralized color is used for the selected tile, Viewer border, and
matching event-source identifier. This interaction uses Streamlit buttons,
session state, selectbox callbacks, and fragments only.

GHCR presentation uses a bounded one-refresh stability window. When the same
commit and workflow run were already correlated successfully, one immediately
following observation may retain that verified GHCR evidence if registry
availability or tag correlation is transiently incomplete. The grace is
consumed after one cycle and is reset only by fresh correlated evidence.
Different workflow runs, authentication or package-missing states, and
explicit GHCR failures bypass the grace and appear immediately. This avoids
normal provider-timing flicker without weakening identifier correlation or
retaining stale evidence indefinitely.

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
- Live DORA data integration
- Background services or non-Streamlit refresh mechanisms

Later-phase technologies may appear during Phase 1 as realistic demonstration data without becoming runtime dependencies.

## Future Evolution

Additional live providers may be introduced behind the normalized lifecycle
boundary. They must remain independent from the lifecycle demonstrator and
must not change the demonstrator into a dashboard dependency.

Models, utilities, charts, integrations, and other abstractions should evolve only in response to implemented and verifiable needs.

Usage and run instructions belong in the root `README.md` once `dashboard_app.py` exists. Installation, deployment, validation, and operational procedures belong in the playbooks.

## Architecture Authority

`docs/Dashboard_Architecture.md` is the authoritative source for the DevOps Dashboard product boundary. Other documentation may reference this decision but should not duplicate its detailed architectural rationale.
