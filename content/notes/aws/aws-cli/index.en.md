---
title: AWS CLI Quick Reference
description: AWS CLI setup, profiles, S3, EC2, and IAM commands.
lastmod: 2026-07-11T00:00:00+08:00
weight: 120
menu:
  notes:
    name: AWS CLI
    identifier: notes-aws-cli
    parent: notes-aws
    weight: 20
---

{{< note title="Version and safety scope" >}}

**Last reviewed: July 11, 2026**

This is a general command reference, not a version-pinned runbook. Check the installed version, current official documentation, and the target account, host, and path before use. Commands that deploy, destroy, delete, prune, sync, upgrade, or change system settings can cause cost, downtime, or data loss; preview changes and back up where appropriate.

{{< /note >}}

{{< note title="Install and configure" >}}

```bash
brew install awscli
aws --version
aws configure
aws configure --profile production
aws configure list --profile production
aws sts get-caller-identity --profile production
```

Use named profiles for production or customer accounts. Avoid long-lived credentials in shell history or shared notes.

{{< /note >}}

{{< note title="S3 operations" >}}

```bash
aws s3 ls
aws s3 ls s3://example-bucket --recursive --human-readable --summarize
aws s3 cp ./dist s3://example-bucket/dist --recursive
aws s3 sync ./public s3://example-bucket --delete
aws s3api head-object --bucket example-bucket --key path/file.txt
```

Prefer `sync --delete` only when the bucket path is dedicated to that deployment target.

{{< /note >}}

{{< note title="EC2 and IAM checks" >}}

```bash
aws ec2 describe-instances --query 'Reservations[].Instances[].{id:InstanceId,state:State.Name,type:InstanceType}'
aws ec2 describe-security-groups --group-ids sg-xxxxxxxx
aws iam get-user
aws iam list-attached-user-policies --user-name example-user
```

For audits, start from `sts get-caller-identity` so the account and role are explicit before changing anything.

{{< /note >}}
