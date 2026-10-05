## {{ .Get "title" | default "Note" }}

{{ .Inner | strings.TrimSpace -}}
