# clarencetw.github.io

English | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md)

![Repository Size](https://img.shields.io/github/repo-size/clarencetw/clarencetw.github.io)
![Last Commit](https://img.shields.io/github/last-commit/clarencetw/clarencetw.github.io)
![License](https://img.shields.io/github/license/clarencetw/clarencetw.github.io)
![Deploy to GitHub Pages](https://github.com/clarencetw/clarencetw.github.io/actions/workflows/deploy-site.yaml/badge.svg)
![Lighthouse CI](https://github.com/clarencetw/clarencetw.github.io/actions/workflows/lighthouse-ci.yaml/badge.svg)

Personal portfolio and technical knowledge base for Clarence.

The site is built with [Hugo](https://gohugo.io/) and the [Toha](https://github.com/hugo-toha/toha) theme. It presents backend engineering, LLM applications, DevOps, cloud, on-prem infrastructure, and network operations work in Traditional Chinese, English, and Japanese.

Website: [clarence.tw](https://clarence.tw/)

## Structure

- `data/zh-tw`, `data/en`, and `data/ja`: multilingual homepage profile data.
- `content/posts`: long-form technical articles.
- `content/notes`: shorter technical notes.
- `assets/images`: source images processed by Hugo.
- `assets/styles/override.scss`: local visual overrides loaded after the Toha theme.
- `layouts/partials/header.html`: local SEO metadata, `hreflang`, `llms.txt` discoverability, and JSON-LD.
- `static/llms.txt`: site guide for AI / LLM crawlers.
- `.github/workflows`: GitHub Pages deployment, Lighthouse checks, and scheduled theme updates.

## Local Development

Requirements:

- Hugo extended `0.163.0` or newer. CI and Netlify currently pin `0.164.0`.
- Node.js `24` or newer.
- Go `1.23` or newer.

Check local versions:

```bash
hugo version
node -v
npm -v
go version
```

On macOS with Homebrew, update Hugo if it is below `0.163.0`:

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

Audit dependencies:

```bash
npm run audit
```

When the Toha module is updated, regenerate the Hugo npm metadata before installing:

```bash
npm run theme:update
```

## Maintenance

- `npm run audit` should report zero vulnerabilities before deployment.
- Dependabot tracks GitHub Actions, npm, and Go module updates.
- The scheduled theme update workflow opens a pull request from `dependencies/update-theme`.
- GitHub Pages publishes the generated `public` directory to the `gh-pages` branch.
- Most npm packages in this repository are generated from the Toha Hugo module by `hugo mod npm pack`; avoid manual major upgrades unless Toha updates its module metadata.
- GitHub issue, pull request, and commit titles should use English Conventional Commits when they map to a change; descriptions should use Traditional Chinese so the work history stays easy to review.

## SEO / AI crawler

- Hugo generates `sitemap.xml`; `layouts/robots.txt` exposes the sitemap and `llms.txt` entry point.
- `static/llms.txt` uses Markdown to summarize core pages, articles, notes, and external profiles.
- `layouts/partials/header.html` emits canonical links, `hreflang`, the `llms.txt` alternate link, the Open Graph image, and Person / WebSite JSON-LD.
- `static/clarencetw-og.png`, `static/_headers`, and `static/_redirects` are published to the `public` root through the `static` mount.

## Vercel

- Project name: `clarence-tw`.
- Framework preset: `Hugo`.
- Install command: `yum install golang -y && npm ci`.
- Build command: `npm run build`.
- Output directory: `public`.
- Required environment variables: `HUGO_VERSION=0.164.0`, `NODE_VERSION=24`, `GO_VERSION=1.23.0`.
- `vercel.json` keeps deploy settings, security headers, and the `gh-pages` ignore command in the repository.
- `static/vercel.json` is published to the `gh-pages` branch so Vercel skips builds if GitHub Pages output triggers a deployment. `gh-pages` is static output, does not include `package-lock.json`, and should not run `npm ci`.

## Cloudflare Pages

- Build system: use Pages v3 and pin required versions with environment variables instead of relying on build image defaults.
- Build command: `npm run build`. Cloudflare Pages installs dependencies from `package-lock.json` before running the build command; only use `SKIP_DEPENDENCY_INSTALL=1` with `npm ci && npm run build` when you intentionally want to own the install step.
- Output directory: `public`.
- `.node-version` pins Node.js `24` so Cloudflare Pages does not use the older Node.js 18 default from the v2 build image.
- Keep Production and Preview environment variables aligned: `HUGO_VERSION=0.164.0`, `GO_VERSION=1.23.0`, `NODE_VERSION=24`, `HUGO_ENV=production`.
- Production branch: `master`.
- Preview branch control: use Custom branches; include `*` and exclude `gh-pages` so the GitHub Pages static output branch is not rebuilt as source.

## License

This repository is licensed under the [Apache License 2.0](LICENSE).
