# ============================================================================
# File: verify_pods.ps1
# Description: Validates that all Argo CD pods are running and ready.
# Project: M_DevOps_Transformation
# ============================================================================

Write-Host ""
Write-Host "========================================="
Write-Host " Argo CD Pod Validation"
Write-Host "========================================="
Write-Host ""

try {
    $pods = kubectl get pods -n argocd -o json | ConvertFrom-Json
}
catch {
    Write-Host "[ERROR] Unable to retrieve Argo CD pods."
    exit 1
}

$failed = $false

foreach ($pod in $pods.items) {

    $name = $pod.metadata.name
    $phase = $pod.status.phase

    $readyContainers = 0
    $totalContainers = 0

    foreach ($container in $pod.status.containerStatuses) {
        $totalContainers++

        if ($container.ready) {
            $readyContainers++
        }
    }

    if ($phase -eq "Running" -and $readyContainers -eq $totalContainers) {

        Write-Host ("[PASS] {0} ({1}/{2})" -f $name, $readyContainers, $totalContainers)

    }
    else {

        Write-Host ("[FAIL] {0} - Status: {1} ({2}/{3})" -f $name, $phase, $readyContainers, $totalContainers)
        $failed = $true

    }
}

Write-Host ""

if ($failed) {
    Write-Host "[FAIL] Pod validation FAILED"
    exit 1
}
else {
    Write-Host "[PASS] All Argo CD pods are running."
    exit 0
}