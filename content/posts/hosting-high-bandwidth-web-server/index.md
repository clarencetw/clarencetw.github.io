---
title: 託管高流量網站經驗
date: 2023-01-21T02:00:00+08:00
description: 長期營運高流量網站經驗
menu:
  sidebar:
    name: 託管高流量網站經驗
    identifier: hosting-high-bandwidth-web-server
    weight: 10
tags: ["Websites"]
categories: ["Websites"]
---

在伺服器管理經驗上有在託管高流量站台，此站台上託管的網站數量有 4000 個以上，平常維運除了定期更新之外還會設定監控系統異常指標減少人力維護的成本。

### CloudFlare 30 天的數據 

可以由下圖看到月流量統計
- 請求高達 1900 萬
- 流量高達 2 TB 
- 造訪次數高達 70 萬以上
- 點閱率高達 100 萬以上

{{< img src="/posts/hosting-high-bandwidth-web-server/images/cf-30day-bandwidth.png" align="center" title="CloudFlare 30 Day Bandwidth">}}

{{< vs >}}
