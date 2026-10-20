#!/usr/bin/env python3
"""Bin2Dec: conversor binario <-> decimal en tiempo real."""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk

MAX_BITS = 64
MAX_VALUE = (1 << MAX_BITS) - 1


def group_binary(digits):
    """Agrupa digitos binarios de 4 en 4 con espacios."""
    return " ".join(digits[i : i + 4] for i in range(0, len(digits), 4))


class Bin2DecWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="Bin2Dec", default_width=420)
        self._updating = False
        self._last_edited = "dec"

        toolbar_view = Adw.ToolbarView()
        header = Adw.HeaderBar()
        header.set_title_widget(Adw.WindowTitle.new("Bin2Dec", "Conversor binario ↔ decimal"))

        copy_button = Gtk.Button.new_from_icon_name("edit-copy-symbolic")
        copy_button.set_tooltip_text("Copiar resultado")
        copy_button.connect("clicked", self.on_copy)
        header.pack_end(copy_button)

        clear_button = Gtk.Button.new_from_icon_name("edit-clear-symbolic")
        clear_button.set_tooltip_text("Limpiar")
        clear_button.connect("clicked", self.on_clear)
        header.pack_start(clear_button)

        toolbar_view.add_top_bar(header)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        content.set_margin_top(24)
        content.set_margin_bottom(24)
        content.set_margin_start(24)
        content.set_margin_end(24)

        self.decimal_entry = Gtk.Entry()
        self.decimal_entry.set_placeholder_text("Decimal (solo positivos)")
        self.decimal_entry.connect("changed", self.on_decimal_changed)
        content.append(self.decimal_entry)

        self.binary_entry = Gtk.Entry()
        self.binary_entry.set_placeholder_text("Binario (solo 0 y 1)")
        self.binary_entry.connect("changed", self.on_binary_changed)
        content.append(self.binary_entry)

        self.status_label = Gtk.Label(label="")
        self.status_label.add_css_class("dim-label")
        content.append(self.status_label)

        toolbar_view.set_content(content)
        self.set_content(toolbar_view)

    # --- conversion -------------------------------------------------------------

    def on_decimal_changed(self, entry):
        if self._updating:
            return
        self._last_edited = "dec"
        text = entry.get_text().strip()
        self._updating = True
        if text == "":
            self._set_valid(entry)
            self.binary_entry.set_text("")
            self.status_label.set_text("")
        elif text.isdigit() and int(text) <= MAX_VALUE:
            self._set_valid(entry)
            self.binary_entry.set_text(group_binary(format(int(text), "b")))
            self.status_label.set_text("")
        else:
            self._set_invalid(entry)
            self.binary_entry.set_text("")
            self.status_label.set_text("Número decimal no válido")
        self._updating = False

    def on_binary_changed(self, entry):
        if self._updating:
            return
        self._last_edited = "bin"
        digits = entry.get_text().replace(" ", "")
        self._updating = True
        if digits == "":
            self._set_valid(entry)
            self.decimal_entry.set_text("")
            self.status_label.set_text("")
        elif set(digits) <= {"0", "1"} and len(digits) <= MAX_BITS:
            self._set_valid(entry)
            self.decimal_entry.set_text(str(int(digits, 2)))
            self.status_label.set_text("")
        else:
            self._set_invalid(entry)
            self.decimal_entry.set_text("")
            self.status_label.set_text("Número binario no válido (máx. 64 dígitos, solo 0 y 1)")
        self._updating = False

    def _set_valid(self, entry):
        entry.remove_css_class("error")

    def _set_invalid(self, entry):
        entry.add_css_class("error")

    # --- acciones ---------------------------------------------------------------

    def on_copy(self, _button):
        # Copia el campo que NO fue el ultimo editado (el resultado).
        if self._last_edited == "dec":
            text = self.binary_entry.get_text()
        else:
            text = self.decimal_entry.get_text()
        if text:
            self.get_clipboard().set(text)
            self.status_label.set_text("Resultado copiado")

    def on_clear(self, _button):
        self._updating = True
        self.decimal_entry.set_text("")
        self.binary_entry.set_text("")
        self._updating = False
        self._set_valid(self.decimal_entry)
        self._set_valid(self.binary_entry)
        self.status_label.set_text("")


class Bin2DecApp(Adw.Application):
    def do_activate(self):
        Bin2DecWindow(self).present()


if __name__ == "__main__":
    Bin2DecApp(application_id="com.github.vishoo.bin2dec").run([])
