Write-Host ""
Write-Host "========================================="
Write-Host " GitOps Validation"
Write-Host "========================================="
Write-Host ""

try {
    $app = kubectl get application root-app -n argocd -o json | ConvertFrom-Json
}
catch {
    Write-Host "[ERROR] Unable to retrieve Argo CD Application."
    exit 1
}

$sync = $app.status.sync.status
$health = $app.status.health.status

Write-Host "Application  : root-app"
Write-Host "Sync Status  : $sync"
Write-Host "Health Status: $health"
Write-Host ""

if ($sync -eq "Synced" -and $health -eq "Healthy") {
    Write-Host "[PASS] GitOps validation PASSED"
    exit 0
}
else {
    Write-Host "[FAIL] GitOps validation FAILED"
    exit 1
}