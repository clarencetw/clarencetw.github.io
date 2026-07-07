# clarencetw.github.io

English | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md)

![Repository Size](https://img.shields.io/github/repo-size/clarencetw/clarencetw.github.io)
![Last Commit](https://img.shields.io/github/last-commit/clarencetw/clarencetw.github.io)
![License](https://img.shields.io/github/license/clarencetw/clarencetw.github.io)
![Security Headers](https://img.shields.io/security-headers?url=https%3A%2F%2Fclarence.tw%2F)

Personal portfolio and technical knowledge base for Clarence Lin.

The site is built with [Hugo](https://gohugo.io/) and the [Toha](https://github.com/hugo-toha/toha) theme. It presents backend engineering, LLM applications, DevOps, cloud, on-prem infrastructure, and network operations work in Traditional Chinese, English, and Japanese.

Website: [clarence.tw](https://clarence.tw/)

## Structure

- `data/zh-tw`, `data/en`, and `data/ja`: multilingual homepage profile data.
- `content/posts`: long-form technical articles.
- `content/notes`: shorter technical notes.
- `assets/images`: source images processed by Hugo.
- `assets/styles/override.scss`: local visual overrides loaded after the Toha theme.
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

## License

This repository is licensed under the [Apache License 2.0](LICENSE).
