# Résumé Sources

This directory keeps the multilingual résumé source reviewable and separate from the PDFs published by Hugo.

## Files

- `resume.multilingual.json` is the source for the published Traditional Chinese, English, and Japanese PDFs. It uses one shared structure so the three versions remain aligned.
- `resume.json` is the earlier conservative English JSON Resume draft retained as a reference source.
- `archive/resume-2023.json` is an exact archival copy of the public Gist revision that generated the superseded 2023 English PDF. It is historical evidence, not current truth.
- `requirements.txt` pins the Python PDF dependencies.
- `scripts/build-resumes.py` renders A4 PDFs with embedded subset fonts and copies them to the locale-specific public paths.
- `output/pdf/clarence-lin-resume-{zh-tw,en,ja}.pdf` contains the review artifacts.
- `static/files/{zh-tw,en,ja}/resume.pdf` contains the files published by the site.

The source JSON is not mounted into Hugo's `static/` directory. The repository itself is public, so do not add private employment, customer, infrastructure, or contact information here. The current public PDFs intentionally omit the Chinese legal name, thesis, customer-specific work, private infrastructure details, and uncertain metrics. Certification titles, component exams, and skill descriptions are checked against official issuer material linked from the source. They preserve the product versions and program names used when earned without inventing personal issue dates or credential IDs.

## Build

Install the pinned dependencies in an isolated environment, then build all locales:

```sh
python3 -m pip install -r resume/requirements.txt
python3 scripts/build-resumes.py \
  --cjk-font /path/to/NotoSansTC-Regular.ttf \
  --cjk-bold-font /path/to/NotoSansTC-SemiBold.ttf \
  --ja-font /path/to/NotoSansJP-Regular.ttf \
  --ja-bold-font /path/to/NotoSansJP-SemiBold.ttf
```

The script can also discover local Noto Sans TC or Arial Unicode fonts. Explicit font paths are preferred for repeatable results. Do not commit proprietary macOS or Microsoft fonts. Noto fonts should retain their SIL Open Font License provenance.

Render every page before publishing:

```sh
mkdir -p tmp/pdfs/resume-en
pdftoppm -png -r 150 output/pdf/clarence-lin-resume-en.pdf tmp/pdfs/resume-en/page
```

## 2023 Legacy PDF Provenance

The superseded 2023 English PDF can be traced to [public Gist revision `0e9ea565`](https://gist.github.com/clarencetw/dbe9d6fac5e716b9d602b6d41b11d541/0e9ea565e0a7877bfe32d8f68c852cac09e51139), committed at `2023-01-16T13:43:46Z`.

Evidence:

- The Gist revision contains the same 13 skill groups, 7 work records, 3 education records, 4 volunteer records, and profile links as the superseded PDF.
- The PDF reports `Creator: Chromium`, `Producer: Skia/PDF m105`, two US Letter pages, and a creation time of `2023-01-16 22:22:12 +08:00`.
- Git commit [`61fbcae`](https://github.com/clarencetw/clarencetw.github.io/commit/61fbcae9a132ab251e7bc8b2778021f598661710) replaced the first PDF with that version later the same day.
- The superseded PDF SHA-256 is `9ad43a1850d4164a3a2cb74a101522ef6f29f14b8c8092151569f32d9e41c990`.

The earlier PDF from commit [`2a940fd`](https://github.com/clarencetw/clarencetw.github.io/commit/2a940fd56385dad41cb084a7877bfe92ff35a23c) was generated with XeTeX and an Awesome-CV-based template. Its creation time was 68 seconds after the Gist's initial revision, and its content matches that initial JSON. No original `.tex`, Word document, or HTML/CSS résumé source exists in this repository's reachable branches, tags, or recoverable Git commits.

## 2023 Legacy PDF Toolchain

The superseded PDF's renderer is reproducible from the 2023 source and these historical versions:

- `resume-cli@3.0.8`
- `jsonresume-theme-paper@0.5.0`
- `puppeteer@16.2.0`, which bundles Chromium `105.0.5173.0`

The likely original command was:

```sh
resume export resume.pdf --theme paper
```

If exact historical reproduction is needed, run those legacy packages in an isolated temporary directory rather than adding them to this site's dependencies. These versions are retained for archaeological reproducibility, not as a recommendation for general browsing or long-term production use.

## Updating The Résumé

1. Review `resume.multilingual.json` with the owner. Verify dates and whether an activity is current; do not infer `Present` from missing information.
2. Keep the public résumé focused. Do not copy private memories, internal systems, customer data, or unapproved metrics into it.
3. Update all three locale objects together so section order and facts remain aligned.
4. Run the pinned ReportLab renderer, then inspect all six pages as images.
5. Extract text to check reading order and verify links, page count, embedded fonts, and clipping before publishing.
