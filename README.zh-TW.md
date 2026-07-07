# clarencetw.github.io

[English](README.md) | 繁體中文 | [日本語](README.ja.md)

![Repository Size](https://img.shields.io/github/repo-size/clarencetw/clarencetw.github.io)
![Last Commit](https://img.shields.io/github/last-commit/clarencetw/clarencetw.github.io)
![License](https://img.shields.io/github/license/clarencetw/clarencetw.github.io)
![Security Headers](https://img.shields.io/security-headers?url=https%3A%2F%2Fclarence.tw%2F)

Clarence Lin 的個人網站、作品集與技術知識庫。

網站使用 [Hugo](https://gohugo.io/) 與 [Toha](https://github.com/hugo-toha/toha) theme 建置，內容涵蓋 Backend engineering、LLM application、DevOps、Cloud / On-prem infrastructure 與 Network operations，並支援繁體中文、English、日本語。

網站：[clarence.tw](https://clarence.tw/)

## 專案結構

- `data/zh-tw`、`data/en`、`data/ja`：多語系首頁與個人資料。
- `content/posts`：長篇技術文章。
- `content/notes`：較短的技術筆記。
- `assets/images`：由 Hugo 處理的原始圖片。
- `assets/styles/override.scss`：載入在 Toha theme 之後的本地視覺樣式。
- `.github/workflows`：GitHub Pages deployment、Lighthouse checks 與定期 theme update workflow。

## 本機開發

需求：

- Hugo extended `0.163.0` 或更新版本。CI 與 Netlify 目前固定使用 `0.164.0`。
- Node.js `24` 或更新版本。
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

## License

本 repository 使用 [Apache License 2.0](LICENSE)。
