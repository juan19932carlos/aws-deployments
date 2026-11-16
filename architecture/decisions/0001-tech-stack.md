# 0001. Tech stack

- **Status:** Accepted
- **Date:** 2026-11-16

## Context

The project is a sandbox to learn how to deploy applications to AWS. It started from `sam init` (Python Hello World). We want a reproducible toolchain and a layout that can grow to several functions with shared code.

## Decision

| Area | Choice | Rejected | Why |
| --- | --- | --- | --- |
| Toolchain | mise, every tool pinned to an exact version | System packages, fnm, pip installs | One file pins aws-cli, aws-sam, Python, uv, make and Node, so the setup is reproducible. |
| Language | Python 3.14 | Python 3.15 | The local version must match a Lambda runtime AWS offers. |
| Python packages | uv workspace: `apps/*` and `packages/*` | `sam init` layout with `requirements.txt` per function | One lock file, shared code in `packages/`, one `pyproject.toml` per app. |
| Deployment tool | AWS SAM | CDK, plain CloudFormation, Terraform | It is what the tutorial being followed uses. It is the current tool, not the subject: others may be tried later. |
| Lambda build | `BuildMethod: makefile`, one Makefile per app, built with uv | SAM's default pip builder | The pip builder ignores `uv.lock` and cannot bundle workspace packages. The Makefile is SAM's only custom hook. |

## Consequences

- `make` must be on `PATH` for `sam build`, so it is pinned in mise (`conda:make`).
- `samconfig.toml` sets `build_in_source`. Without it SAM copies the app to a temp folder and the Makefile cannot reach the workspace root.
- A new function needs its own `apps/<name>/` with a Makefile target `build-<LogicalId>`.
