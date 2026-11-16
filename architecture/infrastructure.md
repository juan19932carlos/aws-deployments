# Infrastructure

The stack as defined in `template.yaml`. Stack name: `aws-deploy-practice`.

## Request path

```mermaid
flowchart LR
    Client([Client]) -->|GET /hello| Api[API Gateway REST<br/>implicit, stage Prod]
    Api --> Alias{{Alias live}}
    Alias -->|old weight| VOld[Version N]
    Alias -->|new weight| VNew[Version N+1]
    VOld & VNew --> Fn[HelloWorldFunction<br/>python3.14, X-Ray on]
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
        loop every minute, +10%
            CD->>Alias: shift weight to new version
            CD->>Alarm: check state
        end
    else Failed or alarm in ALARM
        CD->>Alias: roll back to old version
    end
```

| Resource | Type | Purpose |
| --- | --- | --- |
| `HelloWorldFunction` | `AWS::Serverless::Function` | The app, built from `apps/hello_world` |
| `ErrorsAlarm` | `AWS::CloudWatch::Alarm` | `Errors > 0` on the new version behind `live`, 1-minute period |
| `PreTrafficHook` | `AWS::Serverless::Function` | Inline. Reports `HOOK_STATUS` to CodeDeploy. Named `CodeDeployHook_*` |
| CodeDeploy app, group, role | Created by SAM | Run the `Linear10PercentEvery1Minute` shift |
