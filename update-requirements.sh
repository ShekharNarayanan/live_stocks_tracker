#!/usr/bin/env bash
set -euo pipefail

# ── 1. Re-generate the raw list ────────────────────────────────────────────────
# • --format=freeze  gives  name==version  pairs (no wide “columns” output)
# • Save to a temp file so we can post-process safely
pip list --format=freeze > requirements.tmp

# ── 2. Add platform markers for Windows-only wheels ────────────────────────────
# Define the packages you want to gate behind  platform_system == "Windows"
WINDOWS_ONLY=(
  pywin32
  pywin32-ctypes
  pywinpty
)

# Build a regexp like  ^(pywin32|pywinpty|…)==
REGEX="^($(printf '%s|' "${WINDOWS_ONLY[@]}"))=="

# While reading requirements.tmp line-by-line:
# • If the line starts with one of the Windows packages,
#   append the environment marker   ; platform_system == "Windows"
# • Otherwise, copy the line verbatim
awk -v regex="$REGEX" '
  $0 ~ regex { sub(/==/, "==", $0); print $0 " ; platform_system == \"Windows\""; next }
  { print }
' requirements.tmp > requirements.txt

rm requirements.tmp

echo "✅  requirements.txt updated. Windows-specific packages now have platform markers."
