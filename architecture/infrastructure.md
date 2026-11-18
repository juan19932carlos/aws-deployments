# Infrastructure

The stack as defined in `template.yaml`. Stack name: `aws-deploy-practice`.

`template-cfn.yaml` deploys the same stack with the AWS CLI instead of the SAM CLI. It differs only in where the code comes from:

| Function | `template.yaml` (SAM CLI) | `template-cfn.yaml` (AWS CLI) |
| --- | --- | --- |
| `HelloWorldFunction` | `apps/hello_world/`, built by `sam build` | `build/HelloWorldFunction/`, built by hand with the Makefile |
| `PreTrafficHook` | Inline code | `apps/pre_traffic_hook/src/`, no build step |

## Request path

```mermaid
flowchart LR
    Client([Client]) -->|GET /hello| Api[API Gateway REST<br/>implicit, stage Prod]
    Api --> Alias{{Alias live}}
    Alias -->|old weight| VOld[Version N]
    Alias -->|new weight| VNew[Version N+1]
    VOld & VNew --> Fn[HelloWorldFunction<br/>python3.14, 128 MB, X-Ray on]
```

- API Gateway calls the `live` alias, never `$LATEST`.
- `AutoPublishAlias: live` publishes a new version on every deploy with changed code.

## Gradual deployment

```mermaid
sequenceDiagram
    participant CFN as CloudFormation
    participant CD as CodeDeploy
    participant Hook as PreTrafficHook
    participant Alias as Alias live
    participant Alarm as ErrorsAlarm
    CFN->>CD: new version published
    CD->>Hook: invoke (DeploymentId, HookExecutionId)
    Hook->>CD: PutLifecycleEventHookExecutionStatus
    alt Succeeded
        CD->>Alias: 10% to new version
        CD->>Alarm: check state for 5 minutes
        CD->>Alias: remaining 90% to new version
    else Failed or alarm in ALARM
        CD->>Alias: roll back to old version
    end
```

| Resource | Type | Purpose |
| --- | --- | --- |
| `HelloWorldFunction` | `AWS::Serverless::Function` | The app, built from `apps/hello_world` |
| `ErrorsAlarm` | `AWS::CloudWatch::Alarm` | `Errors > 0` on the new version behind `live`, 1-minute period |
| `PreTrafficHook` | `AWS::Serverless::Function` | Inline, or `apps/pre_traffic_hook` in `template-cfn.yaml`. Reports `HOOK_STATUS` to CodeDeploy. Named `CodeDeployHook_*` |
| CodeDeploy app, group, role | Created by SAM | Run the `Canary10Percent5Minutes` shift |
