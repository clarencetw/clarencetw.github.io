---
title: {{ .Title | jsonify }}
url: {{ .Permalink | jsonify }}
language: {{ .Language.Lang | jsonify }}
---

# {{ .Title }}

{{ with .Description }}{{ . }}{{ end }}

{{ .RenderShortcodes | strings.TrimSpace }}
