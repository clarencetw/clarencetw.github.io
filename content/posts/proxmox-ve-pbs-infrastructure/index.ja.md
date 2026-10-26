---
title: "Proxmox VE と PBS：中小規模 On-prem 基盤の設計とバックアップ戦略"
date: 2026-10-26T00:00:00+08:00
description: Proxmox VE、Proxmox Backup Server、GPU server の設計・運用で意識していること。クラスタ、ストレージ、ネットワークの原則、バックアップ戦略、運用で実際に遭遇した問題をまとめます。
menu:
  sidebar:
    name: Proxmox VE と PBS
    identifier: proxmox-ve-pbs-infrastructure
    weight: 50
tags: ["Proxmox", "Backup", "Infrastructure", "GPU", "On-prem"]
categories: ["Portfolio", "Engineering"]
---

2023 年から、Operator として Proxmox VE、Proxmox Backup Server（PBS）、GPU server、On-prem infrastructure の設計と運用を担当しています。この環境では internal services と AI runtime workload を動かしており、全体の backup strategy も私の担当です。

この記事はインストール手順ではありません。中小規模のオンプレミス環境で私が重視している設計原則と、実際に遭遇して [blog](https://blog.clarence.tw/) に記録した問題をまとめたものです（リンク先の記事は繁体字中国語です）。ホスト名、IP アドレス、ネットワーク構成、セキュリティの詳細は含めていません。設定に関する内容は一般的な指針であり、正確な情報は Proxmox の公式ドキュメントを参照してください。

## 背景と要件

オンプレミスの要件はたいてい現実的です。internal services を長期間安定して動かし、AI workload には GPU が必要で、データはバックアップでき、復元できなければなりません。予算も人手も限られているため、少人数で保守できるプラットフォームであることが重要です。

Proxmox VE はこうした状況に合っています。VM と LXC container を同じ画面で管理でき、クラスタ、ストレージ、バックアップにも標準の仕組みがあり、PBS を組み合わせれば incremental かつ deduplicated なバックアップが取れます。私にとって大事なのは機能の多さではなく、障害時にすばやく調査し、復旧できるかどうかです。

この領域での主な担当業務は次のとおりです。

- Proxmox VE cluster、virtualization、storage、VM lifecycle の設計と運用。
- Proxmox Backup Server の構築と、backup、restore、disaster recovery のプロセス設計。
- NVIDIA GPU server、driver / runtime、inference environment の管理とシステムチューニング。
- Dell、HP、Supermicro の server hardware と GPU server の仕様を評価し、調達・運用できる技術仕様にまとめること。
- 社内外のデータセンター、site-to-site backup、high availability の経路設計と、LibreNMS による network / server monitoring。

## 設計のポイント：クラスタ、ストレージ、ネットワーク

### クラスタ

クラスタには集中管理と VM 移動というメリットがありますが、quorum の問題もついてきます。[Proxmox VE 公式ドキュメント](https://pve.proxmox.com/pve-docs/chapter-pvecm.html)によると、High Availability を使うには信頼できる quorum のために最低 3 ノードが必要です。2 ノード構成の場合は QDevice で 3 票目を補えます。

ほかに早い段階で確認していることがあります。

- **ノードのバージョンをそろえる**：公式ドキュメントでは全ノードを同じバージョンに保つことが推奨されています。アップグレードは計画を立てて 1 台ずつ進めます。
- **CPU の互換性**：online migration が保証されるのは同じ CPU ベンダー間のみです。ハードウェアが混在する場合は VM の CPU model を保守的に選ばないと、live migration が失敗することがあります。
- **ノードのライフサイクル**：ノードの追加、入れ替え、削除は決まった手順で行い、その場の判断に頼らないようにします。

### ストレージ

原則は「増えていくものをシステムから切り離す」ことです。VM disk、ISO / template、バックアップデータにはそれぞれ適した置き場所があります。特にバックアップデータはハイパーバイザーのシステムディスクと同じ領域に置かないようにします。どちらかが急に増えると、もう一方にも影響が出るからです。

VM の disk も増えていく前提で考えます。Proxmox 上でのディスク拡張自体は簡単ですが、ハイパーバイザー側で resize したあと、ゲスト OS 内の partition、LVM、filesystem も調整する必要があります。この手順は blog に [Ubuntu 22.04 VM の場合の手順](https://blog.clarence.tw/2024/08/04/%e5%9c%a8-proxmox-ve-%e4%b8%ad%e6%93%b4%e5%b1%95-ubuntu-22-04-%e8%99%9b%e6%93%ac%e6%a9%9f%e7%9a%84%e7%a3%81%e7%a2%9f%e7%a9%ba%e9%96%93/)としてまとめています。

### ネットワーク

クラスタ通信には Corosync が使われます。帯域はあまり必要としませんが、遅延には敏感です。公式ドキュメントでは、cluster traffic 専用の物理 NIC を用意し、別の物理ネットワーク上に 2 本目の link を冗長化として用意することが推奨されています。VM やバックアップの通信が Corosync を圧迫しないようにするためです。

一般的な原則として、管理、クラスタ、VM、バックアップの通信は分けて設計し、アドレス設計は最初に決めておくべきです。あとからクラスタの通信アドレスを変えるのは、想像以上に手間がかかります（後述の「運用でつまずいた点」を参照）。

## GPU Server と AI Workload

AI runtime は GPU、driver、CUDA、kernel のバージョンに敏感です。そのため GPU server の運用で目指すのは「たまたま動いているマシン」ではなく、「再構築できる環境」です。

Proxmox で GPU を使う一般的な方法は PCI(e) passthrough です。[公式ドキュメント](https://pve.proxmox.com/pve-docs/chapter-qm.html)では、事前に考えておくべきトレードオフがいくつか挙げられています。

- ハードウェアと BIOS / UEFI が IOMMU に対応し、有効になっている必要があります。
- GPU を VM に passthrough すると、ホストや他の VM からはそのカードを使えなくなります。
- passthrough した PCI デバイスを持つ VM は現時点では live migration できないため、ノードのメンテナンスには計画的な停止時間が必要です。

こうした制約があるため、GPU workload はマシン単位で計画するのが向いています。どのサービスが GPU を専有するか、driver と runtime をどうバージョン管理するか、ホストのメンテナンス時にサービスをどう止めてどう戻すか、といった点です。

GPU 運用で最もよく起きるのは driver の問題です。blog には [`nvidia-smi` で No devices were found と表示される問題](https://blog.clarence.tw/2024/02/19/%e8%a7%a3%e6%b1%ba-nvidia-linux-%e4%bd%bf%e7%94%a8-nvidia-smi-%e5%87%ba%e7%8f%be-no-devices-were-found-%e5%95%8f%e9%a1%8c/)への対処や、[Ubuntu 24.04 の Secure Boot 環境で NVIDIA ドライバーが読み込まれない問題](https://blog.clarence.tw/2026/01/31/%e8%a7%a3%e6%b1%ba-ubuntu-24-04-secure-boot-%e7%92%b0%e5%a2%83%e4%b8%8b-nvidia-%e9%a9%85%e5%8b%95%e7%84%a1%e6%b3%95%e8%bc%89%e5%85%a5%e5%95%8f%e9%a1%8c/)の解決方法を記録しています。共通する教訓は、再インストールを繰り返すのではなく、まず kernel、driver、Secure Boot、ビルド環境の関係を確認してから対処を決めることです。

## Proxmox Backup Server のバックアップ戦略

バックアップ戦略は、バックアップ、保持、クリーンアップ、検証の 4 つに分けて考え、そのうえで復元訓練を加えています。

### Prune と Garbage Collection は別物

PBS で最も誤解されやすい点です。[PBS 公式ドキュメント](https://pbs.proxmox.com/docs/maintenance.html)によると、次のとおりです。

- **Prune** が削除するのは snapshot の metadata（manifest や index など）だけで、実データを持つ chunk はすぐには消えません。
- どの snapshot からも参照されなくなった chunk を実際に削除するのは **Garbage Collection（GC）** です。GC は mark と sweep の 2 段階で動き、猶予期間（デフォルトで約 24 時間 5 分）があるため、prune 直後に GC を実行しても、すぐに容量が空くとは限りません。

そのため、保持ポリシー（`keep-last`、`keep-daily`、`keep-weekly` など）と GC のスケジュールはセットで設計する必要があります。prune だけ設定して GC をスケジュールしなければ使用量は増え続けますし、GC を回していても保持ポリシーが緩すぎれば、やはり容量は足りなくなります。

### 100% になる前に余裕を確保する

blog には [PBS のディスク使用率が 100% になった](https://blog.clarence.tw/2024/05/29/%e5%a6%82%e4%bd%95%e8%99%95%e7%90%86-proxmox-backup-server-%e7%a1%ac%e7%a2%9f%e7%a9%ba%e9%96%93%e6%bb%bf-100-%e7%9a%84%e5%95%8f%e9%a1%8c/)ときの対処を記録しています。厄介だったのは、GC を実行するにも多少の空き容量が必要なのに、それがまったく残っていなかったことです。最終的には、90 日以上前の古い task log を削除してわずかな空きを作り、そのうえで GC を手動実行しました。

この経験から、次の点をより重視するようになりました。

- monitoring で datastore の使用率を監視し、書き込めなくなる前の余裕があるうちに対処する。
- datastore と PBS システム自体の領域はできるだけ分け、バックアップデータでシステムが埋まらないようにする。
- prune と GC のジョブが実際に動いているか、失敗していないかを定期的に確認する。

### 検証と復元訓練

バックアップが成功したからといって、復元できるとは限りません。PBS 公式ドキュメントでは verify job を設定し、少なくとも月に 1 回はすべてのバックアップを再検証することが推奨されています。ディスクの経年劣化によって、正常だったバックアップが徐々に壊れること（bit rot）があるためです。新しいバックアップを頻繁に検証する verify job と、週次または月次の全体再検証を組み合わせるのがよい方法です。

検証に加えて、実際の復元訓練も必要です。定期的にいくつかの VM や container をテスト環境に復元し、起動すること、サービスが動くこと、データが想定どおりのバージョンであることを確認します。Proxmox VE には live-restore や single file restore もあるので、訓練の際にあわせて手順を確認しておくとよいでしょう。

### オフサイトと disaster recovery

同じデータセンターにバックアップが 1 つあるだけでは、拠点全体に問題が起きたときに対応できません。PBS は remote と sync job を使って別の PBS にバックアップを同期でき、site-to-site backup の土台になります。大事なのは、データを置いておくだけでなく、別拠点のバックアップを「どこに、どう復元するか」まで disaster recovery の手順に書いておくことです。

## 運用でつまずいた点

以下はいずれも blog で公開して記録した問題です。ここでは要点と学んだことだけをまとめます。

### クラスタ通信 IP の変更

[Proxmox VE Cluster IP の更新と設定の同期](https://blog.clarence.tw/2025/03/19/proxmox-ve-cluster-ip-%e6%9b%b4%e6%96%b0%e8%88%87%e9%85%8d%e7%bd%ae%e5%90%8c%e6%ad%a5%e7%b6%93%e9%a9%97%e8%ab%87/)の手順を blog に記録しています。ポイントは、単一ノード上の `/etc/corosync/corosync.conf` ではなく、クラスタで共有される `/etc/pve/corosync.conf` を編集することです。事前にバックアップを取り、編集時には `config_version` を増やし、各ノードのネットワーク設定と `/etc/hosts` も更新し、最後に `pvecm status` で設定が反映されたことを確認します。quorum に影響する高リスクな変更なので、メンテナンス時間帯に行うべき作業です。

### クラスタからのノード削除

ノード入れ替えのときの手順として、[Proxmox VE クラスタからノードを安全に削除する方法](https://blog.clarence.tw/2025/04/12/%e5%a6%82%e4%bd%95%e5%be%9e-proxmox-ve-%e5%8f%a2%e9%9b%86%e4%b8%ad%e5%ae%89%e5%85%a8%e7%a7%bb%e9%99%a4%e7%af%80%e9%bb%9e/)を blog にまとめています。対象ノードの VM と container をバックアップまたは移行し、シャットダウンして自動で起動しないことを確認してから `pvecm delnode` で削除し、最後に残ったノードディレクトリと SSH key の情報を削除します。公式ドキュメントでも、削除したノードを元の設定のまま同じクラスタネットワークに戻すとクラスタが壊れるおそれがあると強調されています。

### NIC の firmware エラー

ある Proxmox VE ホストで [Intel X550 が ixgbe FWSM firmware error を出し続けた](https://blog.clarence.tw/2026/06/25/%e8%a7%a3%e6%b1%ba-proxmox-debian-%e4%b8%8a-intel-x550-ixgbe-fwsm-firmware-error-%e5%95%8f%e9%a1%8c/)件を blog に記録しています。パケットのカウンターは正常に見え、kernel を更新しても解決せず、最終的に NIC の NVM を更新して本当の power cycle を行うことでエラーが消えました。学んだのは、ハードウェアから読み取った firmware の警告をログのフィルタリングで片付けないことです。firmware を書き換える前には inventory を取り、バージョンの対応を確認し、BMC / IPMI または物理コンソールを用意しておきます。

### VM と container の修復

- **起動しない Windows VM**：[PVE 上の Windows VM を WinPE で修復する方法](https://blog.clarence.tw/2025/10/01/%e5%9c%a8-proxmox-ve%ef%bc%88pve%ef%bc%89windows-vm-%e4%bf%ae%e5%be%a9%e6%95%99%e5%ad%b8%ef%bc%9awinpe-%e4%b8%8b-sfc-scannow%e3%80%81dism-online-%e5%a4%b1%e6%95%88%ef%bc%9f%e7%94%a8-drvload/)を blog に記録しています。WinPE には VirtIO ドライバーが含まれていないことがあるため、まず `drvload` で読み込んでシステムディスクを認識させ、そのうえでオフライン DISM で修復します。
- **LXC での IPv6**：[PVE 上の LXC container で IPv6 を使う](https://blog.clarence.tw/2023/02/24/proxmox-ve-pve-%e4%bd%bf%e7%94%a8-linux-container-lxc-%e5%ae%b9%e5%99%a8%e4%bd%bf%e7%94%a8-ipv6/)には、ホスト側の `accept_ra` 設定を調整する必要があったことを記録しています。
- **Web UI の証明書の入れ間違い**：[PVE で Connection error 596 が出た](https://blog.clarence.tw/2023/01/15/pve-%e5%87%ba%e7%8f%be-connection-error-596-broken-pipe-%e7%9a%84%e8%a7%a3%e6%b1%ba%e6%96%b9%e6%b3%95/)件を記録しています。誤った証明書を入れたことが原因で、SSH でログインして pveproxy の証明書ファイルを正しいものに戻して解決しました。

### 古いハードウェアとハードウェア監視

[HP ProLiant DL380 G6 に PVE や PBS をインストールすると画面に縞模様が出る](https://blog.clarence.tw/2023/04/30/hp-proliant-dl380-g6-%e5%9c%a8%e5%ae%89%e8%a3%9d-proxmox-ve-pve-%e6%88%96-proxmox-backup-server-pbs-%e6%99%82%e5%87%ba%e7%8f%be%e9%bb%91%e7%99%bd%e6%a2%9d%e7%b4%8b%e5%a6%82%e4%bd%95%e8%a7%a3/)問題の対処法や、iLO からホストの状態を読めるようにするための [Proxmox への HPE Agentless Management のインストール](https://blog.clarence.tw/2023/01/22/%e5%9c%a8-proxmox-%e5%ae%89%e8%a3%9d-hpe-agentless-management-ams/)も blog に記録しています。古いハードウェアも延命はできますが、インストーラーや監視ツールのサポートは徐々に減っていくので、入れ替え計画は早めに立てておく必要があります。

### アップグレード前の確認

blog では [Proxmox VE 9.2 の重要な新機能](https://blog.clarence.tw/2026/05/21/proxmox-ve-9-2-%e5%b9%be%e5%80%8b%e6%88%91%e8%a6%ba%e5%be%97%e6%af%94%e8%bc%83%e9%87%8d%e8%a6%81%e7%9a%84%e6%96%b0%e5%8a%9f%e8%83%bd/)として、HA の disarm / arm、CRS の動的負荷分散、Custom CPU Models GUI などを取り上げました。どのバージョンであっても、本番環境をアップグレードする前には、バックアップがそろっているか、kernel / driver の互換性、HA と migration の挙動、ネットワーク設定への影響を確認し、まずテスト環境や重要度の低いノードで検証するようにしています。

## 学んだこと

- **バックアップは「復元できるか」で判断する**：prune、GC、検証、復元訓練のどれも欠かせません。バックアップジョブの成功だけでは不十分です。
- **容量は早めに監視する**：PBS が 100% になると、クリーンアップのツールすら動かしにくくなります。余裕を確保しておくほうが、事後の火消しよりはるかに安上がりです。
- **クラスタの変更はすべて高リスク作業**：IP の変更、ノードの削除、アップグレードは、設定をバックアップし、ドキュメントの手順に従い、メンテナンス時間帯に行います。
- **つまずいたことは書き残す**：上の問題はどれも、次に遭遇したとき自分の記録を見ればすぐ確認できます。これが [blog](https://blog.clarence.tw/) を書き続けている理由です。
