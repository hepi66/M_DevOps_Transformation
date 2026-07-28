from dashboard.lifecycle import (
    aggregate_pipeline_run,
    normalize_argocd_provider,
    normalize_ghcr_provider,
    normalize_github_provider,
    normalize_kubernetes_provider,
)

COMMIT_SHA = "9715faa3d0fc7c7a545ffaec5817adbac0592e91"


def _complete_snapshot() -> dict:
    return {
        "state": "Healthy",
        "repository": "hepi66/M_DevOps_Transformation",
        "repository_url": "https://github.com/hepi66/M_DevOps_Transformation",
        "branch": "main",
        "github_actions": {
            "availability": "available",
            "workflow": {
                "databaseId": 85,
                "number": 85,
                "name": "CI Pipeline",
                "status": "completed",
                "conclusion": "success",
                "headBranch": "main",
                "headSha": COMMIT_SHA,
                "createdAt": "2026-07-26T10:50:00Z",
                "startedAt": "2026-07-26T10:50:05Z",
                "updatedAt": "2026-07-26T10:52:30Z",
            },
            "jobs": [
                {
                    "name": "build",
                    "status": "completed",
                    "conclusion": "success",
                    "steps": [
                        {
                            "name": "Build and push",
                            "status": "completed",
                            "conclusion": "success",
                            "startedAt": "2026-07-26T10:51:00Z",
                            "completedAt": "2026-07-26T10:52:20Z",
                        }
                    ],
                }
            ],
        },
        "docker_build": {
            "availability": "available",
            "job": {
                "name": "build",
                "status": "completed",
                "conclusion": "success",
            },
            "step": {
                "name": "Build and push",
                "status": "completed",
                "conclusion": "success",
                "completedAt": "2026-07-26T10:52:20Z",
            },
        },
        "ghcr": {
            "availability": "available",
            "package_name": "m_devops_transformation",
            "image_name": "ghcr.io/hepi66/m_devops_transformation",
            "tags": ["latest", COMMIT_SHA],
            "latest_tag": "latest",
            "digest": "sha256:abc123",
            "published_at": "2026-07-26T10:52:31Z",
        },
        "argocd": {
            "availability": "available",
            "application": "m-devops-dashboard",
            "revision": COMMIT_SHA,
            "namespace": "m-devops-dashboard",
            "sync_status": "Synced",
            "health_status": "Healthy",
            "observed_at": "2026-07-26T10:53:00Z",
        },
        "kubernetes": {
            "availability": "available",
            "namespace": "m-devops-dashboard",
            "deployment": "m-devops-dashboard",
            "revision": COMMIT_SHA,
            "image_tag": COMMIT_SHA,
            "desired_replicas": 1,
            "available_replicas": 1,
            "pods": [
                {
                    "name": "m-devops-dashboard-example",
                    "phase": "Running",
                    "ready": True,
                    "restart_count": 0,
                    "image_digest": "sha256:abc123",
                }
            ],
        },
        "refreshed_at": "2026-07-26T10:53:05Z",
    }


def test_provider_normalization_preserves_identifiers_and_hierarchy():
    snapshot = _complete_snapshot()

    github = normalize_github_provider(snapshot)
    ghcr = normalize_ghcr_provider(snapshot)
    argocd = normalize_argocd_provider(snapshot)
    kubernetes = normalize_kubernetes_provider(snapshot)

    assert github.commit_sha == COMMIT_SHA
    assert github.workflow_run_id == "85"
    assert github.jobs[0].steps[0].name == "Build and push"
    assert ghcr.tags == ("latest", COMMIT_SHA)
    assert argocd.observed_revision == COMMIT_SHA
    assert kubernetes.pods[0].ready is True


def test_pipeline_run_correlates_complete_lifecycle_by_commit_sha():
    pipeline_run = aggregate_pipeline_run(_complete_snapshot())

    assert pipeline_run.correlation_status == "correlated"
    assert pipeline_run.image_tag == COMMIT_SHA
    assert pipeline_run.image_digest == "sha256:abc123"
    assert pipeline_run.deployment_revision == COMMIT_SHA
    assert pipeline_run.deployment_namespace == "m-devops-dashboard"
    assert pipeline_run.pod_information[0].phase == "Running"
    assert pipeline_run.refresh_status == "success"
    assert pipeline_run.duration_seconds == 145


def test_pipeline_stage_mapping_is_deterministic():
    pipeline_run = aggregate_pipeline_run(_complete_snapshot())

    assert tuple(stage.identifier for stage in pipeline_run.stages) == (
        "code",
        "github",
        "ci",
        "build",
        "ghcr",
        "argocd",
        "kubernetes",
    )
    assert pipeline_run.stage("ci").status == "Success"
    assert pipeline_run.stage("ghcr").status == "Image published"
    assert pipeline_run.stage("argocd").status == "Completed"
    assert pipeline_run.stage("kubernetes").status == "Completed"


def test_unknown_correlation_does_not_guess_deployment_identity():
    snapshot = _complete_snapshot()
    snapshot["ghcr"]["tags"] = ["latest"]
    snapshot["argocd"]["revision"] = "different-revision"
    snapshot["kubernetes"]["revision"] = "another-revision"
    snapshot["kubernetes"]["image_tag"] = "different-image"

    pipeline_run = aggregate_pipeline_run(snapshot)

    assert pipeline_run.correlation_status == "unknown"
    assert pipeline_run.image_tag is None
    assert pipeline_run.image_digest is None
    assert pipeline_run.deployment_revision is None
    assert pipeline_run.deployment_namespace is None
    assert pipeline_run.pod_information == ()


def test_missing_providers_produce_stable_unknown_fallback():
    pipeline_run = aggregate_pipeline_run({})

    assert pipeline_run.commit_sha is None
    assert pipeline_run.workflow_run_id is None
    assert pipeline_run.refresh_status == "unavailable"
    assert pipeline_run.correlation_status == "unknown"
    assert pipeline_run.stage("argocd").source_classification == "LIVE"
    assert pipeline_run.stage("kubernetes").source_classification == "LIVE"
    assert all(stage.status == "Unknown" for stage in pipeline_run.stages)
