# clarencetw.github.io

[English](README.md) | [繁體中文](README.zh-TW.md) | 日本語

![Repository Size](https://img.shields.io/github/repo-size/clarencetw/clarencetw.github.io)
![Last Commit](https://img.shields.io/github/last-commit/clarencetw/clarencetw.github.io)
![License](https://img.shields.io/github/license/clarencetw/clarencetw.github.io)
![Security Headers](https://img.shields.io/security-headers?url=https%3A%2F%2Fclarence.tw%2F)

Clarence Lin の個人サイト、ポートフォリオ、技術ナレッジベースです。

このサイトは [Hugo](https://gohugo.io/) と [Toha](https://github.com/hugo-toha/toha) theme で構築されています。Backend engineering、LLM application、DevOps、Cloud / On-prem infrastructure、Network operations の経験を、繁體中文、English、日本語で紹介します。

Website: [clarence.tw](https://clarence.tw/)

## 構成

- `data/zh-tw`、`data/en`、`data/ja`: 多言語の homepage profile data。
- `content/posts`: 長めの技術記事。
- `content/notes`: 短めの技術メモ。
- `assets/images`: Hugo が処理する source images。
- `assets/styles/override.scss`: Toha theme の後に読み込む local visual overrides。
- `.github/workflows`: GitHub Pages deployment、Lighthouse checks、scheduled theme updates。

## Local Development

Requirements:

- Hugo extended `0.163.0` 以上。CI と Netlify は現在 `0.164.0` に固定しています。
- Node.js `24` 以上。
- Go `1.23` 以上。

Local versions を確認:

```bash
hugo version
node -v
npm -v
go version
```

macOS / Homebrew で Hugo が `0.163.0` より古い場合は更新します:

```bash
brew upgrade hugo
```

Install and run:

```bash
npm ci
npm run dev
```

Production build:

```bash
npm run build
```

Security audit:

```bash
npm run audit
```

Toha module を更新した後は、Hugo npm metadata を再生成してから install します。

```bash
npm run theme:update
```

## Maintenance

- Deploy 前に `npm run audit` が zero vulnerabilities であることを確認します。
- Dependabot が GitHub Actions、npm、Go module updates を追跡します。
- Scheduled theme update workflow は `dependencies/update-theme` から pull request を作成します。
- GitHub Pages は生成された `public` directory を `gh-pages` branch に公開します。
- この repository の npm packages の多くは Toha Hugo module から `hugo mod npm pack` で生成されます。Toha の module metadata が更新されていない場合、manual major upgrade は避けます。

## License

This repository is licensed under the [Apache License 2.0](LICENSE).
