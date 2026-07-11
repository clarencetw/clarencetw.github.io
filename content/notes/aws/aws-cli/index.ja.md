---
title: AWS CLI クイックリファレンス
description: AWS CLI setup、profile、S3、EC2、IAM の基本コマンド。
lastmod: 2026-07-11T00:00:00+08:00
weight: 120
menu:
  notes:
    name: AWS CLI
    identifier: notes-aws-cli
    parent: notes-aws
    weight: 20
---

{{< note title="Version と安全範囲" >}}

**最終確認：2026年7月11日**

これは一般的な command reference であり、特定 version に固定した完全な runbook ではありません。実行前に installed version、最新の公式ドキュメント、対象 account／host／path を確認してください。deploy、destroy、delete、prune、sync、upgrade、system setting の変更は、費用、停止、data loss につながる可能性があります。差分を事前確認し、必要に応じて backup を取得してください。

{{< /note >}}

{{< note title="Install と configure" >}}

```bash
brew install awscli
aws --version
aws configure
aws configure --profile production
aws configure list --profile production
aws sts get-caller-identity --profile production
```

production や customer account では named profile を使う。長期 credential を shell history や共有メモに残さない。

{{< /note >}}

{{< note title="S3 operations" >}}

```bash
aws s3 ls
aws s3 ls s3://example-bucket --recursive --human-readable --summarize
aws s3 cp ./dist s3://example-bucket/dist --recursive
aws s3 sync ./public s3://example-bucket --delete
aws s3api head-object --bucket example-bucket --key path/file.txt
```

`sync --delete` は、その bucket path が deployment target 専用だと確認してから使う。

{{< /note >}}

{{< note title="EC2 と IAM checks" >}}

```bash
aws ec2 describe-instances --query 'Reservations[].Instances[].{id:InstanceId,state:State.Name,type:InstanceType}'
aws ec2 describe-security-groups --group-ids sg-xxxxxxxx
aws iam get-user
aws iam list-attached-user-policies --user-name example-user
```

audit では最初に `sts get-caller-identity` を確認して、account と role を明示する。

{{< /note >}}
