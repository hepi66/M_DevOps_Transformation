# Platform Rebuild Checklist

## Purpose

This checklist provides the validated end-to-end procedure for rebuilding the M-DevOps platform from scratch.

The checklist is intended to be used during:

* New workstation setup
* Platform recovery
* Disaster recovery exercises
* Knowledge transfer
* Playbook validation

Unlike other Playbook documents, this guide focuses on execution rather than explanation.

---

# Rebuild Success Criteria

The rebuild is considered successful when:

```text
Application Running
        ✓

GitOps Operational
        ✓

Kubernetes Healthy
        ✓

Validation Successful
        ✓
```

---

# Phase 1 – Workstation Preparation

## Operating System

Verify:

```text
□ Windows 11 available
```

---

## Development Tools

Verify installation:

```text
□ Visual Studio Code

□ Git

□ Python

□ Docker Desktop

□ kubectl
```

---

## Docker Environment

Verify:

```text
□ Docker Desktop running

□ WSL2 backend operational
```

Validation:

```powershell
docker version
```

Result:

```text
□ Docker operational
```

---

## Kubernetes Tooling

Validation:

```powershell
kubectl version --client
```

Result:

```text
□ kubectl operational
```

---

# Phase 2 – Repository Preparation

## Clone Repository

Execute:

```powershell
git clone <repository-url>
```

Verify:

```text
□ Repository cloned
```

---

## Open Repository

Execute:

```powershell
code .
```

Verify:

```text
□ Repository accessible
```

---

## Repository Structure

Verify presence of:

```text
□ app.py

□ requirements.txt

□ Dockerfile

□ .github/workflows/ci.yml

□ k8s/

□ scripts/

□ docs/
```

---

# Phase 3 – Python Environment

## Virtual Environment

Verify:

```text
□ venv available
```

or create if required.

---

## Activate Environment

Execute:

```powershell
.\venv\Scripts\Activate.ps1
```

Verify:

```text
□ Environment active
```

---

## Install Dependencies

Execute:

```powershell
pip install -r requirements.txt
```

Verify:

```text
□ Dependencies installed
```

---

# Phase 4 – Local Application Validation

## Start Application

Execute:

```powershell
streamlit run app.py
```

Verify:

```text
□ Application starts

□ Browser accessible

□ Application functional
```

---

## Execute Tests

Execute:

```powershell
pytest
```

Verify:

```text
□ Tests pass
```

---

# Phase 5 – Container Validation

## Build Container Image

Execute:

```powershell
docker build -t m-devops-transformation .
```

Verify:

```text
□ Build successful
```

---

## Verify Image

Execute:

```powershell
docker images
```

Verify:

```text
□ Image present
```

---

## Run Container

Execute:

```powershell
docker run -p 8501:8501 m-devops-transformation
```

Verify:

```text
□ Container starts

□ Application accessible
```

---

# Phase 6 – CI/CD Verification

## Git Operations

Verify:

```powershell
git status
```

Result:

```text
□ Repository healthy
```

---

## Pipeline Definition

Verify:

```text
□ .github/workflows/ci.yml exists
```

---

## CI Components

Verify documented stages:

```text
□ Ruff

□ Bandit

□ pytest

□ Docker Build

□ GHCR Publication
```

---

# Phase 7 – Kubernetes Bootstrap

## Verify Cluster

Execute:

```powershell
kubectl cluster-info
```

Verify:

```text
□ Cluster reachable
```

---

## Verify Nodes

Execute:

```powershell
kubectl get nodes
```

Verify:

```text
□ Nodes available
```

---

## Cluster Validation

Execute:

```powershell
.\scripts\verify_cluster.ps1
```

Verify:

```text
□ Cluster validation successful
```

---

# Phase 8 – ArgoCD Bootstrap

## Verify Namespace

Execute:

```powershell
kubectl get namespaces
```

Verify:

```text
□ argocd namespace exists
```

---

## Verify ArgoCD Pods

Execute:

```powershell
kubectl get pods -n argocd
```

Verify:

```text
□ ArgoCD components running
```

---

## Verify ApplicationSet

Execute:

```powershell
kubectl get crd
```

Verify:

```text
□ ApplicationSet CRD present
```

---

## Apply Root Application

Execute:

```powershell
kubectl apply -f k8s/apps/root-app.yml
```

Verify:

```text
□ Root Application created
```

---

# Phase 9 – GitOps Verification

Verify:

```text
□ GitOps synchronization active

□ Desired state applied

□ No critical synchronization errors
```

Target status:

```text
□ Healthy

□ Synced
```

---

# Phase 10 – Runtime Validation

## Verify Deployments

Execute:

```powershell
kubectl get deployments
```

Verify:

```text
□ Deployments available
```

---

## Verify Pods

Execute:

```powershell
kubectl get pods
```

Verify:

```text
□ Pods healthy
```

---

## Verify Services

Execute:

```powershell
kubectl get services
```

Verify:

```text
□ Services available
```

---

# Phase 11 – Platform Validation

## Cluster Validation

Execute:

```powershell
.\scripts\verify_cluster.ps1
```

Result:

```text
□ PASS
```

---

## GitOps Validation

Execute:

```powershell
.\scripts\verify_gitops.ps1
```

Result:

```text
□ PASS
```

---

## Pod Validation

Execute:

```powershell
.\scripts\verify_pods.ps1
```

Result:

```text
□ PASS
```

---

## Full Validation

Execute:

```powershell
.\scripts\verify_all.ps1
```

Expected result:

```text
[PASS] All validation checks completed successfully.
```

Verify:

```text
□ Full validation successful
```

---

# Final Acceptance

The platform rebuild is accepted when:

```text
□ Application operational

□ Docker operational

□ CI/CD operational

□ GHCR operational

□ Kubernetes operational

□ ArgoCD operational

□ GitOps operational

□ Validation successful
```

---

# Rebuild Verification Notes

The following platform areas were reconstructed from validated project artifacts and should be explicitly verified during future rebuild exercises:

```text
□ root-app.yml implementation details

□ ApplicationSet usage details

□ Kubernetes manifest hierarchy

□ GitOps bootstrap sequence
```

Any findings should be incorporated into future Playbook revisions.

---

# Completion Statement

When all checklist items are completed successfully, the M-DevOps platform has been rebuilt from a known-good baseline and is considered operational.
