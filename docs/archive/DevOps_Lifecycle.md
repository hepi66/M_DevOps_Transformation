# DevOps Workflow Lifecycle

To integrate the workflow safely into your daily routine---especially
after being away from the project for several days---this document
describes the complete **DevOps lifecycle** for a typical code change to
`app.py`.

This workflow forms the backbone of the entire project.

------------------------------------------------------------------------

# Workflow Lifecycle: From Idea to Deployment

## 1. Code Change & Local Verification

### Development

-   Modify `app.py` in your local WSL development environment.
-   Test the application locally:

``` bash
streamlit run app.py
```

### Local Container Build

Build the Docker image locally:

``` bash
docker build -t m-devops-transformation .
```

### Purpose

Before pushing any changes, verify that:

-   the application runs correctly,
-   the Docker image builds successfully,
-   no obvious issues exist before triggering the CI pipeline.

------------------------------------------------------------------------

## 2. Git Commit & Push (Pipeline Trigger)

Commit your changes and push them to your GitHub feature branch.

### Important Rule

The CI/CD pipeline only detects changes **after they have been pushed to
GitHub**.

No push → No pipeline execution.

------------------------------------------------------------------------

## 3. Continuous Integration (GitHub Actions)

A push automatically triggers the GitHub Actions workflow.

### Quality Gates

The pipeline performs automated validation, including:

-   automated testing
-   code style validation
-   static code analysis
-   security scanning (e.g., Ruff, Bandit)

### Container Build

If all quality gates pass successfully, the pipeline builds the official
production container image.

------------------------------------------------------------------------

## 4. Container Registry Publishing (GHCR)

The newly built image is published to the **GitHub Container Registry
(GHCR)**.

Each image receives a unique version tag (typically based on the Git
commit SHA).

### Result

A versioned, deployable container image is now available in the
registry.

------------------------------------------------------------------------

## 5. GitOps Synchronization (Argo CD --- Epic E03)

> **Implemented during Epic E03**

Argo CD continuously monitors either:

-   the GitOps manifest repository, or
-   newly available container images.

When a change is detected:

1.  Argo CD pulls the desired state.
2.  Kubernetes deploys the new container image.
3.  The updated application becomes available.

This follows the GitOps **Pull Model**.

------------------------------------------------------------------------

### Automated Deployment Validation

After synchronization, the deployment health is automatically validated
using the project verification scripts.

``` text
verify_cluster.ps1
        │
        ▼
verify_pods.ps1
        │
        ▼
verify_gitops.ps1
        │
        ▼
verify_all.ps1
```

The validation checks confirm:

-   Kubernetes cluster connectivity
-   Argo CD namespace availability
-   ApplicationSet CRD installation
-   Argo CD pod health
-   GitOps synchronization status
-   Application health status

The scripts return standard exit codes:

-   Exit Code `0` → Validation successful
-   Exit Code `1` → Validation failed

This enables the validation to be executed locally as well as integrated
into future CI/CD pipelines.

------------------------------------------------------------------------

# Visual Workflow Overview

``` text
Source Code (app.py)
        │
        ▼
Local Verification
(Streamlit + Docker Build)
        │
        ▼
Git Commit & Push
        │
        ▼
GitHub Actions
(Quality Gates + Container Build)
        │
        ▼
GitHub Container Registry (GHCR)
        │
        ▼
Argo CD
(GitOps Synchronization)
        │
        ▼
Automated Validation
(verify_all.ps1)
        │
        ▼
Kubernetes Cluster
        │
        ▼
Running Cloud Application
```

------------------------------------------------------------------------

# Quick Restart Checklist

Whenever you return to the project after a break, perform these three
checks to quickly regain context.

## 1. Epic Status

Identify the currently active Epic.

**Current Epic:** E03

------------------------------------------------------------------------

## 2. Pipeline Status

Open the **GitHub Actions** tab.

If the most recent workflow executions are green:

-   the repository is healthy,
-   the CI pipeline is functioning correctly,
-   your foundation is stable.

------------------------------------------------------------------------

Run `scripts/verify_all.ps1` before continuing development to verify
that the complete GitOps environment is healthy.

------------------------------------------------------------------------

## 3. Log Review

Inspect your central `system.log`.

This log is the primary reference point for diagnosing:

-   extraction issues
-   build failures
-   pipeline errors
-   runtime problems

It should always be your first stop when troubleshooting.

------------------------------------------------------------------------

# Key Principle

This workflow is considered the project's **standard operating
procedure**.

The lifecycle itself does not change throughout the project.

Epic E03 simply extends the existing workflow by introducing automated
**GitOps synchronization** through **Argo CD**, completing the
end-to-end cloud-native deployment pipeline.
