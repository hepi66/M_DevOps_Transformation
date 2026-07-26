# ============================================================================
# File: verify_dashboard.ps1
# Description: Validates the GitOps-managed M-DevOps Dashboard workload.
# Project: M_DevOps_Transformation
# ============================================================================

$namespace = "m-devops-dashboard"
$application = "m-devops-dashboard"
$deployment = "m-devops-dashboard"
$service = "m-devops-dashboard"

Write-Host ""
Write-Host "========================================="
Write-Host " Dashboard Runtime Validation"
Write-Host "========================================="
Write-Host ""

try {
    $appJson = kubectl get application $application -n argocd -o json
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to retrieve the Argo CD Application."
    }
    $app = $appJson | ConvertFrom-Json

    $workloadJson = kubectl get deployment $deployment -n $namespace -o json
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to retrieve the dashboard Deployment."
    }
    $workload = $workloadJson | ConvertFrom-Json

    kubectl get service $service -n $namespace | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to retrieve the dashboard Service."
    }
}
catch {
    Write-Host "[FAIL] Dashboard GitOps resources are unavailable."
    exit 1
}

$sync = $app.status.sync.status
$health = $app.status.health.status
$available = $workload.status.availableReplicas

Write-Host "Application         : $application"
Write-Host "Sync Status         : $sync"
Write-Host "Health Status       : $health"
Write-Host "Available Replicas  : $available"
Write-Host "Service             : $service"
Write-Host ""

if (
    $sync -eq "Synced" -and
    $health -eq "Healthy" -and
    $available -ge 1
) {
    Write-Host "[PASS] Dashboard runtime validation PASSED"
    exit 0
}

Write-Host "[FAIL] Dashboard runtime validation FAILED"
exit 1
