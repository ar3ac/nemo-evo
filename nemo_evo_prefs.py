#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Nemo Evo Preferences GUI - Graphical Configuration Utility.

Copyright (C) 2026 Nemo Evo Developers
License: GPL-3.0-or-later
"""

import os
import sys
import json
import subprocess
import gettext
import locale

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Gio

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

CONFIG_DIR = os.path.expanduser("~/.config/nemo_evo")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")

ALL_AVAILABLE_BUTTONS = [
    {"id": "cut", "name": _("Cut"), "icon": "edit-cut-symbolic", "shortcut": "Ctrl+X", "enabled": True},
    {"id": "copy", "name": _("Copy"), "icon": "edit-copy-symbolic", "shortcut": "Ctrl+C", "enabled": True},
    {"id": "paste", "name": _("Paste"), "icon": "edit-paste-symbolic", "shortcut": "Ctrl+V", "enabled": True},
    {"id": "trash", "name": _("Move to Trash"), "icon": "user-trash-symbolic", "shortcut": "Canc", "enabled": True},
    {"id": "delete", "name": _("Delete Permanently"), "icon": "edit-delete-symbolic", "shortcut": "Shift+Canc", "enabled": True},
    {"id": "undo", "name": _("Undo"), "icon": "edit-undo-symbolic", "shortcut": "Ctrl+Z", "enabled": False},
    {"id": "redo", "name": _("Redo"), "icon": "edit-redo-symbolic", "shortcut": "Ctrl+Y", "enabled": False},
    {"id": "select_all", "name": _("Select All"), "icon": "edit-select-all-symbolic", "shortcut": "Ctrl+A", "enabled": False},
    {"id": "new_folder", "name": _("New Folder"), "icon": "folder-new-symbolic", "shortcut": "Ctrl+Shift+N", "enabled": False}
]

class NemoEvoPrefsWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title=_("Nemo Evo Preferences"))
        self.set_default_size(520, 580)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_border_width(12)

        # Set window icon
        icon_theme = Gtk.IconTheme.get_default()
        if icon_theme.has_icon("system-file-manager"):
            self.set_icon_name("system-file-manager")

        self.buttons_data = self._load_data()

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.add(main_box)

        # Header
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        header_img = Gtk.Image.new_from_icon_name("system-file-manager", Gtk.IconSize.DIALOG)
        header_box.pack_start(header_img, False, False, 0)

        title_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        title_label = Gtk.Label()
        title_label.set_markup("<b><big>" + _("Nemo Evo Preferences") + "</big></b>")
        title_label.set_xalign(0)
        desc_label = Gtk.Label(label=_("Configure Toolbar Action Buttons for Nemo"))
        desc_label.set_xalign(0)
        title_vbox.pack_start(title_label, False, False, 0)
        title_vbox.pack_start(desc_label, False, False, 0)
        header_box.pack_start(title_vbox, True, True, 0)
        main_box.pack_start(header_box, False, False, 0)

        # Info bar for notifications
        self.infobar = Gtk.InfoBar()
        self.infobar.set_message_type(Gtk.MessageType.INFO)
        self.infobar_label = Gtk.Label()
        self.infobar.get_content_area().add(self.infobar_label)
        self.infobar.set_no_show_all(True)
        main_box.pack_start(self.infobar, False, False, 0)

        # Position selector
        pos_frame = Gtk.Frame(label=_("Toolbar Position"))
        pos_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        pos_box.set_border_width(10)
        
        self.pos_combo = Gtk.ComboBoxText()
        self.pos_combo.append("right_of_pathbar", _("Right of Address Bar (Recommended)"))
        self.pos_combo.append("left_of_pathbar", _("Left of Address Bar"))
        self.pos_combo.append("end_of_toolbar", _("Far Right of Toolbar"))
        self.pos_combo.set_active_id(self.current_position)
        pos_box.pack_start(self.pos_combo, True, True, 0)
        pos_frame.add(pos_box)
        main_box.pack_start(pos_frame, False, False, 0)

        # Buttons List Frame
        btn_frame = Gtk.Frame(label=_("Toolbar Buttons"))
        btn_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        btn_vbox.set_border_width(10)

        hint_label = Gtk.Label(label=_("Enable or disable buttons to display on the toolbar:"))
        hint_label.set_xalign(0)
        btn_vbox.pack_start(hint_label, False, False, 0)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_min_content_height(260)

        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        scrolled.add(self.listbox)
        btn_vbox.pack_start(scrolled, True, True, 0)

        btn_frame.add(btn_vbox)
        main_box.pack_start(btn_frame, True, True, 0)

        self._populate_listbox()

        # Action Buttons
        actions_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        btn_close = Gtk.Button(label=_("Close"))
        btn_close.connect("clicked", lambda b: self.destroy())
        actions_box.pack_end(btn_close, False, False, 0)

        btn_save = Gtk.Button(label=_("Save & Restart Nemo"))
        btn_save.get_style_context().add_class("suggested-action")
        btn_save.connect("clicked", self._on_save_clicked)
        actions_box.pack_end(btn_save, False, False, 0)

        main_box.pack_start(actions_box, False, False, 0)

    def _load_data(self):
        loaded_pos = "right_of_pathbar"
        loaded_buttons = []
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    loaded_pos = cfg.get("position", "right_of_pathbar")
                    loaded_buttons = cfg.get("buttons", [])
            except Exception as e:
                print(f"Error loading config: {e}")

        self.current_position = loaded_pos

        # Merge saved configuration with all available buttons
        saved_dict = {b["id"]: b for b in loaded_buttons}
        result = []
        seen = set()

        # First add in order of saved config
        for b in loaded_buttons:
            bid = b.get("id")
            for av in ALL_AVAILABLE_BUTTONS:
                if av["id"] == bid and bid not in seen:
                    item = dict(av)
                    item["enabled"] = b.get("enabled", True)
                    result.append(item)
                    seen.add(bid)

        # Then append any remaining available buttons
        for av in ALL_AVAILABLE_BUTTONS:
            if av["id"] not in seen:
                result.append(dict(av))
                seen.add(av["id"])

        return result

    def _populate_listbox(self):
        for child in self.listbox.get_children():
            self.listbox.remove(child)

        for idx, item in enumerate(self.buttons_data):
            row = Gtk.ListBoxRow()
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            hbox.set_border_width(6)

            # Checkbox
            check = Gtk.CheckButton()
            check.set_active(item.get("enabled", True))
            check.connect("toggled", self._on_toggle, idx)
            hbox.pack_start(check, False, False, 0)

            # Icon
            img = Gtk.Image.new_from_icon_name(item.get("icon", ""), Gtk.IconSize.MENU)
            hbox.pack_start(img, False, False, 0)

            # Label & Shortcut
            lbl = Gtk.Label()
            lbl.set_markup(f"<b>{item.get('name')}</b> <small>({item.get('shortcut')})</small>")
            lbl.set_xalign(0)
            hbox.pack_start(lbl, True, True, 0)

            # Reorder buttons: Up and Down
            btn_up = Gtk.Button.new_from_icon_name("go-up-symbolic", Gtk.IconSize.MENU)
            btn_up.set_relief(Gtk.ReliefStyle.NONE)
            btn_up.set_sensitive(idx > 0)
            btn_up.connect("clicked", self._on_move_up, idx)
            hbox.pack_start(btn_up, False, False, 0)

            btn_down = Gtk.Button.new_from_icon_name("go-down-symbolic", Gtk.IconSize.MENU)
            btn_down.set_relief(Gtk.ReliefStyle.NONE)
            btn_down.set_sensitive(idx < len(self.buttons_data) - 1)
            btn_down.connect("clicked", self._on_move_down, idx)
            hbox.pack_start(btn_down, False, False, 0)

            row.add(hbox)
            self.listbox.add(row)

        self.listbox.show_all()

    def _on_toggle(self, check, idx):
        self.buttons_data[idx]["enabled"] = check.get_active()

    def _on_move_up(self, btn, idx):
        if idx > 0:
            self.buttons_data[idx - 1], self.buttons_data[idx] = self.buttons_data[idx], self.buttons_data[idx - 1]
            self._populate_listbox()

    def _on_move_down(self, btn, idx):
        if idx < len(self.buttons_data) - 1:
            self.buttons_data[idx + 1], self.buttons_data[idx] = self.buttons_data[idx], self.buttons_data[idx + 1]
            self._populate_listbox()

    def _on_save_clicked(self, btn):
        pos = self.pos_combo.get_active_id() or "right_of_pathbar"
        to_save = {
            "version": 1,
            "position": pos,
            "buttons": [
                {
                    "id": b["id"],
                    "enabled": b["enabled"],
                    "icon": b["icon"],
                    "shortcut": b["shortcut"]
                }
                for b in self.buttons_data
            ]
        }

        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(to_save, f, indent=2, ensure_ascii=False)

        # Restart Nemo to reload extensions
        try:
            subprocess.run(["nemo", "-q"], check=False)
        except Exception as e:
            print(f"Error quitting nemo: {e}")

        self.infobar_label.set_text(_("Configuration saved successfully!"))
        self.infobar.show_all()

def main():
    app = NemoEvoPrefsWindow()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
