# clarencetw.github.io

[English](README.md) | [繁體中文](README.zh-TW.md) | 日本語

![Repository Size](https://img.shields.io/github/repo-size/clarencetw/clarencetw.github.io)
![Last Commit](https://img.shields.io/github/last-commit/clarencetw/clarencetw.github.io)
![License](https://img.shields.io/github/license/clarencetw/clarencetw.github.io)
![Deploy to GitHub Pages](https://github.com/clarencetw/clarencetw.github.io/actions/workflows/deploy-site.yaml/badge.svg)
![Lighthouse CI](https://github.com/clarencetw/clarencetw.github.io/actions/workflows/lighthouse-ci.yaml/badge.svg)

Clarence の個人サイト、ポートフォリオ、技術ナレッジベースです。

このサイトは [Hugo](https://gohugo.io/) と [Toha](https://github.com/hugo-toha/toha) theme で構築されています。Backend engineering、LLM application、DevOps、Cloud / On-prem infrastructure、Network operations の経験を、繁體中文、English、日本語で紹介します。

Website: [clarence.tw](https://clarence.tw/)

## 構成

- `data/zh-tw`、`data/en`、`data/ja`: 多言語の homepage profile data。
- `content/posts`: 長めの技術記事。
- `content/notes`: 短めの技術メモ。
- `assets/images`: Hugo が処理する source images。
- `assets/styles/override.scss`: Toha theme の後に読み込む local visual overrides。
- `layouts/partials/header.html`: local SEO metadata、`hreflang`、`llms.txt` discoverability、JSON-LD。
- `static/llms.txt`: AI / LLM crawler 向けの site guide。
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
- GitHub issue、pull request、commit の title は、change に対応する場合 English Conventional Commits を使います。description は繁體中文で記録します。

## SEO / AI crawler

- Hugo が `sitemap.xml` を生成し、`layouts/robots.txt` が sitemap と `llms.txt` entry point を公開します。
- `static/llms.txt` は Markdown で core pages、articles、notes、external profiles を整理します。
- `layouts/partials/header.html` は canonical、`hreflang`、`llms.txt` alternate link、Open Graph image、Person / WebSite JSON-LD を出力します。
- `static/clarencetw-og.png`、`static/_headers`、`static/_redirects` は `static` mount で `public` root に公開されます。

## Vercel

- Project name: `clarence-tw`。
- Framework preset: `Hugo`。
- Install command: `yum install golang -y && npm ci`。
- Build command: `npm run build`。
- Output directory: `public`。
- Required environment variables: `HUGO_VERSION=0.164.0`、`NODE_VERSION=24`、`GO_VERSION=1.23.0`。
- `vercel.json` で deploy settings、security headers、`gh-pages` ignore command を repository 内に固定します。
- `static/vercel.json` は `gh-pages` branch に公開されるため、GitHub Pages output が Vercel deployment を起動しても build を skip します。`gh-pages` は静的出力で、`package-lock.json` がないため `npm ci` を実行しません。

## Cloudflare Pages

- Build command: `npm ci && npm run build`。
- Output directory: `public`。
- `.node-version` で Node.js `24` を固定し、Cloudflare Pages の v2 build image が既定の Node.js 18 を使わないようにします。
- Required environment variables: `HUGO_VERSION=0.164.0`、`GO_VERSION=1.23.0`。

## License

This repository is licensed under the [Apache License 2.0](LICENSE).
