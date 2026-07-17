# Daily Operations Guide

## Purpose

This guide describes the routine operational activities required to maintain the M-DevOps platform.

The objective is to provide a repeatable operational workflow that helps engineers monitor platform health, identify issues early, and maintain a stable delivery environment.

This guide focuses on normal day-to-day operations.

---

# Operations Philosophy

The platform follows a simple operational principle:

```text id="z2w7pk"
Observe
    ↓
Verify
    ↓
Act
```

The goal is to detect problems before they impact development or deployment activities.

---

# Daily Operations Goals

Daily operations aim to ensure:

```text id="s4r8qt"
Git Repository Healthy

CI/CD Operational

GHCR Available

GitOps Healthy

Kubernetes Healthy

Application Available
```

A healthy platform should require minimal intervention.

---

# Recommended Daily Workflow

The preferred daily workflow is:

```text id="w9m2fy"
Review Platform State
        ↓
Validate Core Components
        ↓
Review Recent Changes
        ↓
Investigate Anomalies
        ↓
Document Findings
```

---

# Step 1 – Review Repository Status

Verify local repository state:

```powershell id="n6t5ax"
git status
```

Expected result:

```text id="m8v2rk"
working tree clean
```

Review recent activity:

```powershell id="a3w9dp"
git log --oneline -10
```

Purpose:

* Understand recent changes
* Identify potentially risky modifications
* Maintain situational awareness

---

# Step 2 – Review CI/CD Status

Review the most recent GitHub Actions runs.

Verify:

```text id="q7f4ys"
Latest workflow successful

No repeated failures

No blocked builds
```

Primary areas of interest:

```text id="x4n8kj"
Linting

Security Checks

Tests

Container Build

Image Publication
```

A failing pipeline should be investigated promptly.

---

# Step 3 – Verify Container Artifact Availability

Confirm deployment artifacts exist in GHCR.

Verify:

```text id="b5t9wv"
Expected image available

Latest image published

No publication failures
```

The deployment chain depends on artifact availability.

---

# Step 4 – Verify Kubernetes Health

Execute:

```powershell id="v2q8rn"
kubectl get nodes
```

Verify:

```text id="z8m6ku"
Nodes Ready
```

Then:

```powershell id="g4w1ph"
kubectl get pods --all-namespaces
```

Review:

* Failed Pods
* Pending Pods
* Restart loops

Unexpected workload behavior should be investigated.

---

# Step 5 – Verify GitOps Health

Review ArgoCD status.

Desired state:

```text id="k3m7ty"
Healthy

Synced
```

Investigate:

```text id="h8w4qn"
OutOfSync

Degraded

Unknown
```

GitOps health directly impacts deployment reliability.

---

# Step 6 – Execute Platform Validation

Preferred validation command:

```powershell id="c9v5dp"
.\scripts\verify_all.ps1
```

Expected result:

```text id="s7j4my"
[PASS] All validation checks completed successfully.
```

This provides the operational health baseline.

---

# Daily Health Indicators

The platform should exhibit:

```text id="p4t9kb"
No failing Pods

No failing workflows

No synchronization issues

No validation failures
```

Any deviation should be recorded and investigated.

---

# Reviewing Recent Changes

Before troubleshooting:

Review:

```text id="f8v3xq"
Recent commits

Recent deployments

Recent configuration changes
```

Many operational issues are linked to recent modifications.

---

# Operational Documentation

Record notable findings:

Examples:

```text id="w1m6yn"
Deployment issue discovered

Validation failure detected

Configuration corrected

Recovery action performed
```

Documenting operational events improves future troubleshooting.

---

# When to Escalate Investigation

Immediate investigation is recommended when:

```text id="t5q8ka"
Validation fails

GitOps unhealthy

Pods repeatedly restarting

CI pipeline repeatedly failing

Application unavailable
```

These conditions indicate potential platform instability.

---

# Daily Operations Checklist

```text id="q9w2ru"
□ Repository healthy

□ CI/CD healthy

□ GHCR healthy

□ Kubernetes healthy

□ GitOps healthy

□ Validation successful

□ Application available
```

A completed checklist indicates a healthy platform state.

---

# Success Criteria

This guide is complete when the engineer understands:

* Daily operational responsibilities
* Core health indicators
* Validation workflow
* Investigation triggers
* Routine monitoring activities

The engineer should be capable of performing a standard platform health review confidently and consistently.
---

# Next Recommended Reading

Continue with:

- [Validation and Health Checks](31_Validation_and_Health_Checks.md)

---

# Related Documents

- [Validation and Health Checks](31_Validation_and_Health_Checks.md)
- [ArgoCD Operations Guide](32_ArgoCD_Operations_Guide.md)
- [Kubernetes Operations Guide](33_Kubernetes_Operations_Guide.md)

---

Return to:

- [Engineering Playbook](README.md)
- [Engineering Documentation Portal](../README.md)
