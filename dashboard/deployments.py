import html

import streamlit as st

from dashboard.layout import (
    render_component_header,
    status_presentation,
)

DEPLOYMENTS = (
    {
        "environment": "production",
        "status": "Healthy",
        "version": "v1.24.7",
    },
    {
        "environment": "staging",
        "status": "Deploying",
        "version": "v1.24.8",
    },
    {
        "environment": "development",
        "status": "Testing",
        "version": "v1.24.9",
    },
    {
        "environment": "preview",
        "status": "Deploying",
        "version": "—",
    },
)


def render_deployments() -> None:
    """Render the static Phase 1 deployment demonstration."""
    render_component_header(
        "Deployments",
        "DEMO",
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

    for deployment in DEPLOYMENTS:
        environment = html.escape(deployment["environment"])
        version = html.escape(deployment["version"])
        presentation = status_presentation(deployment["status"])
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
            f"<td>{version}</td>"
            "<td>—</td>"
            "</tr>"
        )

    rows.append("</tbody></table>")
    st.html("\n".join(rows))
