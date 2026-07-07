---
title: "私の技術的な仕事の進め方：Backend、AI、DevOps、Infrastructure"
date: 2026-07-08T00:30:00+08:00
description: Backend、LLM / Speech AI、DevOps、Cloud、On-prem Infrastructure、Network Operations をひとつの delivery chain として扱う考え方。
menu:
  sidebar:
    name: 私の仕事の進め方
    identifier: technical-delivery-chain
    weight: 5
tags: ["Backend", "LLM", "Speech AI", "DevOps", "Infrastructure", "Network"]
categories: ["Portfolio", "Engineering"]
---

私は Backend、AI、DevOps、Infrastructure、Network を別々の領域としてではなく、実際に動くプロダクトを支えるひとつの delivery chain として扱っています。

機能を使える状態にするには API が安定している必要があります。サービスを更新するには CI/CD が必要です。長期運用するには monitoring、backup、network、security が必要です。LLM、Speech AI、GPU runtime を使う場合も、model integration は deployable、observable、operable でなければなりません。

## 主に扱う領域

### Backend / API

Backend は私の中心的な領域です。API design、service integration、database access、既存システム連携、admin workflow を扱います。Node.js、Python、Go、PHP、C/C++、Shell Script、Java を、既存アーキテクチャや運用性に合わせて使います。

重視しているのは、API が明確であること、data flow を追跡できること、error を診断できること、そして次の担当者が保守できることです。

### LLM / Speech AI

2022 年から LLM と Speech AI を実際のプロダクト workflow に組み込んでいます。単に model API を呼ぶだけではなく、prompt、batch processing、local model、GPU runtime、OpenAI API、Ollama、Kaldi、Whisper、既存 backend workflow を接続します。

入力データの整理、出力の検証、retry、cost control、local model と cloud API の選択、runtime environment の再現性を重視します。

### DevOps / CI/CD

GitLab CI/CD、GitHub Actions、Jest tests、container image build、deployment workflow、release process を扱います。目的は release を repeatable にし、問題が起きたときにどの段階で壊れたか分かるようにすることです。

### Cloud / On-prem Infrastructure

Cloud 側では AWS CDK / IaC、AWS、GCP、Azure、service integration を扱います。On-prem 側では Proxmox VE、Proxmox Backup Server、Harbor、GitLab、LDAP、LibreNMS、GPU server、NAS、backup planning を扱います。

Infrastructure は特定の機械や個人の記憶だけに依存するべきではなく、記述でき、再現でき、review できるべきだと考えています。

### Network / Security Operations

Enterprise network と security operations も扱います。Switch、Firewall、VLAN、VPN、SD-WAN、QoS、Wi-Fi、site-to-site backup、monitoring、基本的な security control が対象です。

実運用では application issue が DNS、routing、firewall、latency、Wi-Fi、certificate、proxy、monitoring visibility に戻ってくることがよくあります。Application から network layer まで追えることは重要です。

## このサイトで伝えたいこと

- Backend、AI、DevOps、Infrastructure をつなぎ、実際に delivery できる system を作れること。
- Application を書くだけでなく、deployment、runtime、monitoring、network も扱えること。
- 技術要件を、運用・調達・引き継ぎ可能な実装に落とし込めること。
- 経験を記事、notes、open source project として整理していくこと。

一言で言えば、私は product を code から stable production operation まで持っていくことを重視する engineer です。
