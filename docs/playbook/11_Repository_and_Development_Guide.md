# Repository and Development Environment Guide

## Purpose

This guide explains how to prepare the local project environment after the workstation has been configured.

The objective is to establish a consistent development environment that supports application development, testing, validation, and future platform operations.

This guide assumes that the Workstation Setup Guide has been completed successfully.

---

# Prerequisites

Before proceeding, verify:

* Workstation Setup Guide completed
* Repository cloned successfully
* Git operational
* Python installed
* Docker Desktop operational
* Visual Studio Code installed

---

# Repository Structure Overview

The repository contains several major areas.

```text id="tbgyds"
Project Root
│
├── Application Source Code
├── Tests
├── CI/CD Configuration
├── Docker Configuration
├── Kubernetes Configuration
├── Documentation
└── Validation Scripts
```

Each area serves a specific role within the platform lifecycle.

---

# Application Layer

Primary files:

```text id="2s4n4l"
app.py
requirements.txt
```

Responsibilities:

* Application logic
* Dependency definitions
* Local execution

This is the primary area for feature development.

---

# Testing Layer

Primary location:

```text id="03mr83"
tests/
```

Responsibilities:

* Automated verification
* Regression prevention
* CI/CD quality validation

Changes to application behavior should be accompanied by appropriate tests whenever possible.

---

# Documentation Layer

Primary location:

```text id="7lf7a6"
docs/
```

Responsibilities:

* Knowledge transfer
* Engineering standards
* Operational guidance
* Playbook maintenance

Documentation should evolve together with the platform.

---

# Validation Layer

Primary location:

```text id="f8uy1y"
scripts/
```

Current validation scripts include:

```text id="s0sd1z"
verify_cluster.ps1
verify_gitops.ps1
verify_pods.ps1
verify_all.ps1
```

These scripts provide the operational definition of platform health.

---

# Open Project in Visual Studio Code

From the repository root:

```powershell id="yj6vjj"
code .
```

Verify:

* Workspace loads successfully
* Files are visible
* Integrated terminal is operational

---

# Activate Virtual Environment

From repository root:

```powershell id="5vpxi3"
.\venv\Scripts\Activate.ps1
```

Verification:

```powershell id="vfqaf9"
python --version
```

The virtual environment should be active.

---

# Verify Installed Dependencies

Run:

```powershell id="if4cv8"
pip list
```

Verify expected dependencies are available.

If dependencies are missing:

```powershell id="6npt4g"
pip install -r requirements.txt
```

---

# Local Application Execution

Start the application:

```powershell id="vjvr7v"
streamlit run app.py
```

Verify:

* Application starts successfully
* Browser opens
* Application responds correctly

This confirms the local development environment is functional.

---

# Local Testing

Execute automated tests:

```powershell id="vlxg1v"
pytest
```

Expected result:

```text id="2b5m8k"
All tests pass.
```

Failures should be resolved before creating commits.

---

# Git Workflow Verification

Check repository status:

```powershell id="7vk4px"
git status
```

Expected result:

```text id="iq4s7x"
working tree clean
```

Review commit history:

```powershell id="rwjlwm"
git log --oneline -10
```

This confirms repository connectivity and local history availability.

---

# Development Workflow

The preferred engineering workflow is:

```text id="d4l7wo"
Create Change
    ↓
Run Application
    ↓
Execute Tests
    ↓
Review Changes
    ↓
Commit
    ↓
Push
```

Small, validated changes are preferred over large, complex modifications.

---

# Engineering Expectations

Before pushing changes:

Verify:

* Application starts
* Tests pass
* No unintended file changes exist
* Documentation is updated when necessary

The objective is to keep the repository continuously deployable.

---

# Common Local Validation Commands

Application:

```powershell id="kzuhso"
streamlit run app.py
```

Tests:

```powershell id="x3w5cc"
pytest
```

Git Status:

```powershell id="mq9f1l"
git status
```

Dependency Installation:

```powershell id="0bkv2j"
pip install -r requirements.txt
```

Virtual Environment Activation:

```powershell id="6j1yo9"
.\venv\Scripts\Activate.ps1
```

---

# Success Criteria

This guide is considered complete when:

* Repository is accessible
* Virtual environment functions correctly
* Dependencies are installed
* Application starts successfully
* Tests execute successfully
* Git operations work correctly

The engineer is now prepared to contribute changes to the platform.

---

# Next Step

Continue with:

**Container Build and Validation Guide**

This introduces the containerization layer that transforms application code into a deployable artifact.
