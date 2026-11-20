# Journal 03: First steps with Elastic Beanstalk
* **Date:** 2026-11-20
* **Main goal:** Use Elastic Beanstalk for the first time: deploy the same small JSON app to EC2 and see its deployment policies and a blue/green swap.

---

## 1. Segment: An app for Beanstalk and `eb init`
* **Action:** Added `apps/hello_beanstalk/`: an `application.py` exposing a WSGI callable named `application`, no framework, no `requirements.txt`. Ran `eb init` in that folder with the Python 3.15 platform.
* **Result:** ✅ *Worked*. `eb init` created the Application `hello_beanstalk` and wrote `.elasticbeanstalk/config.yml`, but in `us-west-2`.
* **Finding / Technical note:** The EB Python platform runs gunicorn with `application:application` by default: module `application.py` at the bundle root, callable `application`. Flask is just one way to build that object.
* **Finding / Technical note:** AWS fixes which runtimes exist: each platform branch ("Python 3.15 running on 64bit Amazon Linux 2023") is an AMI AWS maintains. `eb platform list` shows them; 3.15 was the newest.
* **Finding / Technical note:** `eb init`'s interactive prompt defaults to Oregon (`us-west-2`), unlike the rest of this repo. The console shows nothing in Virginia; switch region to see the app.
* **Finding / Technical note:** Run without `--profile`, `eb init` asked for an access key and secret. It was cancelled: answering would store long-lived keys instead of using `aws login`.
* **Finding / Technical note:** The EB CLI needs `botocore[crt]` to use `aws login` sessions. Even then it failed with `LoginError`: the session had expired, and a fresh `aws login` fixed it.
* **Finding / Technical note:** Beanstalk has three levels: Application, Application versions (a label pointing to a zip in S3) and Environments (EC2 running one version).

## 2. Segment: `eb create frases-blue --single`
* **Action:** Created a single-instance environment and looked at what Beanstalk built.
* **Result:** ✅ *Worked*. In about 2 minutes: security group, Elastic IP, one EC2, the `awseb-e-…-stack` CloudFormation stack, and a public URL under `elasticbeanstalk.com`.
* **Finding / Technical note:** A single-instance environment has no load balancer: the environment's CNAME points to the instance's Elastic IP.
* **Finding / Technical note:** The EB CLI zipped the whole app folder, not a `git archive` (`sc: null` in `config.yml`). The zip carried `pyproject.toml`, `tests/` and `__pycache__/`; an `.ebignore` would trim it.

## 3. Segment: All at once vs Immutable
* **Action:** Changed the message and ran `eb deploy` with the default policy. Then added `.ebextensions/deploy.config` with `DeploymentPolicy: Immutable` and deployed again.
* **Result:** ✅ *Worked*. All at once took about 20 seconds on the same instance. Immutable succeeded but took about 9 minutes and ended on a new instance ID.
* **Finding / Technical note:** With one instance and no load balancer, the policies look alike: nothing to split into batches and no traffic to shift. That is why the first deploy showed no strategy at all.
* **Finding / Technical note:** On EC2 the policies move instances, not traffic. Rolling takes batches out of service; Rolling with additional batch adds a batch first, so capacity never drops.
* **Finding / Technical note:** Immutable timeline: temporary ASG in a second stack, new instance, about 3.5 minutes of health checks, attach to the permanent ASG, post-deployment config, then terminate the old instance.
* **Finding / Technical note:** Booting the EC2 took under a minute. Most of the time went to health verification and CloudFormation updates, which Beanstalk does for safety.
* **Finding / Technical note:** Only Traffic splitting resembles the Lambda canary: it sends a percentage of traffic to new instances, so it needs a load balancer.
* **Finding / Technical note:** The EB CLI stopped after 10 minutes with `TimeoutError`, but the deploy went on in AWS. The CLI only polls events; `--timeout` or `--nohang` change that, and `eb abort` cancels.
* **Finding / Technical note:** `.ebextensions/*.config` travels inside the zip and is applied on each deploy. A value set in the console or API wins over it for that option.

## 4. Segment: A failed Immutable deploy and `eb abort`
* **Action:** Cloned the environment with `eb clone frases-blue -n frases-green`, then ran `eb deploy` meaning green, but it went to blue, still with Immutable.
* **Result:** ⚠️ *With warnings*. The new instance booted fine but never answered the deploy command. After about 15 minutes `eb abort` rolled it back. The cause was not found.
* **Finding / Technical note:** `eb deploy` without a name targets the default environment in `config.yml`, which was blue.
* **Finding / Technical note:** Events showed "have not responded in the allowed command timeout", then "Terminating new instances and temporary Auto Scaling group". Blue served the old version the whole time.
* **Finding / Technical note:** Abort waits for the current non-cancellable step to finish. After the rollback, health stayed Yellow for a while with "Application update failed", though the instance was Ok.
* **Finding / Technical note:** Switched `deploy.config` back to `AllAtOnce`, written explicitly. Removing an option from `.ebextensions` may not reset it.

## 5. Segment: Blue/green with `eb swap`
* **Action:** Deployed a new message to green and ran `eb swap frases-blue -n frases-green` several times, watching a `curl` loop that printed the response and the resolved IP.
* **Result:** ✅ *Worked*. The URL stayed the same while its IP moved between the two instances, and the response changed with it. A second swap is the rollback.
* **Finding / Technical note:** The swap exchanges the two environments' CNAMEs in AWS-managed DNS. It does not move instances or deploy code, and it is all or nothing, unlike the Lambda canary.
* **Finding / Technical note:** Clients switch when their DNS cache expires (TTL 60 s), not at the swap. The browser kept showing the old text because it reused its open connection to the old IP.
* **Finding / Technical note:** So the old environment should live on after a swap until traffic stops reaching it. Blue/green fits changes no deployment policy can do, like a platform change.
* **Finding / Technical note:** The destination flag of `eb swap` is `-n` (`--destination_name`).

## 6. Segment: Reading only: `env.yaml`, `cron.yaml`, saved configurations, database
* **Action:** Read about the optional pieces without deploying them.
* **Result:** ✅ *Read*. Nothing was created.
* **Finding / Technical note:** "Stack" in `env.yaml` means solution stack, the platform, not a CloudFormation stack. The file sits in the bundle, so any deploy of that version creates the same environment.
* **Finding / Technical note:** `.elasticbeanstalk/config.yml` is local EB CLI config and never reaches AWS; `env.yaml` does.
* **Finding / Technical note:** `cron.yaml` only works in Worker environments: Beanstalk puts a message in the SQS queue on schedule and the `sqsd` daemon POSTs it to the app.
* **Finding / Technical note:** A database created from the environment lives in its stack and dies with it. The deletion policy (snapshot, retain, delete) decides what stays; production creates RDS outside Beanstalk.

## 7. Segment: Cleanup
* **Action:** Ran `eb terminate` on both environments.
* **Result:** ⚠️ *With warnings*. Started; the end state was not checked in this session.
* **Finding / Technical note:** Terminate removes environments, not the Application or its versions. The `elasticbeanstalk-us-west-2-<account>` bucket stays.

---

## 📌 Summary and Next Steps
* **Key achievements:** First Beanstalk app deployed; All at once, Immutable, abort with rollback and a CNAME swap all seen live, with their trade-offs.
* **Technical debt or pending items for tomorrow:**
  * Check that both environments and their `awseb-…` stacks are gone; decide whether to delete the Application and the S3 bucket.
  * Decide whether to keep Beanstalk in `us-west-2` or move it to `us-east-1` like the rest.
  * Add an `.ebignore` so the bundle carries only the app.
  * Find out why the second Immutable instance never answered the deploy command.
  * See Rolling and Traffic splitting, which need a load-balanced environment.
