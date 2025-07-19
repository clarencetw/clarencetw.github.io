---
title: AWS CDK 實用技巧
weight: 110
menu:
  notes:
    name: CDK Tips
    identifier: notes-aws-cdk-tips
    parent: notes-aws
    weight: 10
---

<!-- CDK 常用指令 -->
{{< note title="CDK 常用指令" >}}

```bash
# 初始化新專案
cdk init app --language typescript

# 部署所有 Stack
cdk deploy --all

# 查看差異
cdk diff

# 銷毀資源
cdk destroy
```

{{< /note >}}

<!-- CDK 最佳實踐 -->
{{< note title="CDK 最佳實踐" >}}

1. **使用 Environment 變數**
```typescript
const env = {
  account: process.env.CDK_DEFAULT_ACCOUNT,
  region: process.env.CDK_DEFAULT_REGION,
};
```

2. **標籤管理**
```typescript
Tags.of(this).add('Project', 'MyProject');
Tags.of(this).add('Environment', 'Production');
```

{{< /note >}}