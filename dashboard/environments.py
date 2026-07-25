import html

import streamlit as st

from dashboard.layout import render_component_header, status_presentation

ENVIRONMENTS = (
    {
        "environment": "production",
        "status": "Healthy",
        "pods": "12 / 12",
    },
    {
        "environment": "staging",
        "status": "Healthy",
        "pods": "8 / 8",
    },
    {
        "environment": "preview",
        "status": "Deploying",
        "pods": "3 / 4",
    },
    {
        "environment": "development",
        "status": "Healthy",
        "pods": "6 / 6",
    },
)

def render_environments() -> None:
    """Render the static Phase 1 environment demonstration."""
    render_component_header(
        "Environments",
        "DEMO",
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

    for environment in ENVIRONMENTS:
        name = html.escape(environment["environment"])
        pods = html.escape(environment["pods"])
        presentation = status_presentation(environment["status"])
        status = html.escape(presentation["label"])
        symbol = html.escape(presentation["symbol"])
        color = html.escape(presentation["color"], quote=True)
        rendered_status = (
            '<span class="environment-status-symbol" aria-hidden="true" '
            f'style="color: {color}">{symbol}</span> {status}'
        )
        neutral = '<span class="environment-neutral">—</span>'
        health = rendered_status if status == "Healthy" else neutral
        state = rendered_status if status == "Deploying" else neutral
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
