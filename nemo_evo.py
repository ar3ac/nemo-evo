#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Nemo Evo - Customizable Action Buttons Toolbar Extension for Nemo File Manager.
Adds Cut, Copy, Paste, Trash, Delete, and other configurable action buttons
directly next to Nemo's address / path bar.

Copyright (C) 2026 Nemo Evo Developers
License: GPL-3.0-or-later
"""

import os
import json
import gettext
import locale
import ctypes

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('Nemo', '3.0')
from gi.repository import GObject, Nemo, Gtk, Gdk, GLib

# ----------------------------------------------------------------------
# X11 XTest Direct Hardware Keyboard Emulation (64-bit safe)
# ----------------------------------------------------------------------
_x11 = None
_xtst = None
_HAS_XTEST = False

try:
    _x11 = ctypes.CDLL('libX11.so.6')
    _xtst = ctypes.CDLL('libXtst.so.6')

    # Strictly define 64-bit argument and return types to prevent pointer truncation
    _x11.XOpenDisplay.restype = ctypes.c_void_p
    _x11.XOpenDisplay.argtypes = [ctypes.c_char_p]

    _x11.XCloseDisplay.restype = ctypes.c_int
    _x11.XCloseDisplay.argtypes = [ctypes.c_void_p]

    _x11.XFlush.restype = ctypes.c_int
    _x11.XFlush.argtypes = [ctypes.c_void_p]

    _x11.XStringToKeysym.restype = ctypes.c_ulong
    _x11.XStringToKeysym.argtypes = [ctypes.c_char_p]

    _x11.XKeysymToKeycode.restype = ctypes.c_ubyte
    _x11.XKeysymToKeycode.argtypes = [ctypes.c_void_p, ctypes.c_ulong]

    _xtst.XTestFakeKeyEvent.restype = ctypes.c_int
    _xtst.XTestFakeKeyEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int, ctypes.c_ulong]

    _HAS_XTEST = True
except Exception as e:
    print(f"[NemoEvo] XTest initialization warning: {e}")
    _HAS_XTEST = False

def send_x11_shortcut(*keysym_names):
    """Sends authentic hardware keyboard shortcut via X11 XTest safely."""
    if not _HAS_XTEST or not _x11 or not _xtst:
        return False
    try:
        d = _x11.XOpenDisplay(None)
        if not d:
            return False
        try:
            codes = []
            for name in keysym_names:
                sym = _x11.XStringToKeysym(name.encode('ascii'))
                if sym:
                    code = _x11.XKeysymToKeycode(d, sym)
                    if code:
                        codes.append(code)

            if not codes:
                return False

            # Press keys in order
            for c in codes:
                _xtst.XTestFakeKeyEvent(d, c, True, 0)
            _x11.XFlush(d)

            # Release keys in reverse order
            for c in reversed(codes):
                _xtst.XTestFakeKeyEvent(d, c, False, 0)
            _x11.XFlush(d)
            return True
        finally:
            _x11.XCloseDisplay(d)
    except Exception as e:
        print(f"[NemoEvo] Error sending shortcut {keysym_names}: {e}")
        return False

# ----------------------------------------------------------------------
# Internationalization (i18n)
# ----------------------------------------------------------------------
TEXTDOMAIN = "nemo-evo"
POSSIBLE_LOCALE_DIRS = [
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "locale"),
    os.path.expanduser("~/.local/share/locale"),
    "/usr/share/locale"
]

LOCALEDIR = None
for ldir in POSSIBLE_LOCALE_DIRS:
    if os.path.exists(ldir):
        LOCALEDIR = ldir
        break

try:
    if LOCALEDIR:
        locale.bindtextdomain(TEXTDOMAIN, LOCALEDIR)
        gettext.bindtextdomain(TEXTDOMAIN, LOCALEDIR)
    gettext.textdomain(TEXTDOMAIN)
except Exception:
    pass

_ = gettext.gettext

# ----------------------------------------------------------------------
# Configuration Handling
# ----------------------------------------------------------------------
CONFIG_DIR = os.path.expanduser("~/.config/nemo_evo")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")

DEFAULT_CONFIG = {
    "version": 1,
    "position": "right_of_pathbar",
    "buttons": [
        {"id": "cut", "enabled": True, "icon": "edit-cut-symbolic", "shortcut": "Ctrl+X"},
        {"id": "copy", "enabled": True, "icon": "edit-copy-symbolic", "shortcut": "Ctrl+C"},
        {"id": "paste", "enabled": True, "icon": "edit-paste-symbolic", "shortcut": "Ctrl+V"},
        {"id": "trash", "enabled": True, "icon": "user-trash-symbolic", "shortcut": "Canc"},
        {"id": "delete", "enabled": True, "icon": "edit-delete-symbolic", "shortcut": "Shift+Canc"},
        {"id": "undo", "enabled": False, "icon": "edit-undo-symbolic", "shortcut": "Ctrl+Z"},
        {"id": "redo", "enabled": False, "icon": "edit-redo-symbolic", "shortcut": "Ctrl+Y"},
        {"id": "select_all", "enabled": False, "icon": "edit-select-all-symbolic", "shortcut": "Ctrl+A"},
        {"id": "new_folder", "enabled": False, "icon": "folder-new-symbolic", "shortcut": "Ctrl+Shift+N"}
    ]
}

def load_config():
    if not os.path.exists(CONFIG_DIR):
        try:
            os.makedirs(CONFIG_DIR, exist_ok=True)
        except Exception:
            pass

    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[NemoEvo] Error loading config: {e}, falling back to defaults")

    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[NemoEvo] Error writing default config: {e}")

    return DEFAULT_CONFIG

# ----------------------------------------------------------------------
# View Helpers
# ----------------------------------------------------------------------
def find_active_view(window):
    """Find the active NemoView in the given window."""
    focus = window.get_focus()
    w = focus
    while w is not None:
        gtype = GObject.type_name(w)
        if 'View' in gtype and 'Nemo' in gtype:
            return w
        w = w.get_parent()

    def scan(widget):
        gtype = GObject.type_name(widget)
        if 'View' in gtype and 'Nemo' in gtype:
            return widget
        if isinstance(widget, Gtk.Container):
            for c in widget.get_children():
                res = scan(c)
                if res:
                    return res
        return None

    return scan(window)

# ----------------------------------------------------------------------
# Nemo Extension Implementation
# ----------------------------------------------------------------------
class NemoEvoExtension(GObject.GObject, Nemo.LocationWidgetProvider, Nemo.NameAndDescProvider):
    """Nemo extension that injects custom action buttons into the primary toolbar."""

    def __init__(self):
        super().__init__()
        self.config = load_config()

    def get_name_and_desc(self):
        return [
            ("NemoEvo", _("Custom action buttons for Nemo toolbar (Cut, Copy, Paste, Trash, Delete)"))
        ]

    def get_widget(self, uri, window):
        # Ignore desktop window
        if uri.startswith("x-nemo-desktop:///"):
            return None

        # Prevent duplicate injection per window
        if getattr(window, "_nemo_evo_injected", False):
            return None
        window._nemo_evo_injected = True

        self.config = load_config()

        toolbar = self._find_primary_toolbar(window)
        if not toolbar:
            return None

        self._inject_buttons(window, toolbar)
        return None

    def _find_primary_toolbar(self, window):
        def scan(w):
            if isinstance(w, Gtk.Toolbar):
                ctx = w.get_style_context()
                if ctx and 'primary-toolbar' in ctx.list_classes():
                    return w
            if isinstance(w, Gtk.Container):
                for c in w.get_children():
                    res = scan(c)
                    if res:
                        return res
            return None
        return scan(window)

    def _inject_buttons(self, window, toolbar):
        enabled_buttons = [b for b in self.config.get("buttons", []) if b.get("enabled", True)]
        if not enabled_buttons:
            return

        tool_item = Gtk.ToolItem()
        tool_item.set_name("nemo-evo-toolbar-item")

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
        tool_item.add(box)

        # Trigger shortcut safely in idle callback
        def trigger_shortcut(*keys):
            GLib.idle_add(send_x11_shortcut, *keys)

        button_definitions = {
            "cut": {
                "label": _("Cut (Ctrl+X)"),
                "handler": lambda btn: trigger_shortcut("Control_L", "x")
            },
            "copy": {
                "label": _("Copy (Ctrl+C)"),
                "handler": lambda btn: trigger_shortcut("Control_L", "c")
            },
            "paste": {
                "label": _("Paste (Ctrl+V)"),
                "handler": lambda btn: trigger_shortcut("Control_L", "v")
            },
            "trash": {
                "label": _("Move to Trash (Delete)"),
                "handler": lambda btn: self._handle_trash(window)
            },
            "delete": {
                "label": _("Delete Permanently (Shift+Delete)"),
                "handler": lambda btn: self._handle_delete(window)
            },
            "undo": {
                "label": _("Undo (Ctrl+Z)"),
                "handler": lambda btn: trigger_shortcut("Control_L", "z")
            },
            "redo": {
                "label": _("Redo (Ctrl+Y)"),
                "handler": lambda btn: trigger_shortcut("Control_L", "y")
            },
            "select_all": {
                "label": _("Select All (Ctrl+A)"),
                "handler": lambda btn: trigger_shortcut("Control_L", "a")
            },
            "new_folder": {
                "label": _("New Folder (Ctrl+Shift+N)"),
                "handler": lambda btn: trigger_shortcut("Control_L", "Shift_L", "n")
            }
        }

        for b_conf in enabled_buttons:
            bid = b_conf.get("id")
            if bid not in button_definitions:
                continue

            bdef = button_definitions[bid]
            icon_name = b_conf.get("icon", "dialog-information-symbolic")
            tooltip = bdef["label"]

            btn = Gtk.Button()
            btn.set_can_focus(False)
            btn.set_focus_on_click(False)
            btn.set_tooltip_text(tooltip)
            btn.get_style_context().add_class(Gtk.STYLE_CLASS_FLAT)
            img = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.MENU)
            btn.set_image(img)
            btn.connect("clicked", bdef["handler"])

            box.pack_start(btn, False, False, 0)

        tool_item.show_all()
        tool_item.set_margin_left(4)
        tool_item.set_margin_right(4)

        # Determine insertion index
        position = self.config.get("position", "right_of_pathbar")
        pathbar_index = self._find_pathbar_tool_item_index(toolbar)

        if position == "left_of_pathbar" and pathbar_index != -1:
            toolbar.insert(tool_item, pathbar_index)
        elif position == "end_of_toolbar":
            toolbar.insert(tool_item, -1)
        else:
            # Default: right_of_pathbar
            if pathbar_index != -1:
                toolbar.insert(tool_item, pathbar_index + 1)
            else:
                toolbar.insert(tool_item, -1)

    def _find_pathbar_tool_item_index(self, toolbar):
        def contains_stack(container):
            if isinstance(container, Gtk.Stack):
                return True
            if isinstance(container, Gtk.Container):
                for child in container.get_children():
                    if contains_stack(child):
                        return True
            return False

        for idx, item in enumerate(toolbar.get_children()):
            if contains_stack(item):
                return idx
        return -1

    def _handle_trash(self, window):
        view = find_active_view(window)
        if view:
            try:
                view.emit("trash")
                return
            except Exception:
                pass
        send_x11_shortcut("Delete")

    def _handle_delete(self, window):
        view = find_active_view(window)
        if view:
            try:
                view.emit("delete")
                return
            except Exception:
                pass
        send_x11_shortcut("Shift_L", "Delete")
