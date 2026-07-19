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

"""Discovery tools for Katib experiments, trials, and suggestions.

SDK methods used:
    - OptimizerClient.list_jobs()    → list_experiments
    - OptimizerClient.get_job()      → get_experiment, get_experiment_status,
                                       get_trial, get_successful_trials
    - CustomObjectsApi               → list_suggestions (no SDK method)
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


def list_experiments(
    namespace: str | None = None,
    status: str | None = None,
) -> dict[str, Any]:
    """List Katib optimization experiments.

    Returns experiments in the target namespace with optional status filtering.

    Args:
        namespace: K8s namespace. Uses default from kubeconfig when omitted.
        status: Optional status filter (Created, Running, Complete, Failed).

    Returns:
        dict: Response containing list of experiments with name, status, trial counts.
    """
    return _NOT_IMPLEMENTED


def get_experiment(
    name: str,
    namespace: str | None = None,
) -> dict[str, Any]:
    """Get full details of a Katib optimization experiment.

    Returns the complete experiment: spec, status, conditions, trials,
    search space, algorithm, and best trial (if available).

    Args:
        name: Experiment name.
        namespace: K8s namespace. Uses default from kubeconfig when omitted.

    Returns:
        dict: Response containing full experiment details.

    Raises:
        ToolError: If experiment not found (``RESOURCE_NOT_FOUND``).
    """
    return _NOT_IMPLEMENTED


def get_experiment_status(
    name: str,
    namespace: str | None = None,
) -> dict[str, Any]:
    """Lightweight status-only check for an experiment.

    Returns only the status string and trial counts — faster than
    ``get_experiment()`` for polling.

    Args:
        name: Experiment name.
        namespace: K8s namespace. Uses default from kubeconfig when omitted.

    Returns:
        dict: Response containing ``status``, ``total_trials``,
              ``running_trials``, ``succeeded_trials``, ``failed_trials``.
    """
    return _NOT_IMPLEMENTED


def get_trial(
    name: str,
    experiment: str,
    namespace: str | None = None,
) -> dict[str, Any]:
    """Get details of a specific trial within an experiment.

    Returns trial parameters, metrics, and status for debugging.
    Extracted from ``OptimizerClient.get_job().trials``.

    Args:
        name: Trial name.
        experiment: Parent experiment name.
        namespace: K8s namespace. Uses default from kubeconfig when omitted.

    Returns:
        dict: Response containing trial parameters, metrics, and status.

    Raises:
        ToolError: If experiment or trial not found (``RESOURCE_NOT_FOUND``).
    """
    return _NOT_IMPLEMENTED


def get_successful_trials(
    name: str,
    namespace: str | None = None,
) -> dict[str, Any]:
    """Get all successful trials with hyperparameters and metrics.

    Returns only trials with a successful status for comparison.
    Useful for finding the best hyperparameter combinations.

    Args:
        name: Experiment name.
        namespace: K8s namespace. Uses default from kubeconfig when omitted.

    Returns:
        dict: Response containing list of successful trials with
              parameters and metrics.
    """
    return _NOT_IMPLEMENTED


def list_suggestions(
    namespace: str | None = None,
) -> dict[str, Any]:
    """List Katib suggestion resources in namespace.

    Suggestions manage the optimization algorithm state. Useful for
    debugging when experiments are stuck. Uses CustomObjectsApi directly
    (no SDK method available).

    Args:
        namespace: K8s namespace. Uses default from kubeconfig when omitted.

    Returns:
        dict: Response containing list of suggestion resources with
              algorithm, status, and request counts.
    """
    return _NOT_IMPLEMENTED
