"""CodeDeploy PreTraffic hook: reports a status before any traffic shifts to the new version."""

import os

import boto3

# Created once per execution environment, reused across invocations.
codedeploy = boto3.client("codedeploy")


def handler(event, context):
    # Set HOOK_STATUS to Failed to simulate a failing check and watch CodeDeploy roll back.
    status = os.environ["HOOK_STATUS"]
    print(f"PreTraffic -> {status}")
    codedeploy.put_lifecycle_event_hook_execution_status(
        deploymentId=event["DeploymentId"],
        lifecycleEventHookExecutionId=event["LifecycleEventHookExecutionId"],
        status=status,
    )
