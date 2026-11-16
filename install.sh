#!/usr/bin/env bash
#
# Nemo Evo - Installation Script
# Installs Nemo Evo extension and configuration utility for current user.
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXTENSIONS_DIR="${HOME}/.local/share/nemo-python/extensions"
APPLICATIONS_DIR="${HOME}/.local/share/applications"
LOCALE_BASE="${HOME}/.local/share/locale"
CONFIG_DIR="${HOME}/.config/nemo_evo"

echo "=== Installing Nemo Evo ==="

# 1. Ensure required directories exist
mkdir -p "${EXTENSIONS_DIR}"
mkdir -p "${APPLICATIONS_DIR}"
mkdir -p "${CONFIG_DIR}"
mkdir -p "${LOCALE_BASE}/it/LC_MESSAGES"
mkdir -p "${LOCALE_BASE}/en/LC_MESSAGES"

# 2. Compile and install translations
echo "-> Compiling translations..."
if command -v msgfmt >/dev/null 2>&1; then
    msgfmt "${SCRIPT_DIR}/po/en.po" -o "${SCRIPT_DIR}/locale/en/LC_MESSAGES/nemo-evo.mo"
    msgfmt "${SCRIPT_DIR}/po/it.po" -o "${SCRIPT_DIR}/locale/it/LC_MESSAGES/nemo-evo.mo"
    cp "${SCRIPT_DIR}/locale/en/LC_MESSAGES/nemo-evo.mo" "${LOCALE_BASE}/en/LC_MESSAGES/"
    cp "${SCRIPT_DIR}/locale/it/LC_MESSAGES/nemo-evo.mo" "${LOCALE_BASE}/it/LC_MESSAGES/"
    echo "   Translations compiled and installed successfully."
else
    echo "   Warning: msgfmt not found, skipping gettext compilation."
fi

# 3. Clean up any previous probe/test files
rm -f "${EXTENSIONS_DIR}/probe.py" "${EXTENSIONS_DIR}/nemo_evo_extension.py"

# 4. Install main extension (symlink to project directory so edits reflect immediately)
echo "-> Installing Nemo Python extension..."
ln -sf "${SCRIPT_DIR}/nemo_evo.py" "${EXTENSIONS_DIR}/nemo_evo.py"
chmod +x "${SCRIPT_DIR}/nemo_evo.py"
chmod +x "${SCRIPT_DIR}/nemo_evo_prefs.py"

# 5. Install desktop launcher
echo "-> Installing desktop application launcher..."
sed "s|/home/ar3ac/projects/nemo_evo|${SCRIPT_DIR}|g" "${SCRIPT_DIR}/nemo-evo-prefs.desktop" > "${APPLICATIONS_DIR}/nemo-evo-prefs.desktop"
chmod +x "${APPLICATIONS_DIR}/nemo-evo-prefs.desktop"

# 6. Initialize default config if not present
if [ ! -f "${CONFIG_DIR}/config.json" ]; then
    echo "-> Initializing default configuration..."
    cp "${SCRIPT_DIR}/config/default_config.json" "${CONFIG_DIR}/config.json"
fi

# 7. Restart Nemo
echo "-> Restarting Nemo..."
if command -v nemo >/dev/null 2>&1; then
    nemo -q || true
    echo "   Nemo restarted."
fi

echo "=== Nemo Evo installed successfully! ==="
echo "You can open Nemo to see your new buttons, or launch 'Nemo Evo Preferences' to customize them."
