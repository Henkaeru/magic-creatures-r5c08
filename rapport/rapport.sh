#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
pandoc rapport.md -o rapport.pdf \
  --pdf-engine=xelatex \
  -V lang=fr \
  -V geometry:a4paper \
  -V geometry:top=2.3cm \
  -V geometry:left=2.3cm \
  -V geometry:right=2.3cm \
  -V geometry:bottom=3.2cm \
  -V fontsize=11pt \
  -V mainfont="Noto Serif" \
  -V colorlinks=true \
  --resource-path=.:..
