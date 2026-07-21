# Copyright The Kubeflow Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Unit tests for optimizer discovery tools (mocked OptimizerClient)."""

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from kubernetes.client.exceptions import ApiException

from kubeflow_mcp.optimizer.api import discovery

_DISC = "kubeflow_mcp.optimizer.api.discovery"


def _metric(name="accuracy", latest="0.95"):
    return SimpleNamespace(name=name, min="0.5", max=latest, latest=latest)


def _trial(name, status="Complete", params=None, metrics=None):
    trainjob = SimpleNamespace(name=f"{name}-job", status=status)
    return SimpleNamespace(
        name=name,
        parameters=params or {"lr": "0.01"},
        trainjob=trainjob,
        metrics=metrics if metrics is not None else [_metric()],
    )


def _job(name="exp-1", status="Running", trials=None):
    return SimpleNamespace(
        name=name,
        status=status,
        creation_timestamp=datetime(2026, 7, 21, tzinfo=timezone.utc),
        trials=trials if trials is not None else [],
        objectives=[SimpleNamespace(metric="accuracy", direction="maximize")],
        algorithm=SimpleNamespace(random_state=42),
        search_space={},
        trial_config=SimpleNamespace(num_trials=10, parallel_trials=2, max_failed_trials=3),
    )


def _not_found():
    """Build the exception shape the real SDK raises for a missing resource.

    The kubernetes backend wraps a 404 as ``raise RuntimeError(...) from
    ApiException(404)`` — is_k8s_not_found must detect it via ``__cause__``.
    """
    cause = ApiException(status=404, reason="Not Found")
    err = RuntimeError("Failed to get OptimizationJob: default/missing")
    err.__cause__ = cause
    return err


# ─── list_experiments ──────────────────────────────────────────────────────


def test_list_experiments_happy_path():
    client = MagicMock()
    client.list_jobs.return_value = [_job("a", "Running"), _job("b", "Complete")]
    with patch(f"{_DISC}.get_optimizer_client_for_namespace", return_value=client):
        result = discovery.list_experiments()
    assert result["success"] is True
    assert result["data"]["total"] == 2
    names = {e["name"] for e in result["data"]["experiments"]}
    assert names == {"a", "b"}


def test_list_experiments_status_filter():
    client = MagicMock()
    client.list_jobs.return_value = [_job("a", "Running"), _job("b", "Complete")]
    with patch(f"{_DISC}.get_optimizer_client_for_namespace", return_value=client):
        result = discovery.list_experiments(status="Complete")
    assert result["data"]["total"] == 1
    assert result["data"]["experiments"][0]["name"] == "b"


def test_list_experiments_sdk_error():
    client = MagicMock()
    client.list_jobs.side_effect = RuntimeError("boom")
    with patch(f"{_DISC}.get_optimizer_client_for_namespace", return_value=client):
        result = discovery.list_experiments()
    assert result["success"] is False
    assert result["error_code"] == "SDK_ERROR"


# ─── get_experiment ────────────────────────────────────────────────────────


def test_get_experiment_happy_path():
    client = MagicMock()
    client.get_job.return_value = _job(
        "exp-1", "Running", trials=[_trial("t1"), _trial("t2", status="Failed")]
    )
    with patch(f"{_DISC}.get_optimizer_client_for_namespace", return_value=client):
        result = discovery.get_experiment("exp-1")
    assert result["success"] is True
    data = result["data"]
    assert data["name"] == "exp-1"
    assert data["total_trials"] == 2
    assert data["succeeded_trials"] == 1
    assert data["failed_trials"] == 1
    assert len(data["trials"]) == 2
    assert "trial_config" in data


def test_get_experiment_not_found():
    client = MagicMock()
    client.get_job.side_effect = _not_found()
    with patch(f"{_DISC}.get_optimizer_client_for_namespace", return_value=client):
        result = discovery.get_experiment("missing")
    assert result["success"] is False
    assert result["error_code"] == "RESOURCE_NOT_FOUND"


def test_get_experiment_invalid_name():
    result = discovery.get_experiment("Invalid_Name!")
    assert result["success"] is False
    assert result["error_code"] == "VALIDATION_ERROR"


# ─── get_experiment_status ─────────────────────────────────────────────────


def test_get_experiment_status_counts():
    client = MagicMock()
    client.get_job.return_value = _job(
        "exp-1",
        "Running",
        trials=[
            _trial("t1", "Complete"),
            _trial("t2", "Running"),
            _trial("t3", "Failed"),
        ],
    )
    with patch(f"{_DISC}.get_optimizer_client_for_namespace", return_value=client):
        result = discovery.get_experiment_status("exp-1")
    data = result["data"]
    assert data["status"] == "Running"
    assert data["total_trials"] == 3
    assert data["running_trials"] == 1
    assert data["succeeded_trials"] == 1
    assert data["failed_trials"] == 1


def test_get_experiment_status_not_found():
    client = MagicMock()
    client.get_job.side_effect = _not_found()
    with patch(f"{_DISC}.get_optimizer_client_for_namespace", return_value=client):
        result = discovery.get_experiment_status("missing")
    assert result["error_code"] == "RESOURCE_NOT_FOUND"


# ─── get_trial ─────────────────────────────────────────────────────────────


def test_get_trial_found():
    client = MagicMock()
    client.get_job.return_value = _job("exp-1", trials=[_trial("t1"), _trial("t2")])
    with patch(f"{_DISC}.get_optimizer_client_for_namespace", return_value=client):
        result = discovery.get_trial("t2", experiment="exp-1")
    assert result["success"] is True
    assert result["data"]["name"] == "t2"
    assert result["data"]["experiment"] == "exp-1"


def test_get_trial_missing_trial():
    client = MagicMock()
    client.get_job.return_value = _job("exp-1", trials=[_trial("t1")])
    with patch(f"{_DISC}.get_optimizer_client_for_namespace", return_value=client):
        result = discovery.get_trial("nope", experiment="exp-1")
    assert result["success"] is False
    assert result["error_code"] == "RESOURCE_NOT_FOUND"


def test_get_trial_missing_experiment():
    client = MagicMock()
    client.get_job.side_effect = _not_found()
    with patch(f"{_DISC}.get_optimizer_client_for_namespace", return_value=client):
        result = discovery.get_trial("t1", experiment="missing")
    assert result["error_code"] == "RESOURCE_NOT_FOUND"


# ─── get_successful_trials ─────────────────────────────────────────────────


def test_get_successful_trials_filters():
    client = MagicMock()
    client.get_job.return_value = _job(
        "exp-1",
        trials=[
            _trial("t1", "Complete"),
            _trial("t2", "Failed"),
            _trial("t3", "Complete"),
        ],
    )
    with patch(f"{_DISC}.get_optimizer_client_for_namespace", return_value=client):
        result = discovery.get_successful_trials("exp-1")
    assert result["data"]["total"] == 2
    assert {t["name"] for t in result["data"]["trials"]} == {"t1", "t3"}


# ─── list_suggestions ──────────────────────────────────────────────────────


def test_list_suggestions_happy_path():
    api = MagicMock()
    api.list_namespaced_custom_object.return_value = {
        "items": [
            {
                "metadata": {"name": "exp-1"},
                "spec": {"algorithm": {"algorithmName": "random"}, "requests": 5},
                "status": {"suggestionCount": 5, "conditions": [{"type": "Succeeded"}]},
            }
        ]
    }
    with (
        patch(f"{_DISC}.get_custom_objects_api", return_value=api),
        patch(f"{_DISC}.get_optimizer_effective_namespace", return_value="default"),
    ):
        result = discovery.list_suggestions()
    assert result["success"] is True
    assert result["data"]["total"] == 1
    sugg = result["data"]["suggestions"][0]
    assert sugg["algorithm"] == "random"
    assert sugg["condition"] == "Succeeded"


def test_list_suggestions_sdk_error():
    api = MagicMock()
    api.list_namespaced_custom_object.side_effect = RuntimeError("boom")
    with (
        patch(f"{_DISC}.get_custom_objects_api", return_value=api),
        patch(f"{_DISC}.get_optimizer_effective_namespace", return_value="default"),
    ):
        result = discovery.list_suggestions()
    assert result["success"] is False
    assert result["error_code"] == "SDK_ERROR"
