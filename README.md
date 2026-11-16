# Nemo Evo 🚀

[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Support on Ko-fi](https://img.shields.io/badge/Ko--fi-Support-29abe0?style=flat&logo=ko-fi&logoColor=white)](https://ko-fi.com/ar3ac)

Customizable action buttons toolbar extension for the **Nemo File Manager** on **Linux Mint (Cinnamon)**.

![Nemo Toolbar with Action Buttons](assets/screenshot_toolbar.png)

---

## 🌟 Overview

By default, the Nemo file manager in Linux Mint / Cinnamon does not offer toolbar buttons for common file operations such as **Cut**, **Copy**, **Paste**, **Move to Trash**, and **Delete**. Users are typically forced to rely on keyboard shortcuts or right-click context menus.

**Nemo Evo** solves this problem by seamlessly injecting customizable, native GTK action buttons directly onto Nemo's primary toolbar (right next to the address/path bar).

### ✨ Features

- ✂️ **Cut** (`Ctrl+X`)
- 📋 **Copy** (`Ctrl+C`)
- 📄 **Paste** (`Ctrl+V`)
- 🗑️ **Move to Trash** (`Delete`)
- ❌ **Permanently Delete** (`Shift+Delete`)
- ↩️ **Undo** (`Ctrl+Z` - optional)
- ↪️ **Redo** (`Ctrl+Y` - optional)
- ☑️ **Select All** (`Ctrl+A` - optional)
- 📁 **New Folder** (`Ctrl+Shift+N` - optional)
- ⚙️ **GUI Preferences Editor**: Easily enable/disable buttons, reorder them, and choose their toolbar position.
- 🎨 **Native Theme Integration**: Uses standard Cinnamon symbolic icons and flat GTK button styling.
- 🌍 **Internationalization (i18n)**: Out of the box support for English (`en`) and Italian (`it`).

---

## 🖼️ Preferences & Customization

Nemo Evo includes a standalone GTK3 configuration tool to customize your toolbar layout:

![Nemo Evo Preferences](assets/screenshot_preferences.png)

- **Toggle Buttons**: Choose which buttons appear on your toolbar.
- **Reorder Buttons**: Move buttons up or down (▲ / ▼) to match your workflow.
- **Position Options**:
  - *Right of Address Bar* (Default & Recommended)
  - *Left of Address Bar*
  - *Far Right of Toolbar*
- **One-Click Apply**: Save settings and restart Nemo instantly.

You can launch the preferences manager anytime from your application menu under **Preferences -> Nemo Evo Preferences**, or via terminal:
```bash
python3 /path/to/nemo_evo/nemo_evo_prefs.py
```

---

## 📦 Installation

### Method 1: Debian Package (.deb) — Recommended for Users
Download the latest `.deb` package from the [Releases](https://github.com/ar3ac/nemo-evo/releases) page and install it:
```bash
sudo apt update
sudo apt install ./nemo-evo_1.0.0_all.deb
```
Or simply double-click the downloaded `.deb` file to install via GDebi / Linux Mint Package Installer.

---

### Method 2: User-Level Install (from source)
If you prefer running from source or want to modify the code:
```bash
# 1. Install prerequisite if not already present
sudo apt update
sudo apt install python-nemo

# 2. Clone repository & run installer
git clone https://github.com/ar3ac/nemo-evo.git
cd nemo-evo
./install.sh
```

The installer script:
1. Compiles gettext localization catalogs (`.mo`).
2. Symlinks the extension into `~/.local/share/nemo-python/extensions/`.
3. Installs the desktop preferences launcher into `~/.local/share/applications/`.
4. Initializes the default configuration at `~/.config/nemo_evo/config.json`.
5. Restarts Nemo to apply changes immediately.

---

### 🔨 Building the Package (.deb)
To build your own Debian package from source:
```bash
./build_deb.sh
```
The output package will be generated under `dist/nemo-evo_1.0.0_all.deb`.

---

## 🗑️ Uninstallation

To remove the extension and desktop launcher:
```bash
./uninstall.sh
```

---

## 🔧 Configuration File

Your configuration is stored in JSON format at:
```
~/.config/nemo_evo/config.json
```

Example structure:
```json
{
  "version": 1,
  "position": "right_of_pathbar",
  "buttons": [
    {"id": "cut", "enabled": true, "icon": "edit-cut-symbolic", "shortcut": "Ctrl+X"},
    {"id": "copy", "enabled": true, "icon": "edit-copy-symbolic", "shortcut": "Ctrl+C"},
    {"id": "paste", "enabled": true, "icon": "edit-paste-symbolic", "shortcut": "Ctrl+V"},
    {"id": "trash", "enabled": true, "icon": "user-trash-symbolic", "shortcut": "Canc"},
    {"id": "delete", "enabled": true, "icon": "edit-delete-symbolic", "shortcut": "Shift+Canc"},
    {"id": "undo", "enabled": false, "icon": "edit-undo-symbolic", "shortcut": "Ctrl+Z"},
    {"id": "redo", "enabled": false, "icon": "edit-redo-symbolic", "shortcut": "Ctrl+Y"},
    {"id": "select_all", "enabled": false, "icon": "edit-select-all-symbolic", "shortcut": "Ctrl+A"},
    {"id": "new_folder", "enabled": false, "icon": "folder-new-symbolic", "shortcut": "Ctrl+Shift+N"}
  ]
}
```

---

## 🌐 Localization (i18n)

Translations are handled with GNU `gettext`. 
- Language files reside in `po/` (`nemo-evo.pot`, `en.po`, `it.po`).
- Compiled catalogs reside in `locale/<lang>/LC_MESSAGES/nemo-evo.mo`.

To compile translations manually:
```bash
msgfmt po/it.po -o locale/it/LC_MESSAGES/nemo-evo.mo
msgfmt po/en.po -o locale/en/LC_MESSAGES/nemo-evo.mo
```

---

## ☕ Support

If you find **Nemo Evo** helpful and it improves your daily workflow on Linux Mint, feel free to support its development:

<a href="https://ko-fi.com/ar3ac" target="_blank"><img src="https://ko-fi.com/img/githubbutton_sm.svg" alt="Support on Ko-fi" style="height: 42px !important;"></a>

---

## 📄 License

This project is licensed under the [GNU General Public License v3.0 or later](LICENSE).
