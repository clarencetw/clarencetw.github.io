---
title: "Speech AI と GPU Runtime：Kaldi・Whisper のデプロイと運用ノート"
date: 2026-10-26T00:00:00+08:00
description: Speech AI と GPU runtime に対する私の考え方をまとめました。Kaldi と Whisper の特性とトレードオフ、NVIDIA driver / CUDA / container のレイヤー分け、デプロイと性能運用で確認する項目を扱います。
menu:
  sidebar:
    name: Speech AI と GPU Runtime
    identifier: speech-ai-gpu-runtime
    weight: 55
tags: ["Speech AI", "Kaldi", "Whisper", "GPU", "CUDA", "Infrastructure"]
categories: ["Portfolio", "Engineering"]
---

2022 年から、私は Kaldi や Whisper といった speech recognition 技術と GPU runtime を実際のシステムに組み込む仕事をしています。範囲は model inference、system deployment、そしてその後の performance maintenance です。

この記事は特定プロジェクトの詳細な事例紹介ではなく、社内のアーキテクチャ、データ、性能数値は含みません。まとめたいのは、この種の仕事への向き合い方です。Kaldi と Whisper の違いをどう捉えているか、なぜ GPU runtime を先に安定させるのか、デプロイ後に何を確認しているのかを書きます。技術的な説明は公式ドキュメントに基づき、トラブル対応の経験は [blog.clarence.tw](https://blog.clarence.tw/)（中国語）で公開してきた記事から引いています。

## プロダクトにおける Speech AI の位置づけ

[私の仕事の進め方]({{< relref "/posts/technical-delivery-chain" >}}) でも書いたように、LLM や Speech AI の仕事は model API を呼ぶだけでは終わりません。batch processing、local model、GPU runtime、既存の backend workflow とつなげる必要があります。

音声認識は、多くの場合プロダクト全体の流れの一部です。一般的には、認識の前に音声の取得、形式変換、分割があり、認識の後にはテキストの後処理、保存、検索、他サービスへの受け渡しがあります。そのため Speech AI のコンポーネントを評価するときは、認識結果そのものだけでなく、次の点も一緒に見ます。

- 入力音声の形式と品質はそろっているか。前処理はどのレイヤーが担当するか。
- ストリーミング認識か batch 処理か。失敗時にどう retry するか。
- モデル出力をどう検証し、どの場合に人の確認が必要か。
- この runtime を別のマシンで再構築できるか。

同じツールでも内容によって結果が大きく変わることは、早い段階で実感しました。2019 年に Amazon Transcribe が簡体字中国語に対応したとき、[試してみた感想を記事にしました](https://blog.clarence.tw/2019/08/25/amazon-transcribe-supports-simplified-chinese-using-teaching-and-experience/)。歌では結果が良くなかった一方、会話中心の動画ではかなり良くなりました。managed service でも自前でデプロイするモデルでも、実際の利用シーンに近い音声で判断する必要があります。

## Kaldi と Whisper の特性とトレードオフ

私の仕事では Kaldi と Whisper の両方を使います。どちらかがもう一方を置き換えるものではなく、設計思想が大きく異なる二つのツールだと考えています。

### Kaldi

[Kaldi の公式説明](https://kaldi-asr.org/doc/about.html) によると、Kaldi は C++ で書かれ、Apache License v2.0 で公開されている speech recognition toolkit で、speech recognition の研究者向けに作られています。主な特徴は次のとおりです。

- finite state transducer（FST）を中心に据え、OpenFst を利用しています。従来の decoding graph は [HCLG](https://kaldi-asr.org/doc/graph.html) で、HMM、context dependency、lexicon、grammar / language model を合成したものです。
- さまざまなデータセット向けの recipes があり、データ準備から学習、デコードまでの流れを参照できます。
- [online decoding](https://kaldi-asr.org/doc/online_decoding.html) 用のライブラリがあり、`src/cudadecoder` には batched CUDA decoding の実装もあります。

運用の観点では、コンポーネントが細かく分かれていて、lexicon、language model、acoustic model をそれぞれ調整できるのが強みです。その代わり、構築の手順が長く、音声処理の専門知識が多く必要で、コンパイルオプションや依存パッケージの違いで環境が壊れやすいという面があります。

### Whisper

[openai/whisper](https://github.com/openai/whisper) によると、Whisper は Transformer の sequence-to-sequence 構成による汎用の音声認識モデルで、大規模で多様な音声データで学習されています。多言語の文字起こし、英語への翻訳、言語識別に対応し、コードとモデルの重みは MIT License で公開されています。

デプロイ時に気をつけたい点は次のとおりです。

- モデルには tiny、base、small、medium、large、turbo などのサイズがあります。公式に示されている VRAM の目安はおよそ 1 GB から 10 GB で、速度も大きく異なるため、GPU リソースと合わせて選ぶ必要があります。
- `ffmpeg` が必要で、`transcribe()` は音声全体を 30 秒の sliding window で処理します。
- turbo は large-v3 の最適化版で高速ですが、翻訳タスク向けには学習されていないため、翻訳には多言語モデルを使います。
- 公式の [model card](https://github.com/openai/whisper/blob/main/model-card.md) では、音声にない内容を出力する（hallucination）可能性、繰り返し出力の傾向、言語・アクセント・方言による性能差が指摘されており、高リスクな意思決定の場面での利用は推奨されていません。

### 選び方

| 観点 | Kaldi | Whisper |
| :-- | :-- | :-- |
| 設計 | 複数コンポーネントによる pipeline（acoustic model、lexicon、language model、FST decoding） | end-to-end の Transformer モデル |
| 導入の難しさ | 高い。recipe と構築手順の理解が必要 | 低い。パッケージを入れればすぐ文字起こしできる |
| 調整のしやすさ | 語彙や language model などを個別に調整できる | 主にモデルサイズ、デコード設定、前後処理で調整する |
| 多言語対応 | 学習データと recipe 次第 | 多言語の文字起こし、英語への翻訳、言語識別を標準で備える |
| 特に注意する点 | ビルド環境、依存パッケージ、モデルと graph のバージョン管理 | VRAM、長い音声、hallucination、繰り返し出力 |

私の原則はシンプルで、まず実際の利用シーンに近い音声で比較し、そのうえでデプロイと保守のコストを考えます。公開 benchmark だけでは決めません。

### Kaldi への公開コントリビューション

Kaldi への私の公開コントリビューションは小さな修正です。[kaldi-asr/kaldi#4657](https://github.com/kaldi-asr/kaldi/pull/4657) で、2021 年 12 月にマージされました。当時 Gitpod で Kaldi を開くと `.gitpod.dockerfile` が見つからないというエラーが出ていました。原因は設定ファイル上のファイル名と、実際の `.gitpod.Dockerfile` の大文字・小文字の違いです。この PR ではファイル名を修正し、Dockerfile から存在しないユーザーと使われていないパスを削除し、Intel MKL のインストールバージョンを固定しました。

変更は小さいものですが、この種のツールで私がずっと大事にしていることの表れでもあります。開発環境と実行環境は、他の人が再現できるべきです。

## GPU runtime を先に安定させる：driver、CUDA、container

Kaldi でも Whisper でも、GPU を使う以上、モデルの下には runtime のレイヤーが丸ごと存在します。私はそれを次のように分け、問題が起きたときもこの順番で調べます。

1. **ハードウェアとファームウェア設定**：GPU が認識されているか、Secure Boot が有効か。
2. **Kernel と NVIDIA kernel module**：module が現在の kernel 向けにビルドされているか、ロードが許可されているか。
3. **NVIDIA driver**：`nvidia-smi` が正常に応答するか。
4. **CUDA と関連ライブラリ**：CUDA runtime、cuDNN などのバージョンが driver や framework と互換性があるか。
5. **Container runtime**：container から GPU が見えるか。
6. **アプリケーションとモデル**：PyTorch、Kaldi のビルド、モデルファイルそのもの。

### Driver と CUDA のバージョン関係

NVIDIA の [CUDA Compatibility](https://docs.nvidia.com/deploy/cuda-compatibility/index.html) によると、driver と CUDA toolkit は別々のタイミングで更新できます。CUDA 11 からは [minor version compatibility](https://docs.nvidia.com/deploy/cuda-compatibility/minor-version-compatibility.html) があり、同じ major バージョン内でビルドしたアプリケーションは、driver が最低バージョン以上（例：CUDA 12.x なら 525 以上、CUDA 11.x なら 450 以上）であれば実行できます。ただし、新しい driver を必要とする一部の機能は制限され、device code を PTX にして JIT コンパイルするアプリケーションは対象外です。

実務的には、まず driver のバージョンを決め、その上で動かせる CUDA のバージョンを決めるということです。framework を更新するたびに driver を触る必要はありません。

### Container で CUDA と framework を分離する

[NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) は、host に NVIDIA driver がインストールされていることが前提です。Docker の場合、パッケージをインストールした後に次を実行します。

```bash
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

`nvidia-ctk` は host の `/etc/docker/daemon.json` を変更するため、この手順は構成管理に含めるべきです。続いて公式の [sample workload](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/sample-workload.html) で、container から GPU が見えることを確認します。

```bash
sudo docker run --rm --runtime=nvidia --gpus all ubuntu nvidia-smi
```

このように分けると、host は主に driver と container toolkit を担当し、CUDA、cuDNN、framework は image と一緒に管理できます。サービスごとに異なる CUDA バージョンを使え、アップグレードや rollback も host でパッケージを入れ直すのではなく、image の切り替えで済むようになります。

### ブログに記録してきた問題

以下は、私がこれまで公開してきた GPU 環境の問題です（記事は中国語）。同じ環境で起きたとは限りませんが、runtime をレイヤーごとに管理すべき理由がよくわかります。

| 症状 | 原因と対応 | 学んだこと |
| :-- | :-- | :-- |
| [nvidia-smi が driver と通信できない](https://blog.clarence.tw/2023/07/14/%e8%a7%a3%e6%b1%ba-ubuntu-%e4%b8%ad-nvidia-gpu-%e9%a9%85%e5%8b%95%e5%95%8f%e9%a1%8c/) | kernel 更新後に driver module が再ビルドされていなかった。DKMS で新しい kernel 向けに再ビルド | kernel の更新も GPU 環境の変更である |
| [Secure Boot 環境で driver がロードできない](https://blog.clarence.tw/2026/01/31/%e8%a7%a3%e6%b1%ba-ubuntu-24-04-secure-boot-%e7%92%b0%e5%a2%83%e4%b8%8b-nvidia-%e9%a9%85%e5%8b%95%e7%84%a1%e6%b3%95%e8%bc%89%e5%85%a5%e5%95%8f%e9%a1%8c/) | DKMS でローカルビルドした module が未署名で拒否された。Ubuntu の署名済み `linux-modules-nvidia-*` パッケージに切り替え | driver のために Secure Boot を無効にする必要はない |
| [nvidia-smi が No devices were found を表示する](https://blog.clarence.tw/2024/02/19/%e8%a7%a3%e6%b1%ba-nvidia-linux-%e4%bd%bf%e7%94%a8-nvidia-smi-%e5%87%ba%e7%8f%be-no-devices-were-found-%e5%95%8f%e9%a1%8c/) | パッケージでインストールした driver が GPU を初期化できなかった。NVIDIA 公式 installer で入れ直し、kernel と GCC のバージョン不一致を解消 | インストールに失敗したら、まず kernel log と installer log を見る |
| [CUDA パッケージの依存関係を解決できない](https://blog.clarence.tw/2022/05/31/%e5%ae%89%e8%a3%9d-cuda-%e5%87%ba%e7%8f%be-depends-cuda-11-7-11-7-0-but-it-is-not-going-to-be-installed-%e8%a7%a3%e6%b1%ba%e6%96%b9%e6%b3%95/) | GUI が driver を使用中だった。`multi-user.target` に切り替えてから削除・再インストール | driver の更新にはメンテナンス時間が必要 |
| [dpkg のファイル上書きエラー](https://blog.clarence.tw/2023/07/14/%e5%9c%a8-ubuntu-%e7%99%bc%e7%94%9f-dpkg-error-processing-archive-%e7%9a%84%e5%95%8f%e9%a1%8c%e8%a9%b2%e5%a6%82%e4%bd%95%e8%99%95%e7%90%86%ef%bc%9f/) | バージョンの異なる NVIDIA パッケージが同じファイルを上書きしようとした | 1 台のマシンでは driver パッケージの入手元をそろえる |
| [DGX で NO_PUBKEY が出る](https://blog.clarence.tw/2023/03/04/dgx-%e7%b3%bb%e7%b5%b1-ubuntu-18-04-%e5%87%ba%e7%8f%be-no_pubkey-a4b469963bf863cc-%e8%a7%a3%e6%b1%ba%e6%96%b9%e6%b3%95/) | NVIDIA CUDA repository の署名鍵が変更された。鍵を更新して解消 | 外部の repository も変わる。更新に失敗したらまずメッセージを読む |
| [cuDNN の検証サンプルがビルドできない](https://blog.clarence.tw/2022/06/01/%e5%ae%89%e8%a3%9d-cuda-deep-neural-network-cudnn-%e9%81%87%e5%88%b0-test-c110-fatal-error-freeimage-h-no-such-file-or-directory-%e8%a7%a3%e6%b1%ba%e6%96%b9%e6%b3%95/) | サンプルに追加の FreeImage ライブラリが必要だった | 検証手順そのものにも依存関係がある |

ほかにも、[CUDA Toolkit 11.7 のインストール方法](https://blog.clarence.tw/2022/05/31/%e5%ae%89%e8%a3%9d-cuda-toolkit-11-7/)（deb local、deb network、runfile）と [darknet での GPU 番号の指定](https://blog.clarence.tw/2021/10/24/yolo-alexeyab-darknet-set-gpu-number/)（`CUDA_VISIBLE_DEVICES` と framework 側の設定）の 2 本は、GPU 環境を計画するときに今も見返す基本です。

## デプロイと性能運用のチェックリスト

以下は一般的な確認項目で、実際の内容は環境に合わせて調整します。

### デプロイ前

- OS、kernel、NVIDIA driver、CUDA、cuDNN、framework、モデルのバージョン、image tag の組み合わせをすべて記録する。
- Secure Boot の状態（`mokutil --sb-state`）を確認し、kernel module を署名済みパッケージにするか自分で署名するかを決める。
- kernel と driver の更新方針を決め、自動更新で GPU 環境が気づかないうちに変わらないようにする。
- モデルサイズと想定する同時実行数から VRAM を見積もり、GPU ごとに動かすプロセス数と、`CUDA_VISIBLE_DEVICES` による割り当てを決める。

### デプロイ後の検証

- Host：`lsmod | grep nvidia` で module がロードされていること、`nvidia-smi` が正常に応答することを確認する。
- Container：sample workload で container から GPU が見えることを確認する。
- アプリケーション：決まった短いテスト音声で一連の流れを実行し、出力の形式と内容が妥当か確認する。
- 再起動後にもう一度検証し、driver とサービスが自動で復旧することを確認する。

### 日常の監視

- `nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total --format=csv` のようなコマンドや monitoring で、GPU 使用率とメモリを継続的に見る。
- 処理時間とキューの長さを見て、GPU 不足なのか、前処理が遅いのか、I/O が詰まっているのかを切り分ける。
- 大量の繰り返しや、明らかに音声に含まれない内容など、認識結果の異常に注意する。

### リスクのある操作

- `apt purge nvidia*`、`multi-user.target` への切り替え、kernel module の削除や置き換えは、いずれも GPU サービスを止めます。メンテナンス時間に行い、事前に復旧手段を確認します。
- `nvidia-ctk runtime configure` は Docker daemon の設定を書き換えるため、既存の設定と合わせてレビューします。
- 手間を省くために Secure Boot を無効にしないこと。どうしても必要な場合は、先にセキュリティへの影響を評価します。

## 学んだこと

- **モデルはレイヤーのひとつにすぎない。** Speech AI が長期的に安定して動くかどうかは、driver、kernel、CUDA、container といった下のレイヤーがきちんと管理されているかに大きく左右されます。
- **Driver は host に、それ以外は image に。** CUDA と framework を container に入れると、アップグレードも rollback もずっと単純になります。
- **自分の利用シーンで検証する。** Kaldi と Whisper にはそれぞれトレードオフがあります。公開 benchmark は参考にとどめ、最終的には実際に近い音声で比較します。
- **ハマったことは書き残す。** ブログに記録した GPU の問題は、どれも後にデプロイ前後のチェック項目になりました。
