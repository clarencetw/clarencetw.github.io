---
title: 我的技術工作方式：Backend、AI、DevOps 與 Infrastructure
date: 2026-07-08T00:30:00+08:00
description: 介紹我如何把 Backend、LLM / Speech AI、DevOps、Cloud、On-prem Infrastructure 與 Network Operations 放在同一條交付鏈上思考與落地。
menu:
  sidebar:
    name: 我的技術工作方式
    identifier: technical-delivery-chain
    weight: 5
tags: ["Backend", "LLM", "Speech AI", "DevOps", "Infrastructure", "Network"]
categories: ["Portfolio", "Engineering"]
---

我做技術工作時，通常不會把 Backend、AI、DevOps、Infrastructure、Network 當成彼此獨立的領域。對一個實際要上線、要被使用、要能維護的產品來說，這些事情最後會接在同一條交付鏈上。

功能要能被使用，API 要穩定；服務要能更新，CI/CD 要可靠；系統要長期跑，monitoring、backup、network、security 都要進來；如果產品需要 LLM、Speech AI 或 GPU runtime，模型整合也必須能被部署、觀測與維運。

## 我主要處理的工作

### Backend / API

Backend 是我最核心的工作範圍。我常處理 API design、service integration、資料庫存取、既有系統串接與 admin workflow。使用的語言包含 Node.js、Python、Go、PHP、C/C++、Shell Script 與 Java，依照系統既有架構、維護成本與部署環境選擇工具。

我比較在意的是 API 是否清楚、資料流是否能追、錯誤是否容易定位，以及未來是否還能被下一個人維護。

### LLM / Speech AI

自 2022 年起，我開始把 LLM 與 Speech AI 放進實際產品流程。這類工作不只是呼叫 model API，而是要把 prompt、batch processing、local model、GPU runtime、OpenAI API、Ollama、Kaldi、Whisper 與既有 backend workflow 串起來。

我會優先處理可控性與可維運性：輸入資料如何整理、模型輸出如何被驗證、失敗時怎麼 retry、成本怎麼控、local model 與 cloud API 如何選擇，以及 runtime environment 是否能重複部署。

### DevOps / CI/CD

我維護 GitLab CI/CD、GitHub Actions、Jest tests、container image build、deployment workflow 與 release 流程。目標是讓 release 可以被重複執行，並且在出問題時能知道是哪個階段壞掉。

對我來說，CI/CD 不是只有自動部署，而是把測試、build、image registry、環境差異、rollback 與 review 流程串在一起。

### Cloud / On-prem Infrastructure

我同時處理 Cloud 與 On-prem environment。Cloud 端包含 AWS CDK / IaC、AWS、GCP、Azure 與常見 service integration；On-prem 端包含 Proxmox VE、Proxmox Backup Server、Harbor、GitLab、LDAP、LibreNMS、GPU server 與 NAS / backup planning。

這也是我寫 [AWS CDK 完全學習手冊](https://www.tenlong.com.tw/products/9789864349203) 的原因之一：Infrastructure 應該要能被描述、被重複建立、被 review，而不是只存在某台機器或某個人的記憶裡。

### Network / Security Operations

我也會處理 enterprise network 與 security operations，包含 switch、firewall、VLAN、VPN、SD-WAN、QoS、Wi-Fi、site-to-site backup、monitoring 與基本安全控管。

Network 很容易被低估，但在實際營運中，很多 application issue 最後都會回到 DNS、routing、firewall、latency、Wi-Fi、certificate、proxy 或 monitoring visibility。能夠從 application 往下追到 network layer，對維運很重要。

## 我想呈現的履歷重點

這個網站不是只列技術名詞，而是希望讓人看懂我比較擅長的工作型態：

- 把 Backend、AI、DevOps、Infrastructure 串成可交付的系統。
- 能寫 application，也能處理部署、runtime、monitoring 與 network。
- 能把技術需求轉成可維運、可採購、可交接的實作。
- 願意把踩過的坑整理成文章、notes 或 open source project。

如果只用一句話描述，我會說我偏向「能把產品從程式碼一路帶到穩定上線」的工程師。不是每件事都自己做完，而是知道各層之間怎麼接、怎麼查、怎麼讓系統長期運作。
