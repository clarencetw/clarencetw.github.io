#!/usr/bin/env bash

set -euo pipefail

command -v rsvg-convert >/dev/null || { echo "rsvg-convert is required" >&2; exit 1; }
command -v magick >/dev/null || { echo "ImageMagick is required" >&2; exit 1; }

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
tmp_dir="$(mktemp -d "${TMPDIR:-/tmp}/clarencetw-og.XXXXXX")"
trap 'rm -rf "$tmp_dir"' EXIT

rsvg-convert -w 1200 -h 630 \
  -o "$tmp_dir/base.png" \
  "$repo_root/assets/images/site/clarencetw-og-source.svg"

magick "$repo_root/assets/images/author/clarence.jpg" \
  -resize '238x286^' -gravity center -extent 238x286 \
  "$tmp_dir/photo.png"

magick -size 238x286 xc:none -fill white \
  -draw 'roundrectangle 0,0 237,285 20,20' \
  "$tmp_dir/mask.png"

magick "$tmp_dir/photo.png" "$tmp_dir/mask.png" \
  -alpha off -compose CopyOpacity -composite \
  "$tmp_dir/portrait.png"

magick "$tmp_dir/base.png" "$tmp_dir/portrait.png" \
  -geometry +873+92 -compose over -composite \
  "$repo_root/static/clarencetw-og.png"

echo "Generated static/clarencetw-og.png (1200x630)"
