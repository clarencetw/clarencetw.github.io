{{- $home := . -}}
{{- $about := (index hugo.Data .Language.Lang).sections.about -}}
---
title: {{ .Title | jsonify }}
url: {{ .Permalink | jsonify }}
language: {{ .Language.Lang | jsonify }}
---

# {{ .Site.Title }}

{{ replace $about.summary "](#" (printf "](%s#" .Permalink) }}

{{ range $about.resourceLinks -}}
{{- $url := .url | absURL -}}
{{- if hasPrefix .url "#" -}}{{- $url = printf "%s%s" $home.Permalink .url -}}{{- end -}}
{{ printf "- [%s](%s)\n" .title $url -}}
{{ end -}}
- [llms.txt]({{ "llms.txt" | absURL }})
- [Sitemap]({{ "sitemap.xml" | absURL }})
