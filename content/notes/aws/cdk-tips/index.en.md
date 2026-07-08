---
title: AWS CDK Tips
description: AWS CDK init, diff, deploy, destroy, and practical habits.
weight: 110
menu:
  notes:
    name: CDK Tips
    identifier: notes-aws-cdk-tips
    parent: notes-aws
    weight: 10
---

{{< note title="Daily commands" >}}

```bash
cdk init app --language typescript
cdk synth
cdk diff
cdk deploy
cdk deploy --all
cdk destroy
```

Run `cdk diff` before deployment and keep environment-specific values out of construct code.

{{< /note >}}

{{< note title="Environment and tags" >}}

```typescript
const env = {
  account: process.env.CDK_DEFAULT_ACCOUNT,
  region: process.env.CDK_DEFAULT_REGION,
};

Tags.of(this).add("Project", "example");
Tags.of(this).add("Environment", "production");
```

Use tags for ownership, cost review, and incident tracing.

{{< /note >}}
