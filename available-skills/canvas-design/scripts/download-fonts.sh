#!/bin/bash
# Download canvas-design fonts
# Tries Anthropic's GitHub repo first, falls back to Google Fonts API

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FONT_DIR="$SCRIPT_DIR/../canvas-fonts"
mkdir -p "$FONT_DIR"

GITHUB_BASE="https://raw.githubusercontent.com/anthropics/skills/main/skills/canvas-design/canvas-fonts"

FONTS=(
  ArsenalSC-Regular.ttf
  BigShoulders-Bold.ttf
  BigShoulders-Regular.ttf
  Boldonse-Regular.ttf
  BricolageGrotesque-Bold.ttf
  BricolageGrotesque-Regular.ttf
  CrimsonPro-Bold.ttf
  CrimsonPro-Italic.ttf
  CrimsonPro-Regular.ttf
  DMMono-Regular.ttf
  EricaOne-Regular.ttf
  GeistMono-Bold.ttf
  GeistMono-Regular.ttf
  Gloock-Regular.ttf
  IBMPlexMono-Bold.ttf
  IBMPlexMono-Regular.ttf
  IBMPlexSerif-Bold.ttf
  IBMPlexSerif-BoldItalic.ttf
  IBMPlexSerif-Italic.ttf
  IBMPlexSerif-Regular.ttf
  InstrumentSans-Bold.ttf
  InstrumentSans-BoldItalic.ttf
  InstrumentSans-Italic.ttf
  InstrumentSans-Regular.ttf
  InstrumentSerif-Italic.ttf
  InstrumentSerif-Regular.ttf
  Italiana-Regular.ttf
  JetBrainsMono-Bold.ttf
  JetBrainsMono-Regular.ttf
  Jura-Light.ttf
  Jura-Medium.ttf
  LibreBaskerville-Regular.ttf
  Lora-Bold.ttf
  Lora-BoldItalic.ttf
  Lora-Italic.ttf
  Lora-Regular.ttf
  NationalPark-Bold.ttf
  NationalPark-Regular.ttf
  NothingYouCouldDo-Regular.ttf
  Outfit-Bold.ttf
  Outfit-Regular.ttf
  PixelifySans-Medium.ttf
  PoiretOne-Regular.ttf
  RedHatMono-Bold.ttf
  RedHatMono-Regular.ttf
  Silkscreen-Regular.ttf
  SmoochSans-Medium.ttf
  Tektur-Medium.ttf
  Tektur-Regular.ttf
  WorkSans-Bold.ttf
  WorkSans-BoldItalic.ttf
  WorkSans-Italic.ttf
  WorkSans-Regular.ttf
  YoungSerif-Regular.ttf
)

downloaded=0
skipped=0
failed=0

for font in "${FONTS[@]}"; do
  if [ -f "$FONT_DIR/$font" ]; then
    skipped=$((skipped + 1))
    continue
  fi

  # Try Anthropic's GitHub first
  if curl -fsSL "$GITHUB_BASE/$font" -o "$FONT_DIR/$font" 2>/dev/null; then
    downloaded=$((downloaded + 1))
    echo "  Downloaded: $font"
    continue
  fi

  # Fallback: Google Fonts API
  # Extract family name (e.g., "CrimsonPro" -> "Crimson+Pro")
  family=$(echo "$font" | sed 's/-[A-Za-z]*\.ttf$//' | sed 's/\([a-z]\)\([A-Z]\)/\1+\2/g')
  google_url="https://fonts.google.com/download?family=${family}"

  if curl -fsSL "$google_url" -o "/tmp/gfont_${family}.zip" 2>/dev/null; then
    if unzip -o -j "/tmp/gfont_${family}.zip" "*${font}" -d "$FONT_DIR" 2>/dev/null; then
      downloaded=$((downloaded + 1))
      echo "  Downloaded (Google): $font"
      rm -f "/tmp/gfont_${family}.zip"
      continue
    fi
    rm -f "/tmp/gfont_${family}.zip"
  fi

  failed=$((failed + 1))
  echo "  FAILED: $font"
done

echo ""
echo "Done: $downloaded downloaded, $skipped already existed, $failed failed"

if [ $failed -gt 0 ]; then
  echo "Some fonts failed to download. The skill will still work with available fonts."
fi
