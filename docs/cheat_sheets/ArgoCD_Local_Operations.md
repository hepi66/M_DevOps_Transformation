---
title: "ArgoCD Local Operations"
type: "Cheat Sheet"
status: "Active"
version: "1.0"
owner: "Engineering"
last_updated: "2026-07-07"
related_epic: "E03"
---

# ArgoCD Local Operations

## Purpose

This cheat sheet provides the most frequently used commands for operating ArgoCD in the local development environment.

It is intended as a daily engineering reference.

---

# Verify Cluster

Verify cluster connectivity:

```powershell
kubectl get nodes
```

Verify namespaces:

```powershell
kubectl get namespaces
```

---

# Verify ArgoCD Installation

Verify namespace:

```powershell
kubectl get namespace argocd
```

Verify pods:

```powershell
kubectl get pods -n argocd
```

Verify services:

```powershell
kubectl get svc -n argocd
```

Verify deployments:

```powershell
kubectl get deployments -n argocd
```

---

# Retrieve Initial Admin Password

Retrieve the initial ArgoCD admin password:

```powershell
kubectl -n argocd get secret argocd-initial-admin-secret `
-o jsonpath="{.data.password}" `
| %{[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($_))}
```

---

# Port Forward ArgoCD UI

Expose the ArgoCD server locally:

```powershell
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

Open:

```text
https://localhost:8080
```

Default user:

```text
admin
```

---

# Verify Applications

List applications:

```powershell
kubectl get applications -A
```

Describe application:

```powershell
kubectl describe application <application-name> -n argocd
```

---

# Verify Synchronization

Check application sync status:

```powershell
kubectl get applications -n argocd
```

Expected states:

```text
SYNCED
HEALTHY
```

---

# Verify Resources

Deployments:

```powershell
kubectl get deployments -A
```

Pods:

```powershell
kubectl get pods -A
```

Services:

```powershell
kubectl get svc -A
```

---

# Validation Scripts

Cluster validation:

```powershell
.\scripts\verify_cluster.ps1
```

Platform validation:

```powershell
.\scripts\verify_platform.ps1
```

GitOps validation:

```powershell
.\scripts\verify_gitops.ps1
```

Application validation:

```powershell
.\scripts\verify_applications.ps1
```

Complete validation:

```powershell
.\scripts\verify_all.ps1
```

---

# Troubleshooting

## ArgoCD Pods Not Running

```powershell
kubectl get pods -n argocd
kubectl describe pod <pod-name> -n argocd
kubectl logs <pod-name> -n argocd
```

---

## Application Not Syncing

Verify:

- repository URL
- repository accessibility
- application manifest
- target namespace

Useful command:

```powershell
kubectl describe application <application-name> -n argocd
```

---

## Resource Not Deployed

Verify:

```powershell
kubectl get events -A
```

Check:

```powershell
kubectl describe deployment <deployment-name>
```

---

# Engineering Principle

When troubleshooting:

1. Validate Cluster
2. Validate Platform
3. Validate GitOps
4. Validate Applications

Never skip validation layers.

Always resolve lower-level failures before investigating higher-level components.