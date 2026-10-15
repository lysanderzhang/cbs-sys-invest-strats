#!/bin/sh
# Render every PDF page to PNG for visual QA (requires poppler-utils).
OUT=${1:-build/pages}; mkdir -p "$OUT"; rm -f "$OUT"/p-*.png
pdftoppm -r ${2:-110} -png ../../submission/Investor_Presentation.pdf "$OUT/p"
