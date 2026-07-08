# ============================================================================
# File: verify_cluster.ps1
# Description: Validates Kubernetes cluster connectivity and required Argo CD resources.
# Project: M_DevOps_Transformation
# ============================================================================

Write-Host ""
Write-Host "========================================="
Write-Host " Cluster Validation"
Write-Host "========================================="
Write-Host ""

# Check Kubernetes cluster connectivity
try {
    kubectl cluster-info | Out-Null
    Write-Host "[PASS] Kubernetes cluster is reachable."
}
catch {
    Write-Host "[FAIL] Kubernetes cluster is not reachable."
    exit 1
}

# Check Argo CD namespace
try {
    kubectl get namespace argocd | Out-Null
    Write-Host "[PASS] Namespace 'argocd' exists."
}
catch {
    Write-Host "[FAIL] Namespace 'argocd' does not exist."
    exit 1
}

# Check ApplicationSet CRD
try {
    kubectl get crd applicationsets.argoproj.io | Out-Null
    Write-Host "[PASS] ApplicationSet CRD is installed."
}
catch {
    Write-Host "[FAIL] ApplicationSet CRD is missing."
    exit 1
}

Write-Host ""
Write-Host "[PASS] Cluster validation PASSED"

exit 0