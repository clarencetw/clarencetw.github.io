---
title: AWS CLI クイックリファレンス
description: AWS CLI setup、profile、S3、EC2、IAM の基本コマンド。
weight: 120
menu:
  notes:
    name: AWS CLI
    identifier: notes-aws-cli
    parent: notes-aws
    weight: 20
---

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
