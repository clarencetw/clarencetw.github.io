---
title: 高トラフィック Web Hosting 運用
date: 2023-01-21T02:00:00+08:00
description: 高トラフィック Web hosting と多数サイトの運用経験。monitoring、updates、capacity planning、security maintenance を扱います。
menu:
  sidebar:
    name: Web Hosting 運用
    identifier: hosting-high-bandwidth-web-server
    weight: 10
tags: ["Hosting", "Nginx", "Cloudflare", "Monitoring", "Operations"]
categories: ["Infrastructure", "Operations"]
---

私は 4000 以上の Web サイトを載せる high-traffic hosting environment を長期運用した経験があります。この種の仕事は Web server を立てるだけではなく、capacity planning、monitoring、updates、security、DNS / CDN、incident response、日常運用の標準化が必要です。

規模が大きくなるほど、設定変更、証明書、更新、alert 対応を人の記憶だけに頼ることはリスクになります。

### Cloudflare 30-day Metrics

1 か月の traffic 例：

- Requests 約 1900 万
- Bandwidth 約 2 TB
- Visits 70 万以上
- Page views 100 万以上

{{< img src="/posts/hosting-high-bandwidth-web-server/images/cf-30day-bandwidth.png" align="center" title="Cloudflare 30 Day Bandwidth">}}

## 運用で重視すること

### Monitoring は手動確認より先にある

大量サイトの環境では、ページを手で開いて確認するだけでは足りません。System resources、Web server status、certificates、DNS、HTTP response、error rate、traffic trend を monitoring に入れる必要があります。

Monitoring は alert のためだけではなく、問題が application、network、CDN、DNS、storage、upstream service のどこにあるか判断するための材料です。

### Updates は controlled に行う

Hosting environment では security update が必要ですが、同時に既存サイトを壊してはいけません。更新は段階的に行い、観測でき、rollback できる状態にする必要があります。

### Capacity planning は平均値だけでは足りない

Traffic には spike があります。CPU、memory、disk I/O、network throughput、CDN cache hit ratio、static assets、database pressure、log growth を見る必要があります。

### Security は継続的な運用

TLS / certificate management、Web server headers、WAF / CDN rules、permission control、system updates、log review、abnormal traffic monitoring は継続的に扱う必要があります。

## 学んだこと

Hosting operations は operability の重要性を教えてくれました。Demo で動く system と、traffic、updates、incidents、cost、security risk の中で長期的に動き続ける system は別物です。

この考え方は、Backend、DevOps、Infrastructure、Network の仕事にもそのままつながっています。

{{< vs >}}
