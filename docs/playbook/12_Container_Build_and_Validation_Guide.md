# Container Build and Validation Guide

## Purpose

This guide explains how application source code is transformed into a deployable container image.

The objective is to understand, build, validate, and execute Docker images locally before introducing automated CI/CD and GitOps deployment workflows.

This guide represents the transition from software development to software packaging.

---

# Why Containers Exist

Application source code alone is not a deployable artifact.

A running application requires:

* Source code
* Runtime
* Dependencies
* Configuration
* Startup instructions

Docker packages all required components into a single deployable unit.

This unit is called a container image.

---

# Platform Containerization Flow

The platform follows this packaging model:

```text id="zq3ll2"
Python Source Code
        ↓
requirements.txt
        ↓
Dockerfile
        ↓
Docker Build
        ↓
Docker Image
        ↓
Container Runtime
```

The Docker image becomes the artifact that is deployed throughout the platform.

---

# Key Files

## Application Source

```text id="a4v6mx"
app.py
```

Contains application logic.

---

## Dependency Definition

```text id="k8c1ph"
requirements.txt
```

Defines Python dependencies.

---

## Container Definition

```text id="mkup4h"
Dockerfile
```

Defines how the image is built.

The Dockerfile describes:

* Base image
* Dependencies
* Application files
* Startup command

---

# Understanding the Dockerfile

A Dockerfile acts as a build recipe.

Typical responsibilities include:

```text id="50o6c7"
Select base image
        ↓
Install dependencies
        ↓
Copy source code
        ↓
Define startup command
```

The result is a reproducible runtime environment.

---

# Build the Docker Image

From the repository root:

```powershell id="f5e3z4"
docker build -t m-devops-transformation .
```

Explanation:

```text id="xmvw1e"
docker build
        ↓
reads Dockerfile
        ↓
creates image
        ↓
stores image locally
```

---

# Verify Image Creation

List local images:

```powershell id="e1x7zr"
docker images
```

Expected result:

```text id="8v1ewk"
m-devops-transformation
```

appears in the image list.

---

# Run Container Locally

Start the image:

```powershell id="d9bl7m"
docker run -p 8501:8501 m-devops-transformation
```

Explanation:

```text id="olzntf"
Host Port 8501
        ↓
Container Port 8501
```

The application should become accessible through a browser.

---

# Verify Running Container

List running containers:

```powershell id="7gj3vk"
docker ps
```

Expected result:

```text id="6j9wpo"
Container status: Up
```

---

# Inspect Container Logs

View logs:

```powershell id="4yb6r8"
docker logs <container-id>
```

Purpose:

* Startup verification
* Error diagnosis
* Runtime troubleshooting

Logs are often the first troubleshooting step.

---

# Stop Container

Stop execution:

```powershell id="58ljqu"
docker stop <container-id>
```

Verify:

```powershell id="gq7g5r"
docker ps
```

Container should no longer be running.

---

# Understanding the Deployment Artifact

The image created locally is the same type of artifact used later by:

```text id="8t7u5l"
GitHub Actions
        ↓
GHCR
        ↓
ArgoCD
        ↓
Kubernetes
```

Only the storage location changes.

The artifact itself remains a Docker image.

---

# Relationship to CI/CD

Local build:

```text id="5myk9a"
Developer
        ↓
docker build
```

Automated build:

```text id="v6g3pk"
GitHub Actions
        ↓
docker build
```

The CI/CD pipeline performs the same process automatically.

Understanding local image creation is essential before understanding automated image publication.

---

# Common Troubleshooting

## Docker Desktop Not Running

Symptoms:

```text id="jlwm7h"
Cannot connect to Docker daemon
```

Resolution:

* Start Docker Desktop
* Wait until Docker reports healthy status

---

## Build Failure

Symptoms:

```text id="9eq2o7"
docker build fails
```

Possible causes:

* Invalid Dockerfile
* Missing dependencies
* Incorrect file paths

Review build output carefully.

---

## Application Does Not Start

Verify:

* Container running
* Port mapping correct
* Application startup command valid

Inspect logs:

```powershell id="vdb8mh"
docker logs <container-id>
```

---

# Success Criteria

This guide is complete when:

* Docker image builds successfully
* Image appears in local image list
* Container starts successfully
* Application is accessible
* Logs can be inspected
* Container can be stopped cleanly

The engineer now understands the deployable artifact used throughout the platform.
---

# Next Recommended Reading

Continue with:

- [CI/CD and GitHub Actions Guide](13_CICD_and_GitHub_Actions_Guide.md)

---

# Related Documents

- [Repository and Development Guide](11_Repository_and_Development_Guide.md)
- [CI/CD and GitHub Actions Guide](13_CICD_and_GitHub_Actions_Guide.md)
- [CI/CD and GHCR Troubleshooting](42_CICD_and_GHCR_Troubleshooting.md)

---

Return to:

- [Engineering Playbook](README.md)
- [Engineering Documentation Portal](../README.md)
