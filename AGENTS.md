# Repository Guidance

## Purpose

- This repository builds Clarence's public multilingual portfolio and technical knowledge site.
- Treat public accuracy, privacy, accessibility, and maintainability as product requirements.
- Prefer verifiable work, outcomes, dates, and links over broad or unverifiable claims.

## Source Map

- `config.yaml`: Hugo, Toha, language, feature, and site-wide settings.
- `data/<locale>/`: localized homepage profile and section data.
- `content/posts/`: long-form articles; translations use `index.en.md` and `index.ja.md`.
- `content/notes/`: operational references; keep tested versions, review dates, and safety notes explicit.
- `layouts/`: local Hugo overrides, SEO metadata, and custom notes templates.
- `assets/styles/override.scss` and `assets/scripts/`: local presentation and behavior.
- `resume/`: reviewable JSON Resume sources and provenance; the published PDF remains under `static/files/en/`.
- `static/`: files copied verbatim to the public site; anything here is publicly reachable.
- `.github/workflows/`: deploy, Lighthouse, and dependency maintenance automation.

## Commands

- Install: `npm ci`
- Develop: `npm run dev`
- Build: `npm run build`
- Include future-dated content: `npm run build:future`
- Build plus dependency audit: `npm run check`
- Update Toha only when explicitly requested: `npm run theme:update`

There is no repository-specific unit-test, lint, or type-check command. Do not claim otherwise.

## Content Rules

- Traditional Chinese is the primary language. Check matching English and Japanese files for every public-copy change.
- If a change intentionally applies to only one locale, state that in the handoff.
- Keep technical terms when they improve precision, but write surrounding copy naturally for the target language.
- Do not label a project or contribution as current without a current public or user-confirmed source.
- Operational notes must identify risky or destructive commands and include a review date or tested-version context.
- When core pages or positioning change, review `static/llms.txt`, localized site metadata, featured posts, and structured data.

## Privacy And Publication Boundary

- This is a public repository and website. Never publish secrets, credentials, customer data, private infrastructure, internal hostnames, security details, or unapproved employment information.
- Memories and prior private work may help with context but do not grant permission to publish those facts.
- Verify that personal details, customer references, metrics, and résumé claims are already public or explicitly approved before adding them.
- Treat `.env*`, local provider state, and `.claude/` as private local state.

## Generated And Dependency Boundaries

- Do not edit or commit `public/`, `resources/_gen/`, `.lighthouseci/`, `assets/jsconfig.json`, `.hugo_build.lock`, or `node_modules/`.
- Toha is a Hugo module. Prefer local overrides in `layouts/`, `assets/`, and `data/` over editing the module cache.
- Do not manually normalize theme-generated package metadata. Use the documented theme update flow.
- `master` is source. `gh-pages` is generated output and must not be edited as source.

## Verification

- Run at least `npm run build` for content or layout changes.
- Run `npm run check` before deployment when registry access is available.
- Preview every affected locale and verify both desktop and mobile behavior for visual changes.
- For SEO or deployment changes, verify the built output and the live canonical site, not only the source diff.
- Before replacing a résumé PDF, render every page to images and verify text order, links, clipping, dates, and privacy.
- Lighthouse CI must enforce explicit assertions; a report-only successful run is not a quality gate.

## Git And Documentation

- Use English Conventional Commit titles when committing changes.
- Use Traditional Chinese for human-facing issue, PR, and operational descriptions unless another language is requested.
- Stage only task-related files and leave unrelated worktree changes untouched.
- Keep this file concise and behavioral. Put explanatory or operator-facing detail in README or focused documentation.
