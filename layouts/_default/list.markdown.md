---
title: {{ .Title | jsonify }}
url: {{ .Permalink | jsonify }}
language: {{ .Language.Lang | jsonify }}
---

# {{ .Title }}

{{ with .Description }}{{ . }}{{ end }}

{{ .RenderShortcodes | strings.TrimSpace }}

{{ range where (where .Pages "Layout" "!=" "search") "Params.hidden" "!=" true -}}
{{ printf "- [%s](%s)\n" .Title .Permalink -}}
{{ end -}}
