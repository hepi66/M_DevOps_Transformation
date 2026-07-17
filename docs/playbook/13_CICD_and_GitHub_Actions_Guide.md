# CI/CD and GitHub Actions Guide

## Purpose

This guide explains how the M-DevOps platform automates software validation and container image creation using GitHub Actions.

The objective is to understand how source code changes are transformed into validated deployment artifacts without manual intervention.

This guide builds upon the Container Build and Validation Guide.

---

# What is CI/CD?

CI/CD stands for:

```text
Continuous Integration
Continuous Delivery
```

Within this platform:

Continuous Integration (CI) is implemented.

The pipeline automatically:

* Validates source code
* Executes tests
* Performs security checks
* Builds container images
* Publishes deployment artifacts

---

# Why CI Exists

Without automation:

```text
Developer
    ↓
Manual Testing
    ↓
Manual Build
    ↓
Manual Deployment
```

This approach is error-prone and difficult to scale.

With CI:

```text
Git Push
    ↓
GitHub Actions
    ↓
Automated Validation
    ↓
Automated Build
```

Every change is evaluated consistently.

---

# Pipeline Entry Point

Pipeline definition:

```text
.github/workflows/ci.yml
```

This file defines:

* Pipeline triggers
* Validation stages
* Build stages
* Publication stages

The workflow is version-controlled alongside the application.

---

# Pipeline Trigger

The pipeline starts automatically when changes are pushed to the repository.

Typical flow:

```text
Developer
    ↓
git push
    ↓
GitHub Repository
    ↓
GitHub Actions Workflow
```

No manual pipeline execution is required under normal circumstances.

---

# CI Pipeline Stages

## Stage 1 – Source Checkout

Purpose:

Retrieve repository contents for processing.

Result:

Workflow runner receives a working copy of the repository.

---

## Stage 2 – Dependency Installation

Purpose:

Prepare required Python tooling.

Typical responsibilities:

* Install Python
* Install project dependencies
* Install validation tools

Result:

Workflow environment prepared.

---

## Stage 3 – Linting

Tool:

```text
Ruff
```

Purpose:

Detect coding issues and style violations.

Benefits:

* Consistent code quality
* Early defect detection

Result:

Source code quality validated.

---

## Stage 4 – Security Scanning

Tool:

```text
Bandit
```

Purpose:

Detect common Python security issues.

Benefits:

* Early security feedback
* Reduced deployment risk

Result:

Basic security validation completed.

---

## Stage 5 – Automated Testing

Tool:

```text
pytest
```

Purpose:

Validate application behavior.

Benefits:

* Regression detection
* Change verification

Result:

Application functionality confirmed.

---

## Stage 6 – Container Build

Tool:

```text
Docker
```

Purpose:

Create deployable container image.

Equivalent local command:

```powershell
docker build -t m-devops-transformation .
```

Result:

Deployment artifact created.

---

## Stage 7 – Publish to GHCR

Target:

```text
GitHub Container Registry (GHCR)
```

Purpose:

Store deployable images.

Result:

Image becomes available for deployment.

---

# Understanding Pipeline Success

A successful pipeline indicates:

```text
Source Code
        ✓

Linting
        ✓

Security Checks
        ✓

Tests
        ✓

Container Build
        ✓

Image Publication
        ✓
```

Only after all stages succeed is the image considered deployable.

---

# Viewing Workflow Results

GitHub provides visibility into:

* Workflow runs
* Build logs
* Validation results
* Failure details

Recommended review areas:

```text
Actions Tab
    ↓
Workflow Run
    ↓
Job Details
```

This should be the first location investigated when automation fails.

---

# Failure Handling

## Linting Failure

Symptoms:

```text
Ruff failed
```

Resolution:

* Review linting output
* Correct source code issues
* Commit changes
* Push again

---

## Security Scan Failure

Symptoms:

```text
Bandit failed
```

Resolution:

* Review findings
* Evaluate severity
* Correct issue if required

---

## Test Failure

Symptoms:

```text
pytest failed
```

Resolution:

* Review failing test
* Fix defect
* Re-run locally
* Commit correction

---

## Docker Build Failure

Symptoms:

```text
docker build failed
```

Resolution:

* Review Dockerfile
* Review dependency installation
* Verify application startup process

---

## GHCR Publication Failure

Symptoms:

```text
Image not published
```

Possible causes:

* Authentication issues
* Registry permissions
* Workflow configuration problems

Review workflow logs carefully.

---

# Relationship to the Delivery Chain

The CI pipeline occupies the following position:

```text
Developer Change
        ↓
Git Push
        ↓
GitHub Actions
        ↓
Docker Image
        ↓
GHCR
```

The output of CI becomes the input for GitOps deployment.

---

# Success Criteria

This guide is complete when the engineer understands:

* Pipeline trigger mechanism
* Validation stages
* Build process
* Image publication process
* Failure diagnosis workflow

The engineer should be capable of interpreting pipeline results and resolving common failures.
---

# Next Recommended Reading

Continue with:

- [GHCR Guide](14_GHCR_Guide.md)

---

# Related Documents

- [Container Build and Validation Guide](12_Container_Build_and_Validation_Guide.md)
- [GHCR Guide](14_GHCR_Guide.md)
- [CI/CD and GHCR Troubleshooting](42_CICD_and_GHCR_Troubleshooting.md)

---

Return to:

- [Engineering Playbook](README.md)
- [Engineering Documentation Portal](../README.md)
