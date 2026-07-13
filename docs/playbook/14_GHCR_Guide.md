# GitHub Container Registry (GHCR) Guide

## Purpose

This guide explains the role of GitHub Container Registry (GHCR) within the M-DevOps platform.

The objective is to understand how container images are stored, versioned, distributed, and consumed by downstream deployment systems.

This guide bridges the gap between CI/CD automation and GitOps deployment.

---

# What is GHCR?

GHCR stands for:

GitHub Container Registry

Purpose:

* Store Docker images
* Version deployment artifacts
* Distribute images to runtime platforms

GHCR serves as the artifact repository of the platform.

---

# Why a Container Registry Exists

Building an image alone is not sufficient.

Without a registry:

```text id="p8g98z"
Developer
    ↓
Build Image
    ↓
Image remains local
```

The image cannot be consumed by other systems.

A registry provides:

```text id="q0q8ja"
Developer
    ↓
GitHub Actions
    ↓
Build Image
    ↓
GHCR
    ↓
Deployment Systems
```

This allows Kubernetes to retrieve deployment artifacts from a central location.

---

# Position in the Delivery Chain

GHCR occupies the following position:

```text id="k9cgg8"
Developer
    ↓
GitHub Actions
    ↓
Docker Build
    ↓
GHCR
    ↓
ArgoCD
    ↓
Kubernetes
```

GHCR separates image creation from image execution.

---

# Artifact Lifecycle

The platform follows this lifecycle:

```text id="t6pqzg"
Source Code
        ↓
Docker Build
        ↓
Container Image
        ↓
Publish to GHCR
        ↓
Deployment
```

The deployment artifact remains unchanged after publication.

---

# Image Naming Convention

Typical format:

```text id="7v7hdy"
ghcr.io/<owner>/<repository>:<tag>
```

Example:

```text id="x4ntzg"
ghcr.io/<owner>/m-devops-transformation:latest
```

Components:

```text id="8n3x0g"
Registry
    ↓
Owner
    ↓
Repository
    ↓
Tag
```

---

# Understanding Image Tags

Tags identify image versions.

Examples:

```text id="n2l5v3"
latest
v1.0.0
v1.1.0
build-123
```

The current platform commonly references:

```text id="e2x6s5"
latest
```

Future environments may use explicit version tags.

---

# Publishing Images

Publication is performed automatically by GitHub Actions.

Typical process:

```text id="f1w4my"
Git Push
    ↓
CI Pipeline
    ↓
Docker Build
    ↓
GHCR Push
```

Engineers normally do not publish images manually.

---

# Viewing Images

Images can be inspected through GitHub.

Typical information includes:

* Repository name
* Image tags
* Publication history
* Package metadata

These records provide visibility into deployment artifacts.

---

# Why Kubernetes Uses GHCR

Kubernetes does not deploy source code.

Kubernetes deploys container images.

Example deployment reference:

```yaml id="a4x0pq"
image: ghcr.io/<owner>/m-devops-transformation:latest
```

At deployment time:

```text id="s2iwdh"
Kubernetes
        ↓
GHCR
        ↓
Download Image
        ↓
Start Container
```

The registry therefore acts as the software distribution layer.

---

# Relationship to Docker

Docker creates images.

GHCR stores images.

Relationship:

```text id="4k9k2v"
Docker
    ↓
Creates Image

GHCR
    ↓
Stores Image
```

Both components are required.

---

# Relationship to GitOps

GitOps does not deploy source code.

GitOps deploys infrastructure definitions that reference images.

Typical flow:

```text id="t9yzvf"
Git Repository
        ↓
Deployment Manifest
        ↓
Image Reference
        ↓
GHCR Image
        ↓
Kubernetes Deployment
```

GHCR therefore becomes a critical dependency for GitOps deployment.

---

# Common Troubleshooting

## Image Not Found

Symptoms:

```text id="d7vks2"
ImagePullBackOff
```

Possible causes:

* Incorrect image name
* Missing image tag
* Image not published

Verify image existence in GHCR.

---

## Authentication Issues

Symptoms:

```text id="u4e7vh"
Unauthorized
```

Possible causes:

* Registry permissions
* Authentication configuration
* Missing credentials

Review registry access configuration.

---

## Wrong Image Version

Symptoms:

```text id="s0sjw8"
Unexpected application behavior
```

Verify:

* Deployment manifest image reference
* Published image tag
* Latest successful workflow run

---

# Operational Importance

GHCR represents the authoritative source of deployment artifacts.

If an image does not exist in GHCR:

* ArgoCD cannot deploy it
* Kubernetes cannot run it
* Platform updates cannot occur

For this reason GHCR is a critical platform component.

---

# Success Criteria

This guide is complete when the engineer understands:

* Why registries exist
* How images are published
* How images are referenced
* How Kubernetes consumes images
* The relationship between Docker and GHCR

The engineer should be able to explain the complete artifact lifecycle from source code to deployable image.

---

# Next Step

Continue with:

**GitOps and ArgoCD Guide**

This introduces the deployment layer that transforms stored artifacts into running workloads.
