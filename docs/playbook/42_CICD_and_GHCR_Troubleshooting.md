# CI/CD and GHCR Troubleshooting Guide

## Purpose

This guide documents common CI/CD, Docker, and GitHub Container Registry (GHCR) issues encountered during development and operation of the M-DevOps platform.

The objective is to provide repeatable troubleshooting procedures for pipeline failures, container build problems, image publication issues, and deployment artifact availability.

This guide focuses on failures occurring between GitHub source control and GitOps deployment.

---

# CI/CD Architecture Overview

Validated platform flow:

```text id="q5m2wr"
Git Push
        ↓
GitHub Actions
        ↓
Ruff

Bandit

pytest

Docker Build
        ↓
GHCR Publication
        ↓
ArgoCD Deployment
```

Any failure within this chain blocks deployment progression.

---

# Troubleshooting Philosophy

Always identify the failed stage first.

Avoid:

```text id="j7v4mx"
Guessing

Skipping logs

Changing multiple components
```

Prefer:

```text id="x8p2wd"
Identify Stage

Review Logs

Determine Cause

Apply Fix

Validate Again
```

---

# Investigation Workflow

Recommended sequence:

```text id="k4r8vn"
GitHub Actions
        ↓
Workflow Logs
        ↓
Docker Build
        ↓
GHCR
        ↓
GitOps
```

The failed stage usually identifies the affected layer.

---

# Issue: GitHub Actions Workflow Not Starting

## Symptom

Push succeeds but no workflow executes.

---

## Investigation

Verify workflow file exists:

```text id="g5q2pr"
.github/workflows/ci.yml
```

Verify:

```text id="s3v8mk"
Push reached GitHub

Workflow enabled

Actions available
```

---

## Resolution

Review workflow configuration and repository Actions settings.

Confirm the workflow trigger matches the intended branch.

---

# Issue: Workflow Failed

## Symptom

GitHub Actions run reports:

```text id="v7m4tx"
Failed
```

---

## Investigation

Review the failed step.

Typical failure stages:

```text id="n8p5qw"
Ruff

Bandit

pytest

Docker Build
```

Always start with the first failed stage.

---

# Issue: Ruff Failure

## Symptom

Pipeline stops during linting.

---

## Meaning

Code quality rules were violated.

---

## Investigation

Review Ruff output.

Identify:

```text id="a2v9my"
File

Line

Rule
```

---

## Resolution

Correct the reported issue.

Commit and push again.

---

# Issue: Bandit Failure

## Symptom

Pipeline stops during security analysis.

---

## Meaning

Bandit detected a security-related concern.

---

## Investigation

Review reported finding.

Determine:

```text id="u4q7pt"
Real issue

False positive
```

---

## Resolution

Correct the code or document and justify accepted findings where appropriate.

---

# Issue: pytest Failure

## Symptom

Pipeline stops during testing.

---

## Investigation

Review test output.

Identify:

```text id="r8m3vd"
Failed test

Assertion failure

Unexpected behavior
```

---

## Resolution

Correct the application or test logic.

Validate locally before pushing again.

---

# Issue: Docker Build Failure

## Symptom

Pipeline fails during image creation.

---

## Investigation

Review Docker build logs.

Focus on:

```text id="m6p1qy"
Dockerfile

requirements.txt

Missing files

Build commands
```

---

## Useful Local Verification

Execute:

```powershell id="d9t5mk"
docker build -t m-devops-transformation .
```

Reproduce the issue locally before modifying pipeline configuration.

---

# Issue: Dependency Installation Failure

## Symptom

Container build fails while installing Python packages.

---

## Investigation

Review:

```text id="c2w7rp"
requirements.txt
```

Verify:

```text id="n4v9qx"
Package names

Versions

Availability
```

---

## Resolution

Correct invalid dependencies and rebuild.

---

# Issue: Docker Image Builds Locally But Fails In CI

## Symptom

Local build successful.

Pipeline build fails.

---

## Possible Causes

```text id="q7m2pk"
Missing committed file

Environment difference

Incorrect build context
```

---

## Investigation

Verify:

```powershell id="k8v5tw"
git status
```

Ensure required files are committed.

---

# Issue: Image Not Published To GHCR

## Symptom

Pipeline succeeds partially but image unavailable in GHCR.

---

## Investigation

Review publication step.

Verify:

```text id="z5q8vn"
Registry login

Image tag

Push step
```

---

## Resolution

Correct publication configuration and rerun the workflow.

---

# Issue: Image Not Found During Deployment

## Symptom

Deployment fails with image pull errors.

Examples:

```text id="u3v7mr"
ImagePullBackOff
```

---

## Investigation

Verify:

```text id="w8p1qy"
Image exists in GHCR

Image tag correct

Deployment image reference correct
```

---

## Resolution

Publish a valid image and verify deployment configuration.

---

# Issue: GHCR Contains Old Image

## Symptom

Expected changes do not appear after deployment.

---

## Investigation

Verify:

```text id="f7m3vx"
Latest workflow completed

Latest image published

Deployment uses expected tag
```

---

## Resolution

Confirm artifact publication and deployment synchronization.

---

# Issue: Deployment Uses Wrong Image

## Symptom

Application behavior does not match recent changes.

---

## Investigation

Review deployment manifest image reference.

Example:

```text id="b2w9pk"
ghcr.io/<owner>/m-devops-transformation:latest
```

Verify image source and tag.

---

## Resolution

Correct image reference and synchronize GitOps state.

---

# Project Lesson Learned: Local Validation Saves Time

## Observation

Many pipeline failures can be detected before pushing.

---

## Recommended Practice

Execute locally:

```powershell id="x5v2tr"
pytest
```

```powershell id="q9m7wd"
docker build -t m-devops-transformation .
```

before creating a release.

---

# Project Lesson Learned: Artifact Availability Is Part Of Deployment

## Observation

Successful deployment depends on successful artifact publication.

---

## Impact

If GHCR does not contain the expected image:

```text id="p6r4mx"
No Deployment
```

regardless of GitOps health.

---

## Final Practice

Treat GHCR as a critical platform component.

---

# Project Lesson Learned: CI/CD Failures Should Be Solved At Source

## Observation

Engineers sometimes focus on deployment symptoms.

---

## Better Approach

If CI/CD failed:

```text id="j4w8vn"
Fix CI/CD First
```

Deployment troubleshooting should begin only after a successful pipeline.

---

# CI/CD Investigation Checklist

```text id="m7v3pk"
□ Workflow started

□ Workflow completed

□ Ruff passed

□ Bandit passed

□ Tests passed

□ Docker build successful

□ Image published

□ GHCR artifact available
```

This checklist resolves most CI/CD incidents.

---

# Success Criteria

This guide is complete when the engineer understands:

* CI/CD investigation workflow
* GitHub Actions failures
* Docker build failures
* Dependency issues
* GHCR publication issues
* Artifact validation
* Project-specific lessons learned

The engineer should be capable of diagnosing and resolving routine CI/CD and container registry issues independently.
---

# Next Recommended Reading

Continue with:

- [ArgoCD Troubleshooting](43_ArgoCD_Troubleshooting.md)

---

# Related Documents

- [CI/CD and GitHub Actions Guide](13_CICD_and_GitHub_Actions_Guide.md)
- [GHCR Guide](14_GHCR_Guide.md)
- [Troubleshooting Overview](40_Troubleshooting_Overview.md)

---

Return to:

- [Engineering Playbook](README.md)
- [Engineering Documentation Portal](../README.md)
