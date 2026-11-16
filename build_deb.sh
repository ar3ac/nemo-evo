#!/usr/bin/env bash
#
# Nemo Evo - Debian Package Build Script
# Creates a standalone .deb package for Nemo Evo
#

set -e

VERSION="1.0.0"
PACKAGE_NAME="nemo-evo"
ARCH="all"
DIST_DIR="$(pwd)/dist"
BUILD_ROOT="${DIST_DIR}/${PACKAGE_NAME}_${VERSION}_${ARCH}"

echo "=== Building Debian Package: ${PACKAGE_NAME} v${VERSION} ==="

# Clean previous build
rm -rf "${DIST_DIR}"
mkdir -p "${BUILD_ROOT}/DEBIAN"
mkdir -p "${BUILD_ROOT}/usr/bin"
mkdir -p "${BUILD_ROOT}/usr/share/nemo-python/extensions"
mkdir -p "${BUILD_ROOT}/usr/share/nemo-evo"
mkdir -p "${BUILD_ROOT}/usr/share/applications"
mkdir -p "${BUILD_ROOT}/usr/share/locale/en/LC_MESSAGES"
mkdir -p "${BUILD_ROOT}/usr/share/locale/it/LC_MESSAGES"

# 1. Compile translation catalogs
echo "-> Compiling gettext catalogs..."
msgfmt "po/en.po" -o "${BUILD_ROOT}/usr/share/locale/en/LC_MESSAGES/nemo-evo.mo"
msgfmt "po/it.po" -o "${BUILD_ROOT}/usr/share/locale/it/LC_MESSAGES/nemo-evo.mo"

# 2. Copy extension & scripts
echo "-> Copying extension and binaries..."
cp "nemo_evo.py" "${BUILD_ROOT}/usr/share/nemo-python/extensions/nemo_evo.py"
chmod 644 "${BUILD_ROOT}/usr/share/nemo-python/extensions/nemo_evo.py"

cp "nemo_evo_prefs.py" "${BUILD_ROOT}/usr/share/nemo-evo/nemo_evo_prefs.py"
chmod 755 "${BUILD_ROOT}/usr/share/nemo-evo/nemo_evo_prefs.py"

cp "config/default_config.json" "${BUILD_ROOT}/usr/share/nemo-evo/default_config.json"

# Symlink executable to /usr/bin/nemo-evo-prefs
ln -s "/usr/share/nemo-evo/nemo_evo_prefs.py" "${BUILD_ROOT}/usr/bin/nemo-evo-prefs"

# 3. Desktop launcher
echo "-> Creating desktop launcher..."
cat << 'EOF' > "${BUILD_ROOT}/usr/share/applications/nemo-evo-prefs.desktop"
[Desktop Entry]
Type=Application
Name=Nemo Evo Preferences
Name[it]=Preferenze Nemo Evo
Comment=Configure toolbar action buttons for Nemo file manager
Comment[it]=Configura i pulsanti d'azione della barra strumenti per il gestore file Nemo
Exec=/usr/bin/nemo-evo-prefs
Icon=system-file-manager
Terminal=false
Categories=Settings;DesktopSettings;GTK;
Keywords=nemo;toolbar;buttons;cut;copy;paste;trash;delete;filemanager;
EOF
chmod 644 "${BUILD_ROOT}/usr/share/applications/nemo-evo-prefs.desktop"

# 4. Control file
echo "-> Writing DEBIAN/control..."
cat << EOF > "${BUILD_ROOT}/DEBIAN/control"
Package: ${PACKAGE_NAME}
Version: ${VERSION}
Section: utils
Priority: optional
Architecture: ${ARCH}
Depends: python3, python3-gi, gir1.2-gtk-3.0, python-nemo (>= 5.0) | python3-nemo, nemo (>= 5.0)
Maintainer: Nemo Evo Developers <dev@nemo-evo.org>
Description: Customizable action buttons toolbar extension for Nemo File Manager
 Adds Cut, Copy, Paste, Trash, Delete, and other configurable action
 buttons directly next to the address/path bar in Linux Mint Nemo.
 Includes a native GTK3 preferences utility.
EOF

# 5. Post-installation script
echo "-> Writing DEBIAN/postinst..."
cat << 'EOF' > "${BUILD_ROOT}/DEBIAN/postinst"
#!/bin/sh
set -e

if [ "$1" = "configure" ]; then
    # Update desktop database
    if command -v update-desktop-database >/dev/null 2>&1; then
        update-desktop-database -q /usr/share/applications || true
    fi
    # Restart nemo if running in active sessions
    if command -v nemo >/dev/null 2>&1; then
        nemo -q 2>/dev/null || true
    fi
fi
exit 0
EOF
chmod 755 "${BUILD_ROOT}/DEBIAN/postinst"

# 6. Post-removal script
echo "-> Writing DEBIAN/postrm..."
cat << 'EOF' > "${BUILD_ROOT}/DEBIAN/postrm"
#!/bin/sh
set -e

if [ "$1" = "remove" ] || [ "$1" = "purge" ]; then
    if command -v update-desktop-database >/dev/null 2>&1; then
        update-desktop-database -q /usr/share/applications || true
    fi
    if command -v nemo >/dev/null 2>&1; then
        nemo -q 2>/dev/null || true
    fi
fi
exit 0
EOF
chmod 755 "${BUILD_ROOT}/DEBIAN/postrm"

# 7. Build package
echo "-> Building .deb package..."
dpkg-deb --build "${BUILD_ROOT}" "${DIST_DIR}/${PACKAGE_NAME}_${VERSION}_${ARCH}.deb"

echo "=== Build finished successfully! ==="
echo "Package output: ${DIST_DIR}/${PACKAGE_NAME}_${VERSION}_${ARCH}.deb"
