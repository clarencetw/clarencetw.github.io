---
title: AWS CDK Tips
description: AWS CDK init、diff、deploy、destroy と実務上の注意点。
lastmod: 2026-07-11T00:00:00+08:00
weight: 110
menu:
  notes:
    name: CDK Tips
    identifier: notes-aws-cdk-tips
    parent: notes-aws
    weight: 10
---

{{< note title="Version と安全範囲" >}}

**最終確認：2026年7月11日**

これは一般的な command reference であり、特定 version に固定した完全な runbook ではありません。実行前に installed version、最新の公式ドキュメント、対象 account／host／path を確認してください。deploy、destroy、delete、prune、sync、upgrade、system setting の変更は、費用、停止、data loss につながる可能性があります。差分を事前確認し、必要に応じて backup を取得してください。

{{< /note >}}

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
