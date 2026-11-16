# Journal 01: Project setup and CodeDeploy configuration
* **Date:** 2026-11-16
* **Main goal:** Set up the SAM project and configure a gradual Lambda deployment with CodeDeploy.

---

## 1. Segment: Project setup
* **Action:** Scaffolded the SAM Hello World app with a mise toolchain, then reorganized it as a uv workspace with `apps/` and `packages/`.
* **Result:** ⚠️ *Not verified*. Nothing has been built or run yet.
* **Finding / Technical note:** SAM only needs the template: each function's `CodeUri` points to its folder, here `apps/hello_world/`.

## 2. Segment: CodeDeploy configuration
* **Action:** Added `AutoPublishAlias: live`, `DeploymentPreference: Linear10PercentEvery1Minute`, an `ErrorsAlarm` and a `PreTrafficHook` to `template.yaml`.
* **Result:** ⚠️ *Not verified*. Not built and not deployed.
* **Finding / Technical note:** The alias `live` points to a published version; CodeDeploy shifts its traffic to the new version and rolls back if the alarm fires or the hook reports `Failed`.

---

## 📌 Summary and Next Steps
* **Key achievements:** Project set up and gradual deployment defined in the template.
* **Technical debt or pending items for tomorrow:** First `sam build` and `sam deploy`.
