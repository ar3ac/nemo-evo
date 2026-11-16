#!/usr/bin/env bash
#
# Nemo Evo - Uninstallation Script
# Removes Nemo Evo extension, launcher, and locale files for current user.
#

set -e

EXTENSIONS_DIR="${HOME}/.local/share/nemo-python/extensions"
APPLICATIONS_DIR="${HOME}/.local/share/applications"
LOCALE_BASE="${HOME}/.local/share/locale"

echo "=== Uninstalling Nemo Evo ==="

rm -f "${EXTENSIONS_DIR}/nemo_evo.py"
rm -f "${EXTENSIONS_DIR}/probe.py"
rm -f "${EXTENSIONS_DIR}/nemo_evo_extension.py"
rm -f "${APPLICATIONS_DIR}/nemo-evo-prefs.desktop"
rm -f "${LOCALE_BASE}/it/LC_MESSAGES/nemo-evo.mo"
rm -f "${LOCALE_BASE}/en/LC_MESSAGES/nemo-evo.mo"

echo "-> Restarting Nemo..."
if command -v nemo >/dev/null 2>&1; then
    nemo -q || true
fi

echo "=== Nemo Evo uninstalled. (Configuration in ~/.config/nemo_evo kept) ==="
