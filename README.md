# AWS Deploy

A sandbox to learn how applications get deployed to AWS. It is not production: things here are tried, broken and written down.

The point is the mechanism, not the result. Each step records what AWS actually does underneath, not only the command that made it work.

## What is being explored

- **Packaging a Lambda.** How a function and its dependencies become a deployment artifact, and how to plug a custom build (uv, through a Makefile) into AWS SAM.
- **Infrastructure as code.** A SAM template that expands into CloudFormation: an API Gateway endpoint in front of a Python Lambda.
- **Gradual deployment.** Shifting traffic between Lambda versions with an alias and CodeDeploy, guarded by a pre-traffic hook and a CloudWatch alarm that roll back on failure.
- **Tooling around it.** A reproducible toolchain, and a documentation site published to GitHub Pages by GitHub Actions.

SAM is the current deployment tool, not the subject. Other tools, such as CDK or Terraform, may be tried here later.

## How it is documented

Everything is written as the work happens, in `architecture/`:

- **Decisions:** the lasting choices (ADRs), each with the option that was rejected and why.
- **Journal:** one entry per working day, split into segments. Each one says what was tried, whether it worked, and what was learned.
- **Infrastructure:** the stack as it is defined today, with diagrams.

The documentation site is published at <https://juan19932carlos.github.io/aws-deployments/>.

## Stack

| Area | Tool |
| --- | --- |
| Deployment | AWS SAM on CloudFormation, CodeDeploy for traffic shifting |
| Runtime | Python 3.14 on AWS Lambda |
| Python packages | uv workspace: one app per Lambda in `apps/`, shared code in `packages/` |
| Toolchain | mise, every tool pinned to an exact version |
| Docs | Docusaurus in a pnpm workspace, deployed to GitHub Pages |
