# clarencetw.github.io

[English](README.md) | 繁體中文 | [日本語](README.ja.md)

![Repository Size](https://img.shields.io/github/repo-size/clarencetw/clarencetw.github.io)
![Last Commit](https://img.shields.io/github/last-commit/clarencetw/clarencetw.github.io)
![License](https://img.shields.io/github/license/clarencetw/clarencetw.github.io)
![Deploy to GitHub Pages](https://github.com/clarencetw/clarencetw.github.io/actions/workflows/deploy-site.yaml/badge.svg)
![Lighthouse CI](https://github.com/clarencetw/clarencetw.github.io/actions/workflows/lighthouse-ci.yaml/badge.svg)

Clarence 的個人網站、作品集與技術知識庫。

網站使用 [Hugo](https://gohugo.io/) 與 [Toha](https://github.com/hugo-themes/toha) theme 建置，內容涵蓋 Backend engineering、LLM application、DevOps、Cloud / On-prem infrastructure 與 Network operations，並支援繁體中文、English、日本語。

網站：[clarence.tw](https://clarence.tw/)

## 專案結構

- `data/zh-tw`、`data/en`、`data/ja`：多語系首頁與個人資料。
- `content/posts`：長篇技術文章。
- `content/notes`：較短的技術筆記。
- `assets/images`：由 Hugo 處理的原始圖片。
- `assets/styles/override.scss`：載入在 Toha theme 之後的本地視覺樣式。
- `resume`：找回的 JSON Resume 原始資料、保守版現況草稿與來源考證。
- `layouts/partials/header.html`：本地 SEO metadata、`hreflang`、`llms.txt` discoverability 與 JSON-LD。
- `static/llms.txt`：AI / LLM crawler 使用的網站導覽摘要。
- `.github/workflows`：GitHub Pages deployment、Lighthouse checks 與定期 theme update workflow。

## 本機開發

需求：

- Hugo extended `0.163.0` 或更新版本。CI 與 Netlify 目前固定使用 `0.164.0`。
- Node.js `24.x`。
- Go `1.23` 或更新版本。

確認本機版本：

```bash
hugo version
node -v
npm -v
go version
```

macOS / Homebrew 如果 Hugo 版本低於 `0.163.0`，先更新 Hugo：

```bash
brew upgrade hugo
```

安裝並啟動：

```bash
npm ci
npm run dev
```

Production build：

```bash
npm run build
```

重新產生社群預覽圖（需要 `rsvg-convert` 與 ImageMagick）：

```bash
npm run assets:og
```

Security audit：

```bash
npm run audit
```

更新 Toha module 後，先重新產生 Hugo npm metadata 再安裝：

```bash
npm run theme:update
```

## 維護

- 部署前 `npm run audit` 應維持零漏洞。
- Dependabot 追蹤 GitHub Actions、npm 與 Go module updates。
- 定期 theme update workflow 會從 `dependencies/update-theme` 開 pull request。
- GitHub Pages 會將產出的 `public` directory 發佈到 `gh-pages` branch。
- 這個 repository 的多數 npm packages 由 Toha Hugo module 透過 `hugo mod npm pack` 產生；除非 Toha module metadata 已更新，不建議手動升級 major version，避免和 theme 需求衝突。
- GitHub issue、pull request 與 commit title 如果對應到一個變更，應使用英文 Conventional Commits；description 使用繁體中文，方便日後回看脈絡。

## SEO / AI crawler

- Hugo 產生 `sitemap.xml`，`layouts/robots.txt` 會公開 sitemap 與 `llms.txt` 入口。
- `static/llms.txt` 使用 Markdown 格式整理核心頁面、文章、筆記與外部 profile。
- `layouts/partials/header.html` 會輸出 canonical、`hreflang`、`llms.txt` alternate link、Open Graph 圖與 Person / WebSite JSON-LD。
- `static/clarencetw-og.png`、`static/_headers`、`static/_redirects` 會透過 `static` mount 發佈到 `public` root。

## Vercel

- Project name：`clarence-tw`。
- Framework preset：`Hugo`。
- Install command：`yum install golang -y && npm ci`。
- Build command：`npm run build`。
- Output directory：`public`。
- 必要 environment variables：`HUGO_VERSION=0.164.0`、`NODE_VERSION=24`、`GO_VERSION=1.23.0`。
- `vercel.json` 會在 repository 內固定 deploy settings、security headers 與 `gh-pages` ignore command。
- `static/vercel.json` 會被發佈到 `gh-pages` branch，讓 Vercel 如果被 GitHub Pages 輸出 branch 觸發，也會直接 skip build。`gh-pages` 是靜態輸出物，沒有 `package-lock.json`，不應執行 `npm ci`。

## Cloudflare Pages

- Build system：建議使用 Pages v3，並用環境變數固定必要版本，避免依賴 build image 預設值。
- Build command：`npm run build`。Cloudflare Pages 會先依照 `package-lock.json` 自動安裝 dependencies；如果要手動控制安裝流程，才改用 `SKIP_DEPENDENCY_INSTALL=1` 搭配 `npm ci && npm run build`。
- Output directory：`public`。
- `.node-version` 會固定 Node.js `24`，避免 Cloudflare Pages 使用 v2 build image 預設的 Node.js 18。
- Production 與 Preview environment variables 應保持一致：`HUGO_VERSION=0.164.0`、`GO_VERSION=1.23.0`、`NODE_VERSION=24`、`HUGO_ENV=production`。
- Production branch：`master`。
- Preview branch control：使用 Custom branches；Include `*`，Exclude `gh-pages`，避免 GitHub Pages 的靜態輸出 branch 被 Cloudflare 當成原始碼重新 build。

## License

本 repository 使用 [Apache License 2.0](LICENSE)。
