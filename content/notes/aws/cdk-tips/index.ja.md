---
title: AWS CDK Tips
description: AWS CDK init、diff、deploy、destroy と実務上の注意点。
weight: 110
menu:
  notes:
    name: CDK Tips
    identifier: notes-aws-cdk-tips
    parent: notes-aws
    weight: 10
---

{{< note title="日常コマンド" >}}

```bash
cdk init app --language typescript
cdk synth
cdk diff
cdk deploy
cdk deploy --all
cdk destroy
```

deployment 前には `cdk diff` を確認し、環境ごとの値は construct code に直接書かない。

{{< /note >}}

{{< note title="Environment と tags" >}}

```typescript
const env = {
  account: process.env.CDK_DEFAULT_ACCOUNT,
  region: process.env.CDK_DEFAULT_REGION,
};

Tags.of(this).add("Project", "example");
Tags.of(this).add("Environment", "production");
```

tags は ownership、cost review、incident tracing に使う。

{{< /note >}}
