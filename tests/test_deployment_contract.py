from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
WORKLOAD_ROOT = (
    REPOSITORY_ROOT / "k8s" / "workloads" / "m-devops-dashboard"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_docker_runs_dashboard_on_expected_interface_and_port():
    dockerfile = _read(REPOSITORY_ROOT / "Dockerfile")

    assert "EXPOSE 8501" in dockerfile
    assert '"dashboard_app.py"' in dockerfile
    assert '"--server.address=0.0.0.0"' in dockerfile
    assert '"--server.port=8501"' in dockerfile
    assert '"--server.headless=true"' in dockerfile
    assert '"app.py"' not in dockerfile


def test_kustomization_contains_dashboard_workload_resources():
    kustomization = _read(WORKLOAD_ROOT / "kustomization.yaml")

    assert "namespace.yaml" in kustomization
    assert "serviceaccount.yaml" in kustomization
    assert "rbac.yaml" in kustomization
    assert "deployment.yaml" in kustomization
    assert "service.yaml" in kustomization


def test_deployment_uses_ci_image_and_runtime_contract():
    deployment = _read(WORKLOAD_ROOT / "deployment.yaml")

    assert "ghcr.io/hepi66/m_devops_transformation:9715faa3d0fc7c7a545ffaec5817adbac0592e91" in deployment
    assert "containerPort: 8501" in deployment
    assert "path: /_stcore/health" in deployment
    assert "readinessProbe:" in deployment
    assert "livenessProbe:" in deployment
    assert "requests:" in deployment
    assert "limits:" in deployment
    assert "namespace: m-devops-dashboard" in deployment
    assert "serviceAccountName: m-devops-dashboard" in deployment


def test_service_selector_and_port_match_deployment():
    deployment = _read(WORKLOAD_ROOT / "deployment.yaml")
    service = _read(WORKLOAD_ROOT / "service.yaml")
    selector = "app.kubernetes.io/instance: m-devops-dashboard"

    assert selector in deployment
    assert selector in service
    assert "type: ClusterIP" in service
    assert "port: 8501" in service
    assert "targetPort: http" in service


def test_argocd_application_targets_workload_and_namespace():
    application = _read(
        REPOSITORY_ROOT / "k8s" / "apps" / "m-devops-dashboard.yaml"
    )

    assert (
        "repoURL: https://github.com/hepi66/M_DevOps_Transformation.git"
        in application
    )
    assert "targetRevision: main" in application
    assert "path: k8s/workloads/m-devops-dashboard" in application
    assert "namespace: m-devops-dashboard" in application
    assert "CreateNamespace=true" in application
    assert "automated:" not in application


def test_workload_manifests_contain_no_secret_resources_or_values():
    manifests = "\n".join(
        _read(path)
        for path in WORKLOAD_ROOT.glob("*.yaml")
    )

    assert "kind: Secret" not in manifests
    assert "token:" not in manifests.lower()
    assert "password:" not in manifests.lower()


def test_dashboard_rbac_is_read_only_and_namespace_scoped():
    rbac = _read(WORKLOAD_ROOT / "rbac.yaml")

    assert "kind: ClusterRole" not in rbac
    assert "kind: ClusterRoleBinding" not in rbac
    assert "namespace: m-devops-dashboard" in rbac
    assert "namespace: argocd" in rbac
    assert "resourceNames:" in rbac
    assert "- m-devops-dashboard" in rbac
    assert "- get" in rbac
    assert "- list" in rbac
    for forbidden_verb in ("create", "update", "patch", "delete", "watch"):
        assert f"- {forbidden_verb}" not in rbac


def test_local_kubeconfig_is_not_stored_in_repository():
    kubeconfig = REPOSITORY_ROOT / "k8s" / "base" / "k3s.yml"
    gitignore = _read(REPOSITORY_ROOT / ".gitignore")

    assert not kubeconfig.exists()
    assert "/k8s/base/k3s.yml" in gitignore
