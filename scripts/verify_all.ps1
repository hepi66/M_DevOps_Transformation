# ============================================================================
# File: verify_all.ps1
# Description: Executes all verification scripts for the GitOps environment.
# Project: M_DevOps_Transformation
# ============================================================================

Write-Host ""
Write-Host "========================================="
Write-Host " GitOps Environment Validation"
Write-Host "========================================="
Write-Host ""

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

$checks = @(
    "verify_cluster.ps1",
    "verify_pods.ps1",
    "verify_gitops.ps1"
)

foreach ($check in $checks) {

    Write-Host ""
    Write-Host "-------------------------------------------------"
    Write-Host "Running $check"
    Write-Host "-------------------------------------------------"

    & "$scriptRoot\$check"

    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "[FAIL] Validation stopped."
        exit 1
    }
}

Write-Host ""
Write-Host "========================================="
Write-Host "[PASS] All validation checks completed successfully."
Write-Host "========================================="

exit 0