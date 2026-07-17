# Project Baseline

## Purpose

This document describes the current functional baseline of the **M_DevOps_Transformation** project.

It provides a high-level overview of the implemented prototype, technology stack, infrastructure, and engineering dependencies at the current stage of the project.

---

# Application Overview

The project currently consists of a prototype implemented as an interactive **Streamlit** dashboard (`app.py`).

Its primary purpose is to visualize the progress of the DevOps transformation across multiple Epics.

Current functionality includes:

- Epic progress visualization
- Interactive status buttons
- Dynamic UI updates
- Custom CSS styling
- Local and containerized execution

The prototype serves as the reference application for all subsequent DevOps engineering activities.

---

# Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.14.5 |
| Framework | Streamlit |
| Containerization | Docker |
| CI/CD | GitHub Actions |
| Registry | GitHub Container Registry (GHCR) |

---

# Local Development

## Python

```bash
.\venv\Scripts\activate
streamlit run app.py
```

Application URL:

```
http://localhost:8501
```

---

## Docker

```bash
docker build -t m-devops-transformation .
docker run -p 8501:8501 m-devops-transformation
```

Application URL:

```
http://localhost:8501
```

---

# Engineering Baseline

The repository currently provides:

- Local Python development environment
- Docker-based execution
- Automated CI pipeline
- Automated quality gates
- Automated security scanning
- Automated testing
- Automated container image creation
- Automated publishing to GitHub Container Registry (GHCR)

The project is prepared for GitOps-based deployment introduced in Epic E03.

---

# Infrastructure Requirements

- Hardware virtualization enabled (SVM Mode)
- WSL updated and operational
- Docker Desktop configured
- GitHub Actions enabled
- GitHub Container Registry available

---

# Repository Structure

Engineering documentation is maintained within the Engineering Knowledge Base (EKB).

Important directories include:

```
docs/
├── handbook/
├── reports/
├── standards/
├── cheat_sheets/
├── prompts/
├── templates/
├── decisions/
└── archive/
```

---

# Engineering References

Authoritative engineering history is maintained in:

- E00 Transition Report
- E01 Transition Report
- E02 Transition Report

Engineering standards are maintained separately within the Engineering Knowledge Base.

---

# Status

Current project maturity:

- Epic E00 ✅
- Epic E01 ✅
- Epic E02 ✅

Next engineering objective:

**Epic E03 — GitOps & ArgoCD**