# aws-deploy

AWS SAM practice project, organized as a uv workspace.

## Layout

| Path | Purpose |
|---|---|
| `apps/<name>/` | One Lambda function: `src/`, `tests/`, `events/`, `pyproject.toml`, `Makefile` |
| `packages/` | Shared libraries used by apps (workspace members) |
| `template.yaml` | SAM template; each function's `CodeUri` points to its app |
| `mise.toml` | Pinned toolchain: aws-cli, aws-sam, make, Python, uv |

## Usage

```bash
mise install                 # toolchain
uv sync                      # dev environment (.venv)
uv run pytest apps/*/tests/unit   # unit tests
sam build                    # builds each app with uv via its Makefile
sam local invoke HelloWorldFunction -e apps/hello_world/events/event.json
sam deploy --guided
```

Integration tests need a deployed stack:

```bash
AWS_SAM_STACK_NAME=aws-deploy-practice uv run pytest apps/hello_world/tests/integration
```

## Adding a function

1. Create `apps/<name>/` with its own `pyproject.toml` and `src/<name>/`.
2. Copy the `Makefile` and rename the target to `build-<LogicalId>`.
3. Add the function to `template.yaml` with `CodeUri: apps/<name>/` and `Metadata.BuildMethod: makefile`.
