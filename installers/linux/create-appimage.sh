#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APPIMAGE_TOOL="${HOME}/bin/appimagetool.AppImage"
if [[ ! -f "$APPIMAGE_TOOL" ]]; then
  echo "Download appimagetool from https://appimage.org/ and place it at $APPIMAGE_TOOL"
  exit 1
fi

WORKDIR="${ROOT}/appimage"
rm -rf "$WORKDIR"
mkdir -p "$WORKDIR/usr/bin" "$WORKDIR/usr/share/applications" "$WORKDIR/usr/share/icons/hicolor/256x256/apps"

# copy runtime
rsync -av --exclude='.git' "$ROOT/" "$WORKDIR/usr/bin/aurora"

# Create basic desktop file
cat > "$WORKDIR/usr/share/applications/aurora.desktop" <<DESK
[Desktop Entry]
Type=Application
Name=AuroraOS
Exec=/usr/bin/aurora/aurora.sh start
Icon=aurora
Terminal=false
Categories=Development;
DESK

# placeholder icon: you should place your PNG icon
touch "$WORKDIR/usr/share/icons/hicolor/256x256/apps/aurora.png"

chmod +x "$APPIMAGE_TOOL"
"$APPIMAGE_TOOL" "$WORKDIR" "$ROOT/AuroraOS.AppImage"
echo "AppImage created at $ROOT/AuroraOS.AppImage"
