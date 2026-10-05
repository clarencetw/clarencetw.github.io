---
title: "AWS CDK Tips"
url: "https://clarence.tw/en/notes/aws/cdk-tips/"
language: "en"
---

# AWS CDK Tips

AWS CDK init, diff, deploy, destroy, and practical habits.

## Version and safety scope

**Last reviewed: July 11, 2026**

This is a general command reference, not a version-pinned runbook. Check the installed version, current official documentation, and the target account, host, and path before use. Commands that deploy, destroy, delete, prune, sync, upgrade, or change system settings can cause cost, downtime, or data loss; preview changes and back up where appropriate.

## Daily commands

```bash
cdk init app --language typescript
cdk synth
cdk diff
cdk deploy
cdk deploy --all
cdk destroy
```

Run `cdk diff` before deployment and keep environment-specific values out of construct code.

## Environment and tags

```typescript
const env = {
  account: process.env.CDK_DEFAULT_ACCOUNT,
  region: process.env.CDK_DEFAULT_REGION,
};

Tags.of(this).add("Project", "example");
Tags.of(this).add("Environment", "production");
```

Use tags for ownership, cost review, and incident tracing.
