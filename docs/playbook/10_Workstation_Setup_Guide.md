# Workstation Setup Guide

## Purpose

This guide describes how to prepare a new engineering workstation for working with the M-DevOps platform.

The objective is to create a consistent and reproducible development environment before interacting with the project repository, Docker, GitHub, Kubernetes, or ArgoCD.

This guide should be completed before any other rebuild procedure.

---

# Target Environment

Validated development environment:

| Component          | Version                      |
| ------------------ | ---------------------------- |
| Operating System   | Windows 11                   |
| IDE                | Visual Studio Code           |
| Terminal           | PowerShell                   |
| Python             | 3.14.x                       |
| Container Runtime  | Docker Desktop               |
| Git                | Current Stable Version       |
| Source Control     | GitHub                       |
| Container Registry | GHCR                         |
| GitOps             | ArgoCD                       |
| Kubernetes         | Local Kubernetes Environment |

---

# Prerequisites

Before starting, ensure:

* Local administrator permissions are available.
* Internet access is available.
* A GitHub account exists.
* Docker Desktop can be installed.
* Visual Studio Code can be installed.

---

# Install Git

## Purpose

Git provides version control and repository management.

## Verification

Open PowerShell:

```powershell
git --version
```

Expected result:

```text
git version <version>
```

---

# Install Visual Studio Code

## Purpose

Primary development environment.

## Verification

Open Visual Studio Code successfully.

Verify:

* Integrated terminal available
* Extensions can be installed

---

# Install Python

## Purpose

Application runtime.

## Verification

Open PowerShell:

```powershell
python --version
```

Expected result:

```text
Python 3.14.x
```

---

# Install Docker Desktop

## Purpose

Container build and runtime environment.

## Requirements

* WSL2 enabled
* Virtualization enabled

## Verification

Open PowerShell:

```powershell
docker version
```

Expected result:

Docker Client and Docker Server information displayed.

---

# Verify WSL

Open PowerShell:

```powershell
wsl --status
```

Expected result:

* WSL installed
* Default version: WSL2

---

# Configure Git

Verify Git identity:

```powershell
git config --global user.name
git config --global user.email
```

If not configured:

```powershell
git config --global user.name "<your-name>"
git config --global user.email "<your-email>"
```

---

# Verify GitHub Access

Verify:

* GitHub account exists
* Repository access is available
* Repository cloning is possible

---

# Create Workspace

Recommended location:

```text
D:\Projekte\
```

Example:

```text
D:\Projekte\M_DevOps_Transformation
```

The exact path may differ according to local preferences.

---

# Clone Repository

Example:

```powershell
git clone <repository-url>
```

Verification:

```powershell
cd M_DevOps_Transformation
git status
```

Expected result:

```text
On branch main
nothing to commit, working tree clean
```

---

# Create Python Virtual Environment

From repository root:

```powershell
python -m venv venv
```

Activate:

```powershell
.\venv\Scripts\Activate.ps1
```

Verification:

```powershell
python --version
```

Virtual environment should be active.

---

# Install Python Dependencies

From repository root:

```powershell
pip install -r requirements.txt
```

Verification:

```powershell
pip list
```

Dependencies should be installed successfully.

---

# Verify Local Application Start

Run:

```powershell
streamlit run app.py
```

Expected result:

* Application starts successfully
* Local browser window opens
* Application is accessible

---

# Workstation Validation Checklist

Before continuing to additional rebuild guides, verify:

* Git installed
* Visual Studio Code installed
* Python installed
* Docker Desktop installed
* WSL2 operational
* GitHub access working
* Repository cloned
* Virtual environment operational
* Dependencies installed
* Application starts locally

All items should be successful before continuing.

---

# Next Step

After completing this guide, continue with:

**Repository & Development Environment Guide**

This confirms that the workstation is capable of supporting all subsequent platform rebuild activities.
