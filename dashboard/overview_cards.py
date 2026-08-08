from __future__ import annotations

import html
from dataclasses import dataclass
from datetime import datetime, timezone

import streamlit as st

from dashboard.dora_metrics import DoraMetrics, aggregate_dora_metrics
from dashboard.layout import render_component_header
from dashboard.monitoring import MonitoringState

SUMMARY_CARD_TITLES = (
    "Deployment Frequency",
    "Lead Time for Changes",
    "Change Failure Rate",
    "Mean Time to Restore",
    "System Health",
)

PLATFORM_CARD_TITLES = (
    "Active Alerts",
    "DORA Metrics Trend",
    "Images (GHCR)",
    "Cluster Summary",
)


@dataclass(frozen=True)
class SummaryKpi:
    """Presentation-ready KPI backed by historical or live evidence."""

    title: str
    icon: str
    value: str
    context: str
    evidence: str
    accent: str
    semantic: str
    trend: tuple[float | None, ...] = ()
    trend_label: str = ""


def _format_duration(seconds: float | None) -> str | None:
    if seconds is None:
        return None
    rounded_seconds = round(seconds)
    hours, remainder = divmod(rounded_seconds, 3600)
    minutes, remaining_seconds = divmod(remainder, 60)
    if hours:
        return f"{hours}h {minutes}m" if minutes else f"{hours}h"
    if minutes and remaining_seconds:
        return f"{minutes}m {remaining_seconds}s"
    if minutes:
        return f"{minutes}m"
    return f"{remaining_seconds}s"


def _format_percentage(value: float) -> str:
    percentage = value * 100
    return (
        f"{percentage:.0f}%"
        if percentage.is_integer()
        else f"{percentage:.1f}%"
    )


def _change_failure_accent(rate: float | None) -> str:
    if rate is None:
        return "#94A3B8"
    if rate < 0.15:
        return "#22C55E"
    if rate < 0.30:
        return "#F59E0B"
    return "#EF4444"


def _historical_kpis(metrics: DoraMetrics | None) -> tuple[SummaryKpi, ...]:
    if metrics is None:
        return tuple(
            SummaryKpi(
                title,
                icon,
                "Unavailable",
                "Historical telemetry unavailable",
                "LAST 7 DAYS",
                "#94A3B8",
                "unavailable",
            )
            for title, icon in zip(SUMMARY_CARD_TITLES[:4], ("↗", "◷", "◇", "↻"), strict=True)
        )

    buckets = metrics.daily_buckets
    total_deployments = metrics.successful_deployments + metrics.failed_deployments
    lead_time = _format_duration(metrics.lead_time_average_seconds)
    mttr = _format_duration(metrics.mttr_seconds)
    failure_rate = metrics.change_failure_rate
    return (
        SummaryKpi(
            "Deployment Frequency",
            "↗",
            str(metrics.successful_deployments),
            f"deployment{'s' if metrics.successful_deployments != 1 else ''} · Last 7 days",
            "LAST 7 DAYS",
            "#3B82F6",
            "historical",
            tuple(float(bucket.deployment_count) for bucket in buckets),
            "Successful deployments by UTC day",
        ),
        SummaryKpi(
            "Lead Time for Changes",
            "◷",
            lead_time or "Not enough data",
            "7-day average" if lead_time else "No qualifying deployment duration",
            "LAST 7 DAYS",
            "#8B5CF6",
            "historical" if lead_time else "insufficient",
            tuple(bucket.lead_time_average_seconds for bucket in buckets),
            "Average lead time by UTC day",
        ),
        SummaryKpi(
            "Change Failure Rate",
            "◇",
            _format_percentage(failure_rate) if failure_rate is not None else "Not enough data",
            (
                f"{metrics.failed_deployments} failed of {total_deployments} "
                f"deployment{'s' if total_deployments != 1 else ''}"
                if failure_rate is not None
                else "No deployment outcomes · Last 7 days"
            ),
            "LAST 7 DAYS",
            _change_failure_accent(failure_rate),
            "historical" if failure_rate is not None else "insufficient",
            tuple(
                bucket.failed_deployment_count
                / (bucket.deployment_count + bucket.failed_deployment_count)
                if bucket.deployment_count + bucket.failed_deployment_count
                else None
                for bucket in buckets
            ),
            "Failure proportion by UTC day",
        ),
        SummaryKpi(
            "Mean Time to Restore",
            "↻",
            mttr or "No recovery history",
            (
                f"{metrics.recovery_count} recovered incident"
                f"{'s' if metrics.recovery_count != 1 else ''}"
                if mttr
                else "No correlated recovery · Last 7 days"
            ),
            "LAST 7 DAYS",
            "#22C55E" if mttr else "#94A3B8",
            "historical" if mttr else "insufficient",
            tuple(
                float(bucket.recovery_count) if bucket.recovery_count else None
                for bucket in buckets
            ),
            "Recovered incidents by UTC day",
        ),
    )


def _system_health(state: MonitoringState | None) -> SummaryKpi:
    unavailable = SummaryKpi(
        "System Health",
        "♥",
        "Unavailable",
        "Argo CD and Kubernetes evidence required",
        "LIVE EVIDENCE",
        "#94A3B8",
        "unavailable",
    )
    if state is None:
        return unavailable

    run = state.pipeline_run
    argocd = run.argocd
    kubernetes = run.kubernetes
    if (
        argocd.availability != "available"
        or kubernetes.availability != "available"
    ):
        return unavailable

    sync = str(argocd.sync_status or "").lower()
    health = str(argocd.health_status or "").lower()
    desired = kubernetes.desired_replicas
    ready = kubernetes.ready_replicas
    replicas_known = desired is not None and ready is not None
    replica_context = (
        f"{ready}/{desired} replicas ready"
        if replicas_known
        else "Replica readiness unavailable"
    )
    if kubernetes.status == "failed" or health in {"degraded", "missing"}:
        return SummaryKpi(
            "System Health",
            "♥",
            "Degraded",
            f"Argo CD {argocd.health_status or 'Unknown'} · {replica_context}",
            "LIVE RUNTIME",
            "#EF4444",
            "degraded",
        )
    if (
        sync == "synced"
        and health == "healthy"
        and kubernetes.status == "completed"
        and replicas_known
        and ready == desired
        and desired > 0
    ):
        return SummaryKpi(
            "System Health",
            "♥",
            "Healthy",
            f"Argo CD Synced · {replica_context}",
            "LIVE RUNTIME",
            "#22C55E",
            "healthy",
        )
    return SummaryKpi(
        "System Health",
        "♥",
        "Attention",
        f"Argo CD {argocd.sync_status or 'Unknown'} · {replica_context}",
        "LIVE RUNTIME",
        "#EAB308",
        "attention",
    )


def build_summary_kpis(
    monitoring_state: MonitoringState | None,
    dora_metrics: DoraMetrics | None = None,
) -> tuple[SummaryKpi, ...]:
    """Build four historical KPIs and one authoritative live-health KPI."""
    return (*_historical_kpis(dora_metrics), _system_health(monitoring_state))


def _trend_markup(kpi: SummaryKpi) -> str:
    if not kpi.trend:
        return (
            '<div class="summary-kpi-live-strip" '
            'aria-label="Current live status">'
            '<span></span><span></span><span></span></div>'
        )
    available_values = [value for value in kpi.trend if value is not None]
    maximum = max(available_values, default=0)
    bars = []
    for index, value in enumerate(kpi.trend, start=1):
        available = value is not None
        relative = value / maximum if available and maximum > 0 else 0
        height = 18 + round(relative * 82) if available else 8
        classes = "summary-kpi-trend-bar"
        if not available:
            classes += " summary-kpi-trend-missing"
        bars.append(
            f'<span class="{classes}" data-day="{index}" '
            f'style="height:{height}%"></span>'
        )
    return (
        f'<div class="summary-kpi-trend" '
        f'aria-label="{html.escape(kpi.trend_label)}">'
        f'{"".join(bars)}</div>'
    )


def _render_summary_kpi(kpi: SummaryKpi) -> None:
    st.html(
        f"""
<article class="summary-kpi-card summary-kpi-{html.escape(kpi.semantic)}"
         style="--summary-kpi-accent: {html.escape(kpi.accent)}">
  <div class="summary-kpi-header">
    <span class="summary-kpi-icon" aria-hidden="true">{html.escape(kpi.icon)}</span>
    <span class="summary-kpi-evidence">{html.escape(kpi.evidence)}</span>
  </div>
  <h3>{html.escape(kpi.title)}</h3>
  <div class="summary-kpi-value">{html.escape(kpi.value)}</div>
  <p>{html.escape(kpi.context)}</p>
  {_trend_markup(kpi)}
</article>
"""
    )


def _history_disclosure(metrics: DoraMetrics | None) -> str | None:
    if metrics is None or metrics.synthetic_event_count == 0:
        return None
    if metrics.real_event_count:
        return "Observed + lab telemetry"
    return "7-day lab telemetry"


def _load_dora_metrics() -> DoraMetrics | None:
    try:
        return aggregate_dora_metrics(as_of=datetime.now(timezone.utc))
    except Exception:  # noqa: BLE001 - history cannot break the live Overview
        return None


def _render_demo_card(title: str) -> None:
    with st.container(border=True, height="stretch"):
        render_component_header(title, "DEMO")
        st.caption("Awaiting data source")


def _render_ghcr_card(_runtime_snapshot: dict | None = None) -> None:
    with st.container(border=True, height="stretch"):
        render_component_header("Images (GHCR)", "LIVE")
        st.caption("Awaiting image statistics")


def _render_card_row(
    titles: tuple[str, ...],
    runtime_snapshot: dict | None = None,
) -> None:
    columns = st.columns(len(titles), gap="small")
    for column, title in zip(columns, titles, strict=True):
        with column:
            if title == "Images (GHCR)":
                _render_ghcr_card(runtime_snapshot)
            else:
                _render_demo_card(title)


def render_summary_cards(monitoring_state: MonitoringState | None) -> None:
    """Render the five-card KPI header without coupling history to live state."""
    metrics = _load_dora_metrics()
    columns = st.columns(5, gap="small")
    for column, kpi in zip(
        columns,
        build_summary_kpis(monitoring_state, metrics),
        strict=True,
    ):
        with column:
            _render_summary_kpi(kpi)
    disclosure = _history_disclosure(metrics)
    if disclosure:
        st.caption(disclosure)


def render_platform_cards(runtime_snapshot: dict | None = None) -> None:
    """Render the dashboard platform placeholder cards."""
    _render_card_row(PLATFORM_CARD_TITLES, runtime_snapshot)
