[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("Status", "Promote", "Deploy")]
    [string]$Mode,

    [switch]$CreatePullRequest
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Repository = "hepi66/M_DevOps_Transformation"
$ImageRepository = "ghcr.io/hepi66/m_devops_transformation"
$PackageEndpoint = "/user/packages/container/m_devops_transformation/versions?per_page=100"
$ManifestPath = "k8s/workloads/m-devops-dashboard/deployment.yaml"
$Application = "m-devops-dashboard"
$ArgoNamespace = "argocd"
$WorkloadNamespace = "m-devops-dashboard"
$Deployment = "m-devops-dashboard"
$ShaPattern = "^[0-9a-f]{40}$"
$RepositoryRoot = Split-Path -Parent $PSScriptRoot

function Write-Section {
    param([string]$Title)

    Write-Host ""
    Write-Host "=== $Title ===" -ForegroundColor Cyan
}

function Require-Command {
    param([string]$Name)

    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command '$Name' is not available on PATH."
    }
}

function Invoke-Native {
    param(
        [string]$Command,
        [string[]]$Arguments,
        [switch]$AllowFailure
    )

    if (-not (Get-Command $Command -ErrorAction SilentlyContinue)) {
        throw "Required command '$Command' is not available on PATH."
    }

    # Windows PowerShell surfaces native stderr records through its error
    # stream. Git, gh, and kubectl may legitimately write informational output
    # there even when they succeed, so capture both streams without allowing
    # ErrorActionPreference=Stop to preempt the authoritative process exit code.
    $previousErrorActionPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = "Continue"
        $rawOutput = & $Command @Arguments 2>&1
        $exitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }
    $output = @($rawOutput | ForEach-Object {
        if ($_ -is [System.Management.Automation.ErrorRecord]) {
            $_.Exception.Message
        }
        else {
            $_
        }
    })
    if ($exitCode -ne 0 -and -not $AllowFailure) {
        $message = ($output | Out-String).Trim()
        throw "Command failed: $Command $($Arguments -join ' ')`n$message"
    }
    return $output
}

function Get-ObjectProperty {
    param(
        [AllowNull()]$Object,
        [string]$Name
    )

    if ($null -eq $Object) {
        return $null
    }
    $property = $Object.PSObject.Properties[$Name]
    if ($null -eq $property) {
        return $null
    }
    return $property.Value
}

function Assert-FullSha {
    param(
        [string]$Sha,
        [string]$Description
    )

    if ($Sha -cnotmatch $ShaPattern) {
        throw "$Description must be a full 40-character lowercase hexadecimal Git SHA. Received: '$Sha'."
    }
}

function Assert-GitHubAuthentication {
    Invoke-Native -Command "gh" -Arguments @("auth", "status") | Out-Null
}

function Assert-KubernetesAccess {
    Invoke-Native -Command "kubectl" -Arguments @("cluster-info") | Out-Null
}

function Get-WorkingTreeState {
    $lines = @(Invoke-Native -Command "git" -Arguments @("status", "--porcelain"))
    return [pscustomobject]@{
        Clean = $lines.Count -eq 0
        Lines = $lines
    }
}

function Get-RepositoryState {
    $branch = ((Invoke-Native -Command "git" -Arguments @("branch", "--show-current")) | Out-String).Trim()
    $localMain = ((Invoke-Native -Command "git" -Arguments @("rev-parse", "--verify", "main") -AllowFailure) | Out-String).Trim()
    # ls-remote reads the authoritative remote branch without changing the
    # local remote-tracking reference, keeping Status mode read-only.
    $remoteLine = ((Invoke-Native -Command "git" -Arguments @(
        "ls-remote", "--exit-code", "origin", "refs/heads/main"
    )) | Out-String).Trim()
    $originMain = ($remoteLine -split "\s+")[0]
    Assert-FullSha -Sha $originMain -Description "origin/main"
    if ($localMain -and $localMain -notmatch "fatal:") {
        Assert-FullSha -Sha $localMain -Description "local main"
    }
    else {
        $localMain = $null
    }

    return [pscustomobject]@{
        Branch = $branch
        WorkingTree = Get-WorkingTreeState
        LocalMain = $localMain
        OriginMain = $originMain
    }
}

function Get-SuccessfulWorkflowRun {
    param([string]$CommitSha)

    $json = (Invoke-Native -Command "gh" -Arguments @(
        "run", "list",
        "--repo", $Repository,
        "--workflow", "CI Pipeline",
        "--branch", "main",
        "--status", "success",
        "--limit", "50",
        "--json", "databaseId,headSha,status,conclusion,url,createdAt"
    )) | Out-String
    $decodedRuns = $json | ConvertFrom-Json
    $runs = [object[]]$decodedRuns
    $run = $runs | Where-Object { $_.headSha -eq $CommitSha } | Select-Object -First 1
    if ($null -eq $run) {
        throw "No successful CI Pipeline run on main was found for commit $CommitSha. CI success is required before artifact promotion."
    }
    return $run
}

function Get-LatestSuccessfulWorkflowRun {
    $json = (Invoke-Native -Command "gh" -Arguments @(
        "run", "list",
        "--repo", $Repository,
        "--workflow", "CI Pipeline",
        "--branch", "main",
        "--status", "success",
        "--limit", "1",
        "--json", "databaseId,headSha,status,conclusion,url,createdAt"
    )) | Out-String
    $decodedRuns = $json | ConvertFrom-Json
    $runs = [object[]]$decodedRuns
    $run = $runs | Select-Object -First 1
    if ($null -eq $run) {
        throw "No successful CI Pipeline run on main is currently available."
    }
    return $run
}

function Find-GhcrArtifact {
    param(
        [object[]]$Versions,
        [string]$CommitSha
    )

    Assert-FullSha -Sha $CommitSha -Description "GHCR image tag"
    $matches = @($Versions | Where-Object {
        $metadata = Get-ObjectProperty -Object $_ -Name "metadata"
        $container = Get-ObjectProperty -Object $metadata -Name "container"
        $tags = @(
            Get-ObjectProperty -Object $container -Name "tags" |
                Where-Object { $null -ne $_ }
        )
        @($tags | Where-Object { [string]$_ -ceq $CommitSha }).Count -gt 0
    })

    if ($matches.Count -eq 0) {
        throw "GHCR does not contain the required immutable image tag $CommitSha. GHCR publication is required before promotion or deployment."
    }
    if ($matches.Count -gt 1) {
        throw "GHCR returned multiple package versions for the exact immutable image tag $CommitSha. Refusing to guess which digest is authoritative."
    }
    $version = $matches[0]
    $digest = [string](Get-ObjectProperty -Object $version -Name "name")
    if ($digest -notmatch "^sha256:[0-9a-f]{64}$") {
        throw "GHCR returned an invalid or unavailable digest for tag $CommitSha."
    }
    return [pscustomobject]@{
        Image = "${ImageRepository}:$CommitSha"
        Tag = $CommitSha
        Digest = $digest
        VersionId = Get-ObjectProperty -Object $version -Name "id"
    }
}

function Get-GhcrArtifact {
    param([string]$CommitSha)

    Assert-FullSha -Sha $CommitSha -Description "GHCR image tag"
    $json = (Invoke-Native -Command "gh" -Arguments @(
        "api",
        "-H", "Accept: application/vnd.github+json",
        $PackageEndpoint
    )) | Out-String
    # Windows PowerShell returns the top-level JSON array as System.Object[].
    # Wrapping the conversion pipeline in @() creates a nested, single-element
    # array, so normalize the decoded value explicitly instead.
    $decodedVersions = $json | ConvertFrom-Json
    $versions = [object[]]$decodedVersions
    return Find-GhcrArtifact -Versions $versions -CommitSha $CommitSha
}

function Get-ImageFromManifestText {
    param([string]$Manifest)

    $match = [regex]::Match($Manifest, "(?m)^\s*image:\s*(\S+)\s*$")
    if (-not $match.Success) {
        throw "No container image reference was found in $ManifestPath."
    }
    $image = $match.Groups[1].Value
    if ($image -notmatch "^$([regex]::Escape($ImageRepository)):(?<sha>[0-9a-f]{40})$") {
        throw "The deployment image must use $ImageRepository with a full immutable Git SHA tag. Found: $image"
    }
    return [pscustomobject]@{
        Image = $image
        Sha = $Matches.sha
    }
}

function Get-LocalManifestImage {
    $manifest = [IO.File]::ReadAllText((Join-Path (Get-Location) $ManifestPath))
    return Get-ImageFromManifestText -Manifest $manifest
}

function Get-OriginManifestImage {
    $manifest = (Invoke-Native -Command "git" -Arguments @("show", "origin/main:$ManifestPath")) | Out-String
    return Get-ImageFromManifestText -Manifest $manifest
}

function Get-ArgoState {
    $json = (Invoke-Native -Command "kubectl" -Arguments @(
        "get", "application", $Application, "-n", $ArgoNamespace, "-o", "json"
    )) | Out-String
    $app = $json | ConvertFrom-Json
    return [pscustomobject]@{
        Sync = [string](Get-ObjectProperty -Object $app.status.sync -Name "status")
        Health = [string](Get-ObjectProperty -Object $app.status.health -Name "status")
        Revision = [string](Get-ObjectProperty -Object $app.status.sync -Name "revision")
        OperationPhase = [string](Get-ObjectProperty -Object $app.status.operationState -Name "phase")
    }
}

function Get-KubernetesState {
    $deploymentJson = (Invoke-Native -Command "kubectl" -Arguments @(
        "get", "deployment", $Deployment, "-n", $WorkloadNamespace, "-o", "json"
    )) | Out-String
    $workload = $deploymentJson | ConvertFrom-Json
    $container = @($workload.spec.template.spec.containers) | Where-Object { $_.name -eq "dashboard" } | Select-Object -First 1
    if ($null -eq $container) {
        throw "Dashboard container was not found in the Kubernetes Deployment."
    }

    $podsJson = (Invoke-Native -Command "kubectl" -Arguments @(
        "get", "pods", "-n", $WorkloadNamespace,
        "-l", "app.kubernetes.io/instance=m-devops-dashboard", "-o", "json"
    )) | Out-String
    $podList = $podsJson | ConvertFrom-Json
    $pod = @($podList.items) | Sort-Object { $_.metadata.creationTimestamp } -Descending | Select-Object -First 1

    $podName = $null
    $podPhase = $null
    $podReady = $null
    $runningImage = $null
    $runningDigest = $null
    if ($null -ne $pod) {
        $podName = [string]$pod.metadata.name
        $podPhase = [string]$pod.status.phase
        $statuses = @($pod.status.containerStatuses)
        $readyCount = @($statuses | Where-Object { $_.ready -eq $true }).Count
        $podReady = "$readyCount/$($statuses.Count)"
        $dashboardStatus = $statuses | Where-Object { $_.name -eq "dashboard" } | Select-Object -First 1
        if ($null -ne $dashboardStatus) {
            $runningImage = [string]$dashboardStatus.image
            $imageId = [string]$dashboardStatus.imageID
            $digestMatch = [regex]::Match($imageId, "sha256:[0-9a-f]{64}")
            if ($digestMatch.Success) {
                $runningDigest = $digestMatch.Value
            }
        }
    }

    return [pscustomobject]@{
        DesiredImage = [string]$container.image
        DesiredReplicas = [int](Get-ObjectProperty -Object $workload.spec -Name "replicas")
        ReadyReplicas = [int](Get-ObjectProperty -Object $workload.status -Name "readyReplicas")
        PodName = $podName
        PodPhase = $podPhase
        PodReady = $podReady
        RunningImage = $runningImage
        RunningDigest = $runningDigest
    }
}

function Get-Correlation {
    param(
        [string]$MainSha,
        $Artifact,
        $ManifestImage,
        $Argo,
        $Runtime
    )

    if (
        $null -eq $ManifestImage -or
        $null -eq $Runtime -or
        -not $Runtime.DesiredImage -or
        -not $Runtime.RunningImage
    ) {
        return "Unavailable"
    }

    $desiredDiffers = $Runtime.DesiredImage -ne $ManifestImage.Image
    $runningDiffers = $Runtime.RunningImage -ne $ManifestImage.Image
    $digestDiffers = (
        $null -ne $Artifact -and
        $Runtime.RunningDigest -and
        $Runtime.RunningDigest -ne $Artifact.Digest
    )
    if (
        $desiredDiffers -or
        $runningDiffers -or
        $digestDiffers -or
        ($null -ne $Argo -and $Argo.Sync -eq "OutOfSync")
    ) {
        return "Drift"
    }

    $revisionMatches = $null -ne $Argo -and $Argo.Revision -eq $MainSha
    $digestMatches = (
        $null -ne $Artifact -and
        $Runtime.RunningDigest -and
        $Runtime.RunningDigest -eq $Artifact.Digest
    )
    $allMatch = (
        $null -ne $Artifact -and
        $null -ne $Argo -and
        $revisionMatches -and
        $digestMatches -and
        $Argo.Sync -eq "Synced" -and
        $Argo.Health -eq "Healthy" -and
        $Runtime.ReadyReplicas -eq $Runtime.DesiredReplicas
    )
    if ($allMatch) {
        return "Complete"
    }
    return "Partial"
}

function Write-Comparison {
    param(
        [string]$MainSha,
        $CiRun,
        $CiArtifact,
        $OriginArtifact,
        $Artifact,
        $ManifestImage,
        $Argo,
        $Runtime
    )

    Write-Section "REPOSITORY"
    Write-Host "origin/main SHA        : $(if ($MainSha) { $MainSha } else { 'Unavailable' })"
    Write-Section "CI / ARTIFACT"
    if ($null -ne $CiRun) {
        Write-Host "Relevant CI SHA        : $($CiRun.headSha)"
        Write-Host "Successful CI run      : $($CiRun.databaseId) | $($CiRun.url)"
    }
    else {
        Write-Host "Relevant CI            : Unavailable"
    }
    if ($null -ne $CiArtifact) {
        Write-Host "GHCR for relevant CI   : $($CiArtifact.Tag) | $($CiArtifact.Digest)"
    }
    else {
        Write-Host "GHCR for relevant CI   : Unavailable / not found"
    }
    if ($null -ne $OriginArtifact) {
        Write-Host "GHCR for origin/main   : $($OriginArtifact.Tag) | $($OriginArtifact.Digest)"
    }
    else {
        Write-Host "GHCR for origin/main   : Unavailable / not found"
    }
    Write-Section "GITOPS DESIRED STATE"
    if ($null -ne $ManifestImage) {
        Write-Host "Manifest image         : $($ManifestImage.Image)"
        Write-Host "Manifest-selected SHA  : $($ManifestImage.Sha)"
    }
    else {
        Write-Host "Manifest image         : Unavailable"
    }
    if ($null -ne $Artifact) {
        Write-Host "Selected GHCR artifact : Verified"
        Write-Host "Selected digest        : $($Artifact.Digest)"
    }
    else {
        Write-Host "Selected GHCR artifact : Unavailable / not found"
    }
    if ($null -ne $Argo) {
        Write-Host "Argo Sync             : $($Argo.Sync)"
        Write-Host "Argo Health           : $($Argo.Health)"
        Write-Host "Observed Git revision : $($Argo.Revision)"
    }
    else {
        Write-Host "Argo CD           : Unavailable"
    }
    Write-Section "RUNTIME"
    if ($null -ne $Runtime) {
        Write-Host "Desired image     : $($Runtime.DesiredImage)"
        Write-Host "Running image     : $($Runtime.RunningImage)"
        Write-Host "Running digest    : $($Runtime.RunningDigest)"
        Write-Host "Replicas          : $($Runtime.ReadyReplicas)/$($Runtime.DesiredReplicas) ready"
        Write-Host "Pod               : $($Runtime.PodName) | $($Runtime.PodPhase) | ready $($Runtime.PodReady)"
    }
    else {
        Write-Host "Kubernetes        : Unavailable"
    }
    Write-Section "CORRELATION"
    Write-Host (Get-Correlation -MainSha $MainSha -Artifact $Artifact -ManifestImage $ManifestImage -Argo $Argo -Runtime $Runtime)
}

function Invoke-StatusMode {
    $repositoryState = $null
    $run = $null
    $ciArtifact = $null
    $originArtifact = $null
    $manifestImage = $null
    $manifestArtifact = $null
    $githubAvailable = $false

    try {
        $repositoryState = Get-RepositoryState
    }
    catch {
        Write-Warning "Repository evidence is unavailable: $($_.Exception.Message)"
    }
    try {
        $manifestImage = Get-LocalManifestImage
    }
    catch {
        Write-Warning "GitOps manifest evidence is unavailable: $($_.Exception.Message)"
    }
    try {
        Assert-GitHubAuthentication
        $githubAvailable = $true
    }
    catch {
        Write-Warning "GitHub evidence is unavailable: authentication failed or GitHub cannot be reached."
    }
    if ($githubAvailable) {
        try {
            $run = Get-LatestSuccessfulWorkflowRun
        }
        catch {
            Write-Warning "CI evidence is unavailable: $($_.Exception.Message)"
        }
        if ($null -ne $run) {
            try {
                $ciArtifact = Get-GhcrArtifact -CommitSha $run.headSha
            }
            catch {
                Write-Warning "GHCR has no verified artifact for the relevant CI commit $($run.headSha)."
            }
        }
        if ($null -ne $repositoryState) {
            try {
                $originArtifact = Get-GhcrArtifact -CommitSha $repositoryState.OriginMain
            }
            catch {
                Write-Warning "GHCR has no verified artifact for origin/main $($repositoryState.OriginMain)."
            }
        }
        if ($null -ne $manifestImage) {
            try {
                $manifestArtifact = Get-GhcrArtifact -CommitSha $manifestImage.Sha
            }
            catch {
                Write-Warning "GHCR has no verified artifact for the manifest-selected image $($manifestImage.Sha)."
            }
        }
    }

    Write-Section "LOCAL REPOSITORY"
    if ($null -ne $repositoryState) {
        Write-Host "Branch            : $($repositoryState.Branch)"
        Write-Host "Working tree      : $(if ($repositoryState.WorkingTree.Clean) { 'Clean' } else { 'Changes present' })"
        Write-Host "Local main        : $(if ($repositoryState.LocalMain) { $repositoryState.LocalMain } else { 'Unavailable' })"
    }
    else {
        Write-Host "Local repository  : Unavailable"
    }

    $argo = $null
    $runtime = $null
    $kubernetesAvailable = $false
    try {
        Assert-KubernetesAccess
        $kubernetesAvailable = $true
    }
    catch {
        Write-Warning "Kubernetes API is unavailable: cluster access could not be established."
    }
    if ($kubernetesAvailable) {
        try {
            $argo = Get-ArgoState
        }
        catch {
            Write-Warning "Argo CD evidence is unavailable: $($_.Exception.Message)"
        }
        try {
            $runtime = Get-KubernetesState
        }
        catch {
            Write-Warning "Kubernetes runtime evidence is unavailable: $($_.Exception.Message)"
        }
    }
    $mainSha = if ($null -ne $repositoryState) { $repositoryState.OriginMain } else { $null }
    Write-Comparison -MainSha $mainSha -CiRun $run -CiArtifact $ciArtifact -OriginArtifact $originArtifact -Artifact $manifestArtifact -ManifestImage $manifestImage -Argo $argo -Runtime $runtime
}

function Assert-OnlyManifestChanged {
    $changedFiles = @(
        Invoke-Native -Command "git" -Arguments @("diff", "--name-only") |
            ForEach-Object { ([string]$_).Trim() } |
            Where-Object { $_ }
    )
    if ($changedFiles.Count -ne 1 -or $changedFiles[0].Replace("\", "/") -ne $ManifestPath) {
        throw "Promotion must change only $ManifestPath. Changed files: $($changedFiles -join ', ')"
    }

    $diff = (Invoke-Native -Command "git" -Arguments @("diff", "--unified=0", "--", $ManifestPath)) | Out-String
    $contentChanges = @($diff -split "`r?`n" | Where-Object {
        ($_ -match "^[+-]") -and ($_ -notmatch "^(---|\+\+\+)")
    })
    if ($contentChanges.Count -ne 2 -or @($contentChanges | Where-Object {
        $_ -notmatch "^[+-]\s*image:\s*$([regex]::Escape($ImageRepository)):[0-9a-f]{40}\s*$"
    }).Count -ne 0) {
        throw "The manifest diff contains changes beyond the immutable image promotion."
    }
}

function Get-PythonCommand {
    $candidates = @(
        (Join-Path $RepositoryRoot "venv/Scripts/python.exe"),
        (Join-Path $RepositoryRoot ".venv/Scripts/python.exe"),
        "python",
        "py"
    )
    foreach ($candidate in $candidates) {
        if (Get-Command $candidate -ErrorAction SilentlyContinue) {
            return $candidate
        }
    }
    throw "Python is required to run the deployment contract tests."
}

function Invoke-PromoteMode {
    $initialState = Get-WorkingTreeState
    if (-not $initialState.Clean) {
        throw "Promote requires a clean working tree. Commit or restore existing changes before continuing."
    }
    Assert-GitHubAuthentication
    Invoke-Native -Command "git" -Arguments @("fetch", "origin", "main") | Out-Null
    $repositoryState = Get-RepositoryState
    $targetSha = $repositoryState.OriginMain
    $run = Get-SuccessfulWorkflowRun -CommitSha $targetSha
    $artifact = Get-GhcrArtifact -CommitSha $targetSha
    $currentImage = Get-OriginManifestImage

    if ($currentImage.Sha -eq $targetSha) {
        Write-Host "No promotion required. $ManifestPath already references ${ImageRepository}:$targetSha."
        return
    }

    $shortSha = $targetSha.Substring(0, 8)
    $branch = "feature/promote-dashboard-$shortSha"
    $existingBranch = ((Invoke-Native -Command "git" -Arguments @("branch", "--list", $branch)) | Out-String).Trim()
    if ($existingBranch) {
        throw "Promotion branch '$branch' already exists. Inspect it before retrying; the script will not overwrite it."
    }
    Invoke-Native -Command "git" -Arguments @("switch", "--create", $branch, "origin/main") | Out-Null

    $branchImage = Get-LocalManifestImage
    if ($branchImage.Image -ne $currentImage.Image) {
        throw "The promotion branch does not contain the expected origin/main image."
    }

    $fullPath = Join-Path (Get-Location) $ManifestPath
    $manifest = [IO.File]::ReadAllText($fullPath)
    $newImage = "${ImageRepository}:$targetSha"
    $updated = [regex]::Replace(
        $manifest,
        "(?m)^(\s*image:\s*)$([regex]::Escape($currentImage.Image))(\s*)$",
        "`${1}$newImage`${2}"
    )
    if ($updated -eq $manifest) {
        throw "The existing image line could not be updated safely."
    }
    [IO.File]::WriteAllText($fullPath, $updated, [Text.UTF8Encoding]::new($false))

    Assert-OnlyManifestChanged
    $rendered = Invoke-Native -Command "kubectl" -Arguments @("kustomize", "k8s/workloads/m-devops-dashboard")
    if (-not (($rendered | Out-String) -match [regex]::Escape($newImage))) {
        throw "Kustomize output does not contain the promoted image."
    }
    $python = Get-PythonCommand
    Invoke-Native -Command $python -Arguments @("-m", "pytest", "tests/test_deployment_contract.py") | ForEach-Object { Write-Host $_ }
    Invoke-Native -Command "git" -Arguments @("diff", "--check") | Out-Null

    Write-Section "PROMOTION PREPARED"
    Write-Host "CI run            : $($run.databaseId) | successful"
    Write-Host "GHCR digest       : $($artifact.Digest)"
    Write-Host "Old image         : $($currentImage.Image)"
    Write-Host "New image         : $newImage"
    Write-Host "Branch            : $branch"

    if ($CreatePullRequest) {
        $confirmation = Read-Host "Commit, push, and create the promotion PR? Type PROMOTE to continue"
        if ($confirmation -ne "PROMOTE") {
            Write-Host "Commit/push/PR creation cancelled. The validated local promotion remains uncommitted."
        }
        else {
            Invoke-Native -Command "git" -Arguments @("add", "--", $ManifestPath) | Out-Null
            Invoke-Native -Command "git" -Arguments @("commit", "-m", "chore: promote dashboard image $shortSha") | ForEach-Object { Write-Host $_ }
            Invoke-Native -Command "git" -Arguments @("push", "--set-upstream", "origin", $branch) | ForEach-Object { Write-Host $_ }
            Invoke-Native -Command "gh" -Arguments @(
                "pr", "create", "--repo", $Repository,
                "--title", "chore: promote dashboard image $shortSha",
                "--body", "Promote the M-DevOps Dashboard to immutable image tag ``$targetSha``. GHCR digest: ``$($artifact.Digest)``."
            ) | ForEach-Object { Write-Host $_ }
        }
    }

    Write-Host ""
    Write-Host "Next: Review CI -> Merge PR -> run .\scripts\dashboard_release.ps1 -Mode Deploy"
}

function Wait-ForArgoState {
    param(
        [int]$TimeoutSeconds = 180,
        [int]$IntervalSeconds = 5,
        [switch]$RequireHealthy
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    do {
        $state = Get-ArgoState
        Write-Host "Argo CD: Sync=$($state.Sync), Health=$($state.Health), Operation=$($state.OperationPhase)"
        $syncComplete = $state.Sync -eq "Synced" -and $state.OperationPhase -notin @("Running", "Terminating")
        $healthComplete = -not $RequireHealthy -or $state.Health -eq "Healthy"
        if ($syncComplete -and $healthComplete) {
            return $state
        }
        Start-Sleep -Seconds $IntervalSeconds
    } while ((Get-Date) -lt $deadline)
    throw "Argo CD did not reach Synced state within $TimeoutSeconds seconds."
}

function Invoke-DeployMode {
    Assert-GitHubAuthentication
    Assert-KubernetesAccess
    Invoke-Native -Command "git" -Arguments @("fetch", "origin", "main") | Out-Null
    $repositoryState = Get-RepositoryState
    $manifestImage = Get-OriginManifestImage
    $artifact = Get-GhcrArtifact -CommitSha $manifestImage.Sha
    $argoBefore = Get-ArgoState
    $runtimeBefore = Get-KubernetesState

    Write-Section "PRE-DEPLOYMENT COMPARISON"
    Write-Host "Git desired image  : $($manifestImage.Image)"
    Write-Host "Running image      : $($runtimeBefore.RunningImage)"
    Write-Host "Argo Sync / Health : $($argoBefore.Sync) / $($argoBefore.Health)"
    if ($manifestImage.Image -ne $runtimeBefore.RunningImage -and $argoBefore.Sync -eq "OutOfSync") {
        Write-Host "Expected promotion state: Git contains a newer desired image and Argo CD has detected the drift."
    }

    $alreadyCurrent = (
        $manifestImage.Image -eq $runtimeBefore.RunningImage -and
        $runtimeBefore.RunningDigest -eq $artifact.Digest -and
        $argoBefore.Sync -eq "Synced" -and
        $argoBefore.Health -eq "Healthy" -and
        $runtimeBefore.ReadyReplicas -eq $runtimeBefore.DesiredReplicas
    )
    if ($alreadyCurrent) {
        Write-Host "Deployment is already current and verified. No synchronization is required."
        Write-Comparison -MainSha $repositoryState.OriginMain -Artifact $artifact -ManifestImage $manifestImage -Argo $argoBefore -Runtime $runtimeBefore
        return
    }

    $confirmation = Read-Host "Synchronize Argo CD Application '$Application'? Type DEPLOY to continue"
    if ($confirmation -ne "DEPLOY") {
        Write-Host "Deployment cancelled. No Argo CD or Kubernetes state was changed."
        return
    }

    # Git desired state is not running state. This explicit operation preserves
    # manual approval while avoiding fragile shell-escaped JSON.
    $operation = @{ operation = @{ sync = @{} } }
    $patchJson = $operation | ConvertTo-Json -Compress -Depth 4
    Invoke-Native -Command "kubectl" -Arguments @(
        "patch", "application", $Application, "-n", $ArgoNamespace,
        "--type", "merge", "--patch", $patchJson
    ) | ForEach-Object { Write-Host $_ }

    $argoAfter = Wait-ForArgoState
    Invoke-Native -Command "kubectl" -Arguments @(
        "rollout", "status", "deployment/$Deployment", "-n", $WorkloadNamespace, "--timeout=180s"
    ) | ForEach-Object { Write-Host $_ }
    $argoAfter = Wait-ForArgoState -RequireHealthy
    $runtimeAfter = Get-KubernetesState

    Write-Section "DEPLOYMENT VERIFICATION"
    Write-Comparison -MainSha $repositoryState.OriginMain -Artifact $artifact -ManifestImage $manifestImage -Argo $argoAfter -Runtime $runtimeAfter
    $result = Get-Correlation -MainSha $repositoryState.OriginMain -Artifact $artifact -ManifestImage $manifestImage -Argo $argoAfter -Runtime $runtimeAfter
    if ($result -ne "Complete") {
        throw "Deployment verification result is $result. Review the independent Git, GHCR, Argo CD, and Kubernetes evidence above."
    }
    Write-Host "RESULT: VERIFIED" -ForegroundColor Green
    Write-Host ""
    Write-Host "Port-forward does not start the application. It only exposes the verified ClusterIP Service:"
    Write-Host "kubectl port-forward service/m-devops-dashboard 8501:8501 -n m-devops-dashboard"
    Write-Host "http://127.0.0.1:8501"
}

try {
    if (-not (Test-Path (Join-Path (Get-Location) $ManifestPath))) {
        throw "Run this helper from the repository root: $RepositoryRoot"
    }
    if ($Mode -ne "Status") {
        foreach ($command in @("git", "gh", "kubectl")) {
            Require-Command -Name $command
        }
    }
    switch ($Mode) {
        "Status" { Invoke-StatusMode }
        "Promote" { Invoke-PromoteMode }
        "Deploy" { Invoke-DeployMode }
    }
}
catch {
    Write-Error $_.Exception.Message
    exit 1
}
