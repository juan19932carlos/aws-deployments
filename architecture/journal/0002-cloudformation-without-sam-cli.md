# Journal 02: Deploying with CloudFormation instead of the SAM CLI
* **Date:** 2026-11-18
* **Main goal:** Deploy the same stack with the AWS CLI alone, to see what the SAM CLI was doing behind `sam build` and `sam deploy`.

---

## 1. Segment: A copy of the template for the AWS CLI
* **Action:** Copied `template.yaml` to `template-cfn.yaml`, pointed `HelloWorldFunction`'s `CodeUri` at the build output and dropped `Metadata: BuildMethod`.
* **Result:** ✅ *Worked*. Both templates coexist: SAM keeps `template.yaml`, the AWS CLI uses `template-cfn.yaml`.
* **Finding / Technical note:** The SAM CLI is not needed to deploy a SAM template. `Transform: AWS::Serverless-2016-10-31` is a macro that runs inside CloudFormation, on the server.
* **Finding / Technical note:** `BuildMethod` is read only by `sam build`. CloudFormation stores resource `Metadata` but ignores it, so leaving it would change nothing.
* **Finding / Technical note:** The two templates need different `CodeUri`s. SAM builds from the source folder; `aws cloudformation package` only zips, so it needs the already built folder.
* **Finding / Technical note:** The build was done by hand: the app's Makefile with `ARTIFACTS_DIR` set to `build/HelloWorldFunction`. The Makefile does not empty that folder; `sam build` did that before.

## 2. Segment: `aws cloudformation package` zipped the whole repo
* **Action:** Ran `aws cloudformation package` against `template-cfn.yaml`, with the bucket SAM had created for `resolve_s3`.
* **Result:** ❌ *Failed*. It uploaded `HelloWorldFunction` (1705 bytes), then hung while building a 794 MB zip from the repo root, `node_modules` included. It was stopped before uploading it.
* **Finding / Technical note:** The cause was `PreTrafficHook`. It has `InlineCode` and no `CodeUri`, and `package` defaults a missing `CodeUri` to the template's folder. The SAM CLI knows `InlineCode` and skips it.
* **Finding / Technical note:** Without `samconfig.toml`, nothing passes `--profile`: the first run failed with "Unable to locate credentials". The bucket name came from the `aws-sam-cli-managed-default` stack outputs.
* **Finding / Technical note:** Workaround used: zipped the build by hand, uploaded it with `aws s3 cp` and wrote its `s3://` URI as the `CodeUri`.

## 3. Segment: Short-form `!GetAtt` failed outside the SAM CLI
* **Action:** Ran `aws cloudformation deploy` with `CAPABILITY_IAM CAPABILITY_AUTO_EXPAND`.
* **Result:** ❌ *Failed*, then ✅ after a fix. `ErrorsAlarm` failed with "Requested attribute Version.Version does not exist in schema for AWS::Lambda::Function", and the stack rolled back.
* **Finding / Technical note:** `CAPABILITY_AUTO_EXPAND` is required because a transform adds resources you do not see. `sam deploy` passed it without saying so.
* **Finding / Technical note:** The template SAM had uploaded showed `!GetAtt HelloWorldFunction.Version.Version` already as a list. Writing `!GetAtt [HelloWorldFunction, Version.Version]` made the transform resolve it.
* **Finding / Technical note:** The rollback also restored the function's code. `UPDATE_ROLLBACK_COMPLETE` is a stable state; the next deploy starts from it.

## 4. Segment: Change sets as a plan
* **Action:** Ran `deploy` with `--no-execute-changeset`, reviewed the change set, then ran `execute-change-set`.
* **Result:** ✅ *Worked*. The stack reached `UPDATE_COMPLETE` after the CodeDeploy canary; the code came from the hand-uploaded zip.
* **Finding / Technical note:** A change set is the diff CloudFormation computes after running the transform. It is stored on the stack, so it can be read with `describe-change-set` and `get-template --change-set-name`.
* **Finding / Technical note:** Creating a change set does not touch the stack: it stayed in `UPDATE_ROLLBACK_COMPLETE` until the change set was executed.
* **Finding / Technical note:** `aws cloudformation deploy` executes without asking. The confirmation in `sam deploy` came from `confirm_changeset = true` in `samconfig.toml`.

## 5. Segment: The hook in its own folder, then `package` + `deploy`
* **Action:** Moved the hook's code to `apps/pre_traffic_hook/`, set its `CodeUri`, put the build folder back as `HelloWorldFunction`'s `CodeUri`, then ran `package` and `deploy`.
* **Result:** ✅ *Worked*. `package` finished in seconds; the stack reached `UPDATE_COMPLETE` after the canary, with the hook running from its own folder.
* **Finding / Technical note:** `package` names each object by the zip's MD5. The unchanged build gave the same hash as before, so only the hook (631 bytes) was uploaded.
* **Finding / Technical note:** The function got a new Version, and a new canary, with the same code: only its `CodeUri` changed, from the hand-written key to the hash.
* **Finding / Technical note:** The hook needs no build: its only dependency, `boto3`, ships with the Lambda runtime. `package` zips `src/` as is, so a stray `__pycache__` changes the hash.
* **Finding / Technical note:** On each update, CloudFormation logged `DELETE_SKIPPED` for the old Version: it leaves the stack, but is not deleted.

---

## 📌 Summary and Next Steps
* **Key achievements:** The stack deployed with the AWS CLI alone (`package`, `deploy`, change sets), without the SAM CLI.
* **Technical debt or pending items for tomorrow:** `template.yaml` still has the hook inline, so its code is duplicated. The `hello_world` unit test still expects the old greeting. The `cache-keys` root fix is still pending.
