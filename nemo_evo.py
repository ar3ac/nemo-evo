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

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('Nemo', '3.0')
from gi.repository import GObject, Nemo, Gtk, Gdk

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
except Exception as e:
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

    # If file doesn't exist, create it with default configuration
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[NemoEvo] Error writing default config: {e}")

    return DEFAULT_CONFIG

# ----------------------------------------------------------------------
# Helper Utilities
# ----------------------------------------------------------------------
def send_key(window, keyval, state=0):
    """Synthesize a hardware key event sent to GDK event loop."""
    seat = Gdk.Display.get_default().get_default_seat()
    dev = seat.get_keyboard() if seat else None
    gdk_win = window.get_window()

    ev_press = Gdk.Event.new(Gdk.EventType.KEY_PRESS)
    ev_press.keyval = keyval
    ev_press.state = state
    ev_press.window = gdk_win
    if dev:
        ev_press.set_device(dev)
    ev_press.put()

    ev_release = Gdk.Event.new(Gdk.EventType.KEY_RELEASE)
    ev_release.keyval = keyval
    ev_release.state = state
    ev_release.window = gdk_win
    if dev:
        ev_release.set_device(dev)
    ev_release.put()

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

def ensure_view_focus(window):
    """Ensure focus is on the file view unless user is in an entry/input widget."""
    focus = window.get_focus()
    if focus and isinstance(focus, Gtk.Entry):
        return
    view = find_active_view(window)
    if view and hasattr(view, "grab_focus"):
        view.grab_focus()

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

        # Reload config in case it changed
        self.config = load_config()

        # Find primary toolbar
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

        # Definitions of button metadata and handlers
        button_definitions = {
            "cut": {
                "label": _("Cut (Ctrl+X)"),
                "handler": lambda btn: (ensure_view_focus(window), send_key(window, Gdk.KEY_x, Gdk.ModifierType.CONTROL_MASK))
            },
            "copy": {
                "label": _("Copy (Ctrl+C)"),
                "handler": lambda btn: (ensure_view_focus(window), send_key(window, Gdk.KEY_c, Gdk.ModifierType.CONTROL_MASK))
            },
            "paste": {
                "label": _("Paste (Ctrl+V)"),
                "handler": lambda btn: (ensure_view_focus(window), send_key(window, Gdk.KEY_v, Gdk.ModifierType.CONTROL_MASK))
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
                "handler": lambda btn: (ensure_view_focus(window), send_key(window, Gdk.KEY_z, Gdk.ModifierType.CONTROL_MASK))
            },
            "redo": {
                "label": _("Redo (Ctrl+Y)"),
                "handler": lambda btn: (ensure_view_focus(window), send_key(window, Gdk.KEY_y, Gdk.ModifierType.CONTROL_MASK))
            },
            "select_all": {
                "label": _("Select All (Ctrl+A)"),
                "handler": lambda btn: (ensure_view_focus(window), send_key(window, Gdk.KEY_a, Gdk.ModifierType.CONTROL_MASK))
            },
            "new_folder": {
                "label": _("New Folder (Ctrl+Shift+N)"),
                "handler": lambda btn: (ensure_view_focus(window), send_key(window, Gdk.KEY_n, Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.SHIFT_MASK))
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
        """Locates the GtkToolItem that contains the GtkStack/PathBar."""
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
        ensure_view_focus(window)
        view = find_active_view(window)
        if view:
            try:
                view.emit("trash")
                return
            except Exception:
                pass
        send_key(window, Gdk.KEY_Delete, 0)

    def _handle_delete(self, window):
        ensure_view_focus(window)
        view = find_active_view(window)
        if view:
            try:
                view.emit("delete")
                return
            except Exception:
                pass
        send_key(window, Gdk.KEY_Delete, Gdk.ModifierType.SHIFT_MASK)
