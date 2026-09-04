import html

import streamlit as st

from dashboard.deployment_page import build_deployment_page_state
from dashboard.layout import render_component_header, status_presentation
from dashboard.lifecycle import PipelineRun


def _replica_summary(pipeline_run: PipelineRun) -> str:
    ready = pipeline_run.kubernetes.ready_replicas
    desired = pipeline_run.kubernetes.desired_replicas
    if ready is None or desired is None:
        return "—"
    return f"{ready} / {desired}"


def _rendered_status(status: str | None) -> str:
    normalized = str(status or "Unavailable").lower()
    if normalized in {"healthy", "synced"}:
        presentation = status_presentation("Healthy")
    elif normalized in {"running", "progressing"}:
        presentation = status_presentation("Deploying")
    elif normalized == "outofsync":
        presentation = status_presentation("Testing")
    else:
        return '<span class="environment-neutral">—</span>'
    label = html.escape(str(status))
    symbol = html.escape(presentation["symbol"])
    color = html.escape(presentation["color"], quote=True)
    return (
        '<span class="environment-status-symbol" aria-hidden="true" '
        f'style="color: {color}">{symbol}</span> {label}'
    )


def render_environments(pipeline_run: PipelineRun) -> None:
    """Render the live production environment from normalized runtime data."""
    page_state = build_deployment_page_state(pipeline_run)
    environment = {
        "environment": "production",
        "health": page_state.overall_status,
        "pods": _replica_summary(pipeline_run),
        "state": pipeline_run.argocd.sync_status,
    }
    render_component_header(
        "Environments",
        "LIVE",
        key="dashboard-component-header-environments",
    )

    rows = [
        """
<style>
.environment-overview {
    width: 100%;
    border-collapse: collapse;
    table-layout: fixed;
    font-size: 0.875rem;
}
.environment-overview th,
.environment-overview td {
    padding: 0.55rem 0.2rem;
    text-align: left;
    white-space: nowrap;
}
.environment-overview th {
    color: rgba(128, 128, 128, 0.95);
    font-size: 0.875rem;
    font-weight: 600;
}
.environment-overview tbody tr {
    border-top: 1px solid rgba(128, 128, 128, 0.18);
}
.environment-overview .environment-name {
    font-weight: 600;
}
.environment-overview .environment-status-symbol {
    display: inline-block;
    width: 1rem;
    text-align: center;
    font-weight: 700;
}
.environment-overview .environment-neutral {
    color: rgba(128, 128, 128, 0.75);
}
</style>
<table class="environment-overview" aria-label="Environment runtime overview">
  <colgroup>
    <col style="width: 30%">
    <col style="width: 27%">
    <col style="width: 18%">
    <col style="width: 25%">
  </colgroup>
  <thead>
    <tr>
      <th scope="col">Environment</th>
      <th scope="col">Health</th>
      <th scope="col">Pods</th>
      <th scope="col">State</th>
    </tr>
  </thead>
  <tbody>
"""
    ]

    name = html.escape(environment["environment"])
    pods = html.escape(environment["pods"])
    health = _rendered_status(environment["health"])
    state = _rendered_status(environment["state"])
    rows.append(
        "<tr>"
        f'<td class="environment-name">{name}</td>'
        f'<td class="environment-health">{health}</td>'
        f"<td>{pods}</td>"
        f'<td class="environment-state">{state}</td>'
        "</tr>"
    )

    rows.append("</tbody></table>")
    st.html("\n".join(rows))
