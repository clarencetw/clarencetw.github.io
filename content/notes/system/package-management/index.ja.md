---
title: パッケージ管理コマンド
description: Homebrew、APT、DNF、YUM など package manager の基本操作。
lastmod: 2026-07-11T00:00:00+08:00
weight: 310
menu:
  notes:
    name: パッケージ管理
    identifier: notes-system-package
    parent: notes-system
    weight: 10
---

{{< note title="Version と安全範囲" >}}

**最終確認：2026年7月11日**

これは一般的な command reference であり、特定 version に固定した完全な runbook ではありません。実行前に installed version、最新の公式ドキュメント、対象 account／host／path を確認してください。deploy、destroy、delete、prune、sync、upgrade、system setting の変更は、費用、停止、data loss につながる可能性があります。差分を事前確認し、必要に応じて backup を取得してください。

{{< /note >}}

{{< note title="Homebrew" >}}

```bash
brew update
brew install git node hugo
brew install --cask visual-studio-code
brew list
brew outdated
brew upgrade
brew cleanup
```

active development 用の machine では、広範囲 upgrade 前に `brew outdated` を確認する。

{{< /note >}}

{{< note title="APT" >}}

```bash
sudo apt update
sudo apt upgrade
sudo apt install git curl wget vim
apt list --installed
apt list --upgradable
sudo apt autoremove
```

production host では kernel や runtime updates の範囲を確認してから適用する。

{{< /note >}}

{{< note title="DNF と YUM" >}}

```bash
sudo dnf check-update
sudo dnf install git nginx
sudo dnf upgrade

sudo yum check-update
sudo yum install git nginx
sudo yum update
```

distribution native の package manager を使い、service scripts と dependencies の一貫性を保つ。

{{< /note >}}
