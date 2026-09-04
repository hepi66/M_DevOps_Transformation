import html
from datetime import datetime

import streamlit as st

from dashboard.deployment_page import build_deployment_page_state
from dashboard.layout import (
    render_component_header,
    status_presentation,
)
from dashboard.lifecycle import PipelineRun


def _format_deployment_age(
    deployed_at: datetime | None,
    observed_at: datetime,
) -> str:
    if deployed_at is None:
        return "—"
    elapsed_seconds = int((observed_at - deployed_at).total_seconds())
    if elapsed_seconds < 0:
        return "—"
    if elapsed_seconds < 60:
        return "<1m"
    if elapsed_seconds < 3600:
        return f"{elapsed_seconds // 60}m"
    if elapsed_seconds < 86400:
        return f"{elapsed_seconds // 3600}h"
    return f"{elapsed_seconds // 86400}d"


def _status_presentation(status: str) -> dict[str, str]:
    if status == "Healthy":
        return status_presentation(status)
    if status == "Running":
        presentation = status_presentation("Deploying")
        return {**presentation, "label": "Running"}
    if status == "Degraded":
        return {
            "label": "Degraded",
            "symbol": "✕",
            "color": "#EF4444",
        }
    return {
        "label": status,
        "symbol": "—",
        "color": "#94A3B8",
    }


def render_deployments(
    pipeline_run: PipelineRun,
    *,
    observed_at: datetime,
) -> None:
    """Render the live production deployment from normalized runtime data."""
    page_state = build_deployment_page_state(pipeline_run)
    version = (
        page_state.release_sha[:7]
        if page_state.release_sha
        and page_state.desired_evidence == "Confirmed"
        else "—"
    )
    deployed_at = (
        pipeline_run.argocd.operation_at
        if version != "—"
        and str(pipeline_run.argocd.operation_phase or "").lower()
        == "succeeded"
        else None
    )
    deployment = {
        "environment": "production",
        "status": page_state.overall_status,
        "version": version,
        "age": _format_deployment_age(deployed_at, observed_at),
    }
    render_component_header(
        "Deployments",
        "LIVE",
        key="dashboard-component-header-deployments",
    )

    rows = [
        """
<style>
.deployment-overview {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.875rem;
}
.deployment-overview th,
.deployment-overview td {
    padding: 0.55rem 0.15rem;
    text-align: left;
    white-space: nowrap;
}
.deployment-overview th {
    color: rgba(128, 128, 128, 0.95);
    font-size: 0.875rem;
    font-weight: 600;
}
.deployment-overview tbody tr {
    border-top: 1px solid rgba(128, 128, 128, 0.18);
}
.deployment-overview .deployment-environment {
    font-weight: 600;
}
.deployment-overview .deployment-status-symbol {
    display: inline-block;
    width: 1rem;
    text-align: center;
    font-weight: 700;
}
</style>
<table class="deployment-overview" aria-label="Deployment overview">
  <thead>
    <tr>
      <th scope="col">Environment</th>
      <th scope="col">Status</th>
      <th scope="col">Version</th>
      <th scope="col">Age</th>
    </tr>
  </thead>
  <tbody>
"""
    ]

    environment = html.escape(deployment["environment"])
    escaped_version = html.escape(deployment["version"])
    age = html.escape(deployment["age"])
    presentation = _status_presentation(deployment["status"])
    status_label = html.escape(presentation["label"])
    status_symbol = html.escape(presentation["symbol"])
    status_color = html.escape(presentation["color"], quote=True)
    rows.append(
        "<tr>"
        f'<td class="deployment-environment">{environment}</td>'
        "<td>"
        f'<span class="deployment-status-symbol" aria-hidden="true" '
        f'style="color: {status_color}">{status_symbol}</span> '
        f"{status_label}</td>"
        f"<td>{escaped_version}</td>"
        f"<td>{age}</td>"
        "</tr>"
    )

    rows.append("</tbody></table>")
    st.html("\n".join(rows))
