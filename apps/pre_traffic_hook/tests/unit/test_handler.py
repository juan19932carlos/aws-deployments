import os
from unittest import mock

# The module builds its boto3 client at import time, which needs a region.
os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")

from pre_traffic_hook import app  # noqa: E402

EVENT = {"DeploymentId": "d-EXAMPLE111", "LifecycleEventHookExecutionId": "hook-1"}


def test_reports_status_from_env(monkeypatch):
    monkeypatch.setenv("HOOK_STATUS", "Failed")
    with mock.patch.object(app, "codedeploy") as codedeploy:
        app.handler(EVENT, None)
    codedeploy.put_lifecycle_event_hook_execution_status.assert_called_once_with(
        deploymentId="d-EXAMPLE111",
        lifecycleEventHookExecutionId="hook-1",
        status="Failed",
    )
