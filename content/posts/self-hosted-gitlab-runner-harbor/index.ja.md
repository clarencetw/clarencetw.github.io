---
title: "Self-hosted GitLab、Runner、Harbor：ソースコードからデプロイまでの CI/CD フロー"
date: 2026-10-26T00:00:00+08:00
description: Self-hosted GitLab、GitLab Runner、Harbor registry を運用者の視点で整理。セルフホストを選ぶ理由、各コンポーネントのつながり、長期運用でのアップグレード、バックアップ、署名鍵、ログ上限について。
menu:
  sidebar:
    name: Self-hosted GitLab・Runner・Harbor
    identifier: self-hosted-gitlab-runner-harbor
    weight: 45
tags: ["GitLab", "CI/CD", "Harbor", "Docker", "DevOps"]
categories: ["Portfolio", "Engineering"]
---

2022 年から、Operator として Self-hosted GitLab、GitLab Runner、Harbor registry、CI/CD workflow を構築・運用し、source code、container image、deployment をひとつの流れにつないでいます。

この記事は設定手順の解説ではありません。`.gitlab-ci.yml`、Runner のデプロイ、複数環境へのデプロイの例は [GitLab CI/CD 設定ガイド：Runner、.gitlab-ci.yml、Harbor、デプロイ]({{< ref "/posts/gitlab-cicd-complete-guide" >}}) に、`config.toml` の設定項目とよく使う変数は [GitLab Runner config.toml 設定とよく使う CI/CD 変数]({{< ref "/notes/gitlab/runner-config" >}}) にまとめています。ここで扱うのはもう一方の側面です。なぜこの仕組みを自分たちで持つのか、各コンポーネントをどうつなぐのか、そして数年運用して実際に時間がかかるのはどこか。文中の問題には、当時 [blog.clarence.tw](https://blog.clarence.tw/) に書いた記録へのリンクを付けています。

## セルフホストを検討する理由

GitLab.com や各クラウドの registry は十分に成熟しており、セルフホストが標準の答えというわけではありません。セルフホストに向かうのは、たいてい次のような検討事項が重なったときです。

- **コードとデータの置き場所**：source code、image、build log を自分たちが管理できる環境に置く必要があるチームもあります。
- **ネットワーク環境**：デプロイ先がオンプレミスや内部ネットワークにある場合、Runner と registry を同じ側に置くと build や image pull の経路が短くなり、外向き通信も管理しやすくなります。
- **Runner のリソース**：特定のハードウェア、OS、大きな build リソースが必要な job は、自前の Runner のほうが割り当てやすくなります。
- **既存システムとの連携**：既存のアカウント管理、監視、バックアップの仕組みと接続する必要があります。

代償もはっきりしています。アップグレード、バックアップ、証明書、署名鍵、ディスク容量、障害対応がすべて自分たちの仕事になります。セルフホストを決める前に、その仕事を長期的に引き受ける人がいるかを確認しておくべきです。

## 全体の流れ

流れはひとことで言えます。コードを GitLab に入れ、Runner が pipeline に従って build とテストを行い、できた container image を Harbor に push し、デプロイ環境が Harbor から image を pull します。

1. **Source**：開発者が commit や tag を GitLab に push し、pipeline が起動します。
2. **CI**：GitLab が tags の合う Runner に job を割り当て、テストと image build を実行します。
3. **Image**：build した image を tag ルールに従って Harbor の該当 project に push します。
4. **Deploy**：デプロイ環境は pull 権限だけを持つアカウントで、指定バージョンの image を Harbor から取得します。

このように分けると、各段階の責任がはっきりします。pipeline が失敗したとき、チェーン全体を推測するのではなく、source、build、push、deploy のどこで起きたかをまず切り分けられます。

registry がひとつとは限りません。2021 年には、[Jib と Gradle を使って GitLab CI から GitLab Container Registry、Azure Container Registry、Amazon ECR に image を push する方法](https://blog.clarence.tw/2021/07/25/java-jib-gradle-uses-gitlab-ci-cd-to-automatically-upload-docker-to-gitlab-container-registry-azure-container-registry-and-amazon-elastic-container-registry/)を記録しました。ECR のログイン手順のために、AWS CLI と credential helper を入れた build 用 image を別に作っています。registry が増えるたびに、認証方式と壊れる可能性もひとつずつ増えます。

## Runner の構成方針

Runner は CI/CD の中で最も頻繁に調整する部分です。計画時に役立つ一般的な原則がいくつかあります。

- **tags で振り分ける**：通常の build、Docker が必要な job、特殊な環境など、種類の異なる job を別々の Runner に任せ、リソースの取り合いを避けます。
- **権限を最小にする**：`privileged` や Docker socket のマウントは、実質的にホストの権限を job に渡すことになります。本当に必要で信頼できる project に限って有効にします。
- **設定ファイルを重要資産として扱う**：`config.toml` には runner token が含まれます。変更前にバックアップし、repository にはコミットしません。

Runner のバージョンや helper image が原因になることもあります。2020 年には `docker-windows` executor で [Missing gitlab-runner-helper のエラーにより artifacts をアップロードできない問題](https://blog.clarence.tw/2020/02/09/windows-gitlab-runner-in-docker-windows-missing-error-uploading-artifacts-is-disabled-or-missing-gitlab-runner-helper-uploading-artifacts-is-disabled-who-to-fix/)に遭遇し、`config.toml` で `helper_image` を指定して解決しました。具体的な設定項目とリスクは、上でリンクした Runner のノートを参照してください。

## Harbor と image の管理

### Robot account と CI の認証

CI から Harbor に image を push するときは、個人アカウントではなく Harbor の robot account を使います。[Harbor のドキュメント](https://goharbor.io/docs/2.13.0/working-with-projects/project-configuration/create-robot-accounts/)によると、project robot account は所属する project の中でしか操作できず、権限は作成時に選び、有効期限も設定できます。CI には push 権限、デプロイ先には pull 権限だけを与える分け方が管理しやすい形です。

robot account の名前にはデフォルトで `robot$` という接頭辞が付き、この `$` でしばらく悩みました。2023 年に、[GitLab CI と Harbor を連携したときに docker login が unauthorized を返し続ける問題](https://blog.clarence.tw/2023/11/26/%e8%a7%a3%e6%b1%ba%e4%bd%bf%e7%94%a8-gitlab-ci-%e6%95%b4%e5%90%88-harbor-%e5%87%ba%e7%8f%be%e7%9a%84%e5%a5%87%e6%80%aa%e5%95%8f%e9%a1%8c%ef%bc%9a%e5%b8%b3%e8%99%9f%e4%b8%ad%e7%9a%84-%e7%ac%a6/)を記録しています。手動の対話ログインでは問題ないのに、pipeline の中では `$` が変数として展開されていました。当時は `.gitlab-ci.yml` で `$$` と書き、パスワードを `--password-stdin` で渡す形で解決しました。[GitLab CI/CD variables のドキュメント](https://docs.gitlab.com/ci/variables/)によると、UI で定義した変数はデフォルトで `$` の参照を展開しないため、アカウント名も CI/CD variable に入れるのも検討に値する方法です。

### Tag ルールと容量管理

image の tag はソースコードまでたどれる必要があります。よくあるのは、release にはバージョン番号、それ以外の build には commit SHA を使う方法です。2020 年には小さな要件として、[Git tag の `v1.0.0` を image tag の `1.0.0` に変換する方法](https://blog.clarence.tw/2020/11/10/gitlab-ci-docker-tag-removal-version-v/)を記録しました。`${CI_COMMIT_TAG:1}` で先頭の 1 文字を取り除くだけです。ルール自体は単純ですが、最初に決めてすべての project で同じ規約に従うことが大切です。

image は増える一方です。Harbor には管理のための機能がいくつかあります。

- **Tag retention**：repository、件数、期間を条件に必要な tag を残し、それ以外を削除します。実行は取り消せないため、ドキュメントでは先に dry run することが推奨されています。
- **Tag immutability**：release の tag を上書きできないようにし、同じバージョン番号が常に同じ image を指すようにします。
- **Garbage collection**：tag や artifact を削除しても、容量はすぐには解放されません。参照されなくなった blob を消すには [garbage collection](https://goharbor.io/docs/2.13.0/administration/garbage-collection/) の実行が必要です。

## 長期運用：アップグレード、バックアップ、署名鍵、ログ上限

システムを立ち上げるのは始まりにすぎず、本当に時間がかかるのはその後の数年間の保守です。以下は、ブログに記録を残した問題の種類です。

### アップグレード：必須の経由バージョンは飛ばせない

2023 年に [GitLab 14.9.3 からのアップグレード](https://blog.clarence.tw/2023/12/24/gitlab-%e4%bc%ba%e6%9c%8d%e5%99%a8%e5%8d%87%e7%b4%9a%e6%8c%87%e5%8d%97%ef%bc%9a%e5%be%9e%e7%89%88%e6%9c%ac-14-9-3-%e5%8d%87%e7%b4%9a/)を記録しました。apt で直接アップグレードしようとすると、パッケージの preinstall チェックで止められ、先に 14.10.x へ上げるよう求められます。`apt install gitlab-ce=<バージョン>` で 1 段ずつ上げ、各段階で再起動してサービスの状態を確認する方法で対応しました。

教訓は、GitLab を長くアップグレードしないほど、たどる道が長くなるということです。[GitLab upgrade paths のドキュメント](https://docs.gitlab.com/update/upgrade_paths/)によると、required upgrade stops は飛ばせません。各段階で最新の patch release まで上げ、background migrations の完了を待ってから次へ進みます。必要な経由バージョンを計算する Upgrade Path tool も提供されています。数年に一度の大きなアップグレードより、定期的に小さく上げるほうがはるかに安全です。

### バックアップ：何をバックアップしているかを区別する

2023 年には、[GitLab API を使ってアカウント配下のすべての project を clone する Bash スクリプト](https://blog.clarence.tw/2023/11/12/%e5%a6%82%e4%bd%95%e5%82%99%e4%bb%bd%e6%95%b4%e5%80%8b-gitlab-%e6%89%80%e6%9c%89%e5%b0%88%e6%a1%88/)を書きました。同僚がすべての repository を一度に取得する必要があったためです。この種のスクリプトは移行やコードの複製を残す用途には便利ですが、対象は Git repository だけで、issue、merge request、CI/CD 設定などは含まれません。

GitLab の完全なバックアップには、やはり公式のバックアップ手順が必要です。さらに [GitLab のバックアップドキュメント](https://docs.gitlab.com/administration/backup_restore/backup_gitlab/)によると、バックアップタスクは設定ファイルを含みません。Linux package でインストールした場合、少なくとも `/etc/gitlab/gitlab-secrets.json` と `/etc/gitlab/gitlab.rb` を別途バックアップし、データのバックアップと同じ場所に置かないようにします。secrets ファイルがないと、データベース内の暗号化されたデータを復元できません。

### パッケージ署名鍵：必ず期限が来る

apt で GitLab と Runner をインストールしている以上、リポジトリ署名鍵の更新には付き合う必要があります。私は 2 回遭遇しました。

- 2020 年、[`apt update` で `NO_PUBKEY` が出た](https://blog.clarence.tw/2020/04/21/gitlab-gpg-key-update/)ため、新しい GitLab GPG key をインポートしました。
- 2022 年、Ubuntu 18.04 で Runner を更新しようとして [`EXPKEYSIG` が出て鍵の期限切れがわかり](https://blog.clarence.tw/2022/09/11/ubuntu-18-04-lts-gitlab-%e9%87%91%e9%91%b0%e9%81%8e%e6%9c%9f%e8%99%95%e7%90%86%e6%96%b9%e6%b3%95/)、ダウンロードとインポートをやり直しました。

この種の問題はサービスをすぐに止めるわけではありませんが、アップグレードを静かに失敗させます。当時の記事で使った `apt-key` は新しい Debian / Ubuntu では推奨されていないため、現在は GitLab 公式ドキュメントのその時点の手順に従ってください。

### ログ上限：デフォルトは 4 MB

2022 年に [Runner が `Job's log exceeded limit of 4194304 bytes` を出す問題](https://blog.clarence.tw/2022/11/27/gitlab-runner-%e5%87%ba%e7%8f%be-jobs-log-exceeded-limit-of-4194304-bytes-%e7%9a%84%e8%a7%a3%e6%b3%95/)に遭遇しました。[Runner advanced configuration](https://docs.gitlab.com/runner/configuration/advanced-configuration/) によると、`[[runners]]` の `output_limit` はデフォルトで 4096 KB です。この値を上げれば job は続行できますが、より根本的なのは、なぜログがそこまで多いのかを確認し、不要な verbose 出力を止めるなどの対応をすることです。

## 学んだこと

- **セルフホストのコストは後から来る**：インストールは一度きりですが、アップグレード、バックアップ、署名鍵、容量管理は毎年必要で、定期的な運用サイクルに組み込むべきです。
- **段階ごとの境界をはっきりさせる**：source、CI、image、deploy にそれぞれ担当のコンポーネントと権限があれば、問題の場所をすばやく特定できます。
- **アカウントと権限は自動化を前提に設計する**：CI には robot account、デプロイ先には pull 権限だけという形は、個人アカウントの共有より管理もローテーションもしやすくなります。
- **ハマった問題は書き残す**：上のどの問題も、次に遭遇したときに一番早い解決策は、当時の自分が残した記録でした。
