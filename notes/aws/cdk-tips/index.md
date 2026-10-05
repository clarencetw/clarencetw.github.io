---
title: "AWS CDK 實用技巧"
url: "https://clarence.tw/notes/aws/cdk-tips/"
language: "zh-tw"
---

# AWS CDK 實用技巧

AWS CDK init、diff、deploy、destroy 與實務習慣。

## 版本與安全範圍

**最後檢視：2026-07-11**

這是通用指令速查，不是綁定特定版本的完整 runbook。執行前請確認工具版本、目前官方文件、帳號／主機／路徑等目標；涉及 deploy、destroy、delete、prune、sync、upgrade 或系統設定變更的指令，可能造成費用、停機或資料遺失，請先預覽差異並視需要備份。

<!-- CDK 常用指令 -->
## CDK 常用指令

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

<!-- CDK 最佳實踐 -->
## CDK 最佳實踐

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
