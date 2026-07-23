from unittest.mock import MagicMock, Mock

import pytest

from dashboard import operational_detail_viewer as viewer
from dashboard import overview_cards
from dashboard import pipeline
from dashboard import navigation
from dashboard.layout import OPERATIONAL_SOURCE_LEGEND
from dashboard.pipeline_model import PIPELINE_STAGES
from dashboard.operational_events import (
    OperationalEvent,
    order_operational_events,
)


def _docker_snapshot(
    *,
    job_status="completed",
    job_conclusion="success",
    step_status="completed",
    step_conclusion="success",
):
    return {
        "branch": "main",
        "url": "https://github.com/example/repository",
        "repository_url": "https://github.com/example/repository",
        "docker_build": {
            "availability": "available",
            "workflow": {
                "name": "CI Pipeline",
                "databaseId": 82,
                "number": 12,
                "status": job_status,
                "conclusion": job_conclusion,
                "createdAt": "2026-07-22T08:53:55Z",
                "startedAt": "2026-07-22T08:54:05Z",
                "updatedAt": "2026-07-22T08:55:05Z",
                "url": "https://github.com/example/actions/runs/82",
            },
            "job": {
                "name": "build",
                "status": job_status,
                "conclusion": job_conclusion,
                "startedAt": "2026-07-22T08:54:05Z",
                "completedAt": "2026-07-22T08:55:05Z",
            },
            "step": {
                "name": "Build and push",
                "status": step_status,
                "conclusion": step_conclusion,
                "startedAt": "2026-07-22T08:54:10Z",
                "completedAt": "2026-07-22T08:55:00Z",
            },
        },
    }


@pytest.mark.parametrize(
    ("snapshot", "expected_status"),
    [
        (_docker_snapshot(), "Completed"),
        (
            _docker_snapshot(
                job_status="in_progress",
                job_conclusion=None,
                step_status="in_progress",
                step_conclusion=None,
            ),
            "Active",
        ),
        (_docker_snapshot(job_conclusion="failure"), "Failed"),
        (_docker_snapshot(step_conclusion="failure"), "Failed"),
    ],
)
def test_docker_build_stage_status(monkeypatch, snapshot, expected_status):
    monkeypatch.setattr(viewer, "_load_github_status", lambda: snapshot)

    assert viewer.get_docker_build_stage_data()["status"] == expected_status


def test_operational_event_ordering_and_duplicate_handling():
    older = _event("2026-07-22T08:53:00Z", "older", 1)
    same_time_second = _event("2026-07-22T08:54:00Z", "second", 2)
    same_time_first = _event("2026-07-22T08:54:00Z", "first", 1)
    duplicate_record = OperationalEvent(
        **{
            **same_time_first.__dict__,
            "message": "duplicate representation",
        }
    )

    ordered = order_operational_events(
        [older, same_time_second, same_time_first, duplicate_record]
    )

    assert [event.message for event in ordered] == ["first", "second", "older"]


def test_github_feed_uses_established_source_abbreviations():
    details = {
        "state": "Healthy",
        "repository": "example/repository",
        "branch": "main",
        "last_update": "2026-07-22T08:54:00Z",
        "workflow": {
            "name": "CI Pipeline",
            "createdAt": "2026-07-22T08:53:00Z",
        },
        "events": [
            _event(
                "2026-07-22T08:52:00Z",
                "workflow started",
                1,
                source="CI",
            )
        ],
    }

    events = viewer._build_github_feed(details)

    assert {"GI", "GH", "CI"} <= {
        event.source_abbreviation for event in events
    }


@pytest.mark.parametrize(
    ("snapshot", "expected_message", "expected_status"),
    [
        (
            _docker_snapshot(),
            "Build and push completed successfully",
            "SUCCESS",
        ),
        (
            _docker_snapshot(
                job_status="in_progress",
                job_conclusion=None,
                step_status="in_progress",
                step_conclusion=None,
            ),
            "Build and push started",
            "RUNNING",
        ),
        (
            _docker_snapshot(job_conclusion="failure"),
            "Docker Build job failed",
            "FAILED",
        ),
        (
            _docker_snapshot(step_conclusion="failure"),
            "Build and push step failed",
            "FAILED",
        ),
    ],
)
def test_docker_build_events(snapshot, expected_message, expected_status):
    events = viewer._build_docker_build_feed(snapshot)
    matching = [event for event in events if event.message == expected_message]

    assert matching
    assert matching[0].status == expected_status
    assert matching[0].source_abbreviation == "DB"


def test_successful_ghcr_retrieval_normalizes_available_metadata(monkeypatch):
    package = {
        "name": "m_devops_transformation",
        "html_url": "https://github.com/users/example/packages/container/package",
        "visibility": "public",
    }
    versions = [
        {
            "name": "sha256:abc123",
            "created_at": "2026-07-22T08:55:00Z",
            "updated_at": "2026-07-22T08:56:00Z",
            "metadata": {"container": {"tags": ["latest", "1234567"]}},
        }
    ]
    loader = Mock(
        side_effect=[
            (package, "available"),
            (versions, "available"),
        ]
    )
    monkeypatch.setattr(viewer, "_run_gh_json_with_availability", loader)

    details = viewer._load_ghcr_package(
        {
            "name": "M_DevOps_Transformation",
            "owner": {"login": "example"},
        }
    )

    assert details == {
        "availability": "available",
        "package_name": "m_devops_transformation",
        "image_name": "ghcr.io/example/m_devops_transformation",
        "latest_tag": "latest",
        "published_at": "2026-07-22T08:56:00Z",
        "digest": "sha256:abc123",
        "package_url": package["html_url"],
        "visibility": "public",
    }
    assert loader.call_args_list == [
        (
            (
                "api",
                "/users/example/packages/container/m_devops_transformation",
            ),
            {},
        ),
        (
            (
                "api",
                "/users/example/packages/container/"
                "m_devops_transformation/versions?per_page=1",
            ),
            {},
        ),
    ]


@pytest.mark.parametrize(
    ("availability", "expected_reason"),
    [
        ("missing", "does not exist"),
        ("unavailable", "could not be retrieved"),
        ("authentication_unavailable", "authentication is unavailable"),
    ],
)
def test_ghcr_retrieval_failures_are_distinct(
    monkeypatch,
    availability,
    expected_reason,
):
    monkeypatch.setattr(
        viewer,
        "_run_gh_json_with_availability",
        Mock(return_value=(None, availability)),
    )

    details = viewer._load_ghcr_package(
        {
            "name": "M_DevOps_Transformation",
            "owner": {"login": "example"},
        }
    )

    assert details["availability"] == availability
    assert expected_reason in details["reason"]


def test_ghcr_api_permission_failure_is_authentication_unavailable(
    monkeypatch,
):
    result = Mock(
        returncode=1,
        stderr="You need at least read:packages scope. (HTTP 403)",
        stdout="",
    )
    monkeypatch.setattr(
        viewer,
        "_run_gh_process",
        Mock(return_value=result),
    )

    payload, availability = viewer._run_gh_json_with_availability(
        "api",
        "/users/example/packages/container/example",
    )

    assert payload is None
    assert availability == "authentication_unavailable"


@pytest.mark.parametrize(
    ("availability", "expected_status"),
    [
        ("available", "Image published"),
        ("missing", "Image unavailable"),
        ("unavailable", "Retrieval unavailable"),
        ("authentication_unavailable", "Authentication unavailable"),
    ],
)
def test_ghcr_pipeline_stage_status(monkeypatch, availability, expected_status):
    monkeypatch.setattr(
        viewer,
        "get_ghcr_data",
        Mock(
            return_value={
                "availability": availability,
                "published_at": "2026-07-22T08:56:00Z",
                "image_name": "ghcr.io/example/image",
            }
        ),
    )

    stage_data = viewer.get_ghcr_stage_data()

    assert stage_data["source_classification"] == "LIVE"
    assert stage_data["status"] == expected_status


def test_ghcr_operational_event_uses_shared_model():
    events = viewer._build_ghcr_feed(
        {
            "ghcr": {
                "availability": "available",
                "package_name": "m_devops_transformation",
                "image_name": "ghcr.io/example/m_devops_transformation",
                "latest_tag": "latest",
                "published_at": "2026-07-22T08:56:00Z",
                "digest": "sha256:abc123",
                "visibility": "public",
                "package_url": "https://github.com/example/package",
            }
        }
    )

    assert len(events) == 1
    assert events[0].message == "GHCR image published"
    assert events[0].source_abbreviation == "CR"
    assert events[0].status == "SUCCESS"
    assert events[0].external_url == "https://github.com/example/package"


@pytest.mark.parametrize(
    ("availability", "expected_message"),
    [
        ("missing", "GHCR image unavailable"),
        ("unavailable", "GHCR retrieval unavailable"),
        (
            "authentication_unavailable",
            "GHCR authentication unavailable",
        ),
    ],
)
def test_ghcr_operational_fallback_events(availability, expected_message):
    events = viewer._build_ghcr_feed(
        {"ghcr": {"availability": availability, "reason": "Unavailable"}}
    )

    assert events[0].message == expected_message
    assert events[0].status == "WARNING"


def test_ghcr_images_card_renders_live_metadata(monkeypatch):
    container = MagicMock()
    container.__enter__.return_value = container
    monkeypatch.setattr(
        overview_cards.st,
        "container",
        Mock(return_value=container),
    )
    monkeypatch.setattr(overview_cards, "render_component_header", Mock())
    monkeypatch.setattr(
        overview_cards,
        "get_ghcr_data",
        Mock(
            return_value={
                "availability": "available",
                "image_name": "ghcr.io/example/image",
                "latest_tag": "latest",
                "published_at": "2026-07-22T08:56:00Z",
                "digest": "sha256:abc123",
                "visibility": "public",
                "package_url": "https://github.com/example/package",
            }
        ),
    )
    monkeypatch.setattr(overview_cards.st, "markdown", Mock())
    monkeypatch.setattr(overview_cards.st, "caption", Mock())
    monkeypatch.setattr(overview_cards.st, "link_button", Mock())

    overview_cards._render_ghcr_card()

    overview_cards.render_component_header.assert_called_once_with(
        "Images (GHCR)",
        "LIVE",
    )
    overview_cards.st.markdown.assert_called_once_with(
        "**ghcr.io/example/image:latest**"
    )
    overview_cards.st.link_button.assert_called_once_with(
        "Open GHCR Package",
        "https://github.com/example/package",
    )
    overview_cards.get_ghcr_data.assert_called_once_with(None)


def test_runtime_snapshot_is_reused_by_live_consumers(monkeypatch):
    runtime_snapshot = {
        "docker_build": _docker_snapshot()["docker_build"],
        "ghcr": {
            "availability": "available",
            "image_name": "ghcr.io/example/image",
            "published_at": "2026-07-22T08:56:00Z",
        },
    }
    unexpected_load = Mock(
        side_effect=AssertionError("runtime snapshot was regenerated")
    )
    monkeypatch.setattr(viewer, "load_dashboard_snapshot", unexpected_load)

    docker_data = viewer.get_docker_build_stage_data(runtime_snapshot)
    ghcr_data = viewer.get_ghcr_data(runtime_snapshot)
    ghcr_stage = viewer.get_ghcr_stage_data(runtime_snapshot)

    assert docker_data["status"] == "Completed"
    assert ghcr_data is runtime_snapshot["ghcr"]
    assert ghcr_stage["status"] == "Image published"
    unexpected_load.assert_not_called()


def test_refresh_button_invalidates_snapshot_and_reruns(monkeypatch):
    class SessionState(dict):
        __getattr__ = dict.__getitem__
        __setattr__ = dict.__setitem__

    sidebar = Mock()
    sidebar.radio.side_effect = lambda _label, pages, **_kwargs: next(
        iter(pages)
    )
    sidebar.button.return_value = True
    fake_streamlit = Mock(
        sidebar=sidebar,
        session_state=SessionState(),
    )
    refresh_snapshot = Mock()
    monkeypatch.setattr(navigation, "st", fake_streamlit)

    selected_page = navigation.render_navigation(refresh_snapshot)

    assert selected_page == "overview"
    refresh_snapshot.assert_called_once_with()
    fake_streamlit.rerun.assert_called_once_with()
    assert "dashboard_loaded_at" in fake_streamlit.session_state


def test_ghcr_retrieval_reuses_cached_github_snapshot(monkeypatch):
    def git_command(*arguments):
        if arguments == ("remote", "get-url", "origin"):
            return "https://github.com/example/repository.git"
        if arguments == ("branch", "--show-current"):
            return "main"
        return None

    def gh_json(*arguments):
        if arguments[:2] == ("repo", "view"):
            return {
                "name": "repository",
                "nameWithOwner": "example/repository",
                "owner": {"login": "example"},
                "url": "https://github.com/example/repository",
            }
        if arguments[:2] == ("run", "list"):
            return []
        if arguments[:2] == ("pr", "list"):
            return []
        return None

    ghcr_loader = Mock(
        return_value={
            "availability": "available",
            "image_name": "ghcr.io/example/repository",
        }
    )
    monkeypatch.setattr(viewer, "_run_git_command", git_command)
    monkeypatch.setattr(viewer, "_run_gh_command", Mock(return_value="ok"))
    monkeypatch.setattr(viewer, "_run_gh_json", gh_json)
    monkeypatch.setattr(viewer, "_load_ghcr_package", ghcr_loader)
    viewer._load_github_status.clear()

    try:
        first = viewer._load_github_status()
        second = viewer._load_github_status()
    finally:
        viewer._load_github_status.clear()

    assert first["ghcr"] == second["ghcr"]
    ghcr_loader.assert_called_once()


def test_operational_event_classification_keeps_lifecycle_prominent():
    docker_events = viewer._build_docker_build_feed(_docker_snapshot())
    github_events = viewer._build_github_feed(
        {
            "state": "Healthy",
            "branch": "main",
            "last_update": "2026-07-22T08:55:05Z",
            "workflow": {
                "name": "CI Pipeline",
                "databaseId": 82,
                "createdAt": "2026-07-22T08:53:55Z",
            },
            "events": [],
        }
    )

    assert any(
        event.classification == "lifecycle" for event in docker_events
    )
    assert any(
        event.classification == "metadata" for event in github_events
    )
    assert sum(
        event.classification == "lifecycle" for event in docker_events
    ) > sum(
        event.classification == "metadata"
        for event in [*docker_events, *github_events]
    )


def test_shared_renderer_marks_metadata_as_secondary(monkeypatch):
    html_output = Mock()
    monkeypatch.setattr(viewer.st, "html", html_output)
    event = OperationalEvent(
        timestamp=None,
        source_identifier="Git",
        source_abbreviation="GI",
        category="github",
        status="INFO",
        icon="ℹ",
        message="Pipeline branch resolved: main",
        classification="metadata",
        event_id="metadata",
    )

    viewer._render_event_timeline([event])

    assert 'class="event-row metadata"' in html_output.call_args.args[0]


@pytest.mark.parametrize(
    ("details", "expected_message"),
    [
        (None, "Docker Build live data unavailable"),
        (
            {"availability": "unavailable"},
            "GitHub Actions workflow data unavailable",
        ),
        (
            {"availability": "missing"},
            "No Docker Build workflow execution found",
        ),
        (
            {"availability": "incomplete"},
            "Docker Build workflow metadata incomplete",
        ),
        (
            {
                "availability": "unrecognized",
                "reason": "The expected build job was not found.",
            },
            "The expected build job was not found.",
        ),
        (
            {
                "availability": "unrecognized",
                "reason": "The expected Build and push step was not found.",
            },
            "The expected Build and push step was not found.",
        ),
    ],
)
def test_docker_build_fallback_events(details, expected_message):
    events = viewer._build_docker_build_feed({"docker_build": details})

    assert events[0].message == expected_message
    assert events[0].status == "WARNING"
    assert events[0].timestamp is None


@pytest.mark.parametrize(
    ("run_details", "expected_availability"),
    [
        (None, "unavailable"),
        ({"jobs": []}, "unrecognized"),
        (
            {
                "jobs": [
                    {
                        "name": "build",
                        "status": "completed",
                        "conclusion": "success",
                        "steps": [],
                    }
                ]
            },
            "unrecognized",
        ),
    ],
)
def test_docker_build_workflow_structure_fallback(
    monkeypatch,
    run_details,
    expected_availability,
):
    monkeypatch.setattr(viewer, "_run_gh_json", lambda *args: run_details)

    github_actions = viewer._load_github_actions_details(
        [{"name": "CI Pipeline", "databaseId": 82}],
        workflow_name="CI Pipeline",
    )
    details = viewer._project_docker_build(
        github_actions,
        job_name="build",
        step_name="Build and push",
    )

    assert details["availability"] == expected_availability


def test_complete_github_actions_hierarchy_is_normalized(monkeypatch):
    run_details = {
        "jobs": [
            {
                "name": "linting",
                "status": "completed",
                "conclusion": "success",
                "customJobField": "preserved",
                "steps": [
                    {
                        "name": "Run Ruff (Linting)",
                        "status": "completed",
                        "conclusion": "success",
                    },
                    {
                        "name": "Run Bandit (Security)",
                        "status": "completed",
                        "conclusion": "success",
                    },
                ],
            },
            {
                "name": "test",
                "status": "completed",
                "conclusion": "success",
                "steps": [
                    {
                        "name": "Run Tests",
                        "status": "completed",
                        "conclusion": "success",
                    }
                ],
            },
            {
                "name": "build",
                "status": "completed",
                "conclusion": "success",
                "steps": [
                    {
                        "name": "Login to GitHub Container Registry",
                        "status": "completed",
                        "conclusion": "success",
                    },
                    {
                        "name": "Build and push",
                        "status": "completed",
                        "conclusion": "success",
                        "customStepField": "preserved",
                    },
                ],
            },
        ]
    }
    run_loader = Mock(return_value=run_details)
    monkeypatch.setattr(viewer, "_run_gh_json", run_loader)

    hierarchy = viewer._load_github_actions_details(
        [{"name": "CI Pipeline", "databaseId": 82}],
        workflow_name="CI Pipeline",
    )

    assert [job["name"] for job in hierarchy["jobs"]] == [
        "linting",
        "test",
        "build",
    ]
    assert [len(job["steps"]) for job in hierarchy["jobs"]] == [2, 1, 2]
    assert hierarchy["jobs"][0]["customJobField"] == "preserved"
    assert hierarchy["jobs"][2]["steps"][1]["customStepField"] == "preserved"
    run_loader.assert_called_once_with("run", "view", "82", "--json", "jobs")


def test_docker_projection_uses_complete_hierarchy():
    hierarchy = {
        "availability": "available",
        "workflow": {"name": "CI Pipeline", "databaseId": 82},
        "jobs": [
            {"name": "linting", "steps": [{"name": "Run Ruff (Linting)"}]},
            {
                "name": "build",
                "status": "completed",
                "conclusion": "success",
                "steps": [
                    {"name": "Login to GitHub Container Registry"},
                    {
                        "name": "Build and push",
                        "status": "completed",
                        "conclusion": "success",
                    },
                ],
            },
        ],
    }

    docker_build = viewer._project_docker_build(
        hierarchy,
        job_name="build",
        step_name="Build and push",
    )

    assert docker_build["job"] is hierarchy["jobs"][1]
    assert docker_build["step"] is hierarchy["jobs"][1]["steps"][1]


def test_quality_gate_and_docker_events_are_projected():
    snapshot = _complete_execution_snapshot()

    quality_messages = {
        event.message for event in viewer._build_quality_gate_feed(snapshot)
    }
    docker_messages = {
        event.message for event in viewer._build_docker_build_feed(snapshot)
    }

    assert {
        "Linting started",
        "Ruff completed successfully",
        "Security scan completed successfully",
        "Linting completed successfully",
        "Tests started",
        "Tests completed successfully",
    } <= quality_messages
    assert {
        "Docker Build started",
        "Registry login completed successfully",
        "Build and push started",
        "Build and push completed successfully",
        "Docker Build completed successfully",
    } <= docker_messages


def test_running_workflow_preserves_completed_progress():
    snapshot = _complete_execution_snapshot()
    test_job = snapshot["github_actions"]["jobs"][1]
    test_step = test_job["steps"][-1]
    test_job.update(
        status="in_progress",
        conclusion=None,
        completedAt=None,
    )
    test_step.update(
        status="in_progress",
        conclusion=None,
        completedAt=None,
    )

    events = viewer._build_quality_gate_feed(snapshot)
    messages = {event.message for event in events}

    assert "Linting completed successfully" in messages
    assert "Tests are running" in messages
    assert not any(
        event.message == "Testing job completed successfully"
        for event in events
    )


def test_failed_step_retains_previous_success_and_specific_failure():
    snapshot = _complete_execution_snapshot()
    linting = snapshot["github_actions"]["jobs"][0]
    linting.update(conclusion="failure")
    linting["steps"][-1].update(conclusion="failure")

    events = viewer._build_quality_gate_feed(snapshot)
    messages = {event.message for event in events}
    failure = next(
        event for event in events if event.message == "Security scan failed"
    )

    assert "Ruff completed successfully" in messages
    assert "Linting failed" in messages
    assert failure.classification == "failure"
    assert "Run: 12" in failure.detail
    assert "Job: linting" in failure.detail
    assert "Step: Run Bandit (Security)" in failure.detail
    assert failure.external_url


def test_successful_setup_steps_are_hidden_but_failures_are_visible():
    snapshot = _complete_execution_snapshot()
    checkout = snapshot["github_actions"]["jobs"][0]["steps"][0]

    successful_messages = {
        event.message for event in viewer._build_quality_gate_feed(snapshot)
    }
    assert not any("Checkout" in message for message in successful_messages)

    checkout.update(conclusion="failure")
    failed_messages = {
        event.message for event in viewer._build_quality_gate_feed(snapshot)
    }
    assert "Checkout failed" in failed_messages


@pytest.mark.parametrize(
    ("conclusion", "expected_message", "expected_status"),
    [
        ("cancelled", "CI Pipeline cancelled", "CANCELLED"),
        ("timed_out", "CI Pipeline timed out", "FAILED"),
    ],
)
def test_cancelled_and_timed_out_workflows(
    conclusion,
    expected_message,
    expected_status,
):
    workflow = _complete_execution_snapshot()["workflow"]
    workflow["conclusion"] = conclusion

    events = viewer._build_operational_events([workflow])
    event = next(item for item in events if item.message == expected_message)

    assert event.status == expected_status


def test_detailed_history_is_limited_to_normalized_run():
    snapshot = _complete_execution_snapshot()
    older_run = {
        **snapshot["workflow"],
        "databaseId": 81,
        "number": 11,
        "updatedAt": "2026-07-21T22:00:00Z",
    }
    snapshot["events"] = viewer._build_operational_events(
        [snapshot["workflow"], older_run]
    )

    events = viewer._build_github_feed(snapshot)

    assert any("Run: 11" in (event.detail or "") for event in events)
    assert sum(event.message == "Ruff completed successfully" for event in events) == 1


@pytest.mark.parametrize(
    ("selection", "expected_sources"),
    [
        ("GitHub Status", {"GI", "GH", "CI"}),
        ("Docker Build", {"CI", "DB"}),
        ("GHCR", {"CR"}),
    ],
)
def test_categorized_views_use_shared_renderer(
    monkeypatch,
    selection,
    expected_sources,
):
    rendered = _render_viewer(monkeypatch, selection)

    assert {event.source_abbreviation for event in rendered} == expected_sources


def test_all_is_default_and_combines_all_events(monkeypatch):
    rendered = _render_viewer(monkeypatch, "All")

    assert {"GI", "GH", "CI", "DB"} <= {
        event.source_abbreviation for event in rendered
    }
    assert viewer.st.selectbox.call_args.args[1][0] == "All"
    assert viewer.st.selectbox.call_args.args[1] == (
        "All",
        "Git / Local Repository",
        "GitHub Status",
        "Docker Build",
        "GHCR",
    )


def test_filter_change_uses_one_github_snapshot(monkeypatch):
    snapshot_loader = Mock(return_value=_docker_snapshot())
    _configure_viewer_mocks(monkeypatch, "Docker Build", snapshot_loader)

    viewer.render_operational_detail_viewer()

    snapshot_loader.assert_called_once_with()


def test_equal_timestamps_follow_lifecycle_source_order():
    timestamp = "2026-07-22T08:54:00Z"
    events = [
        _event(timestamp, "Docker", 1, source="DB"),
        _event(timestamp, "GitHub", 1, source="GH"),
        _event(timestamp, "Git", 1, source="GI"),
        _event(timestamp, "CI", 1, source="CI"),
    ]

    assert [
        event.source_abbreviation
        for event in order_operational_events(events)
    ] == ["GI", "GH", "CI", "DB"]


@pytest.mark.parametrize(
    "filter_name",
    [
        "All",
        "Git / Local Repository",
        "GitHub Status",
        "Docker Build",
        "GHCR",
    ],
)
def test_existing_filters_order_newest_events_first(filter_name):
    events = [
        _event(
            "2026-07-22T08:53:00Z",
            f"{filter_name} older",
            1,
        ),
        _event(
            "2026-07-22T08:55:00Z",
            f"{filter_name} newest",
            1,
        ),
    ]

    ordered = order_operational_events(events)

    assert ordered[0].message == f"{filter_name} newest"


def test_untimestamped_events_remain_deterministic_and_last():
    events = [
        _event(None, "Docker fallback", 2, source="DB"),
        _event("2026-07-22T08:54:00Z", "Current event", 1, source="CI"),
        _event(None, "GitHub fallback", 1, source="GH"),
    ]

    ordered = order_operational_events(events)

    assert [event.message for event in ordered] == [
        "Current event",
        "GitHub fallback",
        "Docker fallback",
    ]


def test_refresh_time_is_displayed_separately(monkeypatch):
    caption = Mock()
    formatter = Mock(return_value="22 Jul 08:54:05")
    monkeypatch.setattr(viewer.st, "caption", caption)
    monkeypatch.setattr(viewer, "format_dashboard_timestamp", formatter)

    viewer._render_refresh_time(
        {"refreshed_at": "2026-07-22T08:54:05Z"}
    )

    formatter.assert_called_once_with("2026-07-22T08:54:05Z")
    caption.assert_called_once_with("Last refreshed: 22 Jul 08:54:05")


def test_repository_and_branch_context_render_above_timeline(monkeypatch):
    caption = Mock()
    monkeypatch.setattr(viewer.st, "caption", caption)

    viewer._render_operational_context(
        {
            "repository": "example/repository",
            "state": "Healthy",
            "branch": "main",
        }
    )

    caption.assert_called_once()
    rendered_context = caption.call_args.args[0]
    assert "example/repository" in rendered_context
    assert "Healthy" in rendered_context
    assert "main" in rendered_context


def test_context_events_move_outside_timeline_without_mutating_events():
    events = [
        _event(
            "2026-07-22T08:56:00Z",
            "Pipeline branch resolved: main",
            1,
            source="GH",
        ),
        _event(
            "2026-07-22T08:56:00Z",
            "GitHub repository healthy",
            2,
            source="GH",
        ),
        _event(
            "2026-07-22T08:55:00Z",
            "CI Pipeline completed successfully",
            3,
            source="CI",
        ),
    ]
    events[0] = OperationalEvent(
        **{**events[0].__dict__, "event_id": "github:branch"}
    )
    events[1] = OperationalEvent(
        **{**events[1].__dict__, "event_id": "github:health"}
    )

    timeline_events = viewer._timeline_presentation_events(events)

    assert [event.message for event in timeline_events] == [
        "CI Pipeline completed successfully"
    ]
    assert len(events) == 3


def test_timeline_height_exposes_more_compact_event_rows(monkeypatch):
    html_output = Mock()
    monkeypatch.setattr(viewer.st, "html", html_output)
    events = [
        _event(
            f"2026-07-22T08:{minute:02d}:00Z",
            f"Lifecycle event {minute}",
            minute,
            source="CI",
        )
        for minute in range(12)
    ]

    viewer._render_event_timeline(events)

    rendered_html = html_output.call_args.args[0]
    assert "height: 380px" in rendered_html
    assert rendered_html.count('<div class="event-row') == 12


def test_footer_legend_contains_docker_build():
    assert ("GI", "Git") in OPERATIONAL_SOURCE_LEGEND
    assert ("GH", "GitHub") in OPERATIONAL_SOURCE_LEGEND
    assert ("CI", "CI/CD") in OPERATIONAL_SOURCE_LEGEND
    assert ("DB", "Docker Build") in OPERATIONAL_SOURCE_LEGEND
    assert ("CR", "GHCR") in OPERATIONAL_SOURCE_LEGEND


def test_build_pipeline_interaction_selects_docker_build(monkeypatch):
    fake_streamlit = _PipelineStreamlit()
    monkeypatch.setattr(pipeline, "st", fake_streamlit)
    monkeypatch.setattr(
        pipeline,
        "get_pipeline_stages",
        lambda _runtime_snapshot: PIPELINE_STAGES,
    )
    monkeypatch.setattr(pipeline, "render_data_source_indicator", Mock())

    pipeline.render_delivery_pipeline()

    assert fake_streamlit.session_state["operational_detail_source"] == "Docker Build"
    fake_streamlit.rerun.assert_called_once_with()


@pytest.mark.parametrize(
    ("source", "expected_label"),
    [
        ("All", "Open Latest Pipeline Run"),
        ("GitHub Status", "Open Repository"),
        ("Docker Build", "Open GitHub Actions Run"),
    ],
)
def test_context_aware_actions(monkeypatch, source, expected_label):
    link_button = Mock()
    monkeypatch.setattr(viewer.st, "link_button", link_button)

    viewer._render_context_action(_docker_snapshot(), source=source)

    assert link_button.call_args.args[0] == expected_label


def test_context_action_fallback_remains_available(monkeypatch):
    link_button = Mock()
    monkeypatch.setattr(viewer.st, "link_button", link_button)

    viewer._render_context_action(
        {"url": "https://github.com/example/fallback"},
        source="Docker Build",
    )

    link_button.assert_called_once_with(
        "Open GitHub for investigation",
        "https://github.com/example/fallback",
    )


def _render_viewer(monkeypatch, selection):
    timeline = Mock()
    _configure_viewer_mocks(
        monkeypatch,
        selection,
        Mock(return_value=_docker_snapshot()),
        timeline,
    )

    viewer.render_operational_detail_viewer()

    return timeline.call_args.args[0]


def _complete_execution_snapshot():
    workflow = {
        "name": "CI Pipeline",
        "databaseId": 82,
        "number": 12,
        "status": "completed",
        "conclusion": "success",
        "createdAt": "2026-07-22T08:53:50Z",
        "startedAt": "2026-07-22T08:54:00Z",
        "updatedAt": "2026-07-22T08:56:00Z",
        "headBranch": "main",
        "headSha": "1234567890abcdef",
        "url": "https://github.com/example/actions/runs/82",
    }
    jobs = [
        {
            "name": "linting",
            "status": "completed",
            "conclusion": "success",
            "startedAt": "2026-07-22T08:54:01Z",
            "completedAt": "2026-07-22T08:54:30Z",
            "steps": [
                {
                    "name": "Checkout",
                    "status": "completed",
                    "conclusion": "success",
                    "startedAt": "2026-07-22T08:54:01Z",
                    "completedAt": "2026-07-22T08:54:05Z",
                },
                {
                    "name": "Run Ruff (Linting)",
                    "status": "completed",
                    "conclusion": "success",
                    "startedAt": "2026-07-22T08:54:10Z",
                    "completedAt": "2026-07-22T08:54:15Z",
                },
                {
                    "name": "Run Bandit (Security)",
                    "status": "completed",
                    "conclusion": "success",
                    "startedAt": "2026-07-22T08:54:20Z",
                    "completedAt": "2026-07-22T08:54:25Z",
                },
            ],
        },
        {
            "name": "test",
            "status": "completed",
            "conclusion": "success",
            "startedAt": "2026-07-22T08:54:31Z",
            "completedAt": "2026-07-22T08:55:00Z",
            "steps": [
                {
                    "name": "Checkout",
                    "status": "completed",
                    "conclusion": "success",
                    "startedAt": "2026-07-22T08:54:31Z",
                    "completedAt": "2026-07-22T08:54:35Z",
                },
                {
                    "name": "Run Tests",
                    "status": "completed",
                    "conclusion": "success",
                    "startedAt": "2026-07-22T08:54:40Z",
                    "completedAt": "2026-07-22T08:54:55Z",
                },
            ],
        },
        {
            "name": "build",
            "status": "completed",
            "conclusion": "success",
            "startedAt": "2026-07-22T08:55:01Z",
            "completedAt": "2026-07-22T08:55:55Z",
            "steps": [
                {
                    "name": "Checkout",
                    "status": "completed",
                    "conclusion": "success",
                    "startedAt": "2026-07-22T08:55:01Z",
                    "completedAt": "2026-07-22T08:55:05Z",
                },
                {
                    "name": "Login to GitHub Container Registry",
                    "status": "completed",
                    "conclusion": "success",
                    "startedAt": "2026-07-22T08:55:10Z",
                    "completedAt": "2026-07-22T08:55:15Z",
                },
                {
                    "name": "Build and push",
                    "status": "completed",
                    "conclusion": "success",
                    "startedAt": "2026-07-22T08:55:20Z",
                    "completedAt": "2026-07-22T08:55:50Z",
                },
            ],
        },
    ]
    hierarchy = {
        "availability": "available",
        "workflow": workflow,
        "jobs": jobs,
    }
    return {
        "state": "Healthy",
        "branch": "main",
        "workflow": workflow,
        "github_actions": hierarchy,
        "docker_build": viewer._project_docker_build(
            hierarchy,
            job_name="build",
            step_name="Build and push",
        ),
        "events": viewer._build_operational_events([workflow]),
        "last_update": workflow["updatedAt"],
        "refreshed_at": "2026-07-22T08:56:05Z",
        "url": workflow["url"],
    }


def _configure_viewer_mocks(
    monkeypatch,
    selection,
    snapshot_loader,
    timeline=None,
):
    local_event = _event(
        "2026-07-22T08:51:00Z",
        "Branch: main",
        1,
        source="GI",
    )
    github_events = [
        _event(
            "2026-07-22T08:52:00Z",
            "GitHub healthy",
            1,
            source="GH",
        ),
        _event(
            "2026-07-22T08:53:00Z",
            "CI Pipeline running",
            2,
            source="CI",
        ),
        local_event,
    ]
    monkeypatch.setattr(viewer, "render_component_header", Mock())
    monkeypatch.setattr(viewer, "_load_github_status", snapshot_loader)
    monkeypatch.setattr(
        viewer,
        "_load_local_repository_events",
        Mock(return_value=[local_event]),
    )
    monkeypatch.setattr(
        viewer,
        "_build_github_feed",
        Mock(return_value=github_events),
    )
    monkeypatch.setattr(viewer, "_render_event_timeline", timeline or Mock())
    monkeypatch.setattr(viewer, "_render_context_action", Mock())
    monkeypatch.setattr(viewer.st, "selectbox", Mock(return_value=selection))
    monkeypatch.setattr(viewer.st, "session_state", {})


def _event(timestamp, message, order, *, source="DB"):
    return OperationalEvent(
        timestamp=timestamp,
        source_identifier=source,
        source_abbreviation=source,
        category="test",
        status="INFO",
        icon="ℹ",
        message=message,
        order=order,
        event_id=f"{source}:{message}",
    )


class _PipelineColumn:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class _PipelineStreamlit:
    def __init__(self):
        self.session_state = {}
        self.rerun = Mock()

    def subheader(self, *args, **kwargs):
        return None

    def caption(self, *args, **kwargs):
        return None

    def columns(self, specification, **kwargs):
        count = specification if isinstance(specification, int) else len(specification)
        return [_PipelineColumn() for _ in range(count)]

    def button(self, label, **kwargs):
        return label.startswith("Build")
