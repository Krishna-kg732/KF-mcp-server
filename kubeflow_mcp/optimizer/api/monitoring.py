# Copyright The Kubeflow Authors.
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

"""Monitoring tools for Katib experiment tracking and debugging.

SDK methods used:
    - OptimizerClient.get_job()                → get_experiment_trials
    - OptimizerClient.get_best_results()       → get_best_trial
    - OptimizerClient.wait_for_job_status()    → wait_for_experiment
    - OptimizerClient.get_job_logs()           → get_experiment_trial_logs
    - OptimizerClient.get_job_events()         → get_experiment_events
    - CustomObjectsApi                         → get_suggestion (no SDK method)
"""

import logging
from typing import Any

from kubeflow_mcp.common.constants import ErrorCode
from kubeflow_mcp.common.types import ToolError

logger = logging.getLogger(__name__)

_NOT_IMPLEMENTED = ToolError(
    error="Not yet implemented — planned for Phase 2",
    error_code=ErrorCode.SDK_ERROR,
    hint="This tool is registered but not yet implemented. See KEP-34.",
).model_dump()


def get_experiment_trials(
    name: str,
    namespace: str | None = None,
    status: str | None = None,
) -> dict[str, Any]:
    """List trials for a Katib experiment with optional status filter.

    Args:
        name: Experiment name.
        namespace: K8s namespace. Uses default from kubeconfig when omitted.
        status: Optional status filter.

    Returns:
        dict: Response containing list of trials with parameters, metrics, and status.
    """
    return _NOT_IMPLEMENTED


def get_best_trial(
    name: str,
    namespace: str | None = None,
) -> dict[str, Any]:
    """Get the best trial with optimal hyperparameters and metrics.

    Uses ``OptimizerClient.get_best_results()``.

    Args:
        name: Experiment name.
        namespace: K8s namespace. Uses default from kubeconfig when omitted.

    Returns:
        dict: Response containing best hyperparameters and metrics.
    """
    return _NOT_IMPLEMENTED


def get_suggestion(
    name: str,
    namespace: str | None = None,
) -> dict[str, Any]:
    """Get suggestion algorithm status for an experiment.

    Uses CustomObjectsApi directly (no SDK method available).

    Args:
        name: Experiment name (suggestion shares the same name).
        namespace: K8s namespace. Uses default from kubeconfig when omitted.

    Returns:
        dict: Response containing algorithm name, status, and request/reply counts.
    """
    return _NOT_IMPLEMENTED


def wait_for_experiment(
    name: str,
    namespace: str | None = None,
    timeout_seconds: int = 600,
    polling_interval: int = 15,
) -> dict[str, Any]:
    """Block until experiment reaches terminal status (Complete/Failed).

    Uses ``OptimizerClient.wait_for_job_status()``. Timeout is capped
    at 3600 seconds and polling interval has a minimum of 5 seconds.

    Args:
        name: Experiment name.
        namespace: K8s namespace. Uses default from kubeconfig when omitted.
        timeout_seconds: Maximum seconds to wait. Capped at 3600.
        polling_interval: Seconds between status polls. Minimum 5.

    Returns:
        dict: Response containing final experiment status and trial summary.
    """
    return _NOT_IMPLEMENTED


def get_experiment_trial_logs(
    name: str,
    trial: str | None = None,
    namespace: str | None = None,
) -> dict[str, Any]:
    """Get pod logs from an experiment trial.

    Uses ``OptimizerClient.get_job_logs()``. If no trial is specified,
    logs from the current best trial are returned.

    Args:
        name: Experiment name.
        trial: Optional trial name. If omitted, uses the best trial.
        namespace: K8s namespace. Uses default from kubeconfig when omitted.

    Returns:
        dict: Response containing ``logs``, ``trial`` name, and ``failure_patterns``.
    """
    return _NOT_IMPLEMENTED


def get_experiment_events(
    name: str,
    namespace: str | None = None,
) -> dict[str, Any]:
    """Get K8s events for a Katib experiment.

    Uses ``OptimizerClient.get_job_events()``.

    Args:
        name: Experiment name.
        namespace: K8s namespace. Uses default from kubeconfig when omitted.

    Returns:
        dict: Response containing list of events with type, reason, message, timestamp.
    """
    return _NOT_IMPLEMENTED
