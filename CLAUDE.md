# aws-deploy

## Purpose

- This is a sandbox to experiment with and learn about deploying applications to AWS. It is not production.
- SAM is the current deployment tool, not the subject. Other tools or approaches may be tried here.
- Explain the AWS/SAM mechanism behind each change, not just the fix, since learning is the goal.
- Favor approaches that show how deployment works over shortcuts that hide it.
- Warn before running anything that creates billable AWS resources (`sam deploy`, `sam sync`).

## Layout

- uv workspace: each Lambda lives in `apps/<name>/`, shared code in `packages/`.
- Each app owns its `src/`, `tests/`, `events/`, `pyproject.toml` and `Makefile`.

## Build

- Deliberate: every function uses `BuildMethod: makefile`, because SAM's pip builder ignores `uv.lock` and `packages/`.
- One Makefile per app, with a target named `build-<LogicalId>`. SAM runs it; nobody calls make by hand.
- `samconfig.toml` sets `build_in_source` so the Makefile can reach the workspace root. Do not remove it.
- `make` is pinned in mise (`conda:make`) only because SAM needs it; it is not installed system-wide.

## Toolchain

- All tools are pinned in `mise.toml`; uv manages Python dependencies.
- Python stays on 3.14 to match an available Lambda runtime, even though mise offers 3.15.
- No root mise tasks yet; deciding later whether to add them.

## Testing

- Integration tests need a deployed stack and `AWS_SAM_STACK_NAME`; run only `apps/*/tests/unit` by default.
